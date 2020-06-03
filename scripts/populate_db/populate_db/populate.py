import argparse
import asyncio
from os import environ
import json
from typing import Dict

import asyncpg
from asyncpg.connection import Connection

from populate_db.iso693_3 import ISO_693_3


async def store_language_codes(conn: Connection) -> Dict:
    """Store the language codes and return the code -> id dictionary.
    """
    languages_ids = {}
    async with conn.transaction():
        for i, (lang_code, lang_name) in enumerate(ISO_693_3.items()):
            await conn.execute(
                """INSERT INTO languages(
                    id,
                    iso693_3,
                    name)
                    VALUES ($1, $2, $3)""",
                i, lang_code, lang_name
                )
            languages_ids[lang_code] = i
    return languages_ids


async def main(jsonl_file: str):
    conn = await asyncpg.connect(dsn=environ['PG_CONN_STR'])
    languages_ids = await store_language_codes(conn)
    pending = []
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
        except KeyError:
            print(f'Error processing a row: {line}')
        if len(pending) > 5000:
            async with conn.transaction():
                # much slower but allows to specify the target columns:
                # await conn.executemany(
                #     """INSERT INTO cards(
                #         from_lang,
                #         to_lang,
                #         from_id,
                #         to_id,
                #         from_txt,
                #         original_txt,
                #         to_tokens
                #     ) VALUES ($1, $2, $3, $4, $5, $6, $7)""",
                #     pending
                # )
                await conn.copy_records_to_table(
                    'cards',
                    records=pending,
                )
            pending = []
            print(f'Ingested {idx} so far...')
    print('Almost done, writing the remaining entries...')
    async with conn.transaction():
        await conn.copy_records_to_table(
                        'cards',
                        records=pending,
                    )
    print(f'Done!')
    await conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'cards_file', help='the JSONL file to import', type=str)
    args = parser.parse_args()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args.cards_file))
