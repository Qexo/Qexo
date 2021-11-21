pip install -r requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate
rm -rf /vercel/path1/staticfiles_build
python3 manage.py collectstatic