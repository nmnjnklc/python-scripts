from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.message import EmailMessage
from os.path import basename
from pathlib import Path
import smtplib


class MailSender:
    def __init__(self, mail_username: str, mail_password: str):
        self.mail_username: str = mail_username
        self.mail_password: str = mail_password

    def send_email(self, mail: EmailMessage | MIMEMultipart) -> None:
        try:
            server = smtplib.SMTP_SSL(
                host='smtp.gmail.com',
                port=465
            )
            server.ehlo()
            server.login(
                user=self.mail_username,
                password=self.mail_password
            )
            server.send_message(msg=mail)
            server.close()
        except BaseException as e:
            print(f"Mail could not be sent! Exception: {e}")

    def send_email_without_attachments(
            self,
            text: str,
            to: list[str],
            subject: str,
            sender: str | None = None) -> None:

        mail: EmailMessage = EmailMessage()
        mail.set_content(text)
        mail.set_type(type="text/html")
        mail["Subject"] = subject
        mail["From"] = sender if sender else "DEV Checker"
        mail["To"] = ", ".join(to)

        self.send_email(mail=mail)

    def send_email_with_attachments(
            self,
            files: list[Path],
            to: list[str],
            subject: str,
            sender: str | None = None,
            text: str | None = None) -> None:

        mail: MIMEMultipart = MIMEMultipart()
        mail["Subject"] = subject
        mail["From"] = sender if sender else "DEV Checker"
        mail["To"] = ", ".join(to)
        mail.attach(MIMEText(text))

        for file in files:
            with open(file, "rb") as f:
                part = MIMEApplication(f.read(), Name=basename(f))
            part["Content-Disposition"] = f'attachment; filename="{basename(f)}"'
            mail.attach(part)

        self.send_email(mail=mail)
