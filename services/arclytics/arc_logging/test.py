# -*- coding: utf-8 -*-

from arc_logging import AppLogger

logger = AppLogger(__name__)


def log_testing():
    logger.info('Hello World!')


def divide_by_zero():
    try:
        1 / 0
    except Exception:
        logger.error("Here's what you did wrong")
        logger.exception('Woops')


if __name__ == "__main__":
    log_testing()
    divide_by_zero()
