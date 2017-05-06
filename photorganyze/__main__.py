#!/usr/bin/env python3

import os.path
import sys

# Photorganyze imports
from photorganyze.lib import config
from photorganyze import file
from photorganyze.lib import util


def organyze(*directories):
    for directory in directories:
        print('+ ', directory)

        try:
            paths = sorted(os.listdir(directory))
        except FileNotFoundError:
            print('   Directory {} is not found'.format(directory))
            continue

        for path in paths:
            full_path = os.path.join(directory, path)
            if os.path.isdir(full_path):
                organyze(full_path)
            else:
                try:
                    file.store(full_path)
                except StopIteration:
                    print('-> ERROR')
                    util.get_logger().exception('Error working with {}'.format(full_path))


def _normalize_path(path):
    path = os.path.expanduser(path)

    return path


def main():
    util.start_logging()
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    options = [o for o in sys.argv[1:] if o.startswith('-')]

    if args:
        input_dirs = tuple(args)
    else:
        input_dirs = config.get_tuple('default_directories', 'input')

    organyze(*(_normalize_path(d) for d in input_dirs))


if __name__ == '__main__':
    main()
