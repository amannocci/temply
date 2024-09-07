# Base image for build
ARG base_image_version=3.10.12
FROM python:${base_image_version}-slim-bullseye AS builder

# Switch workdir
WORKDIR /opt/temply

# Copy files
COPY . .

# Install build packages
RUN \
  apt-get update > /dev/null \
  && apt-get install -y --no-install-recommends \
    binutils="*" \
  && apt-get clean

# Install poetry
RUN \
  pip3 install --no-cache-dir --upgrade pip poetry

# Build
RUN \
  poetry install --sync --only main,build \
  && poetry run pyinstaller temply.spec
