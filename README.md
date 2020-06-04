# grammar-quiz
Online cloze deletion tool focused on grammar

This is a project for the [Kodoeba event](https://blog.tatoeba.org/2020/05/announcing-kodoeba-1.html) organized
by Tatoeba.

This project aims at using the vast sentence database of Tatoeba to generate grammar exercises, in particular cloze
deletions, that can be used both to study and to evaluate the usage of a language.

This project will be completely FOSS and the produced data will be published when possible and non-personal
(e.g. user account data).


## How to run

First you need to import the Tatoeba data into a local DB. Look at the `scripts/` folder for the various steps and
relative instructions.

To run locally you need Python 3.6 or later, node.js 10.x or later, the yarn package manager and make.

Use `make local-install` to install the dependencies for the frontend and backend.
With `make local-run-backend` the backend will listen at port 8000 and reload on change, then
`make local-run-frontend` will start the frontend server at port 3000, forwarding API calls to the port 8000 to
make developing as simple and quick as possible.

## Test

To test use `make local-install` and then `make test-all`

## Roadmap

You can see the planned roadmap and the progress in the project issues, organized in weekly milestones.
