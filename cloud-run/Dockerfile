FROM python:3.15.2-alpine AS build

WORKDIR /usr/src/cardboard

# install psycopg2 dependencies
RUN apk update && apk add \
    build-base \
    gcc \
    libffi-dev \
    musl-dev \
    postgresql-dev \
    python3-dev \
    tzdata \
    bash

# install npm & yarn
RUN apk add --update nodejs yarn

COPY . /usr/src/cardboard

# Install npm dependencies
RUN yarn install
RUN yarn run build

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN pip install --upgrade pip
RUN pip install poetry
RUN python -m venv /venv

RUN . /venv/bin/activate && poetry install --without dev

COPY cloud-run/.pyproject.toml ./pyproject.toml
COPY poetry.lock ./
RUN . /venv/bin/activate && poetry build && python manage.py collectstatic --no-input

FROM python:3.15.2-alpine
WORKDIR /usr/src/cardboard

RUN apk update && apk add \
    postgresql-dev \
    tzdata \
    procps \
    bash

COPY --from=build /venv /venv
COPY --from=build /usr/src/cardboard .

RUN . /venv/bin/activate && pip install dist/*.whl
ENTRYPOINT [ "./cloud-run/bin/docker-entrypoint.sh" ]
