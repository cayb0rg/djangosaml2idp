FROM python:3.7-slim

RUN apt-get update && apt-get install -y \
    libffi-dev libxmlsec1-dev libxmlsec1-openssl xmlsec1 curl

ADD . /code
WORKDIR /code

ADD requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
