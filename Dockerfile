# create a basic python image that install poetry and use poetry to install dependencies

# Use the official Python image
FROM python:3.8-slim

# Set the working directory
WORKDIR /app

# install poetry
RUN pip install poetry

# Copy the poetry.lock and pyproject.toml files
COPY pyproject.toml poetry.lock ./

# Install the dependencies
RUN poetry install --with pyspark,snowflake,postgresql,dynamodb,aita_lab

# Start the application
CMD ["poetry", "run", "reflex", "run"]
