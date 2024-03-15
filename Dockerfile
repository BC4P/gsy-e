FROM python:3.10-slim

ADD . /app

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -e .

ENTRYPOINT ["gsy-e"]
