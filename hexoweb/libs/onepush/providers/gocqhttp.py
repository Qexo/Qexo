"""
@Project   : onepush
@Author    : y1ndan
@Blog      : https://www.yindan.me
"""

from ..core import Provider


class Gocqhttp(Provider):
    name = 'CqHttp'
    site_url = 'https://docs.go-cqhttp.org'

    _params = {
        'required': ['endpoint'],
        'optional': [
            'title', 'content', 'path', 'token', 'message_type', 'user_id',
            'group_id', 'auto_escape'
        ]
    }

    def __init__(self):
        super().__init__()
        self.method = 'get'

    def _prepare_url(self, endpoint: str, path: str = None, **kwargs):
        if endpoint and '//' not in endpoint:
            endpoint = f'http://{endpoint}'
        if not path:
            path = '/send_msg'

        self.url = f'{endpoint}{path}'
        return self.url

    def _prepare_data(self,
                      title: str = None,
                      content: str = None,
                      token: str = None,
                      message_type: str = None,
                      user_id: int = None,
                      group_id: int = None,
                      auto_escape: bool = False,
                      **kwargs):
        message = self.process_message(title, content)
        self.data = {
            'access_token': token,
            'message_type': message_type,
            'user_id': user_id,
            'group_id': group_id,
            'message': message,
            'auto_escape': auto_escape
        }
        return self.data

