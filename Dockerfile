FROM python:2.7.14-alpine

RUN apk update && apk add gcc musl-dev libffi-dev py-cairo cairo libxml2-dev libxslt-dev zlib-dev

RUN pip install beautifulsoup4 requests mechanize html2text slacker cairosvg==1.0.22 cairocffi cffi lxml

RUN mkdir -p /uws
COPY ./app /uws
COPY credentials.txt /uws

COPY entrypoint.sh /usr/local/bin
RUN chmod +x /usr/local/bin/entrypoint.sh

WORKDIR /uws

# CMD ["python", "summary.py"]
ENTRYPOINT ["entrypoint.sh"]
