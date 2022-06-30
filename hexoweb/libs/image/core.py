"""
@Project   : image
@Author    : abudu
@Blog      : https://www.oplog.cn
"""

from .exceptions import NoSuchProviderError


class Provider(object):
    params = None

    def upload(self, file):
        ...


from .providers import _all_providers


def all_providers():
    return list(_all_providers.keys())


def get_image_host(provider_name: str, **kwargs):
    if provider_name not in _all_providers:
        raise NoSuchProviderError(provider_name)
    return _all_providers[provider_name](**kwargs)


def get_params(provider_name):
    if provider_name not in _all_providers:
        raise NoSuchProviderError(provider_name)
    return _all_providers[provider_name].params
