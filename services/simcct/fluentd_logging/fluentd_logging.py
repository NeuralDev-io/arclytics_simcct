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
to also send logs as events to fluentd with the `fluentd-logger` library 
handler.
"""

import os
import io
import socket
import sys
import traceback
from datetime import datetime
from os import environ as env
from typing import Union, Any

from fluent import sender


CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0


def get_remote_fluentd():
    return (
        env.get('FLUENTD_HOST', 'fluentd-service'),
        int(env.get('FLUENTD_PORT', 24224))
    )


# Hash Set
_levelToName = {
    CRITICAL: 'CRITICAL',
    ERROR: 'ERROR',
    WARNING: 'WARNING',
    INFO: 'INFO',
    DEBUG: 'DEBUG',
    NOTSET: 'NOTSET',
}
# Hash Map
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
    INFO, DEBUG) then you get the corresponding string. If you have
    associated levels with names using addLevelName then the name you have
    associated with 'level' is returned.

    If a numeric value corresponding to one of the defined levels is passed
    in, the corresponding string representation is returned.

    Otherwise, the string "Level {}".format(level) is returned.
    """
    # See Issues #22386, #27937 and #29220 for why it's this way
    result = _levelToName.get(level)
    if result is not None:
        return result
    result = _nameToLevel.get(level)
    if result is not None:
        return result
    return 'Level {}'.format(level)


if hasattr(sys, '_getframe'):
    # noinspection PyProtectedMember
    currentframe = lambda: sys._getframe(3)
else:  # pragma: no cover
    def currentframe():
        """Return the frame object for the caller's stack frame."""
        # noinspection PyBroadException
        try:
            raise Exception
        except Exception:
            return sys.exc_info()[2].tb_frame.f_back


# _srcfile is used when walking the stack to check when we've got the first
# caller stack frame, by skipping frames whose filename is that of this
# module's source. It therefore should contain the filename of this module's
# source file.
#
# Ordinarily we would use __file__ for this, but frozen modules don't always
# have __file__ set, for some reason (see Issue #21736). Thus, we get the
# filename from a handy code object from a function defined in this module.
# (There's no particular reason for picking addLevelName.)
#

_srcfile = os.path.normcase(get_remote_fluentd.__code__.co_filename)

# _srcfile is only used in conjunction with sys._getframe().
# To provide compatibility with older versions of Python, set _srcfile
# to None if _getframe() is not available; this value will prevent
# findCaller() from being called. You can also do this if you want to avoid
# the overhead of fetching caller information, even when _getframe() is
# available.


def _check_level(level):
    if isinstance(level, int):
        rv = level
    elif str(level) == level:
        if level not in _nameToLevel:
            raise ValueError("Unknown level: %r" % level)
        rv = _nameToLevel[level]
    else:
        raise TypeError("Level not an integer or a valid string: %r" % level)
    return rv


# ========================================================================= #
#      LOGGING RECORD
# ========================================================================= #

class EventRecord(object):
    """
    A EventRecord instance represents an event being logged.

    EventRecord instances are created every time something is logged. They
    contain all the information pertinent to the event being logged. The
    main information passed in is in msg to create the message field of the
    record. The record also includes information such as when the record was
    created, the source line where the logging call was made, and any exception
    information to be logged.

    The EventRecord instances are then converted to a dictionary as per the
    requirement for the `fluentd` Event object.
    """

    def __init__(
            self,
            name: str,
            level: Union[int, str],
            pathname,
            lineno,
            msg,
            exc_info,
            func=None,
            stack_info=None,
    ):
        ct = datetime.utcnow()
        self.name = name
        self.msg = msg
        self.hostname = socket.gethostname()

        self.level_name = get_level_name(level)
        self.level_num = level

        self.pathname = pathname
        try:
            self.filename = os.path.basename(pathname)
            self.module = os.path.splitext(self.filename)[0]
        except (TypeError, ValueError, AttributeError):
            self.filename = pathname
            self.module = "Unknown module"

        self.exc_info = exc_info
        self.exc_text = None  # used to cache the traceback text
        self.stack_info = stack_info

        self.funcName = func
        self.lineno = lineno
        self.created = ct

    def level_str(self):
        return str(self.level_name).lower()

    def data_dict(self):
        # TODO(andrew@neuraldev.io): Check for other types.
        # For the log, we want to print the whole stringified msg object
        # sent to us rather than just the message alone.
        log = '{timestamp} : {name} : {level_name} : {message}'.format(
            timestamp=self.created,
            name=self.name,
            level_name=self.level_name,
            message=str(self.msg)
        )

        data = {
            'timestamp': self.created.isoformat(),
            'hostname': self.hostname,
            'severity': self.level_name,
            'log': log,
            'stack_trace': self.stack_info,
            'caller': '{module}.{function}'.format(
                module=self.module, function=self.funcName
            ),
            'line': self.lineno
        }

        if isinstance(self.msg, str):
            extra = {
                'message': self.msg,
                'log': log,
            }
            # Add the extra messages
            data.update(extra)
        elif isinstance(self.msg, dict):
            # Shallow copy so the reference isn't destroying the outer obj.
            _dict = self.msg.copy()
            # We remove the `message` or `msg` keys so we can keep the
            # key consistent with the other EventRecords.
            _message = ''
            if 'message' in _dict.keys():
                _message = _dict.pop('message')
            elif 'msg' in _dict.keys():
                _message = _dict.pop('msg')

            data['message'] = _message
            # Append the dict to the data as extra info
            data.update(_dict)

        return data

    def __str__(self):
        return '<EventRecord {}, {}, {}, {}, {}, {}>'.format(
            self.name,
            self.level_num,
            self.pathname,
            self.module,
            self.funcName,
            self.msg
        )

    __repr__ = __str__

    def get_message(self):
        """Return the message for this EventRecord."""
        return str(self.msg)


