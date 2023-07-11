#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Base module for solver functions."""

__name__ = 'qom.solvers.base'
__authors__ = ["Sampreet Kalita"]
__created__ = "2023-07-04"
__updated__ = "2023-07-09"

# dependencies
from decimal import Decimal
from typing import Union
import numpy as np

def get_all_times(params):
    """Function to obtain all times.
    
    Parameters
    ----------
    params : *dict*
        Parameters of the solver. Required options are:
            ========    ====================================================
            key         value
            ========    ====================================================
            't_min'     (*float*) minimum time at which integration starts.
            't_max'     (*float*) maximum time at which integration stops.
            't_dim'     (*int*) number of values from `'t_max'` to `'t_min'`, both inclusive.
            ========    ====================================================

    Returns
    -------
    T : numpy.ndarray
        All times.
    """

    # extract frequently used variables
    t_min = np.float_(params['t_min'])
    t_max = np.float_(params['t_max'])
    t_dim = int(params['t_dim'])

    # calculate times
    _ts = np.linspace(t_min, t_max, t_dim)
    # truncate values
    _step_size = (Decimal(str(t_max)) - Decimal(str(t_min))) / (t_dim - 1)
    _decimals = - _step_size.as_tuple().exponent

    # set times
    return np.around(_ts, _decimals)

def validate_Modes_Corrs(Modes=None, Corrs=None, is_modes_required:bool=False, is_corrs_required:bool=False):
    """Function to validate the modes and correlations.

    At least one of `Modes` or `Corrs` should be non-`None`.
    
    Parameters
    ----------
    Modes : list or numpy.ndarray, optional
        Classical modes with shape `(dim, num_modes)`.
    Corrs : list or numpy.ndarray, optional
        Quadrature quadrature correlations with shape `(dim, 2 * num_modes, 2 * num_modes)`.
    is_modes_required : bool, optional
        Option to set `Modes` as required.
    is_corrs_required : bool, optional
        Option to set `Corrs` as required.

    Returns
    -------
    Modes : numpy.ndarray
        Classical modes with shape `(dim, num_modes)`.
    Corrs : numpy.ndarray
        Quadrature quadrature correlations with shape `(dim, 2 * num_modes, 2 * num_modes)`.
    """

    # handle null
    assert Modes is not None or Corrs is not None, "At least one of `Modes` or `Corrs` should be non-`None`"

    # check requirements
    assert Modes is not None if is_modes_required else True, "Missing required parameter `Modes`"
    assert Corrs is not None if is_corrs_required else True, "Missing required parameter `Corrs`"

    # handle list
    Modes  = np.array(Modes, dtype=np.complex_) if Modes is not None and type(Modes) is list else Modes
    Corrs  = np.array(Corrs, dtype=np.float_) if Corrs is not None and type(Corrs) is list else Corrs

    # validate shapes
    assert len(Modes.shape) == 2 if Modes is not None else True, "`Modes` should be of shape `(dim, num_modes)`"
    assert (len(Corrs.shape) == 3 and Corrs.shape[1] == Corrs.shape[2]) if Corrs is not None else True, "`Corrs` should be of shape `(dim, 2 * num_modes, 2 * num_modes)`"
    assert 2 * Modes.shape[1] == Corrs.shape[1] if Modes is not None and Corrs is not None else True, "Shape mismatch for `Modes` and `Corrs`; expected shapes are `(dim, num_modes)` and `(dim, 2 * num_modes, 2 * num_modes)`"

    return Modes, Corrs

def validate_As_Coeffs(As=None, Coeffs=None):
    """Function to validate the drift matrices and the coefficients.
    
    Parameters
    ----------
    As : list or numpy.ndarray, optional
        Drift matrix.
    Coeffs : list or numpy.ndarray, optional
        Coefficients of the characteristic equation.

    Returns
    -------
    As : numpy.ndarray
        Drift matrix.
    Coeffs : numpy.ndarray
        Coefficients of the characteristic equation.
    """

    # check non-empty
    assert As is not None or Coeffs is not None, "At least one of `As` and `Coeffs` should be non-`None`"

    # if drift matrices are given
    if As is not None:
        # validate drift matrix
        assert isinstance(As, Union[list, np.ndarray].__args__), "`As` should be of type `list` or `numpy.ndarray`"
        # convert to numpy array
        As = np.array(As, dtype=np.float_) if type(As) is list else As
        # validate shape
        assert len(As.shape) == 3 and As.shape[1] == As.shape[2], "`As` should be of shape `(dim_0, 2 * num_modes, 2 * num_modes)`"
    # if coefficients are given
    else:
        # validate coefficients
        assert isinstance(Coeffs, Union[list, np.ndarray].__args__), "`Coeffs` should be of type `list` or `numpy.ndarray`"
        # convert to numpy array
        Coeffs = np.array(Coeffs, dtype=np.float_) if type(Coeffs) is list else Coeffs
        # validate shape
        assert len(Coeffs.shape) == 2, "`Coeffs` should be of shape `(dim_0, 2 * num_modes + 1)`"

    return As, Coeffs

def validate_system(system, required_system_attributes:list):
    """Function to validate the required system attributes for a given solver method.
    
    Parameters
    ----------
    system : :class:`qom.systems.*`
        Instance of the system.
    required_system_attributes : list
        Required system attributes.
    """

    # check required system attributes
    for attribute in required_system_attributes:
        assert getattr(system, attribute, None) is not None, "Missing required system attribute `{}`".format(attribute)