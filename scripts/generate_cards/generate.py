import argparse
from collections import Counter
from csv import reader
import json
from random import Random
from sys import maxunicode
from unicodedata import category

import icu

# word breakers instances
_breakers = {}

# translation table to remove punctuation or spaces
# this covers all punctuation in the Unicode
PUNCT_TRANSL = dict.fromkeys(
    i for i in range(maxunicode)
    if category(chr(i)).startswith('P')
    )


# how likely is to add an extra cloze
ANOTHER_CLOZE_FACTOR = 4

# how often to add a fake cloze that doesn't replace anything
EMPTY_CLOZE_FACTOR = 100

# how often a space should be tolerated as a cloze
TOLERATE_SPACE_FACTOR = 20

# how many most-common words will be replaced by clozes
WORD_MIN_RANK = 1000

# evil evil words to not cover with the cloze
FORBIDDEN_CLOZE_TOKENS = {'Tom', 'Mary', 'Muriel', 'Layla'}

# how long (characters) can a sentence be to be accepted
MAX_SENTENCE_LENGTH = 250


def normalized(text: str):
    """Remove ounctuation from a token.

    This is used to allow comparison of tokens to extract the frequency,
    but does not affect the tokens that are saved.

    A string containing only punctuation becomes empty.
    """
    return text.translate(PUNCT_TRANSL).lower()


def tokenize(text: str, lang: str):
    """Split a string into tokens."""
    # Is there no word breaker already set up? Instantiate it
    if lang not in _breakers:
        _breakers[lang] = (
            icu.BreakIterator.createWordInstance(icu.Locale(lang))
            )

    _breakers[lang].setText(text)
    boundaries = list(_breakers[lang])
    return [text[i:j] for i, j in zip([0] + boundaries, boundaries)]

    # any other language, just use spaces
    return text.split()


def main_multi(sentence_file: str, link_file: str):
    """Produce the cloze deletion cards.

    This will produce them for all the language pairs!.
    """
    sents = reader(open(sentence_file), delimiter='\t')
    links = reader(open(link_file), delimiter='\t')

    id_sents = {}  # id -> (lang, text)
    langs = set()  # set of seen lanuages
    word_counters = {}  # lang -> Counter
    print(f'Processing files {sentence_file}, {link_file}...')
    for idx, [_id, lang, text] in enumerate(sents):
        if idx % 200_000 == 0:
            print(f'Read {idx} rows from the sentences CSV so far')
        if len(text) > MAX_SENTENCE_LENGTH or len(text) < 20:
            continue
        id_sents[int(_id)] = (lang, text)
        if lang not in word_counters:
            word_counters[lang] = Counter()
        word_counters[lang].update(
            [normalized(token) for token in tokenize(text, lang)]
        )
        langs.add(lang)
    print(f'Imported {len(id_sents)} sentences')

    most_commons = {}
    for l in langs:
        # Note that in here there is an empty string,
        # that's normalized punctuation. Also, a space.
        word_counters[l].pop('', None)
        most_commons[l] = set(
            w for w, _ in word_counters[l].most_common(WORD_MIN_RANK)
            )
    del word_counters

    pairs = []
    for idx, [from_id, to_id] in enumerate(links):
        from_id = int(from_id)
        to_id = int(to_id)
        if idx % 100_000 == 0:
            print(f'Read {idx} rows from the links CSV so far')
        if from_id not in id_sents or to_id not in id_sents:
            continue
        pairs.append(
            (
                id_sents[from_id][0],  # from language
                id_sents[to_id][0],  # to language
                from_id,  # from sentence id
                to_id,  # to sentence id
                id_sents[from_id][1],  # from text
                id_sents[to_id][1],  # to text
            )
        )

    print(f'Found {len(pairs)} sentence pairs, shuffling...')
    # this is because similar sentences are inserted close in time
    # by shuffling they will be inserted in random order and an unsorted
    # select in postgres will give them in that order in the current
    # implementation. Decent random sampling from the DB is a bit expensive
    Random().shuffle(pairs)
    print('Shuffled')
    out = open('universal_cards.tsv', 'w')
    out_details = open('universal_cards.jsonl', 'w')
    for idx, (
        from_lang,
        to_lang,
        from_id,
        to_id,
        from_txt,
        to_txt
            ) in enumerate(pairs):
        tokens = tokenize(to_txt, to_lang)
        # we must be sure this is always valid or the cards are wrong!
        assert to_txt == ''.join(tokens)
        cloze_idx = 1
        if idx % 50_000 == 0:
            print(f'Written {idx} cards out of {len(pairs)} so far')
        # use the card content to make it deterministic
        r = Random(to_txt)
        # do a number of attempts to insert a cloze following some rules
        for _ in range(20):
            to_replace_idx = r.randint(0, len(tokens) - 1)
            # no cloze of a cloze
            if tokens[to_replace_idx].startswith('{{'):
                continue
            # do not put cloze after empty cloze or space
            if (
                    to_replace_idx > 0
                    and (
                        tokens[to_replace_idx - 1].endswith('::-}}')
                        or tokens[to_replace_idx - 1].endswith(':: }}')
                        )
                    ):
                continue
            # only the most common words
            if (normalized(tokens[to_replace_idx])
                    not in most_commons[to_lang]):
                continue
            if tokens[to_replace_idx] == ' ':
                if r.randint(0, TOLERATE_SPACE_FACTOR) > 0:
                    continue
                # if the next element is a cloze, do not replace or would
                # be ambiguous for the user
                if (to_replace_idx < len(tokens) - 1
                        and tokens[to_replace_idx + 1].startswith('{{')):
                        continue
            # ignore forbidden words
            if tokens[to_replace_idx] in FORBIDDEN_CLOZE_TOKENS:
                continue
            tokens[to_replace_idx] = ''.join([
                '{{c',
                str(cloze_idx),
                '::',
                tokens[to_replace_idx],
                '}}'
            ])
            cloze_idx += 1

            if r.randint(0, EMPTY_CLOZE_FACTOR) == 0:
                to_insert_idx = r.randint(0, len(tokens) - 1)
                # do it only if there'not a cloze on the right
                # otherwise the user has no way to know this is a fake one
                if (
                    to_insert_idx == len(tokens) - 1
                        or not tokens[to_insert_idx].startswith('{{')):
                    tokens.insert(
                        to_insert_idx,
                        '{{c' + str(cloze_idx) + '::-}}'
                    )
                    cloze_idx += 1

            if r.randint(0, ANOTHER_CLOZE_FACTOR) == 0:
                continue
            break

        if cloze_idx == 1:
            continue
        out.write(from_txt)
        out.write('<br>')
        out.write(' '.join(tokens))
        out.write('\n')

        out_details.write(json.dumps(dict(
            from_lang=from_lang,
            to_lang=to_lang,
            from_id=from_id,
            to_id=to_id,
            from_txt=from_txt,
            original_txt=to_txt,
            resulting_tokens=tokens,
        )))
        out_details.write('\n')
    out.close()
    out_details.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('sentences', help='the sentence CSV file', type=str)
    parser.add_argument('links', help='the links CSV file', type=str)
    args = parser.parse_args()
    main_multi(args.sentences, args.links)
