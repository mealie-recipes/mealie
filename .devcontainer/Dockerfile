# syntax=docker/dockerfile:1
ARG VARIANT="3.12-trixie"
FROM mcr.microsoft.com/devcontainers/python:${VARIANT}

# Install additional OS packages
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    curl \
    build-essential \
    ffmpeg \
    libpq-dev \
    libwebp-dev \
    libsasl2-dev libldap2-dev libssl-dev \
    gnupg gnupg2 gnupg1

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
ENV UV_LINK_MODE=copy

# Install Taskfile
RUN curl -1sLf 'https://dl.cloudsmith.io/public/task/task/setup.deb.sh' | sudo -E bash \
    && apt-get install -y task

# Create directory for Docker Secrets
RUN mkdir -p /run/secrets

USER vscode
