FROM python:3.11
WORKDIR /root
COPY . .

ARG CN=false
RUN if [ "$CN" = "true" ]; then \
        pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/ && \
        pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn; \
    fi

RUN python -m pip install --upgrade pip && \
    pip install -r requirements_withoutmysql.txt && \
    python3 manage.py makemigrations && \
    python3 manage.py migrate

EXPOSE 3000 8000

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000", "--noreload" ] 
