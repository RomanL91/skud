FROM python:latest

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apk --update add
RUN apk add gcc libc-dev 
RUN apk add postgresql-dev

