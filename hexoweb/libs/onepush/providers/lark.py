from ..core import Provider

import hashlib
import base64
import hmac
import time


class Lark(Provider):
    name = 'Lark'
    _params = {
        'required': ['webhook', 'content'],
        'optional': ['keyword', 'sign']
    }
    def gen_sign(self, timestamp, secret):
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(hmac_code).decode('utf-8')
        return sign

    def _prepare_url(self, webhook: str, **kwargs):
        self.url = webhook

    def _prepare_data(self, keyword: str, sign: str, content: str, **kwargs):
        self.data = {
            "msg_type": "text",
            "content":
                {
                    "text": content if not keyword else content+"\n"+keyword
                }
        }
        if sign:
            timestamp = str(int(time.time()))
            self.data.update({
                "timestamp": timestamp,
                "sign": self.gen_sign(timestamp, sign)
            })
        return self.data

    def _send_message(self):
        return self.request('post', self.url, json=self.data)
