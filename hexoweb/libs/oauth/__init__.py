import os

from authlib.integrations.django_client import OAuth


__oauth_manager = OAuth()

__sso_only: bool = os.environ.get("SSO_ONLY") in ['1', 'true', 'True']

SUPPORTED_LANGUAGES = ['zh_CN', 'zh_TW', 'en_UK', 'en_US', 'fr_FR', 'ja_JP', 'ko_KR']
