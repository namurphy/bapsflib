#!/usr/bin/env python3
#
# This file is part of the bapsflib package, a Python toolkit for the
# BaPSF group at UCLA.
#
# http://plasma.physics.ucla.edu/
#
# Copyright 2017-2018 Erik T. Everson and contributors
#
# License: Standard 3-clause BSD; see "LICENSES/LICENSE.txt" for full
#   license terms and contributor agreement.
#
import codecs
import os
import re

from setuptools import setup, find_packages

# find here
here = os.path.abspath(os.path.dirname(__file__))

# define CLASSIFIERS
CLASSIFIERS = """
Development Status :: 2 - Pre-Alpha
Intended Audience :: Developers
Intended Audience :: Education
Intended Audience :: Science/Research
License :: OSI Approved :: BSD License
Natural Language :: English
Operating System :: MacOS
Operating System :: Microsoft :: Windows
Operating System :: POSIX :: Linux
Programming Language :: Python :: 3
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Topic :: Database
Topic :: Education
Topic :: Scientific/Engineering
Topic :: Scientific/Engineering :: Physics
Topic :: Software Development
Topic :: Software Development :: Libraries :: Python Modules
"""


# ---- Define helpers for version-ing                               ----
# - following 'Single-sourcing the package version' from 'Python
#   Packaging User Guide'
#   https://packaging.python.org/guides/single-sourcing-package-version/
#
def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


# ---- Perform setup                                                ----
setup(
    name='bapsflib',
    version=find_version("bapsflib", "__init__.py"),
    description='A toolkit for handling data collected at BaPSF.',
    license='BSD',
    classifiers=CLASSIFIERS,
    url='https://github.com/rocco8773/bapsflib.git',
    author='Erik T. Everson',
    author_email='eteveson@gmail.com',
    packages=find_packages(),
    install_requires=['h5py>=2.6',
                      'numpy>=1.7',
                      'scipy>=1.0.0'
                      'sphinx>=1.7.2'
                      'sphinx-rtd-theme>=0.3.0'],
    python_requires='>=3.5',
    zip_safe=False,
    include_package_data=True
)
