"""
@Project   : onepush
@Author    : y1ndan & abudu
@Blog      : https://www.yindan.me
"""

from ..core import Provider


class PushDeer(Provider):
    name = 'Pushdeer'
    base_url = 'https://api2.pushdeer.com/message/push'
    site_url = 'https://www.pushdeer.com/official.html'

    _params = {
        'required': ['pushkey', 'content'],
        'optional': ['url', 'title', 'type']
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
            'type': type,
        }
        if title:
            self.data["text"] = title
            self.data["desp"] = content
        else:
            self.data["text"] = content
        return self.data

    def _send_message(self):
        return self.request('post', self.url, json=self.data)
