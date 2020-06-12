FROM node:current-buster
RUN apt-get update && apt-get install -y python3-pip

COPY frontend /frontend
COPY backend /backend
COPY Makefile /Makefile
COPY requirements.txt .

RUN make build-static-frontend
RUN make global-backend-install

CMD uvicorn --host 0.0.0.0 backend.app:app
