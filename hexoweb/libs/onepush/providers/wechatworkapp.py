"""
@Project   : onepush
@Author    : y1ndan
@Blog      : https://www.yindan.me
"""

from ..core import Provider


class WechatWorkApp(Provider):
    name = 'wechatworkapp'
    base_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={}'
    site_url = 'https://work.weixin.qq.com/api/doc/90000/90135/90236'

    _params = {
        'required': ['corpid', 'corpsecret', 'agentid'],
        'optional': ['title', 'content', 'touser', 'markdown']
    }

    def _prepare_url(self, corpid: str, corpsecret: str, **kwargs):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
        data = {'corpid': corpid, 'corpsecret': corpsecret}
        response = self.request('get', url, params=data).json()
        access_token = response.get('access_token')

        self.url = self.base_url.format(access_token)
        return self.url

    def _prepare_data(self,
                      agentid: str,
                      title: str = None,
                      content: str = None,
                      touser: str = '@all',
                      markdown: bool = False,
                      **kwargs):
        message = self.process_message(title, content)
        msgtype = 'text'
        if markdown:
            msgtype = 'markdown'

        self.data = {
            'touser': touser,
            'msgtype': msgtype,
            'agentid': agentid,
            msgtype: {
                'content': message
            }
        }
        return self.data

    def _send_message(self):
        return self.request('post', self.url, json=self.data)
