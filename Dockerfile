# create a basic python image that install poetry and use poetry to install dependencies

# Use the official Python image
FROM python:3.9-slim

# install additional dependencies like unzip
RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    unzip \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# install poetry
RUN pip install poetry

COPY . /app

# Install the dependencies
RUN poetry install --with dev,aita_lab --all-extras

# Deploy templates and prepare app
RUN poetry run reflex init

# Download all npm dependencies and compile frontend
RUN poetry run reflex export --frontend-only --no-zip

RUN poetry run reflex db migrate

# Start the application
CMD ["poetry", "run", "reflex", "run", "--env", "prod"]
