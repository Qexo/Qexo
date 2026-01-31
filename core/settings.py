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
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-mrf1flh+i8*!ao73h6)ne#%gowhtype!ld#+(j^r*!^11al2vz'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

LOCAL_CONFIG = False

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
    'passkeys',
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

# WebAuthn / Passkeys Configuration
AUTHENTICATION_BACKENDS = [
    'passkeys.backend.PasskeyModelBackend',
    'django.contrib.auth.backends.ModelBackend',
]

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
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

errors = ""

if os.environ.get("MONGODB_HOST"):  # 使用MONGODB
    logging.info("使用环境变量中的MongoDB数据库")
    for env in ["MONGODB_HOST", "MONGODB_PORT", "MONGODB_PASS"]:
        if env not in os.environ:
            if env == "MONGODB_USER" and "MONGODB_USERNAME" in os.environ:
                continue
            if env == "MONGODB_PASS" and "MONGODB_PASSWORD" in os.environ:
                continue
            errors += f"\"{env}\" "
    DATABASES = {
        'default': {
            'ENGINE': 'django_mongodb_backend',
            'NAME': os.environ.get("MONGODB_DB") or os.environ.get("MONGODB_NAME") or 'django',
            'HOST': os.environ.get("MONGODB_HOST"),
            'PORT': int(os.environ.get("MONGODB_PORT", "27017")),
            'USER': os.environ.get("MONGODB_USER") or os.environ.get("MONGODB_USERNAME") or "root",
            'PASSWORD': os.environ.get("MONGODB_PASS") or os.environ.get("MONGODB_PASSWORD"),
            'OPTIONS': {
                'authSource': os.environ.get("MONGODB_AUTH_DB") or os.environ.get("MONGODB_AUTHDB") or "admin",
                'authMechanism': os.environ.get("MONGODB_AUTH_MECHANISM") or 'SCRAM-SHA-1',
            }
        }
    }
elif os.environ.get("PG_HOST") or os.environ.get("POSTGRES_HOST"):  # 使用 PostgreSQL
    logging.info("使用环境变量中的PostgreSQL数据库")
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
            'NAME': os.environ.get("PG_DB") or os.environ.get("POSTGRES_DB") or os.environ.get(
                "POSTGRES_DATABASE") or "root",
            'USER': os.environ.get("PG_USER") or os.environ.get("POSTGRES_USERNAME") or os.environ.get(
                "POSTGRES_USER") or "root",
            'PASSWORD': os.environ.get("PG_PASS") or os.environ.get("POSTGRES_PASSWORD"),
            'HOST': os.environ.get("PG_HOST") or os.environ.get("POSTGRES_HOST"),
            'PORT': os.environ.get("PG_PORT") or os.environ.get("POSTGRES_PORT") or 5432,
        }
    }
elif os.environ.get("MYSQL_HOST"):  # 使用MYSQL
    logging.info("使用环境变量中的MySQL数据库")
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
            'OPTIONS': {
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'"
            }
        }
    }
    if os.environ.get("MYSQL_SSL"):
        DATABASES["default"]["OPTIONS"]["ssl"] = {
            "ssl_verify_cert": True,
            "ssl_verify_identity": False,
        }
    if os.environ.get("PLANETSCALE"):
        DATABASES["default"]["ENGINE"] = "hexoweb.libs.django_psdb_engine"
elif os.path.exists(BASE_DIR / "configs.py"):
    import configs

    DATABASES = configs.DATABASES
    LOCAL_CONFIG = True
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

def _load_allowed_hosts(local_config):
    if local_config:
        # 本地配置模式：必须设置 DOMAINS
        try:
            hosts = configs.DOMAINS
        except AttributeError:
            raise exceptions.InitError('本地 configs.py 缺少 DOMAINS, 请设置为 ["example.com"]')
        
        if not isinstance(hosts, (list, tuple)):
            raise exceptions.InitError('本地配置 DOMAINS 必须为列表, 例如 ["example.com"]')
        
        if (not hosts) or hosts == ["*"]:
            raise exceptions.InitError('本地配置 DOMAINS 未配置有效域名, 请填写实际域名, 例如 ["example.com"]')
        
        logging.info(f"从本地配置获取域名: {list(hosts)}")
        return list(hosts)
    
    else:
        # 环境变量模式：收集 DOMAINS 和 Vercel 环境变量
        domains_hosts = []
        vercel_hosts = []
        
        # 解析 DOMAINS 环境变量
        domains_raw = os.environ.get("DOMAINS")
        if domains_raw:
            try:
                parsed = json.loads(domains_raw)
                if not isinstance(parsed, (list, tuple)):
                    raise exceptions.InitError('环境变量 DOMAINS 必须为列表, 例如 ["example.com"]')
                domains_hosts = [h for h in parsed if h and h != "*"]
            except json.JSONDecodeError as exc:
                raise exceptions.InitError(f"DOMAINS 环境变量解析失败: {exc}")
        
        # 收集 Vercel 环境变量
        for env_var in ["VERCEL_URL", "VERCEL_BRANCH_URL", "VERCEL_PROJECT_PRODUCTION_URL"]:
            url = os.environ.get(env_var)
            if url and url not in vercel_hosts:
                vercel_hosts.append(url)
        
        # 确定最终 hosts
        if domains_hosts and vercel_hosts:
            # 两者都有：取交集，交集为空则用并集
            hosts = [h for h in domains_hosts if h in vercel_hosts] or list(set(domains_hosts + vercel_hosts))
            logging.info(f"从 DOMAINS 和 Vercel 环境变量获取域名: {hosts}")
        else:
            hosts = domains_hosts or vercel_hosts
            if not hosts:
                raise exceptions.InitError('DOMAINS 未设置且未检测到 Vercel 环境变量, 请为 DOMAINS 环境变量填写实际域名, 例如 ["example.com"]')
            logging.info(f"从{'环境变量 DOMAINS' if domains_hosts else 'Vercel 环境变量'}获取域名: {hosts}")
        
        return hosts


def _build_csrf_trusted_origins(hosts):
    origins = []
    for host in hosts:
        if (not host) or host == "*":
            continue
        host = host.rstrip("/")
        if "://" in host:
            origins.append(host)
        else:
            origins.append(f"https://{host}")
            origins.append(f"http://{host}")
    return origins


ALLOWED_HOSTS = _load_allowed_hosts(LOCAL_CONFIG)
CSRF_TRUSTED_ORIGINS = _build_csrf_trusted_origins(ALLOWED_HOSTS)

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'zh-Hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True


USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# STATIC_URL = 'static/'
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, "static"),
# ]
# STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SESSION_COOKIE_AGE = 86400

# Passkeys / WebAuthn Configuration
def get_fido_server_id(request=None):
    """动态获取FIDO Server ID（RP ID），与当前访问域名保持一致。"""
    host = None

    # 优先使用实际请求域名（包含端口时去掉端口）
    if request:
        try:
            host = request.get_host()
        except Exception:
            host = None

    # 回退到ALLOWED_HOSTS配置
    if not host:
        host = (ALLOWED_HOSTS[0] if ALLOWED_HOSTS else "localhost")

    # 清理协议和端口
    if "://" in host:
        host = host.split("://", 1)[1]
    host = host.split(":", 1)[0].strip()

    # FIDO要求RP ID是有效的注册域或localhost
    if not host:
        return "localhost"

    return host

FIDO_SERVER_ID = get_fido_server_id
FIDO_SERVER_NAME = "Qexo"
KEY_ATTACHMENT = None  # 允许任何类型的认证器（平台或跨平台）
