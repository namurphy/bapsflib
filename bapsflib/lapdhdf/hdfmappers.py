# This file is part of the bapsflib package, a Python toolkit for the
# BaPSF group at UCLA.
#
# http://plasma.physics.ucla.edu/
#
# Copyright 2017 Erik T. Everson and contributors
#
# License:
#
# TODO: make a pickle save for the hdfMap...
#       Then, if a user adds additional mappings for a specific HDF5
#       file, those can be maintained
#
"""
Some hierarchical nomenclature for the digital acquisition system
    DAQ       -- refers to the whole system, all digitizers, the
                 computer system, etc.
    digitizer -- a device that collects data, e.g. the main digitizer
                 in the LaPD room, an oscilloscope, etc.
    adc       -- analog-digital converter, the element of a digitizer
                 that does the analog-to-digital conversion, e.g.
                 the SIS 3302, SIS 3305, etc.
    board     -- refers to a cluster of channels on an adc
    channel   -- the actual hook-up location on the adc
"""
import h5py


class hdfMap(object):
    """
        Template for all HDF Mapping Classes

        Class Attributes
        ----------------
            msi_group  -- str -- name of MSI group
            data_group -- str -- name of data group

        Object Attributes
        -----------------
            hdf_version  -- str
                - string representation of the version number
                  corresponding the the LaPD HDF Software version used
                  to generate the HDF5 file
            msi_diagnostic_groups -- [str]
                - list of the group names for each diagnostic recorded
                  in the MSI group
            sis_group -- str
                - SIS group name which contains all the DAQ recorded
                  data and associated DAQ configuration
            sis_crates -- [str]
                - list of SIS crates (digitizers) available to record
                  data
            data_configs -- {}
                - dict containing key parameters associated with the
                  crate configurations
                - dict is constructed using method build_data_configs

        Methods
        -------
            sis_path
                - returns the HDF internal absolution path to the
                  sis_group
            build_data_configs
                - used to construct the data_configs attribute
            parse_config_name
            is_config_active
            __config_crates
            __crate_info
            __find_crate_connections

    """
    # MSI stuff
    msi_group = 'MSI'

    # Data and Config stuff
    data_group = 'Raw data + config'
    possible_digitizer_groups = {'main': ['SIS 3301', 'SIS crates'],
                                 'aux': ['LeCroy', 'Waveform']}
    possible_motion_groups = ['6K Compumotor', 'NI_XZ']
    possible_dsequence_groups = ['Data run sequence']

    def __init__(self, hdf_obj):
        self.__hdf_obj = hdf_obj
        self.__attach_msi()

        self.msi_diagnostic_groups = []
        self.sis_group = ''
        self.sis_crates = []
        self.data_configs = {}

    def __attach_msi(self):
        if self.msi_group in self.__hdf_obj.keys():
            self.msi = hdfMap_msi(self.__hdf_obj[self.msi_group])
        else:
            self.msi = None

    @property
    def is_lapd_hdf(self):
        is_lapd = False
        for key in self.__hdf_obj.attrs.keys():
            if 'lapd' in key.casefold():
                is_lapd = True
                break

        return is_lapd

    @property
    def hdf_version(self):
        vers = ''
        for key in self.__hdf_obj.attrs.keys():
            if 'version' in key.casefold():
                vers = self.__hdf_obj.attrs[key].decode('utf-8')
                break

        return vers

    @property
    def sis_path(self):
        return self.data_group + '/' + self.sis_group

    @property
    def main_data(self):
        """
        Return instance of info for the main data group. e.g.
            self.data['SIS 3301']
            or
            self.data['SIS crate']

        :return:
        """
        return None

    def build_data_configs(self, group):
        pass


class hdfMap_msi(object):
    def __new__(cls, msi_group):
        obj = object.__new__(cls)
        obj.__possible_diagnostic_groups = ['Discharge', 'Gas pressure',
                                            'Heater',
                                            'Interferometer array',
                                            'Magnetic field']
        obj.found_diagnostics = []
        for key in msi_group.keys():
            obj.found_diagnostics.append(key)

        return obj

    def __init__(self, msi_group):
        pass
