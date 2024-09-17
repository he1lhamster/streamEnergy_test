# pull official base image
FROM python:3.12-slim

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy project
COPY . .

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

