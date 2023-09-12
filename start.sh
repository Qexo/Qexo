# /bin/bash
if [ ! -z $(ls /blog) ]
then
    echo "Hexo 目录为空，自动初始化..."
    cd / && \
    hexo init blog && \
    cd blog && \
    npm i && \
    hexo g -d
    cd /app
fi
if [ ! -f /db/qexo_data.db ]
then
    echo "未发现 Qexo 数据库文件，自动初始化..."
    python3 manage.py makemigrations && \
    python3 manage.py migrate
fi
caddy file-server --listen :3000 --root /blog/public &
python3 manage.py runserver 0.0.0.0:8000 --noreload