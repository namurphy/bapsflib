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
import warnings

import numpy as np

from warnings import warn

from .control_template import hdfMap_control_cl_template


class hdfMap_control_n5700ps(hdfMap_control_cl_template):
    """
    Mapping module for control device 'N5700_PS'.

    Simple group structure looks like:

    .. code-block:: none

        +-- N5700_PS
        |   +-- Run time list
        |   +-- nsconf_<descr>
        |   |   +--

    """
    def __init__(self, control_group):
        """
        :param control_group: the HDF5 control device group
        :type control_group: :class:`h5py.Group`
        """
        # initialize
        hdfMap_control_cl_template.__init__(self, control_group)

        # define control type
        self._info['contype'] = 'power'

        # define known command list RE patterns
        self._cl_re_patterns.extend([
            r'(?P<VOLT>(\bSOURCE:VOLTAGE:LEVEL\s)'
            + r'(?P<VAL>(\d+\.\d*|\.\d+|\d+\b)))',
        ])

        # populate self.configs
        self._build_configs()

    def _build_configs(self):
        """Builds the :attr:`configs` dictionary."""
        # assume build is successful
        # - alter if build fails
        #
        self._build_successful = True

        # check there are configurations to map
        if len(self.sgroup_names) == 0:
            warn(self.name + ": has no mappable configurations")
            self._build_successful = False
            return

        # build configuration dictionaries
        # - assume every sub-group represents a unique configuration
        #   to the control device
        # - the name of each sub-group is used as the configuration
        #   name
        # - assume all configurations are active (i.e. used)
        #
        for name in self.sgroup_names:
            # get configuration group
            cong = self.group[name]

            # get dataset
            try:
                dset = self.group[self.construct_dataset_name()]
            except KeyError:
                warn_str = ("Dataset '" + self.construct_dataset_name()
                            + "' not found for control device '"
                            + self.name + "' configuration group '"
                            + name + "'")
                warn(warn_str)
                self._build_successful = False
                return

            # initialize _configs
            self._configs[name] = {}

            # ---- define general info values                       ----
            pairs = [
                ('IP address', 'IP address'),
                ('power supply device', 'Model Number'),
                ('initial state', 'Initialization commands'),
                ('command list', 'N5700 power supply command list')
            ]
            for pair in pairs:
                try:
                    # get attribute value
                    val = cong.attrs[pair[1]]

                    # condition value
                    if pair[0] == 'command list':
                        # - val gets returned as a np.bytes_ string
                        # - split line returns
                        # - remove trailing/leading whitespace
                        #
                        val = val.decode('utf-8').splitlines()
                        val = tuple([cls.strip() for cls in val])
                    else:
                        # pair[0] in ('IP address',
                        #             'power supply device',
                        #             'initial state'):
                        # - val is a np.bytes_ string
                        #
                        val = val.decode('utf-8')

                    # assign val to _configs
                    self._configs[name][pair[0]] = val
                except KeyError:
                    self._configs[name][pair[0]] = None
                    warn_str = ("Attribute '" + pair[1]
                                + "' not found in control device '"
                                + self.name + "' configuration group '"
                                + name + "'")
                    if pair[0] != 'command list':
                        warn_str += ", continuing with mapping"
                        warn(warn_str)
                    else:
                        warn(warn_str)
                        self._build_successful = False
                        return

            # ---- define 'dset paths'                              ----
            self._configs[name]['dset paths'] = dset.name

            # ---- define 'shotnum'                                 ----
            # initialize
            self._configs[name]['shotnum'] = {
                'dset paths': self._configs[name]['dset paths'],
                'dset field': ('Shot number',),
                'shape': dset.dtype['Shot number'].shape,
                'dtype': np.int32
            }

            # ---- define 'state values'                            ----
            # catch and suppress warnings only for initialization
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                try:
                    sv_dict = self._construct_state_values_dict(
                        name, self._cl_re_patterns)
                except KeyError:
                    sv_dict = {}

            # initialize
            self._configs[name]['state values'] = sv_dict \
                if bool(sv_dict) \
                else self._default_state_values_dict(name)

    def _default_state_values_dict(self, config_name):
        # define default dict
        default_dict = {
            'command': {
                'dset paths': self._configs[config_name]['dset paths'],
                'dset field': ('Command index',),
                're pattern': None,
                'command list':
                    self._configs[config_name]['command list'],
                'cl str':
                    self._configs[config_name]['command list'],
                'shape': (),
            }
        }
        default_dict['command']['dtype'] = \
            np.array(default_dict['command']['command list']).dtype

        # return
        return default_dict

    def construct_dataset_name(self, *args):
        """
        Constructs name of dataset containing control state value data.
        """
        return 'Run time list'
