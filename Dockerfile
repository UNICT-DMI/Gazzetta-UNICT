# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app

RUN mkdir tmp

COPY requirements.txt requirements.txt

RUN apt-get update \
    && apt-get install -y \
    wkhtmltopdf

RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "main.py"]
