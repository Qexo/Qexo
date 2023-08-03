"""
@Project   : onepush
@Author    : y1ndan
@Blog      : https://www.yindan.me
"""

from ..core import Provider


class PushPlus(Provider):
    name = 'PushPlus'
    base_url = 'https://www.pushplus.plus/send'
    site_url = 'https://www.pushplus.plus/doc'

    _params = {
        'required': ['token', 'content'],
        'optional': ['title', 'topic', 'markdown', 'channel', 'webhook', 'callbackUrl']
    }

    def _prepare_url(self, **kwargs):
        self.url = self.base_url
        return self.url

    def _prepare_data(self,
                      content: str,
                      token: str = None,
                      title: str = None,
                      topic: str = None,
                      markdown: bool = False,
                      channel: str = None,
                      webhook: str = None,
                      callbackUrl: str = None,
                      **kwargs):
        self.data = {
            'token': token,
            'title': title,
            'content': content,
            'template': 'markdown' if markdown else 'html',
            'topic': topic,
            'channel': channel,
            'webhook': webhook,
            'callbackUrl': callbackUrl
        }
        return self.data

    def _send_message(self):
        return self.request('post', self.url, json=self.data)
