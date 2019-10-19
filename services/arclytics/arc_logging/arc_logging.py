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
__version__ = '0.9.0'
__status__ = 'development'
__date__ = '2019.09.21'
"""
fluentd_logger.py

This library is made to be used as a wrapper with Python's logging library and
to also send logs as events to fluentd with the `fluentd-logger` library 
handler.
"""

import io
import os
import socket
import sys
import threading
import time
import traceback
import warnings
import weakref
from os import W_OK, access, makedirs, path
from os import environ as env
from pathlib import Path
from typing import Any, Union

from fluent import sender

# ========================================================================= #
#      LOGGER FILE PATH DATA
# ========================================================================= #
PWD = os.path.dirname(os.path.abspath(__file__))
# should be arclytics_sim/services/simcct/
BASE_DIR = os.path.abspath(os.path.join(PWD, os.pardir))
PREFIX_LOG_PATH = Path(BASE_DIR) / 'logs'


def check_logpath(log_path):
    """
    Tests if the logger has access to the the given path and sets up
    directories.

    Note:
        Should always yield a valid path. May default log directory. Will throw
        warnings.RuntimeWarning if permission do not allow file write at path.

    Args:
        log_path: A str with the path for desired log file. Abspath > relpath.
        debug_mode: Way to make debug easier by forcing path to local.

    Returns:
        str: the path to log to.
             If path exists or can be created, will return log_path else it
             returns '.' as "local path only" response.
    """

    # Try to create path to log
    if not path.exists(PREFIX_LOG_PATH.absolute()):
        try:
            makedirs(PREFIX_LOG_PATH.absolute(), exist_ok=True)
        except PermissionError as e:
            warning_msg = (
                "Unable to create logging file path. Default to '.'\n" +
                "\tLog Path: {}\n".format(log_path) +
                "\tException: {}\n".format(e)
            )
            warnings.warn(warning_msg, RuntimeWarning)

    if not access(PREFIX_LOG_PATH.absolute(), W_OK):
        # Unable to write to log path
        warning_msg = (
            "Write permissions not allowed on path. Defaulting to '.'\n" +
            "\tLog Path: {}".format(log_path)
        )
        warnings.warn(warning_msg, RuntimeWarning)
        return '.'

    return log_path


# ========================================================================= #
#      MISCELLANEOUS MODULE DATA
# ========================================================================= #

#
# _startTime is used as the base when calculating the relative time of events
#
_startTime = time.time()

#
# If you don't want threading information in the log, set this to zero
#
logThreads = True

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
        env.get('FLUENTD_HOST',
                'fluentd-service'), int(env.get('FLUENTD_PORT', 24224))
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

_srcfile = os.path.normcase(check_logpath.__code__.co_filename)

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
#      THREAD-RELATED STUFF
# ========================================================================= #

#
# _lock is used to serialize access to shared data structures in this module.
# This needs to be an RLock because fileConfig() creates and configures
# Handlers, and so might arbitrary user threads. Since Handler code updates
# the shared dictionary _handlers, it needs to acquire the lock. But if
# configuring, the lock would already have been acquired - so we need an
# RLock. The same argument applies to Loggers and Manager.loggerDict.
#
_lock = threading.RLock()


def _acquire_lock():
    """
    Acquire the module-level lock for serializing access to shared data.

    This should be released with _releaseLock().
    """
    if _lock:
        _lock.acquire()


def _release_lock():
    """
    Release the module-level lock acquired by calling _acquireLock().
    """
    if _lock:
        _lock.release()


# ========================================================================= #
#      LOGGING RECORD
# ========================================================================= #
class LogRecord(object):
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
        ct = time.time()
        self.name = name
        self.msg = msg
        self.hostname = socket.gethostname()

        self.level_name = get_level_name(level)
        self.level_num = level

        self.pathname = pathname

        self.exc_info = exc_info
        self.exc_text = None  # used to cache the traceback text
        self.stack_info = stack_info

        self.funcName = func
        self.lineno = lineno

        self.created = ct
        self.msecs = (ct - int(ct)) * 1000
        self.relativeCreated = (self.created - _startTime) * 1000

        try:
            self.filename = os.path.basename(pathname)
            self.module = os.path.splitext(self.filename)[0]
        except (TypeError, ValueError, AttributeError):
            self.filename = pathname
            self.module = "Unknown module"

        if logThreads:
            self.thread = threading.get_ident()
            self.threadName = threading.current_thread().name
        else:  # pragma: no cover
            self.thread = None
            self.threadName = None

    def __str__(self):
        return '<LogRecord {}, {}, {}, {}, {}, {}>'.format(
            self.name, self.level_num, self.pathname, self.module,
            self.funcName, str(self.msg)
        )

    def get_log_formatted(self):
        return (
            '{asctime} : {hostname} : {name} : {module}.{function} : '
            '{level_name} : {message}'
        ).format(
            asctime=format_time(self),
            hostname=self.hostname,
            module=self.module,
            function=self.funcName,
            name=self.name,
            level_name=self.level_name,
            message=str(self.msg)
        )

    __repr__ = __str__

    def get_message(self):
        """Return the message for this LogRecord."""
        return str(self.msg)


