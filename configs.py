# 数据库配置
# DOMAINS处需要加上自己的本机IP或者域名 相当于设置白名单
import pymysql,os

DOMAINS = ["127.0.0.1","10.0.0.10"]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join('/app/db' , 'db.sqlite3'),
    }
}
