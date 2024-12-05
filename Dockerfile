# create a basic python image that install poetry and use poetry to install dependencies

# Use the official Python image
FROM python:3.10-slim

# install additional dependencies like unzip
RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    unzip \
    git \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app