class EventRecord(LogRecord):
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
        stack_info=None
    ):
        super(EventRecord, self).__init__(
            name, level, pathname, lineno, msg, exc_info, func, stack_info
        )

    def level_str(self):
        return str(self.level_name).lower()

    def data_dict(self):
        # TODO(andrew@neuraldev.io): Check for other types.
        # For the log, we want to print the whole stringified msg object
        # sent to us rather than just the message alone.
        log = self.get_log_formatted()

        data = {
            'timestamp':
            format_time(self),
            'hostname':
            self.hostname,
            'severity':
            self.level_name,
            'log':
            log,
            'stack_trace':
            self.stack_info,
            'caller':
            '{module}.{function}'.format(
                module=self.module, function=self.funcName
            ),
            'line':
            self.lineno
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
            self.name, self.level_num, self.pathname, self.module,
            self.funcName, str(self.msg)
        )

    __repr__ = __str__


#
# Not using a Formatter from the `logging` module but we want to use the
# same formatting for the dates so we will make it a module method.
#
CONVERTER = time.localtime
DEFAULT_TIME_FMT = '%Y-%m-%d %H:%M:%S'
DEFAULT_MSEC_FMT = '%s,%03d'


def format_time(record, datefmt=None):
    """
    Return the creation time of the specified EventRecord as formatted text.

    The basic behaviour is as follows: if datefmt (a string) is specified,
    it is used with time.strftime() to format the creation time of the
    record. Otherwise, an ISO8601-like (or RFC 3339-like) format is used.
    The resulting string is returned. This function uses a user-configurable
    function to convert the creation time to a tuple. By default,
    time.localtime() is used; to change this for a particular formatter
    instance, set the 'converter' attribute to a function with the same
    signature as time.localtime() or time.gmtime(). To change it for all
    formatters, for example if you want all logging times to be shown in GMT,
    set the 'converter' attribute in the Formatter class.
    """
    ct = CONVERTER(record.created)
    if datefmt:
        s = time.strftime(datefmt, ct)
    else:
        t = time.strftime(DEFAULT_TIME_FMT, ct)
        s = '{},{:.03f}'.format(t, record.msecs)
    return s


# ========================================================================= #
#      HANDLER CLASSES AND FUNCTIONS
# ========================================================================= #
# map of handler names to handlers
_handlers = weakref.WeakValueDictionary()
# added to allow handlers to be removed in reverse of order initialized
_handler_list = []


def _remove_handler_ref(wr):
    """
    Remove a handler reference from the internal cleanup list.
    """
    # This function can be called during module teardown, when globals are
    # set to None. It can also be called from another thread. So we need to
    # pre-emptively grab the necessary globals and check if they're None,
    # to prevent race conditions and failures during interpreter shutdown.
    acquire, release, handlers = _acquire_lock, _release_lock, _handler_list
    if acquire and release and handlers:
        acquire()
        try:
            if wr in handlers:
                handlers.remove(wr)
        finally:
            release()


