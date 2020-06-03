This script processes the [sentence and links files provided by Tatoeba](https://tatoeba.org/downloads) and builds
a collection of "grammar flashcards" in TSV and JSONL format.

The clozes are generated using word frequency to determine which words should be covered, assuming the most frequent
tokens have a grammatical role (articles, preposition, etc.).

The TSV file can be filtered for the desired language and imported in Anki, whiel the JSONL contains more metadata and
can be later imported in a database or further processed.

## How to run

You need Python3.6 or later. Download the sentence and links file mentioned above and decompress them to get two CSV
files, `sentences.csv` and `links.csv`.

It's a good idea to create a virtual environment, with `python3 -m venv .venv`. If you get an error because there's no
`venv` package and are on Ubuntu or Debian, you need to install it apart with `sudo apt-get install python3-virtualenv`.

Then, run `.venv/python3 generate.py path/to/sentences.csv path/to/links.csv` to produce the JSONL and TSV files.

The script performs a basic tokenization for Chinese (Mandarin) and Japanese, and doesn't handle morphology or
lemmatization yet.
