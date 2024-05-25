# Copyright © 2024 by IoT Spectator. All rights reserved.

"""Log Helper provides the common log configuration and format."""

import pathlib
import logging
import logging.handlers

from typing import Optional

# The maximum size of a log file. When a log file is larger than
# the number, the log will be rotated.
_LOG_FILE_MAX_SIZE = 100 * 1024 * 1024  # 100MB

# Default log format to ensure all the log messages have the same format.
_LOG_FORMATTER = logging.Formatter("%(asctime)s [%(name)s] [%(levelname)s] %(message)s")

# Global variables for logger setup and only for internal use.
# Do not call these variables.
_log_file = None
_log_level = logging.INFO
_console_handler = None
_file_handler = None


def setup_logger(
    level=None, filename: Optional[pathlib.Path] = None, console: bool = False
):
    """Configure the logger.

    This method should be called in the top level of a Spectator process.

    Parameters
    ----------
    level:
        The log level for the whole process.
    filename: pathlib.Path
        Set this parameter if log to a file is preferred.
    console: bool
        Set this parameter if log to console is preferred.
    """
    if level:
        global _log_level
        _log_level = level

    if console:
        global _console_handler
        _console_handler = logging.StreamHandler()
        _console_handler.setFormatter(_LOG_FORMATTER)

    if filename:
        global _file_handler
        _file_handler = logging.handlers.RotatingFileHandler(
            filename=filename, maxBytes=_LOG_FILE_MAX_SIZE, backupCount=5
        )
        _file_handler.setFormatter(_LOG_FORMATTER)


def get_logger(name: str, level=None) -> logging.Logger:
    """Get a logger.

    For each module, class, or function, call this function to get a logger.

    Parameters
    ----------
    name: str
        A name for identifying the log message.
    level:
        Set the log level for the specific logger.
    """
    if _console_handler is None and _file_handler is None:
        raise RuntimeError(f"{name} is not initialized!")

    logger = logging.getLogger(name)
    if level:
        logger.setLevel(level)
    else:
        logger.setLevel(_log_level)

    if _console_handler:
        logger.addHandler(_console_handler)

    if _file_handler:
        logger.addHandler(_file_handler)

    return logger
