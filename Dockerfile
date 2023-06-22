# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8-slim-buster

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install git for pip dependencies from repositories
RUN apt-get -y update
RUN apt-get -y install git

# Install pip requirements
COPY Pipfile .
COPY Pipfile.lock .
RUN python -m pip install pipenv

WORKDIR /app
COPY . /app

RUN pipenv install --dev --system
