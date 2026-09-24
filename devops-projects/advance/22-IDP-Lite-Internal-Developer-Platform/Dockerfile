FROM node:20
WORKDIR /app
COPY . .
RUN yarn install && yarn build
CMD ["yarn","start"]
