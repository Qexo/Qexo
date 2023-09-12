# /bin/bash
caddy file-server --listen :3000 --root /blog/public &
python3 manage.py runserver 0.0.0.0:8000 --noreload