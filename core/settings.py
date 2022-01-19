from pathlib import Path
import os
import json
import random

QEXO_VERSION = "1.5.1"

ALL_SETTINGS = [["ABBRLINK_ALG", "crc16", False, "短链接算法"],
                ["ABBRLINK_REP", "dec", False, "短链接格式dec/hex"],
                ["CDN_PREV", "https://cdn.jsdelivr.net/npm/", True, "调用NPM的CDN前缀"],
                ["GH_REPO", "", False, "Github用户名"],
                ["GH_REPO_BRANCH", "", False, "仓库分支"],
                ["GH_REPO_PATH", "", False, "仓库路径"],
                ["GH_TOKEN", "", False, "Github密钥"],
                ["IMG_API", "", False, "图床API地址"],
                ["IMG_CUSTOM_BODY", "", False, "图床自定义请求主体"],
                ["IMG_CUSTOM_HEADER", "", False, "图床自定义请求头"],
                ["IMG_CUSTOM_URL", "", False, "图床自定义链接前缀"],
                ["IMG_JSON_PATH", "", False, "图床JSON路径"],
                ["IMG_POST", "", False, "图床图片请求名"],
                ["IMG_TYPE", "", False, "图床类别"],
                ["INIT", "2", False, "初始化标识"],
                ["QEXO_ICON",
                 "https://cdn.jsdelivr.net/npm/qexo-static@1.0.6/assets/img/brand/favicon.ico",
                 False, "站点ICON"],
                ["QEXO_LOGO",
                 "https://cdn.jsdelivr.net/npm/qexo-static@1.0.6/assets/img/brand/qexo.png",
                 False, "站点LOGO"],
                ["QEXO_NAME", "Hexo管理面板", False, "站点名"],
                ["QEXO_SPLIT", "-", False, "站点分隔符"],
                ["S3_ACCESS_KEY", "", False, "S3权限密钥"],
                ["S3_BUCKET", "", False, "S3桶"],
                ["S3_ENDPOINT", "", False, "S3边缘节点"],
                ["S3_KEY_ID", "", False, "S3密钥ID"],
                ["S3_PATH", "", False, "S3上传路径"],
                ["S3_PREV_URL", "", False, "S3链接前缀"],
                ["VDITOR_EMOJI",
                 json.dumps({"微笑": "🙂", "撇嘴": "😦", "色": "😍", "发呆": "😍", "得意": "😎",
                             "流泪": "😭", "害羞": "😊", "闭嘴": "😷", "睡": "😴",
                             "大哭 ": "😡", "尴尬": "😡", "发怒": "😛", "调皮": "😀", "呲牙": "😯",
                             "惊讶": "🙁", "难过": "😎", "酷": "😨", "冷汗": "😱", "抓狂": "😵", "吐 ": "😋",
                             "偷笑": "☺", "愉快": "🙄", "白眼": "🙄", "傲慢": "😋", "饥饿": "😪", "困": "😫",
                             "惊恐": "😓", "流汗": "😃", "憨笑": "😃", "悠闲 ": "😆", "奋斗": "😆",
                             "咒骂": "😆", "疑问": "😆", "嘘": "😵", "晕": "😆", "疯了": "😆", "衰": "😆",
                             "骷髅": "💀", "敲打": "😬", "再见 ": "😘", "擦汗": "😆", "抠鼻": "😆",
                             "鼓掌": "👏", "糗大了": "😆", "坏笑": "😆", "左哼哼": "😆", "右哼哼": "😆",
                             "哈欠": "😆", "鄙视": "😆", "委屈 ": "😆", "快哭了": "😆", "阴险": "😆",
                             "亲亲": "😘", "吓": "😓", "可怜": "😆", "菜刀": "🔪", "西瓜": "🍉", "啤酒": "🍺",
                             "篮球": "🏀", "乒乓 ": "⚪", "咖啡": "☕", "饭": "🍚", "猪头": "🐷", "玫瑰": "🌹",
                             "凋谢": "🌹", "嘴唇": "👄", "爱心": "💗", "心碎": "💔", "蛋糕": "🎂", "闪电 ": "⚡",
                             "炸弹": "💣", "刀": "🗡", "足球": "⚽", "瓢虫": "🐞", "便便": "💩", "月亮": "🌙",
                             "太阳": "☀", "礼物": "🎁", "拥抱": "🤗", "强 ": "👍", "弱": "👎", "握手": "👍",
                             "胜利": "✌", "抱拳": "✊", "勾引": "✌", "拳头": "✊", "差劲": "✌", "爱你": "✌",
                             "NO": "✌", "OK": "🙂", "嘿哈": "🙂", "捂脸": "🙂", "奸笑": "🙂", "机智": "🙂",
                             "皱眉": "🙂", "耶": "🙂", "吃瓜": "🙂", "加油": "🙂", "汗": "🙂", "天啊": "👌",
                             "社会社会": "🙂", "旺柴": "🙂", "好的": "🙂", "哇": "🙂"}), True, "自定义表情"],
                ["WEBHOOK_APIKEY", ''.join(random.choice("qwertyuiopasdfghjklzxcvbnm1234567890")
                                           for x in range(12)), False, "API密钥"],
                ["VERCEL_TOKEN", "", False, "Vercel密钥"],
                ["PROJECT_ID", "", False, "Qexo项目ID"]]

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

ALLOWED_HOSTS = json.loads(os.environ["DOMAINS"])

# Application definition

INSTALLED_APPS = [
    # 'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'hexoweb.apps.ConsoleConfig',
    'corsheaders',
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
        'DIRS': [BASE_DIR / 'templates']
        ,
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

DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'ENFORCE_SCHEMA': False,
        'LOGGING': {
            'version': 1,
        },
        'NAME': 'django',
        'CLIENT': {
            'host': os.environ["MONGODB_HOST"],
            'port': int(os.environ["MONGODB_PORT"]),
            'username': os.environ["MONGODB_USER"],
            'password': os.environ["MONGODB_PASS"],
            'authSource': os.environ["MONGODB_DB"],
            'authMechanism': 'SCRAM-SHA-1'
        }
    }
}

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

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_build', 'static')

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SESSION_COOKIE_AGE = 86400
