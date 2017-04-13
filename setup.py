"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
import os.path

# Read some info from the photorganyze package itself
import photorganyze

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the relevant file
with open(os.path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as fid:
    long_description = fid.read()

setup(
    name=photorganyze.__name__,

    # Versions should comply with PEP440.  For a discussion on
    # single-sourcing the version across setup.py and the project
    # code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=photorganyze.__version__,

    description=[s.replace('\n', ' ') for s in photorganyze.__doc__.strip().split('\n\n')][0],
    long_description=long_description,

    # The project's main homepage.
    url='https://photorganyze.readthedocs.io/',

    # Author details
    author=photorganyze.__author__,
    author_email='geirarne@gmail.com',

    # Choose your license
    license='',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 3',
    ],

    # What does your project relate to?
    keywords='photo', 'backup', 'archive'

    # Using find_packages to find all subpackages in photorganyze. This is
    # done explicitly because find_packages uses a VERY long time to
    # traverse the directory tree of data (and the exclude option to
    # find_packages only excludes after doing a full traverse).
    packages=['photorganyze.' + p for p in find_packages(where='photorganyze')],
    # packages=['photorganyze', 'photorganyze.lib'],

    # List run-time dependencies here.  These will be installed by pip
    # when your project is installed. For an analysis of
    # "install_requires" vs pip's requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['pillow', 'imagehash'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    # extras_require={
    #     'dev': ['check-manifest'],
    #     'test': ['coverage'],
    # },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    # package_data={
    #     'sample': ['package_data.dat'],
    # },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],

    # To provide executable scripts, use entry points in preference to
    # the "scripts" keyword. Entry points provide cross-platform
    # support and allow pip to create the appropriate form of
    # executable for the target platform.
    entry_points={
        'console_scripts': [
            'photorganyze=photorganyze.__main__:main',
        ],
        'gui_scripts': [
        ],
    },
)
