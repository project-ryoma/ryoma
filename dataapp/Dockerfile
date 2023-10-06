# build flask app docker file
FROM python:3.8-slim-buster

# sdt working directory
WORKDIR /app

# copy app
COPY . .

# install dependencies
RUN pip install -r requirements.txt

# set environment variables
ENV FLASK_APP=app.py

# run app
CMD [ "flask", "run", "-p", "5000"]