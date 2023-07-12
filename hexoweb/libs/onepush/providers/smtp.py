from ..core import Provider

import smtplib
from email.message import EmailMessage, Message
from typing import Callable


def _default_message_parser(
    self: "SMTP", 
    subject: str = '',
    title: str = '',
    content: str = '',
    From: str = None,
    user: str = None,
    To: str = None,
    **kwargs,
) -> Message:
    msg = EmailMessage()
    # Use subject if avaliable, title for compatibility with other providers
    msg["Subject"] = subject or title
    # Fallback to username if `From` address not provided
    msg["From"] = From or user
    # Send to yourself if `To` address not provided
    msg["To"] = To or user

    msg.add_alternative(content, subtype='html')
    return msg


class SMTP(Provider):
    """
    SMTP provider

    At least provide `host`, `user` and `password` for connection.
    If `port` is not provided, use 25 by default or 465 when ssl=True.
    If `ssl` is not provided, use SMTP_SSL if port is 465, otherwise SMTP.

    If `msg` is not provided, use `_default_message_parser` to generate message from other arguments.
    If `From` is not provided, use `user` as default.
    If `To` is not provided, use `user` as default too. This will send email to yourself.
    See function `_default_message_parser` for more details.
    Use `SMTP.set_message_parser(custom_parser)` to set your custom message parser.
    """
    name = "Smtp邮件"
    _server: smtplib.SMTP
    _message_parser = _default_message_parser
    _params = {
        "required": ["host", "user", "password"],
        "optional": ["port", "ssl", "msg", "subject", "title", "content", "From", "To"],
    }

    @classmethod
    def set_message_parser(cls, parser: Callable[..., Message]) -> None:
        cls._message_parser = parser

    def _prepare_url(
        self, 
        host: str,
        user: str,
        password: str,
        port: int = 0,
        ssl: bool = None,
        **kwargs,
    ):
        if ssl is None:
            if port in (smtplib.SMTP_SSL_PORT,):
                ssl = True
        s = smtplib.SMTP_SSL if ssl else smtplib.SMTP
        self._server = s(host, port)
        # self._server.set_debuglevel(1)
        try:
            self._server.login(user=user, password=password)
        except smtplib.SMTPException as e:
            self._server.close()
            raise ValueError(e) from e

    def _prepare_data(
        self,
        msg: Message = None,
        **kwargs,
    ):
        if msg is None:
            msg = self._message_parser(**kwargs)
        self.data = {
            "msg": msg,
        }
        return self.data

    def _send_message(self):
        with self._server as server:
            return server.send_message(self.data["msg"])
