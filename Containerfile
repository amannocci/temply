# Base image for build
ARG base_image_version=3.10.12
FROM python:${base_image_version}-bullseye as builder

# Switch workdir
WORKDIR /opt/temply

# Arguments
ARG platform_arch
ARG app_version

# Copy files
COPY . .

# Install poetry
ENV \
  PATH="/opt/poetry/bin:${PATH}" \
  POETRY_HOME=/opt/poetry \
  POETRY_VIRTUALENVS_CREATE=false
RUN \
  curl -sSL https://install.python-poetry.org | python3 -

# Build
RUN \
  poetry install \
  && poetry run pyinstaller temply.spec \
  && mv /opt/temply/dist/temply /opt/temply/dist/temply-${app_version}-${platform_arch}
