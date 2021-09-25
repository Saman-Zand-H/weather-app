FROM python:latest

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /Practice-Projects/

COPY requirements.txt /Practice-Projects/

RUN pip install -r requirements.txt

COPY . /Practice-Projects/