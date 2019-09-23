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
# flask_fluentd_logger.py
#
# Date: 21/09/2019
# Attributions:
# [1] https://github.com/python/cpython/blob/3.7/Lib/logging/__init__.py
# [2] https://github.com/fluent/fluent-logger-python
# [3] https://github.com/thread/flask-fluentd
# -----------------------------------------------------------------------------
__author__ = 'Andrew Che <@codeninja55>'
__license__ = 'MIT'
__version__ = '0.1.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.09.21'
"""
This library is made to be used as a wrapper with Python's logging library and
to also send logs as events to fluentd with the fluentd-logger library handler.
"""

import logging
import sys
from enum import Enum
from io import BytesIO
from logging import Handler

import msgpack
from flask import Flask, _app_ctx_stack
from fluent import asynchandler as fluent_handler

# Following the predefined Levels used in `logging` library
CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0

_levelToName = {
    CRITICAL: 'CRITICAL',
    ERROR: 'ERROR',
    WARNING: 'WARNING',
    INFO: 'INFO',
    DEBUG: 'DEBUG',
    NOTSET: 'NOTSET',
}
_nameToLevel = {
    'CRITICAL': CRITICAL,
    'FATAL': FATAL,
    'ERROR': ERROR,
    'WARN': WARNING,
    'WARNING': WARNING,
    'INFO': INFO,
    'DEBUG': DEBUG,
    'NOTSET': NOTSET,
}


def get_level_name(level):
    """
    Return the textual representation of logging level 'level'.

    If the level is one of the predefined levels (CRITICAL, ERROR, WARNING,
    INFO, DEBUG) then you get the corresponding string.

    If a numeric value corresponding to one of the defined levels is passed
    in, the corresponding string representation is returned.

    Otherwise, the string "Level %s" % level is returned.
    """
    result = _levelToName.get(level)
    if result is not None:
        return result
    result = _nameToLevel.get(level)
    if result is not None:
        return result
    return "Level {}".format(level)


def _check_level(level):
    if isinstance(level, int):
        rv = level
    elif str(level) == level:
        if level not in _nameToLevel:
            raise ValueError("Unknown level: {}".format(level))
        rv = _nameToLevel[level]
    else:
        raise TypeError(
            "Level not an integer or a valid string: %r".format(level)
        )
    return rv


def overflow_handler(pendings):
    unpacker = msgpack.Unpacker(BytesIO(pendings))
    for unpacked in unpacker:
        print(unpacked)


class ReportingFormats(Enum):
    """Enum for storing some handy log formats."""
    STDOUT = ("%(asctime)s : %(threadName)s : %(filename)s : %(module)s : "
              "%(funcName)s : %(lineno)s : %(levelname)s : %(message)s")
    FLUENT = {
        'timestamp': '%(asctime)s',
        'host': '%(hostname)s',
        'where': '%(module)s.%(funcName)s',
        'severity': '%(levelname)s',
        'file': '%(filename)s',
        'stack_trace': '%(exc_text)s'
    }
    DATE_FMT = "%Y-%m-%d %H:%M:%S%z"


class FlaskFluentdLogger(object):
    """
    A logger to be used as the default to this application which uses a
    similar style to the Python `logging` module to send a `fluent.event`.
    """
    DEFAULT_LOGGER = logging.getLogger('NULL')
    DEFAULT_LOGGER.addHandler(logging.NullHandler())

    def __init__(self, app: Flask = None):
        self.app: Flask = app

        if app is not None:
            self.init_app(app)

        # Default level should be DEBUG for development
        self.level = _check_level('DEBUG')
        self.logger = self.DEFAULT_LOGGER

        self.log_info = []
        self.log_handlers = []

    # noinspection PyAttributeOutsideInit
    def init_app(self, app: Flask):

        # Set some default configurations for connecting to fluentd
        app.config.setdefault('FLUENTD_HOST', 'localhost')
        app.config.setdefault('FLUENTD_PORT', 24224)
        app.config.setdefault('FLUENTD_SCHEME', 'http')
        app.config.setdefault('FLUENTD_PREFIX_TAG', app.name)

        self.tag = app.config.get('FLUENTD_PREFIX_TAG', app.name)
        self.host = app.config.get('FLUENTD_HOST', 'localhost')
        self.port = int(app.config.get('FLUENTD_PORT', 24225))

        # create a logger
        self.logger = logging.getLogger(self.tag)

        # Ensure that in production we always use 'INFO' to avoid debug msgs
        self.debug = app.env == 'development'
        log_level = 'DEBUG' if app.env == 'development' else 'INFO'

        # A remote handler
        self.fluentd_handler = fluent_handler.FluentHandler(
            self.tag,
            host=self.host,
            port=self.port,
            nanosecond_precision=True,
            buffer_overflow_handler=overflow_handler
        )

        # create the default logger at level.
        self.configure_default_logger(log_level=log_level)

        # Get rid of the connection when outside the context of Flask app
        app.teardown_appcontext(self.teardown)

    # noinspection PyMethodMayBeStatic
    def teardown(self, exception):
        ctx = _app_ctx_stack.top
        if hasattr(ctx, 'logger'):
            ctx.logger.close()

    @property
    def connection(self):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, 'logger'):
                ctx.logger = self.logger
        return ctx.logger

    def close(self):
        self.fluentd_handler.close()

    def _configure_common(
            self,
            log_level: str,
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
        if not self.logger.isEnabledFor(logging.getLevelName(log_level)):
            self.logger.setLevel(log_level)

        self.log_info.append("{0} @ {1} ".format(handler_name, str(log_level)))
        self.log_handlers.append(handler)

    # noinspection PyAttributeOutsideInit
    def configure_default_logger(self, log_level: str):
        """
        Default logger that every application using this library should use.
        """

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
        fluent_fmt = fluent_handler.handler.FluentRecordFormatter(
            ReportingFormats.FLUENT.value
        )

        self.fluentd_handler.setFormatter(fluent_fmt)
        self.fluentd_handler.setLevel(log_level)
        self.fluentd_handler.set_name('fluentd_handler')
        self.logger.addHandler(self.fluentd_handler)

        self.log_info.append(
            "{0} @ {1} ".format('fluentd_handler', get_level_name(log_level))
        )
        self.log_handlers.append(self.fluentd_handler)

    def get_logger(self):
        """Return the logger for the user."""
        return self.logger
