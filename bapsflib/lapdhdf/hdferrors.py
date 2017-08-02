# This file is part of the bapsflib package, a Python toolkit for the
# BaPSF group at UCLA.
#
# http://plasma.physics.ucla.edu/
#
# Copyright 2017 Erik T. Everson and contributors
#
# License:
#


class Error(Exception):
    """
        Base class for exceptions in the lapdhdf module.
    """
    pass


class NotHDFFileError(Error):
    """
        Exception raised if passed object is not and h5py.File
        object.
    """

    def __init__(self):
        print('Object is not of h5py.File type.')


class NotLaPDHDFError(Error):
    """
        Exception raised if passed object is not and h5py.File
        object.
    """
    def __init__(self):
        print('HDF5 Files was not generated by LaPD Systems.')


class NoMSIError(Error):
    """
        Exception raised if no MSI group is detected in the opened
        HDF5 file.
    """
    pass
