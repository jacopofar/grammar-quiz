FROM node:current-buster AS build-image

COPY frontend /frontend
COPY backend /backend
COPY Makefile /Makefile

RUN make build-static-frontend

FROM debian
RUN apt-get update && apt-get install -y python3-pip

# copy only the backend, which includes the already build stuff, no node_modules
COPY --from=build-image /backend /backend
COPY requirements.txt .
COPY Makefile /Makefile

RUN make global-backend-install

CMD uvicorn --host 0.0.0.0 backend.app:app
