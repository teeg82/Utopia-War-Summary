FROM python:2.7.14-alpine

RUN pip install beautifulsoup4 requests mechanize

RUN mkdir -p /uws
COPY ./app /uws
COPY credentials.txt /uws

COPY entrypoint.sh /usr/local/bin
RUN chmod +x /usr/local/bin/entrypoint.sh

WORKDIR /uws

# CMD ["python", "summary.py"]
ENTRYPOINT ["entrypoint.sh"]
