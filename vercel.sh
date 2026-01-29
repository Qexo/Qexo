#!/bin/bash

# Install dependencies
python3 -m pip install --break-system-packages -r requirements.txt

# Migrate database
python3 manage.py makemigrations
python3 manage.py migrate --noinput