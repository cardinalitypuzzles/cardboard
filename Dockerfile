FROM python:3.8.12-alpine

WORKDIR /usr/src/cardboard

# install psycopg2 dependencies
RUN apk update && apk add \
    build-base \
    gcc \
    libffi-dev \
    musl-dev \
    postgresql-dev \
    python3-dev \
    tzdata

# install npm & yarn
RUN apk add --update nodejs yarn

RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry config virtualenvs.create false
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev

# Install npm dependencies
COPY ./package.json ./yarn.lock ./
RUN yarn install
# Install patches
COPY ./patches ./patches
RUN yarn install
