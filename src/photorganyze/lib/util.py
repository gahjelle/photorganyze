"""Photorganyze utility functions

Description:
------------

This module provides the boilerplate code necessary for starting a
script. In particular handling of command line arguments and default
options including --help are done.
"""

# Standard library imports
import atexit
import logging
import os.path
import sys
from datetime import datetime

# Photorganyze imports
from photorganyze.lib import config

## Start time of script, used when calculating run-time.
_STARTTIME = datetime.now()


@atexit.register
def runtime():
    """Log the run-time of the script

    Calculates the running time of the script and logs it.
    """
    runtime = (datetime.now() - _STARTTIME).total_seconds()
    print(f"Finish {get_program_name()} in {runtime} seconds")


def get_program_name():
    """Get the name of the running program

    Returns:
        String trying to be similar to how the user called the program.
    """
    program_name = sys.argv[0]
    if not program_name.startswith("./"):
        program_name = os.path.basename(program_name)
    return program_name


def get_option(key):
    """Get the value of the command line option specified with key

    If the option is specified several times, only returns the last value. If the option is not specified, None is
    returned.

    Args:
        key (String):  The option (with leading dashes).

    Returns:
        String: The value of the option. None if the option is not specified.
    """
    args = [o for o in sys.argv if o.startswith(key + "=")]

    if args:
        return args[-1].split("=", maxsplit=1)[-1]
    else:
        return None


def start_logging():
    logger = logging.getLogger(get_program_name())
    file_handler = logging.FileHandler(config.get_path("file_name", "log"))
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(file_handler)


def get_logger():
    return logging.getLogger(get_program_name())
