"""
@Project   : onepush
@Author    : y1ndan
@Blog      : https://www.yindan.me
"""

from ..core import Provider


class ServerChan(Provider):
    name = 'serverchan'
    base_url = 'https://sc.ftqq.com/{}.send'
    site_url = 'https://sc.ftqq.com/3.version'

    _params = {'required': ['sckey', 'title'], 'optional': ['content']}

    def _prepare_url(self, sckey: str, **kwargs):
        self.url = self.base_url.format(sckey)
        return self.url

    def _prepare_data(self, title: str, content: str = None, **kwargs):
        self.data = {'text': title, 'desp': content}
        return self.data
