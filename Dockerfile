FROM python:3.12.12-alpine3.23 AS build

LABEL org.opencontainers.image.authors="abudulin@foxmail.com"

WORKDIR /app
COPY . /app

ENV DOCKER=1

ARG CN=false
RUN if [ "$CN" = "true" ]; then \
        sed -i 's#https\?://dl-cdn.alpinelinux.org/alpine#https://mirrors.tuna.tsinghua.edu.cn/alpine#g' /etc/apk/repositories && \
        pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/ && \
        pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn; \
    fi

RUN apk add --no-cache build-base musl-dev musl libpq-dev libffi-dev openssl-dev cargo bzip2-dev

RUN python -m pip install --upgrade pip && \
    pip install --prefer-binary -r requirements.txt && \
    chmod +x /app/entrypoint.sh

# 生产阶段
FROM python:3.12.12-alpine3.23

WORKDIR /app
COPY --from=build /app /app
COPY --from=build /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=build /usr/local/bin /usr/local/bin
RUN apk add --no-cache libpq

EXPOSE 8000

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DOCKER=1 \
    WORKERS=4 \
    THREADS=4 \
    TIMEOUT=600

ENTRYPOINT ["/app/entrypoint.sh"]