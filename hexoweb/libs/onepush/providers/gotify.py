from ..core import Provider

class Gotify(Provider):
    name = 'Gotify'
    _params = {
        'required': ['url', 'message', 'token'],
        'optional': ['title', 'priority']
    }

    def _prepare_url(self, url: str, token: str, **kwargs):
        self.url = url + '/message?token=' + token
        return self.url

    def _prepare_data(self,
                      message: str,
                      title: str = None,
                      priority: int = 0,
                      **kwargs):
        self.data = {
            'title': title,
            'message': message,
            'priority': priority
        }
        return self.data

    def _send_message(self):
        return self.request('post', self.url, json=self.data)