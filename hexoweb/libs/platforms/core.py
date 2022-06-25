from .exceptions import NoSuchProviderError


class Provider(object):
    params = None

    def get_post(self, post):
        ...

    def get_content(self, file):
        ...

    def get_path(self, path):
        ...

    def get_posts(self):
        ...

    def get_pages(self):
        ...

    def get_configs(self):
        ...

    def save(self, file, content):
        ...

    def delete(self, path):
        ...

    def delete_hooks(self):
        ...

    def create_hook(self, config):
        ...



from .providers import _all_providers


def all_providers():
    return list(_all_providers.keys())


def get_params(provider_name):
    if provider_name not in _all_providers:
        raise NoSuchProviderError(provider_name)
    return _all_providers[provider_name].params


def get_provider(provider_name: str, **kwargs):
    if provider_name not in _all_providers:
        raise NoSuchProviderError(provider_name)
    return _all_providers[provider_name](**kwargs)
