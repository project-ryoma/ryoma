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
ENV NODE_ENV=production

# run app
CMD [ "npx", "serve", "build" ]