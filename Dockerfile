FROM python:alpine3.17
WORKDIR /root
COPY . .
RUN pip install -r requirements_withoutmsyql.txt && \
    python3 manage.py makemigrations && \
    python3 manage.py migrate

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000", "--noreload" ] 
