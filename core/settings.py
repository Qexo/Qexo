from pathlib import Path
import os
import json
import random
import hexoweb.exceptions as exceptions
import logging
import urllib3

urllib3.disable_warnings()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

LOGIN_REDIRECT_URL = "home"  # Route defined in home/urls.py
LOGOUT_REDIRECT_URL = "home"  # Route defined in home/urls.py

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-mrf1flh+i8*!ao73h6)ne#%gowhtype!ld#+(j^r*!^11al2vz'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

try:
    import configs  # 本地部署
    ALLOWED_HOSTS = configs.DOMAINS
except:
    logging.info("获取本地配置文件失败, 使用环境变量获取配置")  # Serverless部署
    ALLOWED_HOSTS = json.loads(os.environ.get("DOMAINS", False)) if os.environ.get("DOMAINS", False) else ["*"]

# Application definition

INSTALLED_APPS = [
    # 'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # 'django.contrib.staticfiles',
    'hexoweb.apps.ConsoleConfig',
    'corsheaders',
    # "passkeys"
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

try:
    import configs
    print("获取本地配置文件成功, 使用本地数据库配置")
    DATABASES = configs.DATABASES
except:
    errors = ""
    if os.environ.get("MONGODB_HOST"):  # 使用MONGODB
        print("使用环境变量中的MongoDB数据库")
        for env in ["MONGODB_HOST", "MONGODB_PORT", "MONGODB_PASS"]:
            if env not in os.environ:
                if env == "MONGODB_USER" and "MONGODB_USERNAME" in os.environ:
                    continue
                if env == "MONGODB_PASS" and "MONGODB_PASSWORD" in os.environ:
                    continue
                errors += f"\"{env}\" "
        DATABASES = {
            'default': {
                'ENGINE': 'djongo',
                'ENFORCE_SCHEMA': False,
                'NAME': 'django',
                'CLIENT': {
                    'host': os.environ.get("MONGODB_HOST"),
                    'port': int(os.environ.get("MONGODB_PORT")),
                    'username': os.environ.get("MONGODB_USER") or os.environ.get("MONGODB_USERNAME") or "root",
                    'password': os.environ.get("MONGODB_PASS") or os.environ.get("MONGODB_PASSWORD"),
                    'authSource': os.environ.get("MONGODB_DB") or "root",
                    'authMechanism': 'SCRAM-SHA-1'
                }
            }
        }
    elif os.environ.get("PG_HOST") or os.environ.get("POSTGRES_HOST"):  # 使用 PostgreSQL
        print("使用环境变量中的PostgreSQL数据库")
        for env in ["PG_HOST", "PG_PASS"]:
            if (env not in os.environ) and (env.replace("PG_", "POSTGRES_") not in os.environ):  # 识别不同的格式
                if env == "PG_USER" and "POSTGRES_USERNAME" in os.environ:
                    continue
                if env == "PG_PASS" and "POSTGRES_PASSWORD" in os.environ:
                    continue
                errors += f"\"{env}\" "
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.environ.get("PG_DB") or os.environ.get("POSTGRES_DB") or os.environ.get("POSTGRES_DATABASE") or "root",
                'USER': os.environ.get("PG_USER") or os.environ.get("POSTGRES_USERNAME") or os.environ.get("POSTGRES_USER") or "root",
                'PASSWORD': os.environ.get("PG_PASS") or os.environ.get("POSTGRES_PASSWORD"),
                'HOST': os.environ.get("PG_HOST") or os.environ.get("POSTGRES_HOST"),
                'PORT': os.environ.get("PG_PORT") or os.environ.get("POSTGRES_PORT") or 5432,
            }
        }
    elif os.environ.get("MYSQL_HOST"):  # 使用MYSQL
        print("使用环境变量中的MySQL数据库")
        for env in ["MYSQL_HOST", "MYSQL_PORT", "MYSQL_PASSWORD"]:
            if env not in os.environ:
                if env == "MYSQL_PASSWORD" and "MYSQL_PASS" in os.environ:
                    continue
                errors += f"\"{env}\" "
        import pymysql

        pymysql.install_as_MySQLdb()
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': os.environ.get('MYSQL_NAME') or os.environ.get('MYSQL_DB') or 'root',
                'HOST': os.environ.get('MYSQL_HOST'),
                'PORT': os.environ.get('MYSQL_PORT'),
                'USER': os.environ.get('MYSQL_USER') or os.environ.get('MYSQL_USERNAME') or 'root',
                'PASSWORD': os.environ.get('MYSQL_PASSWORD') or os.environ.get('MYSQL_PASS'),
                'OPTIONS': {'ssl': {'ca': False}}
            }
        }
        if os.environ.get("PLANETSCALE"):
            DATABASES["default"]["ENGINE"] = "hexoweb.libs.django_psdb_engine"
    else:
        errors = "数据库"

    # Vercel 无法使用 Sqlite
    # else:  # sqlite
    #     print("使用sqlite数据库")
    #     import sqlite3
    #
    #     DATABASES = {
    #         'default': {
    #             'ENGINE': 'django.db.backends.sqlite3',
    #             'NAME': 'qexo_data.db',
    #         }
    #     }

    if errors:
        logging.error(f"{errors}未设置, 请查看: https://www.oplog.cn/qexo/start/build.html")
        raise exceptions.InitError(f"{errors}未设置, 请查看: https://www.oplog.cn/qexo/start/build.html")

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'zh-Hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

# STATIC_URL = '/static/'
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, "static"),
# ]
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_build', 'static')

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SESSION_COOKIE_AGE = 86400
