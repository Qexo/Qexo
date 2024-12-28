#!/bin/bash

# Install dependencies
python3 -m pip install -r requirements.txt

# Migrate database
python3 manage.py makemigrations
python3 manage.py migrate