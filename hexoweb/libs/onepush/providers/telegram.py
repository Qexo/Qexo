"""
@Project   : onepush
@Author    : y1ndan
@Blog      : https://www.yindan.me
"""

from ..core import Provider


class Telegram(Provider):
    name = 'telegram'
    base_url = 'https://{}/bot{}/sendMessage'
    site_url = 'https://core.telegram.org/bots'

    _params = {
        'required': ['token', 'userid'],
        'optional': ['title', 'content', 'api_url']
    }

    def _prepare_url(self, token: str, api_url: str = 'api.telegram.org', **kwargs):
        self.url = self.base_url.format(api_url, token)
        return self.url

    def _prepare_data(self, userid: str, title: str = None, content: str = None, **kwargs):
        message = self.process_message(title, content)
        self.data = {
            'chat_id': userid,
            'text': message,
            'disable_web_page_preview': True
        }
        return self.data
