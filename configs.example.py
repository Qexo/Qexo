from pathlib import Path
import os
import json

DOMAINS = json.loads(os.environ.get("DOMAINS", "[]")) or ["example.com"]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': Path(__file__).parent / 'db' / 'db.sqlite3',
    }
}