# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# email.py
# 
# Attributions: 
# [1]
# https://medium.com/@taylorhughes/
# three-quick-tips-from-two-years-with-celery-c05ff9d7f9eb
# ----------------------------------------------------------------------------------------------------------------------

__author__ = ['Andrew Che <@codeninja55>']
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.9'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.09.01'

"""email.py: 

This module defines the Email task.
"""

import time
from typing import Tuple

from flask import current_app as app
from flask_mail import Message
from smtplib import (
    SMTPAuthenticationError, SMTPServerDisconnected, SMTPConnectError,
    SMTPException
)
from threading import Thread

from arc_app.extensions import mail


def _retry_email(num_retries: int, msg) -> Tuple[float, str]:
    """Using an exponential retry so we can wait for the server to start
    working again soon on the recommendation of [1].
    """
    # Exponentially increase the retry rate
    seconds_to_wait = 2.0 ** num_retries

    # Set the maximum number of retries
    if num_retries > 20:
        return 0.0, 'Number of retries exceeded.'

    # Because we are recursively retrying below, we will never get to the end
    # and will only stop after failing the above.

    time.sleep(seconds_to_wait)

    try:
        mail.send(msg)
        message = 'Email sent.'
        return -1.0, message
    except SMTPAuthenticationError as e:
        _retry_email(num_retries + 1, msg)
    except SMTPServerDisconnected as e:
        _retry_email(num_retries + 1, msg)
    except SMTPConnectError as e:
        _retry_email(num_retries + 1, msg)
    except SMTPException as e:
        _retry_email(num_retries + 1, msg)
    except Exception as e:
        _retry_email(num_retries + 1, msg)


def _send_async_email(msg):
    # Always retry at least once if needed
    num_retries = 1
    try:
        mail.send(msg)
        message = 'Email sent.'
        return True, message
    except SMTPAuthenticationError as e:
        num_retries, message = _retry_email(num_retries, msg)
    except SMTPServerDisconnected as e:
        num_retries, message = _retry_email(num_retries, msg)
    except SMTPConnectError as e:
        num_retries, message = _retry_email(num_retries, msg)
    except SMTPException as e:
        num_retries, message = _retry_email(num_retries, msg)
    except Exception as e:
        num_retries, message = _retry_email(num_retries, msg)

    # To access this, you will need to use Thread.join() and then see the
    # result in the parent calling function of `send_email()`
    return num_retries < 0.0, message


def send_email(
        to: list, subject_suffix: str, html_template, text_template, **kwargs
) -> Thread:
    """A task to send an email.

    Args:
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
    thr = Thread(target=_send_async_email, args=[msg])
    thr.start()
    return thr
