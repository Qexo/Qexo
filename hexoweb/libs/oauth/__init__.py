import json
import logging
import os
from typing import Dict, Type

from authlib.integrations.django_client import OAuth

from .OAuthProvider import OAuthProvider, GitHub, OIDC

__oauth_manager = OAuth()
__provider_objects: Dict[str, OAuthProvider] = {}
__provider_configs: Dict = {}
if os.environ.get("OAUTH_PROVIDERS"):
    try:
        __provider_configs = json.loads(os.environ["OAUTH_PROVIDERS"])
    except json.decoder.JSONDecodeError:
        logging.error(f"OAUTH_PROVIDERS environment variable not found or format")

__sso_only: bool = os.environ.get("SSO_ONLY") in ['1', 'true', 'True']

SUPPORTED_TYPES: Dict[str, Type[OAuthProvider]] = {
    "github": GitHub,
    "oidc": OIDC
}
SUPPORTED_LANGUAGES = ['zh_CN', 'zh_TW', 'en_UK', 'en_US', 'fr_FR', 'ja_JP', 'ko_KR']
