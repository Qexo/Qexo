"""
@Project   : onepush
@Author    : y1ndan & abudu
@Blog      : https://www.yindan.me
"""

from ..core import Provider


class PushDeer(Provider):
    name = 'pushdeer'
    base_url = 'https://api2.pushdeer.com/message/push'
    site_url = 'https://www.pushdeer.com/official.html'

    _params = {
        'required': ['pushkey', 'title', 'content'],
        'optional': ['url', 'type']
    }

    def _prepare_url(self, url: str = None, **kwargs):
        self.url = self.base_url
        if url:
            self.url = url
        return self.url

    def _prepare_data(self,
                      content: str,
                      pushkey: str,
                      title: str = None,
                      type: str = "markdown",
                      **kwargs):
        self.data = {
            'pushkey': pushkey,
            'text': title,
            'type': type,
            'desp': content
        }
        return self.data

    def _send_message(self):
        return self.request('post', self.url, json=self.data)
