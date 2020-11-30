FROM python:3.8.6-alpine

WORKDIR /usr/src/smallboard

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

# install npm & yarn
RUN apk add --update nodejs yarn

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./package.json .
RUN yarn install

COPY . .
