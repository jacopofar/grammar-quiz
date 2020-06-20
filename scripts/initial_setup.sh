# this script can create an initial DB and populate it
# is supposed to run in the same container of the app
apt-get update && apt-get install -y libicu-dev pkg-config wget postgresql-client
pip3 install -r /scripts/generate_cards/requirements.txt
wget https://downloads.tatoeba.org/exports/sentences.tar.bz2
tar -xvjf sentences.tar.bz2
rm sentences.tar.bz2
wget https://downloads.tatoeba.org/exports/links.tar.bz2
tar -xvjf links.tar.bz2
rm links.tar.bz2
python3 generate_cards/generate.py sentences.csv links.csv
# define the schema
psql $PG_CONN_STR -f populate_db/schema.sql
# now populate the DB
pip3 install -r populate_db/requirements.txt
PYTHONPATH=populate_db/ python3 populate_db/populate_db/populate.py universal_cards.jsonl
