# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# tasks.py
#
# Attributions:
# [1]
# https://medium.com/@taylorhughes/
# three-quick-tips-from-two-years-with-celery-c05ff9d7f9eb
# -----------------------------------------------------------------------------
__author__ = [
    'Andrew Che <@codeninja55>', 'David Matthews <@tree1004>',
    'Dinol Shrestha <@dinolsth>'
]
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'production'
__date__ = '2019.07.25'
"""tasks.py: 

This module defines all the Celery tasks that can be added to the Message Queue. 
"""

from typing import Tuple

from celery.exceptions import MaxRetriesExceededError, CeleryError

from celery_worker import mail, celery, apm
from flask import current_app as app
from flask_mail import Message
from smtplib import (
    SMTPAuthenticationError, SMTPServerDisconnected, SMTPConnectError,
    SMTPException
)

from arc_logging import AppLogger

logger = AppLogger(__name__)


@celery.task()
def log(msg: str):
    """Just a simple task to test if we send a message we receive it back."""
    return msg


# noinspection PyUnusedLocal
@celery.task(bind=True, soft_time_limit=20, max_retries=6)
def send_email(
    self, to: list, subject_suffix: str, html_template, text_template, **kwargs
) -> Tuple[bool, str]:
    """A task to send an email.

    Args:
        self: The instance of the task so we can use it to retry.
        to: A string of the email that it is being sent to.
        subject_suffix: A subject_suffix as a message.
        html_template: A Flask Jinja2 rendered HTML template of the email body.
        text_template: A Flask Jinja2 rendered text template.
        **kwargs: other keyword arguments.

    Returns:
        A Python Threading Thread so we can collect it for return messages.
    """
    subject = '{} {}'.format(app.config['MAIL_SUBJECT_PREFIX'], subject_suffix)

    msg = Message(
        subject=subject, recipients=to, html=html_template, body=text_template
    )
    status = False
    try:
        mail.send(msg)
        status = True
        message = 'Email sent.'
        return status, message
    except SMTPAuthenticationError as e:
        message = 'SMTP Authentication Error'
        log_message = {'message': message, 'error': e}
        logger.error(log_message)
        apm.capture_exception()
        retry_email(self, e)
    except SMTPServerDisconnected as e:
        message = 'SMTP Server Disconnect'
        log_message = {'message': message, 'error': e}
        logger.error(log_message)
        apm.capture_exception()
        retry_email(self, e)
    except SMTPConnectError as e:
        message = 'SMTP Connection Error'
        log_message = {'message': message, 'error': e}
        logger.error(log_message)
        apm.capture_exception()
        retry_email(self, e)
    except SMTPException as e:
        message = 'Generic SMTP Exception Error'
        log_message = {'message': message, 'error': e}
        logger.error(log_message)
        apm.capture_exception()
        retry_email(self, e)
    except MaxRetriesExceededError as e:
        message = 'Max Retries exceeded.'
        log_message = {'message': message, 'error': e}
        logger.error(log_message)
        apm.capture_exception()
    except CeleryError as e:
        message = 'Generic Celery error.'
        log_message = {'message': message, 'error': e}
        logger.error(log_message)
        retry_email(self, e)
    except Exception as e:
        message = 'Number of retries exceeded.'
        log_message = {'message': message, 'error': e}
        logger.error(log_message)
        retry_email(self, e)
    return status, message


def retry_email(task, err) -> None:
    """Using an exponential retry so we can wait for the server to start
    working again soon on the recommendation of [1].

    Args:
        task: the Celery task instance (i.e. setting Bind=True)
        err: The error message returned from the exception.

    Returns:
        None
    """
    # Find the number of attempts so far
    num_retries = task.request.retries
    seconds_to_wait = 2.0**num_retries
    try:
        task.retry(countdown=seconds_to_wait, exc=err)
    except MaxRetriesExceededError as e:
        message = 'Number of retries exceeded.'
        log_message = {'message': message, 'error': e}
        logger.error(log_message)
        raise MaxRetriesExceededError(e)
