"""Loaded by Gunicorn in the master, before any worker is forked."""
from core.secret_key import get_secret_key

get_secret_key()
