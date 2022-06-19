class QexoProviderException(Exception):
    """Base QexoProvider exception."""


class NoSuchProviderError(QexoProviderException):
    """
    An unknown provider was requests, one that was not registered.
    """
