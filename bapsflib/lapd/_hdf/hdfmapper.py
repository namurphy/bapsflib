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
# TODO: make a pickle save for the hdfMap...
#       Then, if a user adds additional mappings for a specific HDF5
#       file, those can be maintained
#
#
# Some hierarchical nomenclature for the digital acquisition system
#     DAQ       -- refers to the whole system, all digitizers, the
#                  computer system, etc.
#     digitizer -- a device that collects data, e.g. the main digitizer
#                  in the LaPD room, an oscilloscope, etc.
#     adc       -- analog-digital converter, the element of a digitizer
#                  that does the analog-to-digital conversion, e.g.
#                  the SIS 3302, SIS 3305, etc.
#     board     -- refers to a cluster of channels on an adc
#     channel   -- the actual hook-up location on the adc
#
import os
import h5py
import warnings

from typing import (Dict, Union)
from warnings import warn

from bapsflib._hdf_mappers.controls import HDFMapControls
from bapsflib._hdf_mappers.controls.templates import (
    HDFMapControlTemplate, HDFMapControlCLTemplate)
from bapsflib._hdf_mappers.map_digitizers import hdfMap_digitizers
from bapsflib._hdf_mappers.map_digitizers.digi_template import \
    HDFMapDigiTemplate
from bapsflib._hdf_mappers.msi import HDFMapMSI
from bapsflib._hdf_mappers.msi.templates import HDFMapMSITemplate


# define type aliases
ControlMap = Union[HDFMapControlTemplate, HDFMapControlCLTemplate]
DigiMap = HDFMapDigiTemplate
MSIMap = HDFMapMSITemplate


