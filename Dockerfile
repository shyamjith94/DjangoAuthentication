FROM python:3.8
MAINTAINER Tom <tom.victor@admaren.com>
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
