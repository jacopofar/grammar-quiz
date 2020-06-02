This script processes the [sentence and links files provided by Tatoeba](https://tatoeba.org/downloads) and builds
a collection of "grammar flashcards" in TSV and JSONL format.

The clozes are generated using word frequency to determine which words should be covered, assuming the most frequent
tokens have a grammatical role (articles, preposition, etc.).

The TSV file can be filtered for the desired language and imported in Anki, whiel the JSONL contains more metadata and
can be later imported in a database or further processed.

## How to run

At the moment you need only Python 3.6 or later, no dependencies, use `python3 generate.py sentences.csv links.csv`.

The script doesn't perform a proper tokenizing so it does not work well on Chinese, Japanese or other languages not
using spaces between words, and likewise doesn't handle morphology or lemmatization yet.
