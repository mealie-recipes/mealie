# Sandbox for workflow 5. No git credentials, SSH keys, or registry tokens are
# mounted. Shares the dev container's network namespace so 127.0.0.1:9000 is
# the Python oracle and 127.0.0.1:9001+ are PHP builds.
FROM php:8.4-cli-bookworm

RUN apt-get update \
 && apt-get install -y --no-install-recommends git unzip sqlite3 libzip-dev libpng-dev libjpeg-dev libwebp-dev libicu-dev curl ca-certificates libxml2 libcurl4 python3 \
 && docker-php-ext-configure gd --with-jpeg --with-webp \
 && docker-php-ext-install -j"$(nproc)" gd intl zip bcmath \
 && rm -rf /var/lib/apt/lists/*

COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

ARG HURL_VERSION=8.0.1
RUN curl -fsSL "https://github.com/Orange-OpenSource/hurl/releases/download/${HURL_VERSION}/hurl-${HURL_VERSION}-$(uname -m)-unknown-linux-gnu.tar.gz" \
  | tar -xz -C /tmp \
 && install /tmp/hurl-${HURL_VERSION}-*/bin/hurl /usr/local/bin/hurl \
 && rm -rf /tmp/hurl-*

RUN useradd -m -u 1000 dev
USER dev
WORKDIR /workspaces/mealie/.worktrees/w5
