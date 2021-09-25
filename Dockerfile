FROM python:latest

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /Sample-Projects/

COPY requirements.txt conf /Sample-Projects/

RUN pip install -r requirements.txt
RUN gunicorn conf.wsgi

COPY . /Sample-Projects/