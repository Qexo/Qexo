"""
@Project   : smtp
@Author    : y1ndan & abudu
@Blog      : https://www.yindan.me
"""

from ..core import Provider


class Smtp(Provider):
    import smtplib
    name = 'smtp'
    _params = {
        'required': ['host', 'port', 'user', 'passwd', 'sender', 'receiver', 'title', 'content'],
        'optional': ['type', 'sender_name']
    }

    def _prepare_url(self, host: str, user: str, passwd: str, receiver: str, sender: str, port: str = "25", type: str = "", **kwargs):
        if type.upper() == "SSL" or port == "465":
            self.smtpObj = self.smtplib.SMTP_SSL(host, int(port))
        elif type.upper() == "TLS" or port == "587":
            self.smtpObj = self.smtplib.SMTP(host, int(port))
            self.smtpObj.starttls()
        else:
            self.smtpObj = self.smtplib.SMTP(host, int(port))
        self.smtpObj.login(user, passwd)
        self.receiver = receiver
        self.sender = sender
        return self.smtpObj

    def _prepare_data(self,
                      content: str,
                      title: str,
                      receiver: str,
                      sender_name: str = "邮件提醒",
                      **kwargs):
        from email.mime.text import MIMEText
        from email.utils import formataddr, parseaddr
        self.message = MIMEText(content, 'html', 'utf-8')
        self.message['From'] = formataddr(parseaddr(sender_name + " <%s>" % self.sender))
        self.message['To'] = formataddr(parseaddr(receiver))
        self.message['Subject'] = title
        return self.message

    def _send_message(self):
        return self.smtpObj.sendmail(self.sender, self.receiver, self.message.as_string())
