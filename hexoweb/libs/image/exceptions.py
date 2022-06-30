"""
@Project   : image
@Author    : abudu
@Blog      : https://www.oplog.cn
"""


class ImageException(Exception):
    """Base OnePush exception."""


class UploadError(ImageException):
    """
    A Upload error. Raised after an issue with the sent notification.
    """


class NoSuchProviderError(ImageException):
    """
    An unknown notifier was requests, one that was not registered.
    """
