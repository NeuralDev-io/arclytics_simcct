# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# email_service.py
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
"""email_service.py: 

This module defines the Email service for sending emails using Celery.
"""


def send_email(
    to: list, subject_suffix: str, html_template, text_template, **kwargs
) -> None:
    """A task to send an email using a Celery Flask worker in another container.

    Args:
        to: A string of the email that it is being sent to.
        subject_suffix: A subject_suffix as a message.
        html_template: A Flask Jinja2 rendered HTML template of the email body.
        text_template: A Flask Jinja2 rendered text template.
        **kwargs: other keyword arguments.

    Returns:
        The Celery task instance that can be used to retrieve the task ID.
    """
    from celery_runner import celery

    email_task = celery.send_task(
        'tasks.send_email',
        kwargs={
            'to': to,
            'subject_suffix': subject_suffix,
            'html_template': html_template,
            'text_template': text_template
        }
    )

    return email_task
