import argparse
from collections import Counter
from csv import reader
import json
from random import Random
from sys import maxunicode
from typing import Dict, Tuple, Set
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
ANOTHER_CLOZE_FACTOR = 2

# how likely to not insert a base form when possible but hide the cloze completely
# if a dictionary form was always shown when available, the user would learn its
# presence as a fact marking the type of word, which invalidates the efficacy of
# cloze deletion. So sometimes they are hidden nonetheless
HIDE_BASE_FORM_FACTOR = 2

# how many clozes per sentence, it never goes above
MAX_CLOZES = 4

# how often to add a fake cloze that doesn't replace anything
EMPTY_CLOZE_FACTOR = 200

# how often a space should be tolerated as a cloze
# e.g. 5 means every 5 times a space is selected, it's used
TOLERATE_SPACE_FACTOR = 200


# how many most-common words will be replaced by clozes
WORD_MIN_RANK = 1000

# evil evil words to not cover with the cloze
FORBIDDEN_CLOZE_TOKENS = {'Layla', 'Maria', 'Mary', 'Marias', 'Muriel', 'Tom'}

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


def get_unambiguous_roots(base_forms_file: str) -> Dict[str, Dict[str, str]]:
    """Get the list of words repleaceable with an unambiguous lemma.

    This is a dictionary having the ISO 3-letter code of each language as
    a key, and as values dictionaries mapping words with their dictionary
    form. When a word has multiple possible senses or base forms, it's
    omitted.
    Since this data is generated from en.wiktionary, some languages are
    missing and some have very little data.
    """
    ret = {}
    with open(base_forms_file) as f:
        for line in f:
            form = json.loads(line)
            lang = form['lang']
            if lang not in ret:
                ret[lang] = {}
            if len(form['base_forms']) == 1:
                ret[lang][form['word']] = form['base_forms'][0]
    return ret


def read_sentences(sentence_file: str) -> Tuple[Dict[int, Tuple[str, str]], Dict[str, Set[str]]]:
    """Read and process a sentence file.

    Paramenters
    -----------
    sentence_file: str
        name or path of a sentence file, usually sentences.csv from Tatoeba

    Returns
    -------
    Tuple[Dict[int, Tuple[str, str]], Dict[str, Set[str]]]

    A tuple with two elements:
    * a dictionary mapping a sentence ID with its language code and content
    * a dictionary mapping each language with a list of most common words

    """
    sents = reader(open(sentence_file), delimiter='\t')
    id_sents = {}  # id -> (lang, text)
    langs = set()  # set of seen lanuages
    word_counters = {}  # lang -> Counter
    for idx, [_id, lang, text] in enumerate(sents):
        if idx % 200_000 == 0:
            print(f'Read {idx} rows from the sentences CSV so far')
        if len(text) > MAX_SENTENCE_LENGTH or len(text) < 20:
            continue
        # null value for the language, ignore it
        if lang == '\\N':
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
    for lng in langs:
        # Note that in here there is an empty string,
        # that's normalized punctuation. Also, a space.
        word_counters[lng].pop('', None)
        # remove the space character
        word_counters[lng].pop('', None)
        most_commons[lng] = set(
            w for w, _ in word_counters[lng].most_common(WORD_MIN_RANK)
            )
    return id_sents, most_commons


def main_multi(sentence_file: str, link_file: str, base_forms_file: str):
    """Produce the cloze deletion cards.

    This will produce them for all the language pairs!
    """
    print(f'Processing files {sentence_file}, {link_file}, {base_forms_file}...')

    links = reader(open(link_file), delimiter='\t')

    id_sents, most_commons = read_sentences(sentence_file)
    base_forms = get_unambiguous_roots(base_forms_file)

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
    Random(42).shuffle(pairs)
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
            if cloze_idx > MAX_CLOZES:
                break
            to_replace_idx = r.randint(0, len(tokens) - 1)
            # no cloze of a cloze
            if tokens[to_replace_idx].startswith('{{'):
                continue
            norm_token = normalized(tokens[to_replace_idx])
            # do not put cloze after empty cloze or space
            if (
                    to_replace_idx > 0
                    and (
                        tokens[to_replace_idx - 1].endswith('::-}}')
                        or tokens[to_replace_idx - 1].endswith(':: }}')
                        )
                    ):
                continue
            # is it an unambiguous inflected form?
            if norm_token in base_forms.get(to_lang, {}):
                if r.randint(1, HIDE_BASE_FORM_FACTOR) != 1:
                    tokens[to_replace_idx] = ''.join([
                        '{{c',
                        'XXX',
                        ':',
                        base_forms[to_lang][norm_token],
                        ':',
                        tokens[to_replace_idx],
                        '}}'
                    ])
                    cloze_idx += 1
                    continue

            # only the most common words
            if (norm_token not in most_commons[to_lang]):
                continue
            if tokens[to_replace_idx] == ' ':
                if r.randint(1, TOLERATE_SPACE_FACTOR) != 1:
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
                'XXX',
                '::',
                tokens[to_replace_idx],
                '}}'
            ])
            cloze_idx += 1
            if cloze_idx > MAX_CLOZES:
                continue

            if r.randint(1, EMPTY_CLOZE_FACTOR) == 1:
                to_insert_idx = r.randint(0, len(tokens) - 1)
                # do it only if there'not a cloze on the right
                # otherwise the user has no way to know this is a fake one
                if (
                    to_insert_idx == len(tokens) - 1
                        or not tokens[to_insert_idx].startswith('{{')):
                    tokens.insert(
                        to_insert_idx,
                        '{{cXXX::-}}'
                    )
                    cloze_idx += 1
                    if cloze_idx > MAX_CLOZES:
                        continue

            if r.randint(0, ANOTHER_CLOZE_FACTOR) == 0:
                continue
            break

        if cloze_idx == 1:
            continue
        out.write(from_txt)
        out.write('<br>')
        # replace XXX with the cloze ids, so they are ordered
        cloze_idx = 1
        for i, t in enumerate(tokens):
            if t.startswith('{{'):
                tokens[i] = t.replace('XXX', str(cloze_idx))
                cloze_idx += 1

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
    parser.add_argument('base_forms', help='the base forms JSONL file', type=str)

    args = parser.parse_args()
    main_multi(args.sentences, args.links, args.base_forms)
