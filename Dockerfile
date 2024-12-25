FROM python:3.11.11-bookworm AS build

LABEL org.opencontainers.image.authors="abudulin@foxmail.com"

WORKDIR /app
COPY . /app

SHELL ["/bin/bash", "-c"]
ENV DOCKER=1

ARG CN=false
RUN if [ "$CN" = "true" ]; then \
        pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/ && \
        pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn && \
        apt-get update && apt-get install -y build-essential; \
    fi

RUN curl https://sh.rustup.rs -sSf | sh -s -- -y

RUN source $HOME/.cargo/env && \
    python -m pip install --upgrade pip && \
    pip install --prefer-binary -r requirements-slim.txt && \
    chmod +x /app/entrypoint.sh

# 生产阶段
FROM python:3.11.11-slim-bookworm

WORKDIR /app
COPY --from=build /app /app
COPY --from=build /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=build /usr/local/bin /usr/local/bin

EXPOSE 8000

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DOCKER=1 \
    WORKERS=4 \
    THREADS=4 \
    TIMEOUT=600

ENTRYPOINT ["/app/entrypoint.sh"]