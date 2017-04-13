"""Access the photorganyze configuration file.

"""
from configparser import ConfigParser, ExtendedInterpolation
from functools import wraps
import os.path
import sys

## Base directory of the Photorganyze installation
_BASE_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__),
                                          '..', '..'))

## Prioritized list of Photorganyze config filenames
_CONFIG_FILENAMES = ('photorganyze.conf', 'photorganyze_local.conf')

## Possible locations of Photorganyze config files
_CONFIG_LOCATIONS = ('.', os.path.expanduser('~'), os.path.join(_BASE_DIR, 'config'))

## Photorganyze configuration as a ConfigParser, loaded when needed
_CONFIG = ConfigParser(interpolation=ExtendedInterpolation())


def ensure_config(func):
    """Make sure config is loaded before running function.

    Args:
        func:  Function to execute

    Returns:
        function: Decorated function that ensures that config is loaded before executing.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not _CONFIG.sections():
            load_config()
        return func(*args, **kwargs)

    return wrapper


@ensure_config
def get(key, section, fallback=None, cfg=_CONFIG):
    return cfg[section].get(key, fallback)


@ensure_config
def get_int(key, section, fallback=0, cfg=_CONFIG):
    return cfg[section].getint(key, fallback)


@ensure_config
def get_float(key, section, fallback=0, cfg=_CONFIG):
    return cfg[section].getfloat(key, fallback)


@ensure_config
def get_boolean(key, section, fallback=False, cfg=_CONFIG):
    return cfg[section].getboolean(key, fallback)


@ensure_config
def get_list(key, section, fallback=None, cfg=_CONFIG):
    config_str = get(key, section, fallback=None, cfg=cfg)
    if config_str is None:
        return fallback
    return config_str.replace(',', ' ').split()

@ensure_config
def get_tuple(key, section, fallback=None, cfg=_CONFIG):
    return tuple(get_list(key, section, fallback=fallback, cfg=cfg))

@ensure_config
def get_path(key, section, fallback='', cfg=_CONFIG, **vars_):
    path = get(key, section, fallback=fallback, cfg=cfg)
    if path and '~' in path:
        path = os.path.expanduser(path)

    return path

@ensure_config
def get_sections(cfg=_CONFIG):
    return cfg.sections()


def load_config():
    """Load configuration from config-files.
    """
    for config_path in _config_paths():
        _CONFIG.read(config_path)


def _config_paths(filenames=_CONFIG_FILENAMES):
    for filename in filenames:
        for location in _CONFIG_LOCATIONS:
            path = os.path.join(location, filename)
            if os.path.exists(path):
                yield path
                break
