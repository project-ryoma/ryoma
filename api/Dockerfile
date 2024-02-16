# build flask app docker file
FROM python:3.8-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# sdt working directory
WORKDIR /app

# copy app
COPY . .

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# install mariadb connector
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y gcc default-libmysqlclient-dev pkg-config curl \
    && rm -rf /var/lib/apt/lists/*

# install dependencies
RUN pip install -r requirements.txt

EXPOSE 3001

# run app
CMD ["uvicorn", "--port", "3001", "main:app"]