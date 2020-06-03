Script to initialize the database with the card data.

Once you used the `generate_cards` script you'll want to put them in a DB to run the web app.

First, you need a Postgres database. You can quickly create a local one with Docker:

    docker run --name grammar-quiz-db -v grammar-quiz-db:/var/lib/postgresql/data -p 5452:5432 -e POSTGRES_PASSWORD=secret -d postgres:12

This will create a local database listening at port `5452` with default password `secret` for user `postgres`.
Or you can install Postgres using the installer fromt he website or your system package manager.

In this database, run the code in `schema.sql` to create the empty tables.

Then, create a virtual environment and install the dependencies:

    python3 -m venv .venv
    .venv/bin/python3 -m pip install -r requirements.txt

Run with

    export PG_CONN_STR=postgresql://postgres:secret@localhost:5452/grammarquiz
    export PYTHONPATH=.
    .venv/bin/python3 populate_db/populate.py universal_cards.jsonl

the first command sets the environment variable used to retrieve the connection string. This is in the
[standard format used by libpq](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING).