# ========================================================================= #
#      HANDLER CLASSES AND FUNCTIONS
# ========================================================================= #

class Handler(object):
    """
    Handler instances dispatch logging events to specific destinations.

    The base handler class. Acts as a placeholder which defines the Handler
    interface. Handlers can optionally use Formatter instances to format
    records as desired. By default, no formatter is specified; in this case,
    the 'raw' message as determined by record.message is logged.
    """
    def __init__(self, level=NOTSET):
        # Handler name
        self._name = None
        self.level = _check_level(level)

    # Property encapsulation
    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    name = property(get_name, set_name)

    def emit(self, record):
        """Do whatever it takes to actually log the specified logging record.

        This version is intended to be implemented by subclasses and so
        raises a NotImplementedError.
        """
        raise NotImplementedError(
            '`emit` must be implemented by Handler subclass'
        )

    def handle(self, record):
        """
        Conditionally emit the specified logging record.

        Emission depends on filters which may have been added to the handler.
        Wrap the actual emission of the record with acquisition/release of
        the I/O thread lock. Returns whether the filter passed the record for
        emission.
        """
        rv = record
        if rv:
            self.emit(record)
        return rv

    # noinspection PyBroadException,PyMethodMayBeStatic
    def handle_errors(self, record: EventRecord):
        """
        Handle errors which occur during an emit() call.

        This method should be called from handlers when an exception is
        encountered during an emit() call. This is what is mostly wanted
        for a logging system - most users will not care about errors in
        the logging system, they are more interested in application errors.
        You could, however, replace this with a custom handler if you wish.
        The record which was being processed is passed in to this method.
        """
        t, v, tb = sys.exc_info()
        try:
            sys.stderr.write('--- Logging error ---\n')
            traceback.print_exception(t, v, tb, None, sys.stderr)
            sys.stderr.write('Call stack:\n')
            # Walk the stack frame up until we're out of logging,
            # so as to print the calling context.
            frame = tb.tb_frame
            while (frame and os.path.dirname(frame.f_code.co_filename) ==
                   __path__[0]):
                frame = frame.f_back
            if frame:
                traceback.print_stack(frame, file=sys.stderr)
            else:
                # couldn't find the right stack frame, for some reason
                sys.stderr.write(
                    'Logged from file {filename}}, line {line}\n'.format(
                        filename=record.filename, line=record.lineno
                    )
                )
            # Issue 18671: output logging message and arguments
            try:
                sys.stderr.write('Message: {msg}\n'.format(msg=record.msg))
            except Exception:
                sys.stderr.write(
                    'Unable to print the message and arguments - possible '
                    'connection error.\nUse the traceback above to help '
                    'find the error.\n'
                )
        except OSError:  # pragma: no cover
            pass  # see issue 5971
        finally:
            del t, v, tb

    def __str__(self):
        return '<{name}>'.format(name=self.__class__.__name__)

    __repr__ = __str__


