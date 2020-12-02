FROM python:3.8.6-alpine

WORKDIR /usr/src/smallboard

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev libffi-dev

RUN pip install --upgrade pip
RUN pip install pipenv
COPY Pipfile* .
RUN pipenv lock --requirements > requirements.txt
RUN pip install -r requirements.txt

COPY . .
