# syntax=docker/dockerfile:1.4
FROM artifactory.raiffeisen.ru/python-community-docker/python:3.9.12-slim-rbru

ARG DEBIAN_REPO_URL

RUN --mount=type=secret,id=creds \
    cat /kaniko/creds > /etc/apt/auth.conf \
    && rm -f /etc/apt/sources.list.d/debian.sources \
    && eval "$(grep ^VERSION_CODENAME= /etc/os-release)" \
    && echo "deb $DEBIAN_REPO_URL ${VERSION_CODENAME} main" > /etc/apt/sources.list.d/sources.list \
    && echo "deb $DEBIAN_REPO_URL ${VERSION_CODENAME}-updates main" >> /etc/apt/sources.list.d/sources.list \
    && echo "deb $DEBIAN_REPO_URL ${VERSION_CODENAME}-proposed-updates main" >> /etc/apt/sources.list.d/sources.list \
    && echo "deb ${DEBIAN_REPO_URL}-security ${VERSION_CODENAME}-security main" >> /etc/apt/sources.list.d/sources.list \
    && apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        bash \
        ca-certificates \
        curl \
        jq \
        dnsutils \
        iputils-ping \
        netcat-openbsd \
        openssl \
        vim \
        less \
        procps \
        tzdata \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/* \
    && rm /etc/apt/auth.conf

WORKDIR /app
COPY pyproject.toml README.md /app/
COPY src /app/src

RUN --mount=type=secret,id=creds2 \
    bash -euxo pipefail -c '\
      python -m venv /opt/venv && \
      ARTIFACTORY_USER=$(head -1 /kaniko/creds2) && \
      ARTIFACTORY_PASSWORD=$(tail -1 /kaniko/creds2) && \
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