class hdfMap(object):
    """
    Constructs a complete file mapping of :obj:`hdf_obj` that is
    utilized by :class:`bapsflib.lapd.files.File` to manipulate and
    read data out of the HDF5 file.

    The following classes are leveraged to construct the mappings:

    * :class:`~.controls.map_controls.HDFMapControls`.
    * :class:`~.map_digitizers.map_digis.hdfMap_digitizers`.
    * :class:`~.msi.map_msi.HDFMapMSI`.
    """
    # MSI stuff
    _MSI_GNAME = 'MSI'
    """Name of the MSI HDF5 group."""

    # Data and Config stuff
    _DATA_GNAME = 'Raw data + config'
    """Name of the DATA HDF5 group"""

    def __init__(self, hdf_obj, silent=False):
        """
        :param hdf_obj: the HDF5 file object
        :type hdf_obj: :class:`h5py.File`
        """
        # store an instance of the HDF5 object for hdfMap
        self.__hdf_obj = hdf_obj

        # check if hdf_obj was generated by the LaPD
        # TODO: CAN I SETUP AS WARN AND STILL ALLOW ACCESS WHEN NOT LAPD
        if not self.is_lapd_hdf:
            raise ValueError(
                'HDF5 file ({}) was'.format(self.__hdf_obj.filename)
                + ' not generated by the LaPD')

        # initialize attributes dict
        self._attrs = {
            self._MSI_GNAME: {},
            self._DATA_GNAME: {}
        }

        # populate attributes
        if self.has_msi_group:
            # populate 'MSI' key
            self._attrs[self._MSI_GNAME].update(
                self.__hdf_obj[self._MSI_GNAME].attrs)

            # decode all string values
            for key, val in self._attrs[self._MSI_GNAME].items():
                if isinstance(val, bytes):
                    self._attrs[self._MSI_GNAME][key] = \
                        val.decode('utf-8')
        if self.has_data_group:
            # populate 'Raw data + config' key
            self._attrs[self._DATA_GNAME].update(
                self.__hdf_obj[self._DATA_GNAME].attrs)

            # decode all string values
            for key, val in self._attrs[self._DATA_GNAME].items():
                if isinstance(val, bytes):
                    self._attrs[self._DATA_GNAME][key] = \
                        val.decode('utf-8')

        # attach the mapping dictionaries
        warn_filter = "ignore" if silent else "default"
        with warnings.catch_warnings():
            warnings.simplefilter(warn_filter)
            self.__attach_msi()
            self.__attach_digitizers()
            self.__attach_controls()
            self.__attach_unknowns()

    def __repr__(self):
        filename = self.__hdf_obj.filename
        if isinstance(filename, bytes):
            filename = filename.decode('utf-8')
        filename = os.path.basename(filename)
        rstr = ("<" + self.__class__.__name__
                + " of HDF5 file '" + filename + "'>")
        return rstr

    @property
    def attrs(self):
        """Dictionary of the 'MSI' and 'Raw data + config' attributes"""
        return self._attrs

    @property
    def has_msi_group(self):
        """
        :return: :code:`True` if MSI group (:attr:`msi_gname`) is
            detected
        :rtype: bool
        """
        # determine if there is a MSI group
        detected_msi = True if self._MSI_GNAME in self.__hdf_obj \
            else False

        # warn
        if not detected_msi:
            warn('No {} group'.format(self._MSI_GNAME)
                 + ' found in {}'.format(self.__hdf_obj.filename))

        # return
        return detected_msi

    @property
    def has_data_group(self):
        """
        :return: :code:`True` if data group (:attr:`data_gname`) group
            is detected
        :rtype: bool
        """
        # determine if there is a 'Raw data + config' group
        detected_data = True if self._DATA_GNAME in self.__hdf_obj \
            else False

        # warn
        if not detected_data:
            warn('No {} group'.format(self._DATA_GNAME)
                 + ' found in {}'.format(self.__hdf_obj.filename))

        # return
        return detected_data

    @property
    def has_data_run_sequence(self):
        """
        :return: :code:`True` if the 'Data run sequence/' group is found
            in the data group
        :rtype: bool
        """
        # TODO: update when 'Data run squence/' is incorporated
        return False

    @property
    def has_msi_diagnostics(self):
        """
        :return: :code:`True` if any known MSI diagnostics are
            discovered in the MSI group (i.e. :attr:`msi` is not empty)
        :rtype: bool
        """
        if len(self.__msi) == 0:
            has_diagnostics = False
        else:
            has_diagnostics = True
        return has_diagnostics

    @property
    def has_digitizers(self):
        """
        :return: :code:`True` if any known digitizers are discovered in
            the data group (i.e :attr:`digitizers` is not empty)
        :rtype: bool
        """
        if len(self.__digitizers) == 0:
            has_digis = False
        else:
            has_digis = True
        return has_digis

    @property
    def has_controls(self):
        """
        :return: :code:`True` if known control devices are discovered
            in the data group (i.e. :attr:`controls` is not empty)
        :rtype: bool
        """
        if len(self.__controls) == 0:
            has_controls = False
        else:
            has_controls = True
        return has_controls

    @property
    def has_unknowns(self):
        """
        :return: :code:`True` if there are any subgroups in the data
            group that are not known by the mapping constructors.
        """
        has_unknowns = False if len(self.__unknowns) == 0 else True
        return has_unknowns

    def __attach_msi(self):
        """
        Attaches a dictionary (:attr:`__msi`) containing all MSI
        diagnostic mapping objects constructed by
        :class:`~.msi.map_msi.HDFMapMSI`.
        """
        if self.has_msi_group:
            self.__msi = HDFMapMSI(self.__hdf_obj[self._MSI_GNAME])
        else:
            self.__msi = {}

    @property
    def msi(self) -> Dict[str, MSIMap]:
        """
        :return: A dictionary containing all MSI diagnostic mappings
            objects.
        :rtype: dict

        For example, to retrieve mappings of LaPD's Magnetic field one
        would call::

            fmap = hdfMap(file_obj)
            bmap = fmap.msi['Magnetic field']
        """
        return self.__msi

    def __attach_digitizers(self):
        """
        Attaches a dictionary (:attr:`__digitizers`) containing all
        digitizer mapping objects constructed by
        :class:`~.map_digitizers.map_digis.hdfMap_digitizers`.
        """
        if self.has_data_group:
            self.__digitizers = hdfMap_digitizers(
                self.__hdf_obj[self._DATA_GNAME])
        else:
            self.__digitizers = {}

    @property
    def digitizers(self) -> Dict[str, DigiMap]:
        """
        :return: A dictionary containing all digitizer mapping objects.
        :rtype: dict

        For example, to retrieve mappings of digitizer
        :code:`'SIS 3301'` one would call::

            fmap = hdfMap(file_obj)
            dmap = fmap.digitizers['SIS 3301']
        """
        return self.__digitizers

    def __attach_controls(self):
        """
        Attaches a dictionary (:attr:`__controls`) containing all
        control device mapping objects constructed by
        :class:`~.controls.map_controls.HDFMapControls`.
        """
        if self.has_data_group:
            self.__controls = HDFMapControls(
                self.__hdf_obj[self._DATA_GNAME])
        else:
            self.__controls = {}

    @property
    def controls(self) -> Dict[str, ControlMap]:
        """
        :return: A dictionary containing all control device mapping
            objects.
        :rtype: dict

        For example, to retrieve mappings of the control device
        :code:`'6K Compumotor'` one would call::

            fmap = hdfMap(file_obj)
            mmap = fmap.controls['6K Compumotor']
        """
        return self.__controls

    def __attach_unknowns(self):
        """
        Attaches a list (:attr:`__unknowns`) with the subgroup names of
        all the subgroups in the data group (:attr:`data_gname`) that
        are unknown to the mapping constructors.
        """
        # add unknowns (Groups & Datasets) from levels
        # 1. root -- '/'
        # 2. MSI group -- '/MSI'
        # 3. data group -- '/Raw data + config'
        self.__unknowns = []

        # scan through root
        for item in self.__hdf_obj:
            if item not in [self._MSI_GNAME, self._DATA_GNAME]:
                self.__unknowns.append(self.__hdf_obj[item].name)

        # scan through MSI group
        if self.has_msi_group:
            for item in self.__hdf_obj[self._MSI_GNAME]:
                if item not in self.msi:
                    self.__unknowns.append(
                        self.__hdf_obj[self._MSI_GNAME][item].name)

        # scan through data group
        if self.has_data_group:
            dknowns = list(self.digitizers) + list(self.controls)
            for item in self.__hdf_obj[self._DATA_GNAME]:
                if item not in dknowns:
                    self.__unknowns.append(
                        self.__hdf_obj[self._DATA_GNAME][item].name)

    @property
    def unknowns(self):
        """
        :return: A list containing all the subgroup names for the
            subgroups in the data group (:attr:`data_gname` that are
            unknown to the mapping constructor.
        :rtype: list
        """
        return self.__unknowns

    @property
    def is_lapd_hdf(self):
        """
        :return: :code:`True` if the HDF5 file was generated by the LaPD
        :rtype: bool
        """
        is_lapd = True \
            if 'LaPD HDF5 software version' in self.__hdf_obj.attrs \
            else False

        return is_lapd

    @property
    def hdf_version(self):
        """
        :return: the LaPD DAQ Software version number used to generated
            the HDF5 file ('' if NOT LaPD generated)
        :rtype: str
        """
        vers = self.__hdf_obj.attrs[
            'LaPD HDF5 software version'].decode('utf-8')

        return vers

    @property
    def main_digitizer(self):
        """
        :return: the mapping object for the digitizer that is assumed
            to be the 'main digitizer' in :attr:`digitizers`

        The main digitizer is determine by scanning through the local
        tuple :const:`possible_candidates` that contains a
        hierarchical list of digitizers. The first digitizer found is
        assumed to be the 'main digitizer'.::

            possible_candidates = ('SIS 3301', 'SIS crate')
        """
        # possible_candidates is a hierarchical tuple of all digitizers
        # such that the first found digitizer is assumed to be the main
        # digitizer
        possible_candidates = ('SIS 3301', 'SIS crate')
        digi = None
        try:
            for key in possible_candidates:
                if key in self.__digitizers:
                    digi = self.__digitizers[key]
                    break
        except TypeError:
            # catch if __digitizers is None
            pass

        return digi

    @property
    def run_info(self):
        """Dictionary of experimental run info."""
        # initialize
        run_info = {
            'run name': '',
            'run description': '',
            'run status': '',
            'run date': ''
        }

        # assign values
        for key, val in self._attrs[self._DATA_GNAME].items():
            if key == 'Data run':
                run_info['run name'] = val
            elif key == 'Description':
                run_info['run description'] = val
            elif key == 'Status':
                run_info['run status'] = val
            elif key == 'Status date':
                run_info['run date'] = val

        # return
        return run_info

    @property
    def exp_info(self):
        """Dictionary of experiment info"""
        # initialize
        exp_info = {
            'investigator': '',
            'exp name': '',
            'exp description': '',
            'exp set name': '',
            'exp set description': ''
        }

        # assign values
        for key, val in self._attrs[self._DATA_GNAME].items():
            if key == 'Investigator':
                exp_info['investigator'] = val
            elif key == 'Experiment name':
                exp_info['exp name'] = val
            elif key == 'Experiment description':
                exp_info['exp description'] = val
            elif key == 'Experiment set name':
                exp_info['exp set name'] = val
            elif key == 'Experiment set description':
                exp_info['exp set description'] = val

        # return
        return exp_info
