# [Choice] Python version (use -bullseye variants on local arm64/Apple Silicon): 3, 3.10, 3.9, 3.8, 3.7, 3.6, 3-bullseye, 3.10-bullseye, 3.9-bullseye, 3.8-bullseye, 3.7-bullseye, 3.6-bullseye, 3-buster, 3.10-buster, 3.9-buster, 3.8-buster, 3.7-buster, 3.6-buster
ARG VARIANT="3.12-bullseye"
FROM mcr.microsoft.com/devcontainers/python:${VARIANT}

# Remove outdated yarn GPG key, if it exists
RUN rm -f /etc/apt/sources.list.d/yarn.list /usr/share/keyrings/yarn-archive-keyring.gpg || true

# [Choice] Node.js version: none, lts/*, 16, 14, 12, 10
ARG NODE_VERSION="none"
RUN if [ "${NODE_VERSION}" != "none" ]; then su vscode -c "umask 0002 && . /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} 2>&1"; fi

RUN echo "export PROMPT_COMMAND='history -a'" >> /home/vscode/.bashrc \
    && echo "export HISTFILE=~/commandhistory/.bash_history" >> /home/vscode/.bashrc \
    && chown vscode:vscode -R /home/vscode/

RUN npm install -g @go-task/cli
RUN npm install -g json-schema-to-typescript

# Install additional OS packages
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    curl \
    build-essential \
    libpq-dev \
    libwebp-dev \
    libsasl2-dev libldap2-dev libssl-dev \
    gnupg gnupg2 gnupg1

# Install uv
RUN pip install uv
ENV UV_LINK_MODE=copy

# Create directory for Docker Secrets
RUN mkdir -p /run/secrets
