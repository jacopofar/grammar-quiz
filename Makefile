local-install:
	cd frontend && \
		yarn install
	cd backend && \
		python3 -m venv .venv
	backend/.venv/bin/python3 -m pip install -r requirements.txt

.PHONY: local-install


build-static-frontend:
	cd frontend && \
		yarn install && yarn build
	rm -rf backend/static
	mv frontend/build backend/static

.PHONY: build-static-frontend

local-run-backend:
	backend/.venv/bin/uvicorn backend.app:app --reload

.PHONY: local-run-backend


local-run-frontend:
	cd frontend && \
		yarn start

.PHONY: local-run-frontend

test-frontend:
	cd frontend && \
		CI=true yarn test

.PHONY: test-frontend

test-backend:
	backend/.venv/bin/python3 -m pytest tests

.PHONY: test-backend

test-all: test-backend test-frontend

.PHONY: test-all
