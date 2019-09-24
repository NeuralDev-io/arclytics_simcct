# -*- coding: utf-8 -*-
#  MIT License
#
#  Copyright (c) 2018, Andrew Che <@codeninja55>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

# -----------------------------------------------------------------------------
# arclytics_sim
# fluentd_logger.py
#
# Date: 21/09/2019
# Attributions:
# [1] https://github.com/python/cpython/blob/3.7/Lib/logging/__init__.py
# [2] https://github.com/fluent/fluent-logger-python
# [3] https://github.com/thread/flask-fluentd
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__license__ = 'MIT'
__version__ = '0.3.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.09.21'
"""
fluentd_logger.py

This library is made to be used as a wrapper with Python's logging library and
to also send logs as events to fluentd with the `fluentd-logger` library handler.
"""

import logging
import platform
import sys
from enum import Enum
from io import BytesIO
from logging import Handler
from os import environ as env
from typing import Union

import msgpack
from fluent import handler as fluent_handler


def overflow_handler(pendings):
    # Handle any overflow.
    unpacker = msgpack.Unpacker(BytesIO(pendings))
    for unpacked in unpacker:
        print(unpacked)


class ReportingFormats(Enum):
    """Enum for storing some handy log formats."""
    STDOUT = "%(asctime)s : %(name)s : %(levelname)s : %(message)s"
    FLUENT = {
        'timestamp': '%(asctime)s',
        'where': '%(module)s.%(funcName)s',
        'host': '%(hostname)s',
        'severity': '%(levelname)s',
        'log': STDOUT,
        'message': '%(message)s',
        'stack_trace': '%(exc_text)s'
    }
    DATE_FMT = "%Y-%m-%d %H:%M:%S%z"


class HostnameFilter(logging.Filter):
    """Custom `logging` filter to add hostname."""
    hostname = platform.node()

    def filter(self, record):
        record.hostname = HostnameFilter.hostname
        return True


