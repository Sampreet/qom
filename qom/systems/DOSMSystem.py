#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Module to interface a double-optical single-mechanical system."""

__name__    = 'qom.systems.DOSMSystem'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-12-04'
__updated__ = '2022-04-24'

# dependencies
import logging

# qom modules
from .BaseSystem import BaseSystem

# module logger
logger = logging.getLogger(__name__)

class DOSMSystem(BaseSystem):
    """Class to interface a double-optical single-mechanical system.
        
    Parameters
    ----------
    params : dict
        Parameters for the system.

    .. note:: All the options defined in ``params`` supersede individual method arguments. Refer :class:`qom.systems.BaseSystem` for a complete list of supported options.
    """

    def __init__(self, params, cb_update=None):
        """Class constructor for DOSMSystem."""

        # initialize super class
        super().__init__(params=params, code='DOSMSystem', name='Double-optical Single-mechanical System', num_modes=3, cb_update=cb_update)