import argparse
from collections import Counter
from csv import reader
import json
from random import randint
from sys import argv

# how often to add an extra cloze
ANOTHER_CLOZE_FACTOR = 50

# how often to add a fake cloze that doesn't replace anything
EMPTY_CLOZE_FACTOR = 50

# how many most-common words will be replaced by clozes
WORD_MIN_RANK = 1000

# evil evil words to not cover with the cloze
FORBIDDEN_CLOZE_TOKENS = {'Tom', 'Mary'}


def normalize(text: str, lang: str):
    """Normalize the text.

    This is used to allow comparison of tokens to extract the frequency
    """
    if text[:-1] in '.,?!;':
        text = text[:-1]
    return text.lower()


def tokenize(text: str, lang: str):
    """Split a string into tokens."""
    # TODO actually tokenize according to the language
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
    for [_id, lang, text] in sents:
        if len(text) > 140 or len(text) < 20:
            continue
        id_sents[int(_id)] = (lang, text)
        if lang not in word_counters:
            word_counters[lang] = Counter()
        word_counters[lang].update(tokenize(normalize(text, lang), lang))
        langs.add(lang)
    print(
        f'Imported {len(id_sents)} sentences')

    most_commons = {}
    for l in langs:
        most_commons[l] = set(
            w for w, _ in word_counters[l].most_common(WORD_MIN_RANK)
            )
    del word_counters

    pairs = []
    for [from_id, to_id] in links:
        from_id = int(from_id)
        to_id = int(to_id)

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

    print(f'Found {len(pairs)} sentence pairs')

    out = open('universal_cards.tsv', 'w')
    out_details = open('universal_cards.jsonl', 'w')
    for (
        from_lang,
        to_lang,
        from_id,
        to_id,
        from_txt,
        to_txt
            ) in pairs:
        tokens = tokenize(to_txt, to_lang)
        cloze_idx = 1
        for _ in range(100):
            to_replace_idx = randint(0, len(tokens) - 1)
            # no cloze of a cloze
            if tokens[to_replace_idx].startswith('{{'):
                continue
            # only the most common words
            if (normalize(tokens[to_replace_idx], to_lang)
                    not in most_commons[to_lang]):
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

            if randint(0, EMPTY_CLOZE_FACTOR) == 0:
                to_insert_idx = randint(0, len(tokens) - 1)
                tokens.insert(
                    to_insert_idx,
                    '{{c' + str(cloze_idx) + '::-}}'
                )
                cloze_idx += 1

            if randint(0, ANOTHER_CLOZE_FACTOR) == 0:
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