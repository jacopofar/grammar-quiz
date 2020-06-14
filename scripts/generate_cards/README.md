This script processes the [sentence and links files provided by Tatoeba](https://tatoeba.org/downloads) and builds
a collection of "grammar flashcards" in TSV and JSONL format.

The clozes are generated using word frequency to determine which words should be covered, assuming the most frequent
tokens have a grammatical role (articles, preposition, etc.).

The TSV file can be filtered for the desired language and imported in Anki, whiel the JSONL contains more metadata and
can be later imported in a database or further processed.

## How to run

You need Python3.6 or later. Download the sentence and links file mentioned above and decompress them to get two CSV
files, `sentences.csv` and `links.csv`.

## ICU component
To perform word segmentation on some languages the [ICU library](https://site.icu-project.org/) is used.
This requires ICU to be installed first.
The exact installation procedure depends on the system, you'll have to look at the site and be ready to search
on the internet.

However, here is how I installed it on macOS Catalina:

* `brew install intltool icu4c gettext` to install the packages using Brew, may be already installed
* `export ICU_VERSION=67` to set the library version
* `export CFLAGS=-I/usr/local/opt/icu4c/include LDFLAGS=-L/usr/local/opt/icu4c/lib` to make the library accessible
* `export PKG_CONFIG_PATH="/usr/local/opt/icu4c/lib/pkgconfig"` to allow pyICU build to find the package
* `export PATH=/usr/local/opt/icu4c/bin:$PATH` to allow pyICU build to run icu-config

On Debian/Ubuntu:

* `apt-get update && apt-get install libicu-dev gettext`

should be enough (tested with the official Python 3.8 docker image, based on Debian).

Then you can proceed with the Python dependencies installation.

## Install the Python dependencies

It's a good idea to create a virtual environment, with `python3 -m venv .venv`. If you get an error because there's no
`venv` package and are on Ubuntu or Debian, you need to install it apart with `sudo apt-get install python3-virtualenv`.

Install the dependencies with `.venv/bin/python3 -m pip install -r requirements.txt`

Then, run `.venv/bin/python3 generate.py path/to/sentences.csv path/to/links.csv` to produce the JSONL and TSV files.

The script performs a basic tokenization for Chinese (Mandarin) and Japanese, and doesn't handle morphology or
lemmatization yet.
