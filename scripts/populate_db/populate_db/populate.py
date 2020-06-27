import argparse
import asyncio
from os import environ
import logging
import json
from time import time
from typing import Dict

import asyncpg
from asyncpg.connection import Connection

from populate_db.iso693_3 import ISO_693_3

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
)

logger = logging.getLogger(__name__)


async def store_language_codes(conn: Connection) -> Dict[str, int]:
    """Update the language codes and return the code -> id dictionary.

    The DB is updated if the name changed or a language is new.

    If a language is in the DB but not in the hardcoded list, an exception is raised.

    Returns
    -------
    Dict[str, int]
        A dictionary mapping the ISO code of a language with its ID

    Raises
    ------
    ValueError
        In case a language was in the DB but not in the hardcoded list
    """
    languages_ids = {}  # ISO -> (id, name)
    max_id = 0
    async with conn.transaction():
        res = await conn.fetch('SELECT id, name, iso693_3 FROM language')
        for lng in res:
            languages_ids[lng['iso693_3']] = (lng['id'], lng['name'])
            if max_id < lng['id']:
                max_id = languages_ids['id']
    for iso, name in ISO_693_3.items():
        if iso in languages_ids:
            pre_name = languages_ids[iso][1]
            # different name? update it
            if pre_name != name:
                logger.info(
                    f'Language with ISO {iso} is now named {name} instead of {pre_name}'
                    )
                await conn.execute(
                    """UPDATE language
                        SET name = $1
                        WHERE iso693_3 = $2
                    """,
                    name,
                    iso,
                )
        else:
            # not there, insert it
            max_id += 1
            logger.info(f'New language, {iso} => {name} will have id {max_id}')
            languages_ids[iso] = (max_id, name)
            await conn.execute(
                """INSERT INTO language(
                    id,
                    iso693_3,
                    name)
                    VALUES ($1, $2, $3)""",
                max_id, iso, name
                )
    # now all of ISO_693_3 elements are in the DB and in language_ids
    # let's check for language_ids which are gone

    gone_languages = set(languages_ids.keys()).difference(ISO_693_3.keys())
    if len(gone_languages) > 0:
        raise ValueError(
            f'Some languages are in the DB but are unknow! They are {gone_languages}'
        )

    return {iso: id_ for iso, (id_, _) in languages_ids.items()}


async def create_staging_table(conn: Connection):
    """Create a staging table for the cards, empties it if it exists.

    Note that the table is unlogged, so it's supposed to be used for this
    operation only, then lost.
    """
    async with conn.transaction():
        await conn.execute("DROP TABLE IF EXISTS card_stg")
    async with conn.transaction():
        await conn.execute("""
        CREATE UNLOGGED TABLE card_stg (
            from_lang    SMALLINT NOT NULL,
            to_lang      SMALLINT NOT NULL,
            from_id      INTEGER  NOT NULL,
            to_id        INTEGER  NOT NULL,
            from_txt     TEXT     NOT NULL,
            original_txt TEXT     NOT NULL,
            to_tokens    TEXT[]   NOT NULL
        ) PARTITION BY HASH (from_id, to_id);
        """)
        for i in range(10):
            await conn.execute(f"""
        CREATE UNLOGGED TABLE card_stg_h{i}
            PARTITION OF card_stg
                FOR VALUES WITH (MODULUS 10, REMAINDER {i});
        """)


async def delete_staging_table(conn: Connection):
    """Delete the staging table."""
    async with conn.transaction():
        await conn.execute("DROP TABLE card_stg")


async def ingest_cards_file(
        conn: Connection, jsonl_file: str, languages_ids: Dict[str, int]):
    """Insert a cards file in the staging table card_stg."""
    pending = []
    last_update = time()
    for idx, line in enumerate(open(jsonl_file)):
        card = json.loads(line)
        try:
            pending.append((
                languages_ids[card['from_lang']],
                languages_ids[card['to_lang']],
                card['from_id'],
                card['to_id'],
                card['from_txt'],
                card['original_txt'],
                card['resulting_tokens'],
            ))
        except KeyError as ke:
            # missing language or weird line
            logger.warning(f'Error processing a row: {line}: {ke}')
        if len(pending) > 2000:
            async with conn.transaction():
                await conn.copy_records_to_table(
                    'card_stg',
                    records=pending,
                )
            pending = []
            if time() > last_update + 60:
                logger.debug(f'Ingested {idx} so far...')
                last_update = time()
    logger.debug('Almost done, writing the remaining entries...')
    async with conn.transaction():
        await conn.copy_records_to_table(
            'card_stg',
            records=pending,
        )


async def merge_tables(conn: Connection, p_id: int):
    """Merge the staging table and the final one."""
    async with conn.transaction():
        logger.debug('Detecting cards no longer valid...')
        res = await conn.fetchrow(f"""
            SELECT count(1) AS to_delete
            FROM card_h{p_id} c
                LEFT JOIN card_stg_h{p_id} s
                USING (from_id, to_id)
            WHERE c.from_id IS NULL
            """)
        if res['to_delete'] > 100:
            # around 10 cards are deleted per day, too many may be an issue with the
            # file, so better stop rather than deleting everything
            raise ValueError(f"Suspect number of cards to delete: {res['to_delete']}")
        if res['to_delete'] > 0:
            logger.info(f"Deleting these {res['to_delete']} cards")
            await conn.execute("""
                DELETE
                FROM card_h{p_id}
                WHERE
                    (from_lang, to_lang) IN
                    (
                        SELECT
                            c.from_lang,
                            c.to_lang
                        FROM card_h{p_id} c
                            LEFT JOIN card_stg_h{p_id} s
                                USING (from_id, to_id)
                        WHERE
                            c.from_id IS NULL)
                """)
        else:
            logger.info('There were no cards to delete')
        logger.info('Updating the cards which changed...')
        res = await conn.fetchrow(f"""
                UPDATE card_h{p_id} c
                SET
                    from_txt     = s.from_txt,
                    original_txt = s.original_txt,
                    to_tokens    = s.to_tokens
                FROM card_stg_h{p_id} s
                WHERE
                    c.from_id = s.from_id
                AND c.to_id = s.to_id
                AND (
                        c.from_txt <> s.from_txt
                    OR  c.original_txt <> s.original_txt
                    OR  c.to_tokens   <> s.to_tokens
                    )
            """)
        logger.info(f'Update successful: changes {res}')
        logger.info('Inserting new cards...')
        res = await conn.fetchrow(f"""
        INSERT INTO card_h{p_id}
            SELECT
                s.*
            FROM
                card_stg_h{p_id} s
                LEFT JOIN card_h{p_id} c
                    USING(from_id, to_id)
            WHERE
                c.from_lang IS NULL
        """)


async def main(jsonl_file: str):
    conn = await asyncpg.connect(dsn=environ['PG_CONN_STR'])
    language_ids = await store_language_codes(conn)
    logger.info(f'There are {len(language_ids)} total languages')
    await create_staging_table(conn)
    logger.info('Staging table ready, ingesting the cards...')
    await ingest_cards_file(conn, jsonl_file, language_ids)
    logger.info('Staging table ingested!')
    for i in range(10):
        logger.info(f'Merging partition {i}')
        await merge_tables(conn, i)
    await delete_staging_table(conn)
    # TODO and maybe also a VACUUM ANALYZE to be safe
    await conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'cards_file', help='the JSONL file to import', type=str)
    args = parser.parse_args()
    # this is not taking advantage of any async operation
    # but the library is used in the app so it's used here for consistency
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args.cards_file))
