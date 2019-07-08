# base image
FROM node:10.15.3-alpine

# set working directory
WORKDIR /usr/src/app

# add `/usr/src/app/node_modules/.bin` to $PATH
ENV PATH /usr/src/app/node_modules/.bin:$PATH

# install and cache app dependencies
COPY package.json /usr/src/app/package.json
COPY package-lock.json /usr/src/app/package-lock.json
RUN npm ci

# Seems to be an issue with Alpine based images using Pipelines and React 2 Node
# Fix recommendation found here:
# https://stackoverflow.com/questions/52196518/could-not-get-uid-gid-when-building-node-docker
# Atlassian issue raised here:
# https://bitbucket.org/site/master/issues/16846/npm-error-eacces-permission-denied
RUN npm config set unsafe-perm true

RUN npm install react-scripts@2.1.8 -g --silent
RUN pwd
RUN npm run lint-fix-docker

# start app
CMD ["npm", "start"]
