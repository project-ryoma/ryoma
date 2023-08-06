FROM node:18-alpine

# set working directory
WORKDIR /app

# copy app
COPY . .

# install dependencies
RUN npm install

# build app
RUN npm run build

EXPOSE 3000

# set environment variables
ENV REACT_APP_BACKEND_URL="https://infiniteai.azurewebsites.net/"

# run app
CMD [ "npx", "serve", "build" ]