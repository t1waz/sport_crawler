FROM python:3.11-alpine

RUN apk update \
    && apk upgrade \
    && apk add python3-dev gcc libc-dev \
    && apk add bash

WORKDIR /app

COPY ./compose/admin/requirements.txt /app

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY ./services/admin /app
