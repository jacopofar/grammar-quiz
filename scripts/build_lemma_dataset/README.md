This script produces a list of strings that can be unambiguously matched with a base form for a given language.
When a word has multiple possible base forms for a language, it's ignored.

# Usage

You need a [recent dump of en.wiktionary](https://dumps.wikimedia.org/enwiktionary/), the file is the one called
`enwiktionary-{date}-pages-articles.xml.bz2`.

Then, download and run [Wiktextract](https://github.com/tatuylonen/wiktextract) to process this file.

The project did not release a stable version, so the command may change, now it's something like

    /wiktwords enwiktionary-20200620-pages-articles.xml.bz2 --out extracted_words.jsonl --all-languages --statistics --verbose

be warned that it took 8 hours on my computer. May be faster in the future thanks to parallelism.

This will produce a file of at least 7 million rows.

Then, run:

    python3 build_lemma_dataset/extract_lemmas.py extracted_words.jsonl

This will produce three JSONL files in the working directory:

* __base_forms.jsonl__, mapping words with the possible base forms for a language
* __inflections.jsonl__, mapping base forms with their inflections for a language
* __unused.jsonl__, the entries in the words file from which no forms where extracted, useful for troubleshooting

The data in the first two files match, so if a base form is listed in one it will be present as an inflected form in the other

