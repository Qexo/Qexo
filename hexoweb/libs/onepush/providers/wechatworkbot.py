"""
@Project   : onepush
@Author    : y1ndan
@Blog      : https://www.yindan.me
"""

from ..core import Provider


class WechatWorkBot(Provider):
    name = '企业微信机器人'
    base_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={}'
    site_url = 'https://work.weixin.qq.com/api/doc/90000/90136/91770'

    _params = {
        'required': ['key'],
        'optional': ['title', 'content', 'markdown']
    }

    def _prepare_url(self, key: str, **kwargs):
        self.url = key
        if 'https' not in key or 'http' not in key:
            self.url = self.base_url.format(key)
        return self.url

    def _prepare_data(self,
                      title: str = None,
                      content: str = None,
                      markdown: bool = False,
                      **kwargs):
        message = self.process_message(title, content)
        msgtype = 'text'
        if markdown:
            msgtype = 'markdown'

        self.data = {'msgtype': msgtype, msgtype: {'content': message}}
        return self.data

    def _send_message(self):
        return self.request('post', self.url, json=self.data)
