FROM node:lts as builder

WORKDIR /app

COPY . .

# Install Caddy
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    curl \
    apt-transport-https \
    && curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | apt-key add - \
    && curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list \
    && apt-get update \
    && apt-get install --no-install-recommends -y \
    caddy 

RUN yarn install \
  --prefer-offline \
  --frozen-lockfile \
  --non-interactive \
  --production=false

RUN yarn build

RUN rm -rf node_modules && \
  NODE_ENV=production yarn install \
  --prefer-offline \
  --pure-lockfile \
  --non-interactive \
  --production=true

FROM node:15-alpine

WORKDIR /app

# copying caddy into image
COPY --from=builder /usr/bin/caddy /usr/bin/caddy
COPY ./Caddyfile /app
COPY --from=builder /app  .

ENV HOST 0.0.0.0
EXPOSE 3000

RUN ["caddy", "start", "--config", "/app/Caddyfile"]

CMD [ "yarn", "start" ]
