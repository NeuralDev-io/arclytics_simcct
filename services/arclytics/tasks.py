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

import os
from threading import Thread

import redis
import tenacity
from flask_mail import Mail, Message
from rq import Queue, Connection

from arc_app.middleware import async_func
from arc_app.app import create_app
# from arc_app.extensions import mail

mail = Mail()

app_settings = os.environ.get('APP_SETTINGS')

app = create_app(configs_path=app_settings)

app.config.update(
    dict(
        MAIL_SUBJECT_PREFIX='[Arclytics]',
        MAIL_DEFAULT_SENDER='Arclytics Team <admin@arclytics.io>',
        MAIL_SERVER=os.environ.get('MAIL_SERVER', None),
        MAIL_PORT=os.environ.get('MAIL_PORT', None),
        MAIL_USE_TLS=True,
        MAIL_USERNAME=os.environ.get('MAIL_USERNAME', ''),
        MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD', '')
    )
)

mail.init_app(app)


# FIXME(andrew@neuraldev.io) This is pretty bad not to retry since we're working
#  with an external service that requires a socket connection.
# @tenacity.retry(
#     wait=tenacity.wait_exponential(),
#     stop=tenacity.stop_after_attempt(3)
# )
@async_func
def _send_async_email(msg) -> None:
    with app.app_context():
        mail.send(msg)


def send_email(
    to: list, subject_suffix: str, html_template, text_template, **kwargs
) -> None:
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

    _send_async_email(msg)

    # NOTE:
    # redis_url = app.config['REDIS_URL']
    # with Connection(redis.from_url(redis_url)):
    #     q = Queue('default')
    #     q.enqueue(_send_async_email, msg=msg)
    # with app.app_context():
