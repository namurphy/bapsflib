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
import numpy as np

from .control_template import hdfMap_control_cl_template


class hdfMap_control_n5700ps(hdfMap_control_cl_template):
    """
    .. Warning::

        In development
    """
    def __init__(self, control_group):
        hdfMap_control_cl_template.__init__(self, control_group)

        # define control type
        self._info['contype'] = 'power'

        # define known command list RE patterns
        self._cl_re_patterns.extend([
        ])

        # populate self.configs
        self._build_configs()

    def _build_configs(self):
        # build configuration dictionaries
        # - assume all subgroups are control device configuration groups
        #   and their names correspond to the configuration name
        # - assume all configurations are active (i.e. used)
        #
        for name in self.sgroup_names:
            # get configuration group
            cgroup = self.group[name]

            # get IP address
            # - ip gets returned as a np.bytes_ string
            #
            ip = cgroup.attrs['IP address']
            ip = ip.decode('utf-8')

            # get device (generator) model
            # - gdevice is returned as a np.bytes_ string
            #
            gdevice = cgroup.attrs['Model Number']
            gdevice = gdevice.decode('utf-8')

            # get initialization command
            init_command = cgroup.attrs['Initialization commands']
            init_command = init_command.decode('utf-8')

            # get command list
            # - cl gets returned as a np.bytes_ string
            # - remove trailing/leading whitespace
            #
            cl = cgroup.attrs['N5700 power supply command list']
            cl = cl.decode('utf-8').splitlines()
            cl = tuple([cls.strip() for cls in cl])

            # get dataset
            dset = self.group[self.construct_dataset_name()]

            # ---- start assigning values to _configs               ----
            # assign non-critical values
            self._configs[name] = {
                'IP address': ip,
                'device model': gdevice,
                'init command': init_command,
            }

            # assign 'command list'
            self._configs[name]['command list'] = cl

            # assign 'dset paths'
            self._configs[name]['dset paths'] = dset.name

            # ---- define 'shotnum'                                 ----
            # initialize
            self._configs[name]['shotnum'] = {
                'dset paths': self._configs[name]['dset paths'],
                'dset field': 'Shot number',
                'shape': dset.dtype['Shot number'].shape,
                'dtype': np.int32
            }

            # ---- define 'state values'                            ----
            # initialize
            pstate = self._construct_state_values_dict(
                name, self._cl_re_patterns)
            self._configs[name]['state values'] = pstate \
                if pstate is not None \
                else self._default_state_values_dict(name)

        # indicate build was successful
        self._build_successful = True

    def _default_state_values_dict(self, config_name):
        # define default dict
        default_dict = {
            'command': {
                'dset paths': self._configs[config_name]['dset paths'],
                'dset field': ('Command index',),
                're pattern': None,
                'command list': np.array(
                    self._configs[config_name]['command list']),
                'shape': (),
            }
        }
        default_dict['command']['cl str'] = \
            default_dict['command']['command list']
        default_dict['command']['dtype'] = \
            default_dict['command']['command list'].dtype

        # return
        return default_dict

    def construct_dataset_name(self, *args):
        """
        Constructs name of dataset containing control state value data.
        """
        return 'Run time list'