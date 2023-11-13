# This docker file is used for local development via docker-compose
# Creating image based on official python3 image
FROM python:3.10
LABEL maintainer="FAroogh"

# Fix python printing
# Prevent Python from writing .pyc files.
ENV PYTHONDONTWRITEBYTECODE=1
# Ensure Python output is sent directly to the terminal without buffering.
ENV PYTHONUNBUFFERED=1

# Get the django project into the docker container
WORKDIR /app
COPY ./requirements /app/
COPY ./ /app/

# Installing all python dependencies
RUN pip install -r requirements/local.txt
