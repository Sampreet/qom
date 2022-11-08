#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Module to interface a single-optical double-mechanical system."""

__name__    = 'qom.systems.SODMSystem'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-12-04'
__updated__ = '2022-09-23'

# dependencies
import logging

# qom modules
from .BaseSystem import BaseSystem

# module logger
logger = logging.getLogger(__name__)

class SODMSystem(BaseSystem):
    """Class to interface a single-optical double-mechanical system.
        
    Parameters
    ----------
    params : dict, optional
        Parameters for the system.
    cb_update : callable, optional
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is an integer and ``reset`` is a boolean.

    .. note:: All the options defined in ``params`` supersede individual method arguments. Refer :class:`qom.systems.BaseSystem` for a complete list of supported options.
    """

    def __init__(self, params={}, cb_update=None):
        """Class constructor for SODMSystem."""

        # initialize super class
        super().__init__(params=params, code='SODMSystem', name='Single-optical Double-mechanical System', num_modes=3, cb_update=cb_update)