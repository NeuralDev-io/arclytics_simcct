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
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# arc_logger.py
#
# Date: 16/12/18
# Attributions:
# [1] https://medium.com/@HLIBIndustry/python-logging-custom-handlers-f3ba784a9452
# [2] https://github.com/EVEprosper/ProsperCommon
#
# TODO: Make changes to the way a filename is handled by adding and removing the file handler
# ----------------------------------------------------------------------------------------------------------------------

__author__ = 'Andrew Che <@codeninja55>'
__copyright__ = 'Copyright (C) 2019, Andrew Che <@codeninja55>'
__credits__ = []
__license__ = 'MIT'
__version__ = '1.0.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = 'development'
__date__ = '2019.06.24'
"""Module level logger that can be used as a wrapper that extends the default logging module."""

import sys
import os
import logging
import warnings
import json
from enum import Enum
from pprint import pprint, pformat
from os import path, makedirs, access, W_OK, getcwd
from pathlib import Path

__name__ = "ArcLogger"

PWD = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(
    PWD, os.pardir))  # should be arclytics_sim/services/server/
PREFIX_LOG_PATH = Path(BASE_DIR) / 'logs'
PREFIX_CONFIG_PATH = os.path.abspath(os.path.join(BASE_DIR, 'configs'))
DEFAULT_CONFIG = Path(BASE_DIR) / 'configs' / 'app.json'
DEFAULT_LOGGER = logging.getLogger('NULL')
DEFAULT_LOGGER.addHandler(logging.NullHandler())


class ReportingFormats(Enum):
    """Enum for storing some handy log formats."""
    FILE = "%(asctime)s : %(threadName)s : %(filename)s : %(name)s : %(funcName)s : %(lineno)s: " \
           "%(levelname)s : %(message)s"
    STDOUT = "[%(asctime)s--%(name)s] [%(levelname)s] : %(message)s"
    PROFILER = "[%(asctime)s] [%(name)s %(levelname)s] ==> %(message)s"
    SLACK_PRINT = '%(message).1000s'
    DATE_FMT = "%Y-%m-%d %H:%M:%S"


