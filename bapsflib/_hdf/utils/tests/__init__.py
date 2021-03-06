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
import unittest as ut

from bapsflib._hdf.maps import FauxHDFBuilder
from functools import wraps

from ..file import File


def with_bf(func):
    """
    Context decorator for managing the opening and closing BaPSF HDF5
    Files :class:`bapsflib._hdf.utils.file.File`.  Intended for use on
    test methods.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        with File(self.f.filename,
                  control_path='Raw data + config',
                  digitizer_path='Raw data + config',
                  msi_path='MSI') as bf:
            return func(self, bf, *args, **kwargs)
    return wrapper


class TestBase(ut.TestCase):
    """Base test class for all test classes here."""

    f = NotImplemented   # type: FauxHDFBuilder

    @classmethod
    def setUpClass(cls):
        # create HDF5 file
        super().setUpClass()
        cls.f = FauxHDFBuilder()

    def tearDown(self):
        self.f.reset()

    @classmethod
    def tearDownClass(cls):
        # cleanup and close HDF5 file
        super().tearDownClass()
        cls.f.cleanup()
