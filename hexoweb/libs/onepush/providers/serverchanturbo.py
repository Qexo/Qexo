"""
@Project   : onepush
@Author    : y1ndan
@Blog      : https://www.yindan.me
"""

from ..core import Provider


class ServerChanTurbo(Provider):
    name = 'Server酱·Turbo版'
    base_url = 'https://sctapi.ftqq.com/{}.send'
    site_url = 'https://sct.ftqq.com'

    _params = {
        'required': ['sctkey', 'title'],
        'optional': ['content', 'channel', 'openid']
    }

    def _prepare_url(self, sctkey: str, **kwargs):
        self.url = self.base_url.format(sctkey)
        return self.url

    def _prepare_data(self,
                      title: str,
                      content: str = None,
                      channel: int = None,
                      openid: str = None,
                      **kwargs):
        self.data = {
            'text': title,
            'desp': content,
            'channel': channel,
            'openid': openid
        }
        return self.data
