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

# ----------------------------------------------------------------------------------------------------------------------
# deep_learning_4_computer_vision
# timer.py
#
# Attributions:
# [1] https://medium.com/pythonhive/python-decorator-to-measure-the-execution-
# time-of-methods-fa04cb6bb36d
# [2] https://cyrille.rossant.net/profiling-and-optimizing-python-code/
# [3] https://www.blog.pythonlibrary.org/2016/05/24/python-101-an-intro-to-
# benchmarking-your-code/
# [4] https://zapier.com/engineering/profiling-python-boss/
# [5] https://www.tutorialspoint.com/python/time_clock.htm
# [6] https://jakevdp.github.io/PythonDataScienceHandbook/01.07-timing-and-
# profiling.html
# [7] https://www.pythoncentral.io/measure-time-in-python-time-time-vs-time-
# clock/
#
# TODO: Add a 'PROFILER' log level to AppLogger.
# TODO: Create a Profiler logger and log all timer to that using the PROFILER
#  log level.
# ----------------------------------------------------------------------------------------------------------------------

__author__ = 'Andrew Che <@codeninja55>'
__copyright__ = 'Copyright (C) 2018, Andrew Che <@codeninja55>'
__credits__ = ['']
__license__ = 'MIT'
__version__ = '1.0.0'
__maintainer__ = 'Andrew Che'
__email__ = 'andrew@neuraldev.io'
__status__ = '{dev_status}'
__date__ = '2018.12.18'
"""timer.py: 

{Description}
"""

import time
from logger import AppLogger

start: float = 0.0

__name__ = "Timer"

logger = AppLogger(__name__)


def timeit(method):
    """
    Decorator to time the execution time benchmark of a function.
    Example:
        Add @timeit to any function to time it.
        Additionally, add logger as a keyword arg to the function to store it in a dictionary.
    Args:
        method: The method to execute.

    Returns:
        A float as the time taken for the execution of the method.
    """

    def timed(*args, **kwargs):
        ts = time.time()
        result = method(*args, **kwargs)
        te = time.time()

        logger.profile(method=method.__name__, duration=(te - ts))
        return result

    return timed


def start_timer():
    global start
    start = time.time()


def end_timer(method: str):
    end = time.time()
    logger.profile(method=method, duration=(end - start))


def time_func(f, *args):
    """
    Call a function f with args and return the time (in seconds) that it took
    to execute.
    """
    tic = time.time()
    f(*args)
    toc = time.time()
    return toc - tic
