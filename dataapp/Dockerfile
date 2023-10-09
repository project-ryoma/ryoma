# build flask app docker file
FROM python:3.8-slim

# sdt working directory
WORKDIR /app

# copy app
COPY . .

# install mariadb connector
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y gcc default-libmysqlclient-dev pkg-config curl \
    && rm -rf /var/lib/apt/lists/*


# install dependencies
RUN pip install -r requirements.txt

# set environment variables
ENV FLASK_APP=app.py

EXPOSE 5000

# run app
CMD [ "flask", "run", "-p", "5000"]