class AppLogger(object):
    """
    A logger to be used as the default which extends the default logging module.

    Attributes:
        _config_mode: Check whether there is a config to parse.
        _debug_mode: Check whether to use the debugger logger by default. Will take precedence over stdout_mode
        if both are set to true. Alternatively, you can use configure_stdout_logger() to explicitly create both.
        _stdout_mode: Check whether to use the stdout logger by default which overrides the debug mode. Will not
        be created by default if debug_mode is true. Alternatively, you can set debug_mode to false and explicitly
        call configure_debug_logger() to create a debug logger just for a specific module.
        _profiler_mode: Check to see whether to add a profiler logger which can be used to profile execution time.
        caller: The module that created the logger and thus is effectively the logger name.
        custom_config: A Path to a custom config file to use. The config file must have [LOGGING] and set the bool
        values for 'debug', 'stdout', and 'profiler'.
    """

    _config_mode = False
    _debug_mode = True
    _stdout_mode = True
    _profiler_mode = False

    def __init__(self,
                 caller: str,
                 prefix_logpath: str = PREFIX_LOG_PATH,
                 custom_config: str = ""):
        # Get the debug level from the default app config if no custom config has been set
        self._config_mode = self._check_config(custom_config=custom_config)

        # create a logger
        self.logger = logging.getLogger(caller)

        self.caller = caller

        if not os.path.isdir(PREFIX_LOG_PATH):
            try:
                os.makedirs(PREFIX_LOG_PATH)
            except OSError as e:
                print("Error: %s - %s." % (e.filename, e.strerror))
        logfile_path = os.path.abspath(
            os.path.join(PREFIX_LOG_PATH, (caller + ".log")))
        if prefix_logpath is not PREFIX_LOG_PATH:
            logfile_path = Path(prefix_logpath) / "logs" / (caller + ".log")
        self.log_path = check_logpath(logfile_path, not self._debug_mode)
        # self.log_path = logfile_path  # to be used if above not working

        self.log_info = []
        self.log_handlers = []

        # create the default logger at DEBUG level.
        self.configure_default_logger(log_level="DEBUG")

    def get_logger(self):
        """Return the logger for the user."""
        return self.logger

    def __str__(self):
        """Return a list of 'handler_name @ log_level' for debugging purposes."""
        return ','.join(self.log_info)

    def __iter__(self):
        """Returns each handler in order."""
        for handler in self.log_handlers:
            yield handler

    def _check_config(self, custom_config):
        """
        Check if there is a config file to use. Initially, it will ensure the custom_config passed
        to the constructor is properly in the correct default CONFIG_PATH. If no custom_config
        has been passed then there will be a check for the DEFAULT_CONFIG. If neither of those
        are available, then the logger will run without configurations to use.

        Args:
            custom_config: The str file name of the config that is placed into the CONFIG_PATH directory.

        Returns:
            bool value whether to run in _config_mode or not.
        """
        self.config = None

        if custom_config is not "" and not (PREFIX_CONFIG_PATH /
                                            custom_config).is_file():
            warning_msg = ("Configuration files must go into ../configs/" +
                           'config_path={0}'.format(custom_config))
            warnings.warn(warning_msg, RuntimeWarning)
            return False

        if custom_config is not "":

            with open(custom_config) as config_file:
                self.config = json.load(config_file)

            self._debug_mode = self.config["logging"]["debug"]
            self._profiler_mode = self.config["logging"]["profiler"]
            self._stdout_mode = self.config["logging"]["stdout"]
            return True
        elif DEFAULT_CONFIG.is_file():
            # Default configs
            with open(DEFAULT_CONFIG) as config_file:
                self.config = json.load(config_file)

            self._debug_mode = self.config["logging"]["debug"]
            self._stdout_mode = self.config["logging"]["stdout"]
            self._profiler_mode = self.config["logging"]["profiler"]
            return True
        return False

    def _configure_common(self, log_level: str, log_format: str,
                          handler_name: str, handler):
        """
        Common configuration code.

        Args:
            log_level: The str representation of the log level to use.
            log_format: The log formatting to use.
            handler_name" The handler to be used in debug messages
            handler: The logging Handler to configure and use.
        """

        # Attach handlers and formatters
        formatter = logging.Formatter(fmt=log_format,
                                      datefmt=ReportingFormats.DATE_FMT.value)
        handler.setFormatter(fmt=formatter)
        handler.setLevel(log_level)
        self.logger.addHandler(handler)

        # Ensure the logger level is not lower than the handler level
        if not self.logger.isEnabledFor(logging.getLevelName(log_level)):
            self.logger.setLevel(log_level)

        self.log_info.append("{0} @ {1} ".format(handler_name, str(log_level)))
        self.log_handlers.append(handler)

    def configure_default_logger(self, log_level: str):
        """Default logger that every application using this library should use."""
        log_filename = Path(self.log_path)
        log_abspath = log_filename.absolute()

        general_handler = logging.FileHandler(filename=log_abspath,
                                              mode='a',
                                              delay=True)

        self._configure_common(
            log_level=log_level,
            log_format=ReportingFormats.FILE.value,
            handler_name="default_file",
            handler=general_handler,
        )

        # NOTE: If debug_mod or std_mode is one, create a Stream Handler with appropriate log level.
        #  debug_mode: will take precedence over stdout.
        #  stdout_mode: for when you are building an application and you need to print results to stdout
        if self._config_mode:
            if self._debug_mode or self._stdout_mode:
                console_handler = logging.StreamHandler()
                stream_log_level = None
                handler_name = ""
                if self._debug_mode:
                    console_handler.stream = sys.stderr
                    stream_log_level = "DEBUG"
                    handler_name = "default_debug"
                elif self._stdout_mode:
                    console_handler.stream = sys.stdout
                    stream_log_level = "INFO"
                    handler_name = "default_stdout"
                console_handler.setLevel(stream_log_level)
                self._configure_common(
                    log_level=stream_log_level,
                    log_format=ReportingFormats.STDOUT.value,
                    handler_name=handler_name,
                    handler=console_handler,
                )
            # NOTE: If profiler_mode is set
            # FIXME: NO IDEA WHY EVEN WHEN THIS IS FALSE A PROFILER HANDLER IS CREATED
            #  ALSO CHECK WHY THE PROFILER HANDLER LOGS AT THE INFO LEVEL
            # print("[DEBUG] {}".format(self._profiler_mode), file=sys.stderr)
            # if self._profiler_mode:
            #     logging.addLevelName(5, "PROFILER")
            #     self._configure_common(
            #             log_level="PROFILER",
            #             log_format=ReportingFormats.PROFILER.value,
            #             handler_name="profiler",
            #             handler=logging.StreamHandler(stream=sys.stderr),
            #     )

    def configure_debug_logger(self,
                               log_level="DEBUG",
                               log_format=ReportingFormats.STDOUT.value):
        """
        Debug logger for stdout messages that will be used as sys.stderr. This is an explicit call
        of the debugger if no configuration has been created to allow you to use a specific debugger
        in only certain parts of the application and not others.

        Args:
            log_level: The str representation log level which will default to DEBUG.
            log_format: The log format which will default to STDOUT enum value.
        """
        self._configure_common(
            log_level=log_level,
            log_format=log_format,
            handler_name="stream_debug",
            handler=logging.StreamHandler(stream=sys.stderr),
        )

    def configure_stdout_logger(self,
                                log_level="INFO",
                                log_format=ReportingFormats.STDOUT.value):
        """
        Stdout logger for stdout messages that will use the sys.stdout as stream. This is an explicit
        call of the logger if no configuration has been created to allow you to use a specific default
        stdout logger in only certain parts of the application and not others.

        Args:
            log_level: The log level which will default to logging.INFO.
            log_format: The log format which will default to STDOUT enum value.
        """
        self._configure_common(
            log_level=log_level,
            log_format=log_format,
            handler_name="stream_stdout",
            handler=logging.StreamHandler(stream=sys.stdout),
        )

    def debug(self, msg: str, *args, **kwargs):
        """
        Log 'message % args' with severity DEBUG.

        To pass exception information, use the keyword arg exc_info with a true value.
        Example:
            logger.debug("Houston, we have a %s", "thorny problem", exc_info=1)

        Args:
            msg: the message to log.
        """
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        """
        Log 'message'.format(*args) with severity INFO.

        To pass exception information, use the keyword argument exc_info with a true value.
        Example:
            logger.info("Houston, we have a %s", "interesting problem", exc_info=1)

        Args:
            msg: the message to log
        """
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        """
        Log 'message'.format(*args) with severity WARNING.

        To pass exception information, use the keyword argument exc_info with a true value.
        Example:
            logger.info("Houston, we have a %s", "bit of a problem", exc_info=1)

        Args:
            msg: the message to log
        """
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, stack_info=True, *args, **kwargs):
        """
        Log 'message'.format(*args) with severity ERROR.

        To pass exception information, use the keyword argument exc_info with a true value.
        Example:
            logger.info("Houston, we have a %s", "major problem", exc_info=1)

        Args:
            stack_info: whether to print the stack trace. Default is true.
            msg: the message to log
        """
        self.logger.error(msg, stack_info=stack_info, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        """
        Log 'message'.format(*args) with severity CRITICAL.

        To pass exception information, use the keyword argument exc_info with a true value.
        Example:
            logger.info("Houston, we have a %s", "interesting problem", exc_info=1)

        Args:
            msg: the message to log.
        """
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg: str, *args, exc_info=True, **kwargs):
        """
        Convenience method for logging an ERROR with exception information.

        Args:
            msg: the message to log.
            exc_info: default set to true to provide exception information
        """
        self.error(msg, *args, exc_info=exc_info, **kwargs)

    def profile(self, method: str, duration: float, *args, **kwargs):
        """
        Custom method for logging an PROFILER log level with execution time information.

        Args:
            method: The method that was profiled.
            duration: A float of time.time() for the time duration of the method execution.
        """
        msg = "Method: {method:<18} {arrow:8} Executed: {duration:.4f}s".format(
            method=method, arrow="==>", duration=duration)

        # Log if DEBUG is enabled
        if self.logger.isEnabledFor(logging.getLevelName("DEBUG")):
            self._log(20, str(msg), *args, exc_info=False, **kwargs)

    def pprint(self, msg: any, *args, **kwargs):
        """
        Convenience method for logging an at INFO level with pretty print (pprint) formatting.

        Args:
            msg: the message to log.
        """
        # self.info(msg=pformat(msg, indent=1))
        pmsg = pformat(msg, indent=2)
        out = '\n{}'.format(pmsg)
        self._log(level=20, msg=out, pretty=True, *args, **kwargs)

    def _log(self, level: int, msg: str, *args, **kwargs):
        """
        Generalised log method to log 'msg'.format(*args) with the integer severity 'level'

        Args:
            level:
            msg:
            *args:
            **kwargs:
        """
        pretty = False
        for k, v in kwargs.items():
            if k == 'pretty':
                pretty = True
                self.logger.log(level, msg)

        if not pretty:
            self.logger.log(level, msg, *args, **kwargs)


