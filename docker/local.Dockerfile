# This docker file is used for local development via docker-compose
# Creating image based on official python3 image
FROM python:3.10
LABEL maintainer="FAroogh"

# Fix python printing
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Get the django project into the docker container
WORKDIR /app
COPY ./requirements /app/
COPY ./ /app/

# Installing all python dependencies
RUN pip install -r requirements/local.txt
