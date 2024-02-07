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
    return _all_providers[provider_name].Main(**kwargs)


def get_params(provider_name):
    if provider_name not in _all_providers:
        raise NoSuchProviderError(provider_name)
    return _all_providers[provider_name].Main.params


def delete_image(config):
    if not config:
        return "已删除本地记录"
    if config["provider"] not in _all_providers:
        raise NoSuchProviderError(config["provider"])
    return _all_providers[config["provider"]].delete(config)
