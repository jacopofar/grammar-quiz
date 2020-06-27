import argparse
import json


# From Wiktionary name to ISO 3-letter code used by Tatoeba
# Note that this is based on the content of Wiktionary in June, 2020
WIKTIONARY_NAME_ISO_MAP = {
    'Afrikaans': 'afr',
    'Albanian': 'sqi',
    'Ancient Greek': 'grc',
    'Arabic': 'ara',
    'Armenian': 'hye',
    'Asturian': 'ast',
    'Azerbaijani': 'aze',
    'Basque': 'eus',
    'Bulgarian': 'bul',
    'Catalan': 'cat',
    'Cebuano': 'ceb',
    'Chichewa': 'nya',
    'Cimbrian': '',
    'Classical Nahuatl': 'nah',
    'Classical Syriac': 'syc',
    'Cornish': 'cor',
    'Czech': 'ces',
    'Danish': 'dan',
    'Dutch': 'nld',
    'Emilian': 'egl',
    'English': 'eng',
    'Esperanto': 'epo',
    'Estonian': 'est',
    'Faroese': 'fao',
    'Finnish': 'fin',
    'French': 'fra',
    'Friulian': 'fur',
    'Galician': 'glg',
    'Georgian': 'kat',
    'German': 'deu',
    'German Low German': 'nds',
    'Gothic': 'got',
    'Greek': 'ell',
    'Greenlandic': 'kal',
    'Hebrew': 'heb',
    'Hindi': 'hin',
    'Hungarian': 'hun',
    'Hunsrik': 'hrx',
    'Icelandic': 'isl',
    'Ido': 'ido',
    'Interlingua': 'ina',
    'Irish': 'gle',
    'Italian': 'ita',
    'Japanese': 'jpn',
    'Kurdish': 'kur',
    'Ladin': 'lld',
    'Latin': 'lat',
    'Latvian': 'lvs',
    'Ligurian': 'lij',
    'Lithuanian': 'lit',
    'Livonian': 'liv',
    'Low German': 'nds',
    'Lower Sorbian': 'dsb',
    'Luxembourgish': 'ltz',
    'Macedonian': 'mkd',
    'Maltese': 'mlt',
    'Manx': 'glv',
    'Mapudungun': '',
    'Middle Dutch': '',
    'Middle English': 'enm',
    'Middle French': 'frm',
    'Moksha': 'mdf',
    'Mongolian': 'mon',
    'Moroccan Arabic': 'ary',
    'Navajo': 'nav',
    'Neapolitan': '',
    'Norman': '',
    'Northern Sami': 'sme',
    'Norwegian Bokmål': 'nob',
    'Norwegian Nynorsk': 'nno',
    'Occitan': 'oci',
    'Old Armenian': '',
    'Old Church Slavonic': '',
    'Old English': 'ang',
    'Old French': 'fro',
    'Old Irish': '',
    'Old Norse': 'non',
    'Old Spanish': 'osp',
    'Pali': '',
    'Pennsylvania German': 'pdc',
    'Persian': 'pes',
    'Polish': 'pol',
    'Portuguese': 'por',
    'Romanian': 'ron',
    'Romansch': 'roh',
    'Russian': 'rus',
    'Sanskrit': 'san',
    'Scots': 'sco',
    'Scottish Gaelic': 'gla',
    'Serbo-Croatian': '',
    'Sicilian': 'scn',
    'Slovak': 'slk',
    'Slovene': 'slv',
    'Spanish': 'spa',
    'Swahili': 'swh',
    'Swedish': 'swe',
    'Tagalog': 'tgl',
    'Telugu': 'tel',
    'Tetelcingo Nahuatl': '',
    'Thai': 'tha',
    'Translingual': '',
    'Turkish': 'tur',
    'Ukrainian': 'ukr',
    'Uyghur': 'uig',
    'Venetian': 'vec',
    'Veps': 'vep',
    'Vilamovian': '',
    'Volapük': 'vol',
    'Welsh': 'cym',
    'West Frisian': 'fry',
    'Westrobothnian': '',
    'Yiddish': 'yid',
    'Zulu': 'zul'
}


def main(wiktextract: str):
    base_forms = {}
    inflections = {}
    with open(wiktextract) as wikt, open('unused.jsonl', 'w') as unused:
        for i, line in enumerate(wikt):
            if i % 100_000 == 0:
                print(f'Processed {i} so far...')
            obj = json.loads(line)
            if 'lang' not in obj:
                print('Entry without a language:', line)
                continue
            lang = obj['lang']
            inflection = obj['word']
            if 'senses' not in obj:
                continue
            produced = 0
            for sense in obj['senses']:
                # sometimes a string, sometimes a list
                bases = sense.get('inflection_of',  [])
                if type(bases) != list:
                    bases = [bases]
                if len(bases) > 0:
                    if lang not in base_forms:
                        base_forms[lang] = {}
                    if lang not in inflections:
                        inflections[lang] = {}
                for base in bases:
                    if inflection not in base_forms[lang]:
                        base_forms[lang][inflection] = set()
                    base_forms[lang][inflection].add(base)
                    if base not in inflections[lang]:
                        inflections[lang][base] = set()
                    inflections[lang][base].add(inflection)
                    produced += 1
                # complex inflections

                complex_inflections = sense.get('complex_inflection_of', [])
                if type(complex_inflections) != list:
                    complex_inflections = [complex_inflections]
                # this is a template, the element 2 is the used one
                bases = [b["2"] for b in complex_inflections]
                if len(bases) > 0:
                    if lang not in base_forms:
                        base_forms[lang] = {}
                    if lang not in inflections:
                        inflections[lang] = {}
                for base in bases:
                    if inflection not in base_forms[lang]:
                        base_forms[lang][inflection] = set()
                    base_forms[lang][inflection].add(base)
                    if base not in inflections[lang]:
                        inflections[lang][base] = set()
                    inflections[lang][base].add(inflection)
                    produced += 1
            if produced == 0:
                unused.write(line)
    with open('base_forms.jsonl', 'w') as of:
        for lang_name in base_forms:
            if lang_name not in WIKTIONARY_NAME_ISO_MAP:
                continue
            lang = WIKTIONARY_NAME_ISO_MAP[lang_name]
            print(f'Language {lang} ({lang_name}) has {len(base_forms[lang_name])} base forms')
            for k, v in base_forms[lang_name].items():
                of.write(json.dumps(dict(
                    lang=lang, word=k, base_forms=list(v))))
                of.write('\n')
    print()
    with open('inflections.jsonl', 'w') as of:
        for lang_name in inflections:
            if lang_name not in WIKTIONARY_NAME_ISO_MAP:
                continue
            lang = WIKTIONARY_NAME_ISO_MAP[lang_name]
            print(f'Language {lang} ({lang_name}) has {len(inflections[lang_name])} inflections')
            for k, v in inflections[lang_name].items():
                of.write(json.dumps(dict(
                    lang=lang, word=k, inflections=list(v))))
                of.write('\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('wiktextract', help='the JSONL from Wiktionary', type=str)
    args = parser.parse_args()
    main(args.wiktextract)
