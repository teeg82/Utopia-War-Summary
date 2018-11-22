FROM python:2.7.14-alpine

RUN apk update && apk add postgresql-dev gcc musl-dev libffi-dev libxml2-dev libxslt-dev zlib-dev

RUN pip install beautifulsoup4 \
                requests \
                mechanize \
                html2text \
                slacker \
                lxml \
                peewee \
                psycopg2 \
                click

RUN mkdir -p /uws
COPY ./ /uws
COPY ./credentials/utopia.txt /uws/credentials.txt

# COPY entrypoint.sh /usr/local/bin
# RUN chmod +x /usr/local/bin/entrypoint.sh

WORKDIR /uws