# noinspection PyBroadException
class FluentdHandler(Handler):
    """
    A handler class which writes logging records, appropriately formatted,
    to the `fluentd` driver using the `sender.emit` method.
    """
    def __init__(self, stream=None, tag: str = ''):
        """Initialize the `fluentd` handler.

        Args:
            tag: the prefix tag to be used for a `fluentd` event log.
        """
        Handler.__init__(self)

        # The prefix tag to use with a `fluentd` log.
        if not tag:
            tag = env.get('FLUENTD_PREFIX_TAG', 'flask')
        self.tag = tag

        # A handler that logs to a remote instance of `elasticsearch`.
        # The values `FLUENTD_HOST` and `FLUENTD_PORT` must be in the ENV vars.
        if stream is None:
            host, port = get_remote_fluentd()
            stream = sender.FluentSender(self.tag, host=host, port=port)
        self.__stream = stream

    def emit(self, record: EventRecord):
        """Emit a record using the `fluentd-logger.sender.emit`. We also
        handle any exceptions that occurs from trying to send.

        Args:
            record: an EventRecord that has all the necessary information.
        """
        try:
            # Ensure we send the logs and if it's not sent we handle the error
            # by printing to `sys.stderr` at a more low-level.
            if not self.__stream.emit(record.level_str(), record.data_dict()):
                self.handle_errors(record)
                self.__stream.clear_last_error()
                # reraise the exception so we can handle it
                raise
        except Exception:
            self.handle_errors(record)

    def __str__(self):
        name = getattr(self.__stream, 'name', '')
        if name:
            name += ' '
        return '<{base} {stream}>'.format(
            base=self.__class__.__name__, stream=name
        )

    __repr__ = __str__


# noinspection PyBroadException
class StreamHandler(Handler):
    """
    A handler class which writes logging records, appropriately formatted,
    to a stream. Note that this class does not close the stream, as
    sys.stdout or sys.stderr may be used.
    """
    terminator = '\n'

    def __init__(self, stream=None):
        """
        Initialize the handler.

        If stream is not specified, sys.stderr is used.
        """
        Handler.__init__(self)
        if stream is None:
            stream = sys.stderr
        self.stream = stream

    def flush(self):
        """Flushes the stream."""
        if self.stream and hasattr(self.stream, "flush"):
            self.stream.flush()

    def emit(self, record):
        """
        Emit a record.

        If a formatter is specified, it is used to format the record.
        The record is then written to the stream with a trailing newline.  If
        exception information is present, it is formatted using
        traceback.print_exception and appended to the stream.  If the stream
        has an 'encoding' attribute, it is used to determine how to do the
        output to the stream.
        """
        try:
            msg = record
            stream = self.stream
            # issue 35046: merged two stream.writes into one.
            stream.write(msg + self.terminator)
            self.flush()
        except Exception:
            self.handle_errors(record)

    def set_stream(self, stream):
        """
        Sets the StreamHandler's stream to the specified value,
        if it is different.

        Returns the old stream, if the stream was changed, or None
        if it wasn't.
        """
        if stream is self.stream:
            result = None
        else:
            result = self.stream
            self.flush()
            self.stream = stream
        return result

    def __str__(self):
        # level = get_level_name(self.level)
        name = getattr(self.stream, 'name', '')
        if name:
            name += ' '
        return '<{} {}>'.format(self.__class__.__name__, name)

    __repr__ = __str__


class _StderrHandler(StreamHandler):
    """
    This class is like a StreamHandler using sys.stderr, but always uses
    whatever sys.stderr is currently set to rather than the value of
    sys.stderr at handler construction time.
    """

    # noinspection PyUnusedLocal
    def __init__(self, level=NOTSET):
        """Initialize the `sys.stderr` stream handler."""
        Handler.__init__(self)

    @property
    def stream(self):
        return sys.stderr


_default_last_resort = _StderrHandler(WARNING)
last_resort_handler = _default_last_resort


# ========================================================================= #
#      LOGGER
# ========================================================================= #

