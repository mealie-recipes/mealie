# syntax=docker/dockerfile:1
FROM mcr.microsoft.com/devcontainers/python:3.14-trixie

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

# Python stays with the base image so the interpreter path in devcontainer.json doesn't move.
COPY --from=jdxcode/mise:2026.11.2 /usr/local/bin/mise /usr/local/bin/mise
ENV MISE_DISABLE_TOOLS=python \
    MISE_TRUSTED_CONFIG_PATHS=/workspaces \
    PATH="/home/vscode/.local/share/mise/shims:${PATH}" \
    UV_LINK_MODE=copy

# Create directory for Docker Secrets
RUN mkdir -p /run/secrets

USER vscode
