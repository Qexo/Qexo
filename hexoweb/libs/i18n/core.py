"""
@Project   : i18n
@Author    : abudu
@Blog      : https://www.oplog.cn
"""

from .exceptions import NoSuchLanguageError


class Language(object):
    name = None
    default = dict()


from .languages import _all_languages


def all_languages():
    return list(_all_languages.keys())


def get_language(language_name: str):
    if language_name not in _all_languages:
        raise NoSuchLanguageError(language_name)
    return _all_languages[language_name].Main()
