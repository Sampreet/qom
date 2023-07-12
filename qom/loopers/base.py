#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module to interface loopers."""

__name__ = 'qom.loopers.base'
__authors__ = ["Sampreet Kalita"]
__created__ = "2020-12-21"
__updated__ = "2023-07-12"

# dependencies
from decimal import Decimal
from typing import Union
import copy
import logging
import numpy as np
import time

# qom dependencies
from ..io import Updater

# TODO: Support for gradients at specific indices.

class BaseLooper():
    """Class to interface loopers.

    Initializes ``func``, ``params``, ``axes``, ``results`` and ``updater``.

    Parameters
    ----------
    func : callable
        Function to loop, formatted as ``func(system_params)``, where ``system_params`` is a dictionary of the updated parameters for the system for that iteration of the looper.
    params : dict
        Parameters of the looper containing the key ``'X'``, each with the keys ``'var'`` and ``'val'`` (or ``'min'``, ``'max'`` and ``'dim'``) for the name of the parameter to loop and its corresponding values (or minimum and maximum values along with dimension). Refer to **Notes** below for all available options.
    params_system : dict
        Parameters of the system. If not provided, new keys are created for the looper variables.
    cb_update : callable
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is a float and ``reset`` is a boolean.
    parallel : bool
        Option to format outputs when running in parallel.
    p_index : int
        Index of the process.
    p_start : float
        Time at which the process was started. If not provided, the value is initialized to current time.

    Notes
    -----
        The ``params`` dictionary currently supports the following keys:
            ====================    ====================================================
            key                     value
            ====================    ====================================================
            'show_progress'         (*bool*) option to display the progress for the looper. Default is ``False``.
            'file_path_prefix'      (*str*) prefix for the file path to save the looper results. If not provided, the results are not saved.
            'prefix_with_system'    (*bool*) option to append the system parameters in the file path. Default is ``False``.
            'grad'                  (*bool*) option to calculate gradients with respect to the X-axis. Default is ``False``.
            'grad_position'         (*int* or *float* or *str*) a value denoting the position or a mode to calculate the position. Options are ``'mean'`` for the mean of the axis values and ``'all'`` to output all positions. Default is ``'all'``.
            'threshold_mode'        (*str*) Mode of calculation of threshold values. Options are ``'minmax'`` for minimum value at which maximum is reached and ``'minmin'`` for minimmum value at which minimum is reached. Default is ``'minmax'``.
            'X'                     (*dict*) parameters of the X-axis.
            'Y'                     (*dict*) parameters of the Y-axis.
            'Z'                     (*dict*) parameters of the Z-axis.
            ====================    ====================================================

        Each axis dictionary (``'X'``, ``'Y'`` or ``'Z'``) can contain the following keys (arranged in the descending order of their priorities):
            ========    ====================================================
            key         value
            ========    ====================================================
            'var'       (*str*) name of the parameter to loop. Its value defaults to the axis name in lower case if the axis is a sequence of values and not a dictionary.
            'idx'       (*int*) index of the parameter if the parameter is a sequence of values.
            'val'       (*list* or *numpy.ndarray*) values of the parameter. The remaining keys are not checked if its value is given. Otherwise, the values of ``'min'``, ``'max'``, ``'dim'`` and ``'scale'`` are used to obtain ``'val'``.
            'min'       (*float*) minimum value of the parameter. Default is ``-5.0``.
            'max'       (*float*) maximum value of the parameter. Default is ``5.0``.
            'dim'       (*int*) number of values from 'min' to 'max', both inclusive. Default is ``101``.
            'scale'     (*str*) step scale of the values. Options are ``'log'`` for logarithmic and ``'linear'`` for linear. Default is ``'linear'``
            ========    ====================================================
    """

    # attributes
    looper_defaults = {
        'show_progress': False,
        'file_path_prefix': None,
        'prefix_with_system': False,
        'grad': False,
        'grad_position': 'all',
        'threshold_mode': 'minmax',
        'X': None,
        'Y': None,
        'Z': None
    }
    """dict : Default parameters of the looper."""

    def __init__(self, func, params:dict, params_system:dict, cb_update, parallel:bool, p_index:int, p_start:float):
        """Class constructor for BaseLooper."""

        # set constants
        self.func = func
        self.parallel = parallel
        self.p_index = p_index
        self.time = time.time()
        self.p_start = p_start if p_start is not None else self.time

        # set parameters
        self.set_params(params)
        self.params_system = params_system

        # initialize variables
        self.axes = dict()
        self.results = None
        self.pos = 0
        self.dim = 1

        # set axes
        if 'X' in self.name:
            self.set_axis(axis='X')
        if 'Y' in self.name:
            self.set_axis(axis='Y')
        if 'Z' in self.name:
            self.set_axis(axis='Z')

        # set updater
        self.updater = Updater(
            logger=logging.getLogger('qom.loopers.' + self.name),
            cb_update=cb_update,
            parallel=parallel,
            p_index=p_index,
            p_start=self.p_start
        )
        # display initialization
        self.updater.update_info(
            status="-" * (47 - len(self.name)) + "Looper Initialized"
        )

    def set_params(self, params:dict):
        """Method to validate and set the looper parameters.

        Parameters
        ----------
        params : dict
            Parameters for the looper.
        """

        # set looper parameters
        self.params = dict()
        for key in self.looper_defaults:
            self.params[key] = params.get(key, self.looper_defaults[key])

    def set_axis(self, axis:str):
        """Method to set the list of axis values.
        
        Parameters
        ----------
        axis : str
            Name of the axis (``'X'``, ``'Y'`` or ``'Z'``).
        """

        # validate parameters
        assert axis in self.params, "Parameters should contain key ``'{}'`` for axis parameters".format(axis)

        # extract frequently used variables
        _axis = self.params[axis]

        # validate variable
        assert 'var' in _axis, "Key ``'{}'`` should contain key ``'var'`` for the name of the variable".format(axis)

        # check index of variable
        _idx = _axis.get('idx', None)

        # if axis values are provided
        _val = _axis.get('val', None)
        # convert to numpy array
        if type(_val) is list:
            _val = np.array(_val, dtype=np.float_)
        # update values
        if type(_val) is np.ndarray:
            # validate values
            assert len(_val) != 0, "Key ``'{}'`` should contain key ``'val'`` with a non-empty list".format(axis)
        # update values
        else:
            # validate range
            assert 'min' in _axis and 'max' in _axis, "Key ``'{}'`` should contain keys ``'min'`` and ``'max'`` to define axis range".format(axis)

            # extract dimension
            _min = np.float_(_axis['min'])
            _max = np.float_(_axis['max'])
            _dim = int(_axis.get('dim', 101))
            _scale = str(_axis.get('scale', 'linear'))

            # handle single value
            if _dim == 1:
                _val = np.array([_min], dtype=np.float_)

            # set values
            else:
                if _scale == 'log':
                    _val = np.logspace(np.log10(_min), np.log10(_max), _dim)
                else:
                    _val = np.linspace(_min, _max, _dim)
                    # truncate values
                    _step_size = (Decimal(str(_max)) - Decimal(str(_min))) / (_dim - 1)
                    _decimals = - _step_size.as_tuple().exponent
                    _val = np.around(_val, _decimals)

        # set axis
        self.axes[axis] = dict()
        self.axes[axis]['var'] = _axis['var']
        self.axes[axis]['idx'] = int(_idx) if _idx is not None else None
        self.axes[axis]['min'] = _val[0]
        self.axes[axis]['max'] = _val[-1]
        self.axes[axis]['dim'] = len(_val)
        self.axes[axis]['val'] = _val

    def get_full_file_path(self):
        """Method to obtain the full file path.
            
        Returns
        -------
        file_path : str
            Full file path.
        """

        # extract frequently used parameters
        file_path = self.params['file_path_prefix']

        # complete filename with system parameters
        if self.params['prefix_with_system']:
            file_path += '_' + '_'.join([str(value) for value in self.params_system.values()])

        # update for XLooper variable
        file_path += self.get_params_str('X')

        # update for XYLooper variable
        if 'XY' in self.name:
            file_path += self.get_params_str('Y')

        # update for XYZLooper variable
        if 'XYZ' in self.name:
            file_path += self.get_params_str('Z')

        return file_path

    def get_params_str(self, axis:str):
        """Method to obtain a string containing the parameters used in the looper.
        
        Parameters
        ----------
        axis : {``'X'``, ``'Y'``, ``'Z'``}
            Name of the axis.

        Returns
        -------
        params_str: str
            String containing the parameters used in the looper.
        """

        # initialize
        params_str = ''

        # concatenate values
        _axis = self.axes[axis]
        _keys = ['var'] + (['idx'] if 'idx' in _axis else []) + ['min', 'max', 'dim']
        for key in _keys:
            if _axis.get(key, None) is not None:
                params_str += ('_' + axis.lower() + '=' if key == 'var' else '_') + str(_axis[key])

        return params_str

    def get_X_results(self):
        """Method to obtain results for variation in X-axis.

        Returns
        -------
        xs : numpy.ndarray
            Values of the X-axis.
        vs : numpy.ndarray
            Calculated values.
        """

        # extract frequently used variables
        show_progress = self.params['show_progress']
        x_var = self.axes['X']['var']
        x_idx = self.axes['X']['idx']
        x_val = self.axes['X']['val']
        x_dim = len(x_val)

        # initialize
        vals = list()
        flag = False
            
        # iterate
        for i in range(x_dim):
            # update progress
            if show_progress:
                self.updater.update_progress(
                    pos=self.pos * x_dim + i,
                    dim=x_dim if self.dim == 1 else x_dim * self.dim,
                    status="-" * (13 - len(self.name)) + "Looping axes values (BaseLooper)",
                    reset=False
                )
            # update a deep copy
            params_system = copy.deepcopy(self.params_system)
            if x_idx is not None:
                # handle non system parameter
                if params_system.get(x_var, None) is None:
                    params_system[x_var] = [0 for _ in range(x_idx + 1)]
                params_system[x_var][x_idx] = x_val[i]
            else:
                params_system[x_var] = x_val[i]
            # update values
            vals.append(self.func(params_system))

            # detect shape mismatch
            if len(vals) > 0 and len(np.shape(vals[i])) == 1:
                flag= True if len(vals[i - 1]) != len(vals[i]) else flag
            
        # convert to numpy array
        if not flag:
            xs = x_val
            vs = vals
        # reshape with NaN if shape mismatch
        else:
            xs = x_val
            # get max entries and data type
            count = 0
            dtype = None
            for i in range(len(vals)):
                count = len(vals[i]) if len(vals[i]) > count else count
                dtype = type(vals[i][0]) if len(vals[i]) > 0 and dtype is None else dtype
            vs = np.empty((len(vals), count), dtype=np.float_ if dtype is None else dtype)
            # update info
            self.updater.update_info(
                status="-" * (12 - len(self.name) - len(str(count))) + "Reshaping with NaN values (BaseLooper): New Length = {}".format(count)
            )
            # update extra entries to NaN
            for i in range(len(vals)):
                vs[i, :len(vals[i])] = vals[i]
                vs[i, len(vals[i]):] = np.NaN
            # convert to lists
            vs = vs.tolist()

        # calculate gradients
        if self.params['grad']:
            vs = np.gradient(vs, xs)

        return xs, vs

    def get_grad_index(self, axis_values:list):
        """Method to obtain the index of a particular position to calculate the gradients.
        
        Parameters
        ----------
        axis_values : numpy.ndarray
            Values of the axis.

        Returns
        -------
        idx : int
            Index of the required position.
        """

        # extract frequently used variables
        grad_position = self.params['grad_position']

        # validate parameters
        supported_types = Union[str, int, float].__args__
        assert isinstance(grad_position, supported_types), "Parameter ``'grad_position'`` should be one of the types: {}".format(supported_types)

        # handle inherited exceptions
        if grad_position == 'all':
            grad_position = 'mean'
        
        # fixed position
        if type(grad_position) is not str:
            idx = np.argmin(np.abs(np.asarray(axis_values) - grad_position))
        # mean mode
        else:
            idx = np.argmin(np.abs(np.asarray(axis_values) - np.mean(axis_values)))

        return idx
     
    def get_thresholds(self):
        """Method to calculate the threshold values for the results.
        
        Returns
        -------
        thresholds : dict
            Threshold values. Keys are ``'X'``, ``'Y'``, ``'Z'`` and ``'V'``.
        """

        # initialize
        thresholds = dict()

        # get index
        _index = {
            'minmax': np.argmax,
            'minmin': np.argmin
        }.get(self.params['threshold_mode'], np.argmax)(self.results['V'])

        # 3D looper
        if self.name == 'XYZLooper':
            _x_dim = len(self.axes['X']['val'])
            _xy_dim = len(self.axes['Y']['val']) * _x_dim
            thresholds['X'] = self.results['X'][int(_index / _xy_dim), int((_index % (_xy_dim)) / _x_dim), _index % _x_dim]
            thresholds['Y'] = self.results['Y'][int(_index / _xy_dim), int((_index % (_xy_dim)) / _x_dim), _index % _x_dim]
            thresholds['Z'] = self.results['Z'][int(_index / _xy_dim), int((_index % (_xy_dim)) / _x_dim), _index % _x_dim]
            thresholds['V'] = self.results['V'][int(_index / _xy_dim), int((_index % (_xy_dim)) / _x_dim), _index % _x_dim]
        # 2D looper
        elif self.name == 'XYLooper':
            _x_dim = len(self.axes['X']['val'])
            thresholds['X'] = self.results['X'][int(_index / _x_dim), _index % _x_dim]
            thresholds['Y'] = self.results['Y'][int(_index / _x_dim), _index % _x_dim]
            thresholds['V'] = self.results['V'][int(_index / _x_dim), _index % _x_dim]
        # 1D looper
        else:
            thresholds['X'] = self.results['X'][_index]
            thresholds['V'] = self.results['V'][_index]

        return thresholds
    
    def load_results(self):
        """Method to load the results from a .npz file.

        Returns
        -------
        loaded : bool
            Boolean denoting whether results were successfully loaded.
        """

        # if save not opted
        if self.params['file_path_prefix'] is None:
            return False

        # get full file path
        file_path = self.get_full_file_path()

        # update directory
        self.updater.create_directory(file_path=file_path)

        # initialize status
        loaded = False

        # attempt to load results if exists
        if self.updater.exists(file_path):
            # load results
            V = self.updater.load(file_path).tolist()

            # initialize variables
            _axes = [self.axes.get('X', None), self.axes.get('Y', None), self.axes.get('Z', None)]
            _len = sum([1 if _axes[i] is not None else 0 for i in range(3)])
            _dim = np.shape(V)

            # XYLooper
            if _len == 2:
                X = [_axes[0]['val']] * _dim[0]
                Y = [[_axes[1]['val'][i]] * _dim[1] for i in range(_dim[0])]
                Z = None
            # XYZLooper
            elif _len == 3:
                X = [[_axes[0]['val']] * _dim[1]] * _dim[0]
                Y = [[_axes[1]['val'][i]] * _dim[2] for i in range(_dim[1])] * _dim[0]
                Z = [[[_axes[2]['val'][i]] * _dim[2]] * _dim[1] for i in range(_dim[0])]
            # XLooper
            else:
                X = _axes[0]['val']
                Y = None
                Z = None

            # update results
            self.results = {
                'X': X,
                'Y': Y,
                'Z': Z,
                'V': V
            }
            
            # display completion
            if self.params['show_progress']:
                self.updater.update_progress(
                    pos=1,
                    dim=1,
                    status="-" * (31 - len(self.name)) + "Loading values",
                    reset=False
                )
            self.updater.update_info(
                status="-" * (51 - len(self.name)) + "Results Loaded"
            )

            loaded = True

        return loaded

    def save_results(self):
        """Method to save the results to a .npz file.

        Returns
        -------
        saved : bool
            Boolean denoting whether results were successfully saved.
        """

        # if save not opted
        if self.params['file_path_prefix'] is None:
            return False

        # get full file path
        file_path = self.get_full_file_path()

        # update directory
        self.updater.create_directory(
            file_path=file_path
        )

        # save data
        self.updater.save(
            file_path=file_path,
            array=np.array(self.results['V'])
        )
        
        # display completion
        self.updater.update_info(
            status="-" * (52 - len(self.name)) + "Results Saved"
        )

        return True