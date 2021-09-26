FROM python:latest

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /Sample-Projects/

COPY requirements.txt /Sample-Projects/

RUN pip install -r requirements.txt

COPY . /Sample-Projects/

CMD gunicorn conf.wsgi:application -b 0.0.0.0:$PORT