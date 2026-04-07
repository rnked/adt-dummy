# Первый слой, для всех проектов идетичен. Тут мы копируем зависимости из собранного ранее в пайплайне кеша.
ARG BASE_IMAGE="artifactory.raiffeisen.ru/python-community-docker/python:3.9.12-slim-rbru"

FROM ${BASE_IMAGE} AS deps-image

ENV VENV_PATH="/srv/www/.venv"

COPY [".venv", "${VENV_PATH}"]

RUN find ${VENV_PATH}/bin -type f -exec sed -i 's#/.*/\.venv#/srv/www/.venv#g' {} + \
    && ln -sf /usr/local/bin/python ${VENV_PATH}/bin/python

# Второй слой. Собираем итоговый образ
FROM ${BASE_IMAGE} as app-image

# Обявляем нужные переменные
ENV REQUESTS_CA_BUNDLE="/etc/ssl/certs/ca-certificates.crt"
ENV VENV_PATH="/srv/www/.venv"
ENV PATH="${VENV_PATH}/bin:${PATH}"
ENV PYTHONPATH="/app/src"

ARG DEBIAN_REPO_URL

# Обновляем и скачиваем нужные пакеты debian
RUN --mount=type=secret,id=creds \
    cat /kaniko/creds > /etc/apt/auth.conf \
    && rm -f /etc/apt/sources.list.d/debian.sources \
    && echo 'Acquire::https::artifactory.raiffeisen.ru::Verify-Peer "false";' > /etc/apt/apt.conf.d/80-ssl-exceptions \
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
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую деррикторию
WORKDIR /app

# Копируем необходимые файлы
COPY --from=deps-image ${VENV_PATH} ${VENV_PATH}
COPY pyproject.toml README.md /app/
COPY src /app/src

ENV ADT_DUMMY_IN_CLUSTER=1

CMD ["sleep", "infinity"]