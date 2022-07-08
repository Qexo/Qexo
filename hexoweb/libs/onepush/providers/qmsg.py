"""
@Project   : onepush
@Author    : y1ndan
@Blog      : https://www.yindan.me
"""

from ..core import Provider


class Qmsg(Provider):
    name = 'qmsg'
    base_url = 'https://qmsg.zendee.cn/{}/{}'
    site_url = 'https://qmsg.zendee.cn/api.html'

    _params = {
        'required': ['key'],
        'optional': ['title', 'content', 'mode', 'qq']
    }

    def _prepare_url(self, key: str, mode: str = 'send', **kwargs):
        self.url = self.base_url.format(mode, key)
        return self.url

    def _prepare_data(self,
                      title: str = None,
                      content: str = None,
                      qq: str = None,
                      **kwargs):
        message = self.process_message(title, content)
        self.data = {'msg': message, 'qq': qq}
        return self.data