class FluentdLogging(object):
    """
    A Python `logging` library inspired logger that uses a EventRecord and logs
    a message to the `fluentd` driver in a specific format depending on the
    data type of the message.
    """
    def __init__(self, name: str = '', level=NOTSET):
        """Instantiate the `FluentdLogger` instance with optional values
        passed in.

        Usage:
            >>> logger = FluentdLogging(name=__name__, tag='logger')
            >>> logger.info({'message': 'Log Hello World'})

        Args:
            name: the name of the calling module.
        """
        self.name = name
        self.level = _check_level(level)
        # By default we always use the `FluentdHandler` subclass
        self.handlers = [FluentdHandler()]
        self.propagate = False

    @staticmethod
    def find_caller(stack_info=False):
        """
        Find the stack frame of the caller so that we can note the source
        file name, line number and function name.
        """
        f = currentframe()
        # On some versions of IronPython, currentframe() returns None if
        # IronPython isn't run with -X:Frames.
        if f is not None:
            f = f.f_back
        rv = "(unknown file)", 0, "(unknown function)", None
        while hasattr(f, "f_code"):
            co = f.f_code
            filename = os.path.normcase(co.co_filename)
            if filename == _srcfile:
                f = f.f_back
                continue
            _stack_info = None
            if stack_info:
                sio = io.StringIO()
                sio.write('Stack (most recent call last):\n')
                traceback.print_stack(f, file=sio)
                _stack_info = sio.getvalue()
                # Want to print the last \n
                # if _stack_info[-1] == '\n':
                #     _stack_info = _stack_info[:-1]
                sio.close()
            rv = (co.co_filename, f.f_lineno, co.co_name, _stack_info)
            break
        return rv

    # noinspection PyUnusedLocal
    def _log(
            self,
            level: int,
            msg: Union[str, dict, Any],
            exc_info: bool = None,
            stack_info=False,
            **kwargs
    ):
        """
        Low-level logging routine which creates a EventRecord and then handles.
        """
        _stack_info = None
        if _srcfile:
            # IronPython doesn't track Python frames, so findCaller raises an
            # exception on some versions of IronPython. We trap it here so that
            # IronPython can use logging.
            try:
                filename, lno, func, _stack_info = self.find_caller(stack_info)
            except ValueError:  # pragma: no cover
                filename, lno, func = "(unknown file)", 0, "(unknown function)"
        else:  # pragma: no cover
            filename, lno, func = "(unknown file)", 0, "(unknown function)"
        if exc_info:
            if isinstance(exc_info, BaseException):
                exc_info = (type(exc_info), exc_info, exc_info.__traceback__)
            elif not isinstance(exc_info, tuple):
                exc_info = sys.exc_info()
        record = EventRecord(
            name=self.name,
            level=level,
            pathname=filename,
            lineno=lno,
            msg=msg,
            exc_info=exc_info,
            func=func,
            stack_info=_stack_info
        )
        self.handle(record)

    def handle(self, record: EventRecord):
        """Send the record to the `fluentd` driver."""
        self.call_handlers(record)

    def call_handlers(self, record):
        """Pass a record to all relevant handlers.

        Loop through all handlers for this logger and its parents in the
        logger hierarchy. If no handler was found, output a one-off error
        message to sys.stderr. Stop searching up the hierarchy whenever a
        logger with the "propagate" attribute set to zero is found - that
        will be the last logger whose handlers are called.

        Args:
            record: an EventRecord that has all the necessary information.

        Returns:
            None
        """
        # We actually only have one handler for now but keeping this logic
        # in case we need to add a StreamHandler down the track.
        c = self
        found = 0
        while c:
            for handler in c.handlers:
                found = found + 1
                handler.handle(record)
            if not c.propagate:
                c = None   # break out
        if found == 0:
            if last_resort_handler:
                last_resort_handler.handle(record)

    def debug(self, msg: Union[str, dict], **kwargs):
        """Log 'msg' with severity 'DEBUG'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.debug("Houston, we have a thorny problem", exc_info=True)
        """
        self._log(DEBUG, msg, **kwargs)

    def info(self, msg: Union[str, dict], **kwargs):
        """Log 'msg' with severity 'INFO'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.info("Houston, we have a interesting problem", exc_info=True)
        """
        self._log(INFO, msg, **kwargs)

    def warning(self, msg: Union[str, dict], **kwargs):
        """Log 'msg' with severity 'WARNING'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.warning("Houston, we have a bit of a problem", exc_info=True)
        """
        self._log(WARNING, msg, **kwargs)

    def error(self, msg: Union[str, dict], stack_info: bool = True, **kwargs):
        """Log 'msg' with severity 'ERROR'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.error("Houston, we have a major problem", exc_info=True)
        """
        self._log(ERROR, msg, stack_info=stack_info, **kwargs)

    def critical(self, msg: Union[str, dict], **kwargs):
        """Log 'msg' with severity 'CRITICAL'.

        To pass exception information, use the keyword argument
        exc_info with a true value, e.g.

        logger.critical("Houston, we have a major disaster", exc_info=True)
        """
        self._log(CRITICAL, msg, exc_info=True, stack_info=True, **kwargs)

    fatal = critical

    def exception(self, msg: Union[str, dict], **kwargs):
        """Convenience method for logging an ERROR with exception info."""
        self.error(msg, exc_info=True, stack_info=True, **kwargs)