def _add_handler_ref(handler):
    """
    Add a handler to the internal cleanup list using a weak reference.
    """
    _acquire_lock()
    try:
        _handler_list.append(weakref.ref(handler, _remove_handler_ref))
    finally:
        _release_lock()


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

        # Add the handler to the global `_handler_list`
        # (for cleanup on shutdown)
        _add_handler_ref(self)
        self.lock = self.create_lock()

    # Property encapsulation
    def get_name(self):
        return self._name

    def set_name(self, name):
        _acquire_lock()
        try:
            # Look for the handlers by their weak reference in the global
            # `_handlers` dict
            if self._name in _handlers:
                del _handlers[self._name]
            self._name = name
            if name:
                _handlers[name] = self
        finally:
            _release_lock()

    name = property(get_name, set_name)

    # noinspection PyMethodMayBeStatic
    def create_lock(self):
        """
        Acquire a thread lock for serializing access to the underlying I/O.
        """
        return threading.RLock()

    def acquire(self):
        """Acquire the I/O thread lock."""
        if self.lock:
            self.lock.acquire()

    def release(self):
        """Release the I/O thread lock."""
        if self.lock:
            self.lock.release()

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
            self.acquire()
            try:
                self.emit(record)
            finally:
                self.release()
        return rv

    def close(self):
        """
        Tidy up any resources used by the handler.

        This version removes the handler from an internal map of handlers,
        _handlers, which is used for handler lookup by name. Subclasses
        should ensure that this gets called from overridden close()
        methods.
        """
        # get the module data lock, as we're updating a shared structure.
        _acquire_lock()
        try:  # unlikely to raise an exception, but you never know...
            if self._name and self._name in _handlers:
                del _handlers[self._name]
        finally:
            _release_lock()

    # noinspection PyBroadException,PyMethodMayBeStatic
    def handle_errors(self, record: Union[EventRecord, LogRecord]):
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
            while (
                frame
                and os.path.dirname(frame.f_code.co_filename) == __path__[0]
            ):
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


