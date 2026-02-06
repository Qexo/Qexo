from functools import wraps
from typing import Callable


def check_if_sso_only(func: Callable) -> Callable:
    """
    This decorator is used to check if SSO_ONLY enabled.
    Please use it for another login functions besides SSO login function.
    When SSO_ONLY_ENABLED is true and any OAuthIdentity is existing,
    decorators will skip the login flow and return SSO_ONLY_ENABLED error.
    """
    from django.http import JsonResponse
    from .models import OAuthIdentity
    from .functions import check_sso_only
    from ...functions import gettext

    @wraps(func)
    def wrapper(request, *args, **kwargs) -> JsonResponse:
        if not check_sso_only():
            return func(request, *args, **kwargs)
        elif not OAuthIdentity.objects.exists():
            return func(request, *args, **kwargs)
        else:
            return JsonResponse({"msg": gettext("SSO_ONLY_ENABLED"), "status": False})

    return wrapper


def mixin_oauth_languages(func: Callable) -> Callable:
    """
    Mixin OAuth languages to Qexo`s i18n libs
    """
    from . import SUPPORTED_LANGUAGES
    from pathlib import Path
    import json
    base_path = Path(__file__).parent / 'languages'

    @wraps(func)
    def wrapper(*args, **kwargs):
        language = func(*args, **kwargs)
        if language.name in SUPPORTED_LANGUAGES:
            path = (base_path / f'{language.name}.json').resolve()
            if path.exists():
                with open(path) as f:
                    data = json.load(f)
                    language.default['data'] = {**language.default['data'], **data}
                return language
        return language

    return wrapper
