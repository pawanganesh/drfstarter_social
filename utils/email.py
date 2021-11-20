import logging
from threading import Thread

from django.conf import settings
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from sendgrid.helpers.mail import To

# Get an instance of a logger
logger = logging.getLogger(__name__)


class EmailThread(Thread):
    def __init__(self, email):
        self.email = email
        Thread.__init__(self)

    def run(self):
        self.email.send()
        logger.info("Email successfully sent")


class SendGridEmailThread(Thread):
    def __init__(self, message):
        self.message = message
        Thread.__init__(self)

    def run(self):
        try:
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.send(self.message)
            logger.info(response.status_code)
            logger.info(response.body)
            logger.info(response.headers)
        except Exception as e:
            logger.info(e.message)
        logger.info("Email successfully sent")


class Email:
    @staticmethod
    def send_email(data):
        """
        Send an email
        """
        email = EmailMessage(
            to=data['to'],
            subject=data['subject'],
            body=data['body'],
        )
        EmailThread(email).start()

    @staticmethod
    def send_html_email(path_to_html_template, data):
        """
        Send an email with html template

        path_to_html_template: email/template.html
        data = {
            'to': [],
            'subject': '',
            'context': {},
        }
        """
        html_content = render_to_string(path_to_html_template, data['context'])
        text_content = strip_tags(html_content)
        email = EmailMultiAlternatives(
            subject=data['subject'],
            body=text_content,
            from_email=settings.EMAIL_HOST_USER,
            to=data['to'],
        )
        email.attach_alternative(html_content, "text/html")
        EmailThread(email).start()

    @staticmethod
    def sendgrid_email(data):
        """
        Send an email with SendGrid
        """
        message = Mail(
            subject=data['subject'], html_content=data['body'], to_emails=To(data['to']),
            from_email=settings.SENDGRID_HOST_USER, )
        SendGridEmailThread(message).start()

    @staticmethod
    def sendgrid_html_email(path_to_html_template, data):
        """
        Send an email with SendGrid and html template

        path_to_html_template: email/template.html
        data = {
            'to': [],
            'subject': '',
            'context': {},
        }
        """
        message = Mail(
            subject=data['subject'], html_content=render_to_string(path_to_html_template, data['context']),
            to_emails=To(data['to']),
            from_email=settings.SENDGRID_HOST_USER, )
        SendGridEmailThread(message).start()
