#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Module to interface a single-optical single-mechanical system."""

__name__    = 'qom.systems.SOSMSystem'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-12-04'
__updated__ = '2021-09-03'

# dependencies
import logging
import numpy as np

# qom modules
from .BaseSystem import BaseSystem

# module logger
logger = logging.getLogger(__name__)

class SOSMSystem(BaseSystem):
    """Class to interface a single-optical single-mechanical system.
        
    Parameters
    ----------
    params : dict
        Parameters for the system.
    cb_update : callable, optional
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is an integer and ``reset`` is a boolean.

    .. note:: All the options defined in ``params`` supersede individual function arguments. Refer :class:`qom.systems.BaseSystem` for a complete list of supported options.
    """

    def __init__(self, params, cb_update=None):
        """Class constructor for SOSMSystem."""

        # initialize super class
        super().__init__(params=params, code='dodm_system', name='Double-optical Double-mechanical System', num_modes=2, cb_update=cb_update)

        # update attributes
        self.required_funcs.update({
            'get_optical_stability_zone': ['get_ivc', 'get_mode_rates', 'get_oss_args']
        })
        self.required_params.update({
            'get_optical_stability_zone': []
        })

    def get_optical_stability_zone(self, solver_params: dict):
        """Method to obtain the optical stability zone.

        Parameters
        ----------
        solver_params : dict
            Parameters for the solver.

        Returns
        -------
        osz : list
            Stability zone indicator of the optical steady state. The indicator codes are: 
                ==========  ================================================
                value       meaning
                ==========  ================================================
                1           one stable root.
                2           one unstable root.
                3           one unstable and two stable roots.
                4           one stable and two unstable roots.
                ==========  ================================================
        """

        # validate required functions
        assert self.validate_required_funcs(func_name='get_optical_stability_zone', mode='verbose') is True, 'Missing required predefined functions'

        # get mean optical occupancies
        N_o, _ = self.get_mean_optical_occupancies()

        # get Routh-Hurwitz criteria for stability
        counts, _ = self.get_rhc_count_stationary()

        # get stationary optical modes
        modes, _ = self.get_modes_corrs_stationary()
        n_o = np.real(np.conjugate(modes[0]) * modes[0])

        # initialize zone
        osz = len(N_o)

        # if single root
        if osz == 1:
            # if RHC unstable and root is away to numerical steady state
            if counts > 0 or np.abs(n_o - N_o[0]) > 1e-6:
                print(counts)
                osz = 2  

        # if three roots
        if osz == 3:
            # count roots away from numerical steady state
            count_away = sum([1 if np.abs(n_o - n) > 1e-6 else 0 for n in N_o]) 

            # if RHC unstable or all roots are away from numerical steady state
            if counts > 0 or count_away == 3:
                osz = 4 

        return osz