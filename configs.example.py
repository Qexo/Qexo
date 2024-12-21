from pathlib import Path

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': Path(__file__).parent / 'db' / 'db.sqlite3',
    }
}