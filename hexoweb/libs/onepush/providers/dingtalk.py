"""
@Project   : onepush
@Author    : y1ndan
@Blog      : https://www.yindan.me
"""

from ..core import Provider


class DingTalk(Provider):
    name = 'dingtalk'
    base_url = 'https://oapi.dingtalk.com/robot/send?access_token={}'
    site_url = 'https://developers.dingtalk.com/document/app/custom-robot-access'

    _params = {
        'required': ['token'],
        'optional': ['title', 'content', 'secret', 'markdown']
    }

    @staticmethod
    def encrypt(secret: str):
        import time
        import hmac
        import hashlib
        import base64
        import urllib.parse

        timestamp = str(round(time.time() * 1000))
        secret_enc = secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(
            secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return timestamp, sign

    def _prepare_url(self, token: str, secret: str = None, **kwargs):
        self.url = token
        if 'https' not in token or 'http' not in token:
            self.url = self.base_url.format(token)

        if secret:
            timestamp, sign = self.encrypt(secret)
            self.url = self.url + '&timestamp={}&sign={}'.format(
                timestamp, sign)
        return self.url

    def _prepare_data(self,
                      title: str = None,
                      content: str = None,
                      markdown: bool = False,
                      **kwargs):
        message = self.process_message(title, content)
        self.data = {'msgtype': 'text', 'text': {'content': message}}

        if markdown:
            self.data = {
                'msgtype': 'markdown',
                'markdown': {
                    'title': title,
                    'text': content
                }
            }
        return self.data

    def _send_message(self):
        headers = {'Content-Type': 'application/json'}
        return self.request('post', self.url, json=self.data, headers=headers)
