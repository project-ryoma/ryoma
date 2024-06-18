# create a basic python image that install poetry and use poetry to install dependencies

# Use the official Python image
FROM python:3.9-slim

# install additional dependencies like unzip
RUN apt-get update && apt-get install -y \
    unzip \
    curl

# Set the working directory
WORKDIR /app

# install poetry
RUN pip install poetry

COPY . /app

# Install the dependencies
RUN poetry install --with dev,aita_lab --all-extras


RUN reflex init

EXPOSE 3000

# Start the application
CMD ["poetry", "run", "reflex", "run"]