class FluentdLogger(object):
    """
    A logger to be used as the default to this application which uses a
    similar style to the Python `logging` module to send a `fluent.event`.
    """
    DEFAULT_LOGGER = logging.getLogger('NULL')
    DEFAULT_LOGGER.addHandler(logging.NullHandler())

    def __init__(self, caller: str = '', tag: str = ''):

        # Caller is the module calling this logger.
        self.caller = caller
        # The prefix tag to use with a `fluentd` log.
        if not tag:
            self.tag = '{}.app.access'.format(
                env.get('FLUENTD_PREFIX_TAG', 'flask')
            )
        else:
            self.tag = tag

        # create a logger
        self.logger = logging.getLogger(caller)

        # Ensure that in production we always use 'INFO' to avoid debug msgs
        self.debug = env.get('FLASK_ENV') == 'development'
        log_level = logging.DEBUG if self.debug else logging.INFO

        # A handler that logs to a remote instance of `elasticsearch`.
        # The values `FLUENTD_HOST` and `FLUENTD_PORT` must be in the ENV vars.
        self.fluentd_handler = fluent_handler.FluentHandler(
            self.tag,
            host=env.get('FLUENTD_HOST', 'fluentd-service'),
            port=int(env.get('FLUENTD_PORT', 24224)),
            buffer_overflow_handler=overflow_handler
        )

        self.log_info = []
        self.log_handlers = []

        # create the default logger at level.
        self.configure_default_logger(log_level=log_level)

    def __str__(self):
        """
        Return a list of 'handler_name @ log_level' for debugging purposes.
        """
        return ','.join(self.log_info)

    def __iter__(self):
        """Returns each handler in order."""
        for handler in self.log_handlers:
            yield handler

    def get_logger(self):
        """Return the logger for the user."""
        return self.logger

    def close(self):
        self.fluentd_handler.close()

    def _configure_common(
            self, log_level: str,
            log_format: str,
            handler_name: str,
            handler: Handler
    ):
        """Common configuration code.

        Args:
            log_level: The str representation of the log level to use.
            log_format: The log formatting to use.
            handler_name: The handler to be used in debug messages
            handler: The logging Handler to configure and use.
        """

        # Attach handlers and formatters
        formatter = logging.Formatter(
            fmt=log_format, datefmt=ReportingFormats.DATE_FMT.value
        )
        handler.setFormatter(fmt=formatter)
        handler.setLevel(log_level)
        self.logger.addHandler(handler)

        # Ensure the logger level is not lower than the handler level
        if not self.logger.isEnabledFor(log_level):
            self.logger.setLevel(log_level)

        self.log_info.append('{0} @ {1} '.format(handler_name, str(log_level)))
        self.log_handlers.append(handler)

    # noinspection PyAttributeOutsideInit
    def configure_default_logger(self, log_level: logging.BASIC_FORMAT):
        """
        Default logger that every application using this library should use.
        """
        # We only want a `logging.StreamHandler` to send to `sys.stdout` in
        # development environments.
        if self.debug:
            # Standard `logging` stdout handler
            console_handler = logging.StreamHandler(stream=sys.stdout)
            console_handler.setLevel(log_level)
            self._configure_common(
                log_level=log_level,
                log_format=ReportingFormats.STDOUT.value,
                handler_name='stderr_stream_handler',
                handler=console_handler,
            )

        # Add the handler and the formatter to the logger
        fluent_fmt = fluent_handler.FluentRecordFormatter(
            ReportingFormats.FLUENT.value
        )

        self.fluentd_handler.setFormatter(fluent_fmt)
        self.fluentd_handler.setLevel(log_level)
        self.fluentd_handler.set_name('fluentd_handler')
        self.logger.addHandler(self.fluentd_handler)

        self.log_info.append(
            "{0} @ {1} ".format('fluentd_handler', log_level)
        )
        self.log_handlers.append(self.fluentd_handler)

    def debug(self, msg: Union[str, dict], *args, **kwargs):
        """Log 'message % args' with severity DEBUG.

        To pass exception information, use the keyword arg exc_info with a true
        value.

        Example:
            logger.debug("Houston, we have a %s", "thorny problem", exc_info=1)

        Args:
            msg: the message to log.
        """
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: Union[str, dict], *args, **kwargs):
        """Log 'message'.format(*args) with severity INFO.

        To pass exception information, use the keyword argument exc_info with
        a true value.

        Example:
            logger.info("Houston, we have a %s", "interesting problem",
                        exc_info=1)

        Args:
            msg: the message to log
        """
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: Union[str, dict], *args, **kwargs):
        """
        Log 'message'.format(*args) with severity WARNING.

        To pass exception information, use the keyword argument exc_info with a
        true value.

        Example:
            logger.info("Houston, we have a %s", "bit of a problem", exc_info=1)

        Args:
            msg: the message to log
        """
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: Union[str, dict], stack_info=True, *args, **kwargs):
        """
        Log 'message'.format(*args) with severity ERROR.

        To pass exception information, use the keyword argument exc_info with a
        true value.

        Example:
            logger.info("Houston, we have a %s", "major problem", exc_info=1)

        Args:
            stack_info: whether to print the stack trace. Default is true.
            msg: the message to log
        """
        self.logger.error(msg, stack_info=stack_info, *args, **kwargs)

    def critical(self, msg: Union[str, dict], *args, **kwargs):
        """
        Log 'message'.format(*args) with severity CRITICAL.

        To pass exception information, use the keyword argument exc_info with a
        true value.

        Example:
            logger.info("Houston, we have a %s", "interesting problem",
                        exc_info=1)

        Args:
            msg: the message to log.
        """
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg: Union[str, dict], *args, exc_info=True, **kwargs):
        """Convenience method for logging an ERROR with exception information.

        Args:
            msg: the message to log.
            exc_info: default set to true to provide exception information
        """
        self.error(msg, *args, exc_info=exc_info, **kwargs)
