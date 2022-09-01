"""
@Project   : onepush
@Author    : y1ndan
@Blog      : https://www.yindan.me
"""

from ..core import Provider


class Bark(Provider):
    name = 'Bark'
    base_url = 'https://api.day.app/{}'
    site_url = 'https://apps.apple.com/us/app/bark-customed-notifications/id1403753865'

    _params = {
        'required': ['key'],
        'optional': [
            'title', 'content', 'sound', 'isarchive', 'icon', 'group', 'url', 'copy',
            'autocopy'
        ]
    }

    def _prepare_url(self, key: str, **kwargs):
        self.url = key
        if 'https' not in key and 'http' not in key:
            self.url = self.base_url.format(key)
        return self.url

    def _prepare_data(self,
                      title: str = None,
                      content: str = None,
                      sound: str = 'healthnotification',
                      isarchive: int = None,
                      icon: str = None,
                      group: str = None,
                      url: str = None,
                      copy: str = None,
                      autocopy: int = None,
                      **kwargs):
        self.data = {
            'title': title,
            'body': content,
            'sound': sound,
            'isArchive': 1 if isarchive else isarchive,
            'icon': icon,
            'group': group,
            'url': url,
            'copy': copy,
            'autoCopy': 1 if autocopy else autocopy
        }
        return self.data
