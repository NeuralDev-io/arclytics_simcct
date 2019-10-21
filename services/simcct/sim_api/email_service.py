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
__author__ = ['David Matthews <@tree1004>', 'Dinol Shrestha <@dinolsth>']
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'production'
__date__ = '2019.09.01'
"""email_service.py: 

This module defines the Email service for sending emails using Celery.
"""

from typing import Union


# noinspection PyUnusedLocal
def send_email(
    to: list, subject_suffix: str, html_template, text_template, **kwargs
) -> Union[str, None]:
    """An adapter task to send an email using a Celery Flask worker in
    another service/container.

    Args:
        to: A list of the email(s) that it is being sent to.
        subject_suffix: A subject_suffix as a message.
        html_template: A Flask Jinja2 rendered HTML template of the email body.
        text_template: A Flask Jinja2 rendered text template.
        **kwargs: other keyword arguments.

    Returns:
        The Celery task instance that can be used to retrieve the task ID.
    """
    # Must import locally to ensure proper Flask context.
    from celery_runner import celery

    # Be generous and let them put a single email as a string even if they
    # have ignored our extension type annotation and comments.
    if isinstance(to, str):
        to = [to]

    # Cannot send an email with something that is not a list of emails.
    # Emails are usually validated upstream so we don't really need to worry
    # about that.
    if not isinstance(to, list):
        from arc_logging import AppLogger
        from sim_api.extensions import apm
        AppLogger(__name__
                  ).exception('Emails must either be a list or string.')
        apm.capture_exception()
        return

    send_to = to

    email_task = celery.send_task(
        'tasks.send_email',
        kwargs={
            'to': send_to,
            'subject_suffix': subject_suffix,
            'html_template': html_template,
            'text_template': text_template
        }
    )

    # Return the celery task id in case we want to do something with it.
    return email_task
