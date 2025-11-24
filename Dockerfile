# syntax=docker/dockerfile:1.6
# ADT Dummy: toolbox container for k8s connectivity & diagnostics
FROM artifactory.raiffeisen.ru/python-community-docker/python:3.9.12-slim-rbru

ARG TRINO_CLI_VERSION=426
ARG DEBIAN_FRONTEND=noninteractive
ARG PIP_ARTIFACTORY_HOST=artifactory.raiffeisen.ru
ARG PIP_ARTIFACTORY_INDEX_PATH=artifactory/api/pypi/remote-pypi/simple
ARG PIP_ARTIFACTORY_EXTRA_INDEX_PATH=artifactory/api/pypi/datalake-release-pypi/simple

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
      bash \
      ca-certificates \
      coreutils \
      procps \
      less \
      grep \
      sed \
      gawk \
      vim-tiny \
      curl \
      wget \
      iproute2 \
      netcat-openbsd \
      dnsutils \
      telnet \
      jq \
      postgresql-client \
      default-jre-headless \
      libpq5 \
    ; \
    rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=secret,id=artifactory_user,required \
    --mount=type=secret,id=artifactory_password,required \
    HOST="${PIP_ARTIFACTORY_HOST}" INDEX_PATH="${PIP_ARTIFACTORY_INDEX_PATH}" EXTRA_INDEX_PATH="${PIP_ARTIFACTORY_EXTRA_INDEX_PATH}" \
    bash -euxo pipefail -c '\
      ARTIFACTORY_USER=$(cat /run/secrets/artifactory_user); \
      ARTIFACTORY_PASSWORD=$(cat /run/secrets/artifactory_password); \
      python -m pip install --upgrade pip \
        --trusted-host "${HOST}" \
        --index-url "https://${ARTIFACTORY_USER}:${ARTIFACTORY_PASSWORD}@${HOST}/${INDEX_PATH}" \
        --extra-index-url "https://${ARTIFACTORY_USER}:${ARTIFACTORY_PASSWORD}@${HOST}/${EXTRA_INDEX_PATH}"; \
      python -m pip install --no-cache-dir \
        --trusted-host "${HOST}" \
        --index-url "https://${ARTIFACTORY_USER}:${ARTIFACTORY_PASSWORD}@${HOST}/${INDEX_PATH}" \
        --extra-index-url "https://${ARTIFACTORY_USER}:${ARTIFACTORY_PASSWORD}@${HOST}/${EXTRA_INDEX_PATH}" \
        trino==0.326.0 \
        urllib3==1.26.18 \
        requests==2.31.0 \
        idna==3.7 \
        psycopg2-binary==2.9.9
    '

RUN set -eux; \
    curl -fsSL "https://repo1.maven.org/maven2/io/trino/trino-cli/${TRINO_CLI_VERSION}/trino-cli-${TRINO_CLI_VERSION}-executable.jar" \
      -o /usr/local/bin/trino; \
    chmod +x /usr/local/bin/trino

WORKDIR /opt/adt-dummy

COPY scripts/entrypoint.sh scripts/http-health.sh ./scripts/
COPY scripts/helpers ./scripts/helpers

RUN chmod +x ./scripts/entrypoint.sh ./scripts/http-health.sh ./scripts/helpers/*.sh; \
    ln -s /opt/adt-dummy/scripts/entrypoint.sh /usr/local/bin/adt-dummy; \
    ln -s /opt/adt-dummy/scripts/http-health.sh /usr/local/bin/http-health; \
    ln -s /opt/adt-dummy/scripts/helpers/psql.sh /usr/local/bin/psql-helper; \
    ln -s /opt/adt-dummy/scripts/helpers/trino.sh /usr/local/bin/trino-helper; \
    ln -s /opt/adt-dummy/scripts /usr/local/lib/adt-dummy

ENV PATH="/opt/adt-dummy/scripts:${PATH}"
ENTRYPOINT ["/opt/adt-dummy/scripts/entrypoint.sh"]
CMD ["bash"]
