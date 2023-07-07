FROM python:alpine3.17
WORKDIR /root
COPY . .
RUN chmod +x ./migrate.sh && ./migrate.sh

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000", "--noreload" ] 
