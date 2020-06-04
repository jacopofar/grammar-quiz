local-install:
	cd frontend && \
		yarn install
	cd backend && \
		python3 -m venv .venv &&\
		.venv/bin/python3 -m pip install -r requirements.txt

build-static-frontend:
	cd frontend && \
		yarn install && yarn build
	rm -rf backend/static
	mv frontend/build backend/static

local-run-backend:
	backend/.venv/bin/uvicorn backend.app:app --reload

local-run-frontend:
	cd frontend && \
		yarn start

test-frontend:
	cd frontend && \
		CI=true yarn test
