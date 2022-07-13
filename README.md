# grammar-quiz
Online cloze deletion tool focused on grammar


[![Build Status](https://travis-ci.org/jacopofar/grammar-quiz.svg?branch=master)](https://travis-ci.org/jacopofar/grammar-quiz)

This is a project for the [Kodoeba event](https://blog.tatoeba.org/2020/05/announcing-kodoeba-1.html) organized
by Tatoeba.

This project aims at using the vast sentence database of Tatoeba to generate grammar exercises, in particular cloze
deletions, that can be used both to study and to evaluate the usage of a language.

This project will be completely FOSS and the produced data will be published when possible and non-personal
(e.g. user account data).


## How to run

First you need to import the Tatoeba data into a local Postgres DB. Look at the `scripts` folder for the various steps
 and relative instructions. There are a few steps:
 * build the lemma dataset, using a dump of en.wiktionary to extract lists of inflected words
 * generate the cards from an export of Tatoeba sentences
 * Load the cards into a database, this step is incremental and can also update an existing database

### Run locally

To run locally you need Python 3.7 or later, node.js 10.x or later, the yarn package manager and make.

Use `make local-install` to install the dependencies for the frontend and backend.
With `make local-run-backend` the backend will listen at port 8000 and reload on change, then
`make local-run-frontend` will start the frontend server at port 3000, forwarding API calls to the port 8000 to
make developing as simple and quick as possible.

### Run using Docker

You need to set up the environment variables listed in the `env.list` file. The easiest way is probably to use
the [dotenv CLI](https://github.com/venthur/dotenv-cli) tool.
Use `make build-docker-image` to build the Docker image, then run it with

    dotenv docker run --name grammarquiz --env-file env.list -p 8000:8000 grammarquiz:latest

or, if you want to connect to a postgres instance running in docker:

    dotenv docker run --name grammarquiz --env-file env.list --link grammar-quiz-db -p 8000:8000 grammarquiz:latest

in this case the environment variable PG_CONN_STR needs

## Test

To test use `make local-install` and then `make test-all`

## Roadmap

You can see the planned roadmap and the progress in the project issues, organized in weekly milestones.
