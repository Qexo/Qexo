"""
@Project   : onepush
@Author    : y1ndan
@Blog      : https://www.yindan.me
"""

class OnePushException(Exception):
    """Base OnePush exception."""


class NotificationError(OnePushException):
    """
    A notification error. Raised after an issue with the sent notification.
    """


class NoSuchNotifierError(OnePushException):
    """
    An unknown notifier was requests, one that was not registered.
    """
