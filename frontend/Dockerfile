FROM node:16 as builder

WORKDIR /app

COPY . .

RUN yarn install \
  --prefer-offline \
  --frozen-lockfile \
  --non-interactive \
  --production=false \ 
  # https://github.com/docker/build-push-action/issues/471
  --network-timeout 1000000
  
RUN yarn build

RUN rm -rf node_modules && \
  NODE_ENV=production yarn install \
  --prefer-offline \
  --pure-lockfile \
  --non-interactive \
  --production=true

FROM node:16-alpine

WORKDIR /app

# copying caddy into image
COPY --from=builder /app  .

ENV HOST 0.0.0.0
EXPOSE 3000

CMD [ "yarn", "start" ]