class FluentdHandler(Handler):
    """
    A handler class which writes logging records, appropriately formatted,
    to the `fluentd` driver using the `sender.emit` method.
    """
    def __init__(self, tag: str = ''):
        """Initialize the `fluentd` handler.

        There is no need for a level as we would like all messages to be
        sent to the Handler.

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
        host, port = get_remote_fluentd()
        self.__stream = sender.FluentSender(self.tag, host=host, port=port)

    # noinspection PyBroadException
    def emit(self, record: Union[LogRecord, EventRecord]):
        """Emit a record using the `fluentd-logger.sender.emit`. We also
        handle any exceptions that occurs from trying to send.

        Args:
            record: an EventRecord that has all the necessary information.
        """
        try:
            # Ensure we send the logs and if it's not sent we handle the error
            # by printing to `sys.stderr` at a more low-level.

            ev_record = record
            if isinstance(record, LogRecord):
                import copy
                ev_record = copy.copy(record)
                ev_record.__class__ = EventRecord

            if not self.__stream.emit(
                ev_record.level_str(), ev_record.data_dict()
            ):
                self.handle_errors(record)
                self.__stream.clear_last_error()
                # reraise the exception so we can handle it
                raise Exception
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
        self.acquire()
        try:
            if self.stream and hasattr(self.stream, "flush"):
                self.stream.flush()
        finally:
            self.release()

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
            stream.write(msg.get_log_formatted() + self.terminator)
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
            self.acquire()
            try:
                self.flush()
                self.stream = stream
            finally:
                self.release()
        return result

    def __str__(self):
        level = get_level_name(self.level)
        name = getattr(self.stream, 'name', '')
        if name:
            name += ' '
        return '<{} {}({})>'.format(self.__class__.__name__, name, level)

    __repr__ = __str__


class FileHandler(StreamHandler):
    """
    A handler class which writes formatted logging records to disk files.
    """
    def __init__(self, filename, mode='a', encoding=None, delay=False):
        """Open the specified file and use it as the stream for logging."""
        # Issue #27493: add support for Path objects to be passed in
        filename = os.fspath(filename)
        # keep the absolute path, otherwise derived classes which use this
        # may come a cropper when the current directory changes
        self.base_filename = os.path.abspath(filename)
        self.mode = mode
        self.encoding = encoding
        self.delay = delay
        if delay:
            # We don't open the stream, but we still need to call the
            # Handler constructor to set level, formatter, lock etc.
            Handler.__init__(self)
            self.stream = None
        else:
            StreamHandler.__init__(self, self._open())

    def close(self):
        """
        Closes the stream.
        """
        self.acquire()
        try:
            try:
                if self.stream:
                    try:
                        self.flush()
                    finally:
                        stream = self.stream
                        self.stream = None
                        if hasattr(stream, "close"):
                            stream.close()
            finally:
                # Issue #19523: call unconditionally to
                # prevent a handler leak when delay is set
                StreamHandler.close(self)
        finally:
            self.release()

    def _open(self):
        """
        Open the current base file with the (original) mode and encoding.
        Return the resulting stream.
        """
        return open(self.base_filename, self.mode, encoding=self.encoding)

    def emit(self, record):
        """
        Emit a record.

        If the stream was not opened because 'delay' was specified in the
        constructor, open it before calling the superclass's emit.
        """
        if self.stream is None:
            self.stream = self._open()
        StreamHandler.emit(self, record)

    def __str__(self):
        # level = get_level_name(self.level)
        level = get_level_name(self.level)
        return '<{} {}({})>'.format(
            self.__class__.__name__, self.base_filename, level
        )

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


_DEFAULT_LAST_RESORT = _StderrHandler(WARNING)
LAST_RESORT_HANDLER = _DEFAULT_LAST_RESORT

# ========================================================================= #
#      LOGGER
# ========================================================================= #


class AppLogger(object):
    """
    A Python `logging` library inspired logger that uses a EventRecord and logs
    a message to the `fluentd` driver in a specific format depending on the
    data type of the message.
    """
    def __init__(self, name: str, level: int = NOTSET):
        """Instantiate the `FluentdLogger` instance with optional values
        passed in.

        Usage:
            >>> import arc_logging
            >>> logger = AppLogger(name=__name__, level=arc_logging.DEBUG)
            >>> logger.info({'message':'Houston we have an interesting prob.'})

        Args:
            name: a required name of the calling module.
            level: the level to set the logger to print messages.
        """
        # The name is used to store loggers and define how a LogRecord is
        # created for the logger.
        self.name = name
        # Check the level is correctly passed
        self.level = _check_level(level)

        self.handlers = []
        self.propagate = False
        # By default we always use the `FluentdHandler` subclass
        self.handlers.append(FluentdHandler())

        # Because this logger is specific to Arclytics Sim, we check what
        # environment we are in and by default use development
        _production = env.get('FLASK_ENV', 'development') == 'production'

        # If we are using development mode, we want to print to sys.stderr too
        if not _production:
            # Add a console handler that prints to `sys.stderr`
            console_handler = StreamHandler(stream=sys.stderr)
            console_handler.set_name('console_handler')
            self.handlers.append(console_handler)

            if not os.path.isdir(PREFIX_LOG_PATH):
                try:
                    os.makedirs(PREFIX_LOG_PATH)
                except OSError as e:
                    print(
                        "Error: {} - {}.".format(e.filename, e.strerror),
                        file=sys.stderr
                    )
            logfile_path = os.path.abspath(
                os.path.join(PREFIX_LOG_PATH, (self.name + ".log"))
            )
            log_path = check_logpath(logfile_path)

            self.handlers.append(FileHandler(log_path, delay=True))

    def set_level(self, level):
        """Set the logging level of this logger.

        Args:
            level: must be an int or a str.
        """
        self.level = _check_level(level)

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

        # We always use the BASE superclass and then we use Python duck typing
        # to cast it later to any Record we subclass with.
        record = LogRecord(
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

    def handle(self, record: LogRecord):
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
                # This checks the handler vs. logger levels and only calls
                # the emit for the handlers required. We are not concerned
                # here as we want to print everything for development.
                # if record.levelno >= handler.level:
                handler.handle(record)
            if not c.propagate:
                c = None  # break out
        if found == 0:
            if LAST_RESORT_HANDLER:
                LAST_RESORT_HANDLER.handle(record)

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

    def error(
        self,
        msg: Union[str, dict],
        stack_info: bool = True,
        exc_info: bool = False,
        **kwargs
    ):
        """Log 'msg' with severity 'ERROR'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.error("Houston, we have a major problem", exc_info=True)
        """
        self._log(
            ERROR, msg, stack_info=stack_info, exc_info=exc_info, **kwargs
        )

    def critical(self, msg: Union[str, dict], **kwargs):
        """Log 'msg' with severity 'CRITICAL'.

        To pass exception information, use the keyword argument
        exc_info with a true value, e.g.

        logger.critical("Houston, we have a major disaster", exc_info=True)
        """
        self._log(CRITICAL, msg, exc_info=True, stack_info=True, **kwargs)

    fatal = critical

    def exception(
        self, msg: Union[str, dict], exc_info: bool = True, **kwargs
    ):
        """Convenience method for logging an ERROR with exception info."""
        self.error(msg, exc_info=exc_info, stack_info=True, **kwargs)
