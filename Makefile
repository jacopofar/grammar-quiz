.PHONY: local-install
local-install:
	cd frontend && \
		yarn install
	cd backend && \
		python3 -m venv .venv
	backend/.venv/bin/python3 -m pip install -r requirements.txt


.PHONY: build-static-frontend
build-static-frontend:
	cd frontend && \
		yarn install && yarn build
	rm -rf backend/static
	mv frontend/build/ backend/static/

.PHONY: global-backend-install
global-backend-install:
	python3 -m pip install -r requirements.txt

.PHONY: local-run-backend
local-run-backend:
	backend/.venv/bin/uvicorn backend.app:app --reload


.PHONY: local-run-frontend
local-run-frontend:
	cd frontend && \
		yarn start


.PHONY: test-frontend
test-frontend:
	cd frontend && \
		CI=true yarn test


.PHONY: test-backend
test-backend:
	backend/.venv/bin/python3 -m pytest tests


# this abomination really should be done better. How?
# pg_virtualenv is not cross platform, travis has its own working solution
# everything else require manual operations...
# still would be nice to differentiate tests and run only the "destructive" ones here
.PHONY: create-local-tests-postgres
create-local-test-postgres:
	docker run --name grammar-quiz-test-db -p 15432:5432 -e POSTGRES_PASSWORD=testpassword -d postgres:12
	# wait for the DB to be up
	docker exec grammar-quiz-test-db sh -c 'until pg_isready; do echo "Waiting for the DB to be up..."; sleep 2; done'
	docker exec grammar-quiz-test-db sh -c "echo 'CREATE USER foo WITH PASSWORD '\''secret'\'' LOGIN;' |psql -U postgres"
	docker exec grammar-quiz-test-db sh -c "echo 'CREATE DATABASE grammarquiz OWNER foo;' |psql -U postgres"
	# create empty schema
	docker cp scripts/populate_db/schema.sql grammar-quiz-test-db:/schema.sql
	docker exec grammar-quiz-test-db sh -c "psql -U postgres -f /schema.sql grammarquiz"
	# insert test data
	docker cp tests/database_content.sql grammar-quiz-test-db:/database_content.sql
	docker exec grammar-quiz-test-db sh -c "psql -U postgres -q -f /database_content.sql grammarquiz"
	# now use PG_CONN_STR=postgresql://postgres:testpassword@localhost:15432/grammarquiz

.PHONY: destroy-local-test-postgres
destroy-local-test-postgres:
	docker kill grammar-quiz-test-db
	docker rm grammar-quiz-test-db

.PHONY: test-all
test-all: test-backend test-frontend

.PHONY: build-docker-image
build-docker-image:
	docker build -t grammarquiz:$(shell git describe --always) -t grammarquiz:latest .
