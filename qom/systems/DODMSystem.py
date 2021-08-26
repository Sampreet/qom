#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Module to interface a double-optical double-mechanical system."""

__name__    = 'qom.systems.DODMSystem'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-12-04'
__updated__ = '2021-08-26'

# dependencies
import logging

# qom modules
from .BaseSystem import BaseSystem

# module logger
logger = logging.getLogger(__name__)

class DODMSystem(BaseSystem):
    """Class to interface a double-optical double-mechanical system.
        
    Parameters
    ----------
    params : dict
        Parameters for the system.
    cb_update : callable, optional
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is an integer and ``reset`` is a boolean.

    .. note:: All the options defined in ``params`` supersede individual function arguments. Refer :class:`qom.systems.BaseSystem` for a complete list of supported options.
    """

    def __init__(self, params, cb_update=None):
        """Class constructor for DODMSystem."""

        # initialize super class
        super().__init__(params=params, code='dodm_system', name='Double-optical Double-mechanical System', num_modes=4, cb_update=cb_update)