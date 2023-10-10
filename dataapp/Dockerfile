# build flask app docker file
FROM python:3.8-slim

# install mariadb connector
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y gcc default-libmysqlclient-dev pkg-config curl \
    && rm -rf /var/lib/apt/lists/*

# install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# sdt working directory
WORKDIR /app

# copy app
COPY . ./app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

EXPOSE 5000

# run app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]