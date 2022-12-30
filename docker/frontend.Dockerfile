FROM node:16 as builder

WORKDIR /app

COPY ./frontend .

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

RUN apk add caddy

WORKDIR /app

# copying caddy into image
COPY --from=builder /app  .
COPY ./docker/frontend.Caddyfile /app/Caddyfile
COPY ./docker/frontend.entry.sh /app/run.sh

ENV HOST 0.0.0.0
EXPOSE 3000

RUN chmod +x /app/run.sh
ENTRYPOINT /app/run.sh