def check_logpath(log_path, debug_mode=False):
    """
    Tests if the logger has access to the the given path and sets up directories.

    Note:
        Should always yield a valid path. May default log directory. Will throw
        warnings.RuntimeWarning if permission do not allow file write at path.

    Args:
        log_path: A str with the path for desired log file. Abspath > relpath.
        debug_mode: Way to make debug easier by forcing path to local.

    Returns:
        str: the path to log to.
        If path exists or can be created, will return log_path else it returns '.' as "local path only" response.
    """
    # NOTE: If not debug, do not deploy to production paths.
    if debug_mode:
        return '.'

    # NOTE: Try to create path to log
    if not path.exists(PREFIX_LOG_PATH.absolute()):
        try:
            makedirs(PREFIX_LOG_PATH.absolute(), exist_ok=True)
        except PermissionError as e:
            warning_msg = (
                "Unable to create logging file path. Default to '.'\n" +
                "\tLog Path: {}\n".format(log_path) +
                "\tException: {}\n".format(e))
            warnings.warn(warning_msg, RuntimeWarning)

    if not access(PREFIX_LOG_PATH.absolute(), W_OK):
        # Unable to write to log path
        warning_msg = (
            "Write permissions not allowed on path. Defaulting to '.'\n" +
            "\tLog Path: {}".format(log_path))
        warnings.warn(warning_msg, RuntimeWarning)
        return '.'

    return log_path
