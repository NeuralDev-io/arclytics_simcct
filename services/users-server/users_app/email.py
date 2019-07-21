# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# email.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.22'
"""email.py: 

{Description}
"""

from threading import Thread

from flask import current_app
from flask_mail import Message

from users_app import mail


def send_async_email(app, msg) -> None:
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    """

    Args:
        to:
        subject:
        template:
        **kwargs:

    Returns:
        A Python Threading Thread so we can collect it for return messages.
    """
    msg = Message(
        subject=(
            current_app.config['MAIL_SUBJECT_PREFIX'] + ' ' + subject
        ),
        recipients=[to],
        html=template
    )
    # thr = Thread(target=send_async_email, args=[current_app, msg])
    # thr.start()
    # return thr
    mail.send(msg)
