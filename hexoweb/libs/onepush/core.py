"""
@Project   : onepush
@Author    : y1ndan
@Blog      : https://www.yindan.me
"""

import logging

import requests
from requests.exceptions import SSLError

from .exceptions import NoSuchNotifierError
from .exceptions import OnePushException

log = logging.getLogger('onepush')


class Provider(object):
    base_url = None
    site_url = None

    _params = None

    def __init__(self):
        self.method = 'post'
        self.datatype = 'data'
        self.url = None
        self.data = None

    def _prepare_url(self, **kwargs):
        ...

    def _prepare_data(self, **kwargs):
        ...

    def _send_message(self):
        if self.method.upper() == 'GET':
            response = self.request('get', self.url, params=self.data)
        elif self.method.upper() == 'POST':
            if self.datatype.lower() == 'json':
                response = self.request('post', self.url, json=self.data)
            else:
                response = self.request('post', self.url, data=self.data)
        else:
            raise OnePushException('Request method {} not supported.'.format(self.method))

        return response

    @property
    def params(self):
        return self._params

    @staticmethod
    def process_message(title, content):
        message = content
        if title and content:
            message = '{}\n\n{}'.format(title, content)
        if title and not content:
            message = title
        return message

    @staticmethod
    def request(method, url, **kwargs):
        session = requests.Session()
        response = None
        try:
            response = session.request(method, url, **kwargs)
            log.debug('Response: {}'.format(response.text))
        except SSLError as e:
            log.error(e)
            response = session.request(method, url, verify=False, **kwargs)
            log.debug('Response: {}'.format(response.text))
        except Exception as e:
            log.error(e)
        finally:
            return response

    def notify(self, **kwargs):
        self._prepare_url(**kwargs)
        self._prepare_data(**kwargs)
        return self._send_message()


from .providers import _all_providers  # noqa: E402


def all_providers():
    return list(_all_providers.keys())


def get_notifier(provider_name: str):
    if provider_name not in _all_providers:
        raise NoSuchNotifierError(provider_name)
    return _all_providers[provider_name]()


def notify(provider_name: str, **kwargs):
    return get_notifier(provider_name).notify(**kwargs)
