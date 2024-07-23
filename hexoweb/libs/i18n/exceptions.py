"""
@Project   : i18n
@Author    : abudu
@Blog      : https://www.oplog.cn
"""


class LanguageException(Exception):
    """Base i18n exception."""


class NoSuchLanguageError(LanguageException):
    """
    An unknown language was requests, one that was not registered.
    """
