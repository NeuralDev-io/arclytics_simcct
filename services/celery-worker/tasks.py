# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# arclytics_sim
# tasks.py
#
# Attributions:
# [1]
# -----------------------------------------------------------------------------
__author__ = ['Andrew Che <@codeninja55>']
__credits__ = ['']
__license__ = 'TBA'
__version__ = '0.5.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.07.25'
"""tasks.py: 

This module defines all the Celery tasks that can be added to the Message Queue. 
"""

from flask import current_app as app
from flask_mail import Message
from celery_worker import mail
from celery_worker import celery


@celery.task()
def log(msg: str):
    """Just a simple task to test if we send a message we receive it back."""
    return msg


@celery.task()
def send_email(
    to: str, subject_suffix: str, html_template, text_template, **kwargs
) -> None:
    """A task to send an email.

    Args:
        to: A string of the email that it is being sent to.
        subject_suffix: A subject_suffix as a message.
        html_template: A Flask Jinja2 rendered HTML template of the email body.
        text_template: A Flask Jinja2 rendered text template.
        **kwargs:

    Returns:
        A Python Threading Thread so we can collect it for return messages.
    """
    subject = '{} {}'.format(app.config['MAIL_SUBJECT_PREFIX'], subject_suffix)
    msg = Message(
        subject=subject,
        recipients=[to],
        html=html_template,
        body=text_template
    )
    mail.send(msg)
