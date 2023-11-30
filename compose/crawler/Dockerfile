FROM mcr.microsoft.com/playwright:v1.39.0-jammy

RUN apt update \
    && apt upgrade -y \
    && apt install python3.11 -y \
    && apt install python3-pip -y \
    && apt install python3-dev gcc libc-dev -y \
    && apt install bash -y

WORKDIR /app

COPY ./compose/crawler/requirements.txt /app

COPY ./compose/crawler/scrapy.cfg /etc/scrapyd/scrapyd.conf

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

RUN playwright install

COPY ./services/crawler /app
