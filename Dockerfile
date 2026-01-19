# syntax=docker/dockerfile:1.4
FROM artifactory.raiffeisen.ru/python-community-docker/python:3.9.12-slim-rbru

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash \
        ca-certificates \
        curl \
        jq \
        dnsutils \
        iputils-ping \
        netcat-openbsd \
        openssl \
        vim-tiny \
        less \
        procps \
        tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml README.md /app/
COPY src /app/src

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=secret,id=artifactory_user \
    --mount=type=secret,id=artifactory_password \
    bash -euxo pipefail -c '\
      python -m venv /opt/venv && \
      ARTIFACTORY_USER=$(cat /run/secrets/artifactory_user) && \
      ARTIFACTORY_PASSWORD=$(cat /run/secrets/artifactory_password) && \
      /opt/venv/bin/pip install --upgrade pip && \
      /opt/venv/bin/pip install --no-cache-dir . \
        --trusted-host artifactory.raiffeisen.ru \
        --index-url "https://${ARTIFACTORY_USER}:${ARTIFACTORY_PASSWORD}@artifactory.raiffeisen.ru/artifactory/api/pypi/remote-pypi/simple" \
        --extra-index-url "https://${ARTIFACTORY_USER}:${ARTIFACTORY_PASSWORD}@artifactory.raiffeisen.ru/artifactory/api/pypi/datalake-release-pypi/simple" \
    '

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

ENV ADT_DUMMY_IN_CLUSTER=1

CMD ["sleep", "infinity"]
