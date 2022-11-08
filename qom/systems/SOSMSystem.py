#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Module to interface a single-optical single-mechanical system."""

__name__    = 'qom.systems.SOSMSystem'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-12-04'
__updated__ = '2022-09-23'

# dependencies
import logging

# qom modules
from .BaseSystem import BaseSystem

# module logger
logger = logging.getLogger(__name__)

class SOSMSystem(BaseSystem):
    """Class to interface a single-optical single-mechanical system.
        
    Parameters
    ----------
    params : dict, optional
        Parameters for the system.
    cb_update : callable, optional
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is an integer and ``reset`` is a boolean.

    .. note:: All the options defined in ``params`` supersede individual method arguments. Refer :class:`qom.systems.BaseSystem` for a complete list of supported options.
    """

    def __init__(self, params={}, cb_update=None):
        """Class constructor for SOSMSystem."""

        # initialize super class
        super().__init__(params=params, code='SOSMSystem', name='Single-optical Single-mechanical System', num_modes=2, cb_update=cb_update)