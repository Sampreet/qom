#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module to solve for stability.

References
----------

.. [1] E. X. DeJesus and C. Kaufman, *Routh-Hurwitz Criterion in the Examination of Eigenvalues of a System of Nonlinear Ordinary Differential Equations*, Phys. Rev. A **35**, 5288 (1987).
"""

__name__ = 'qom.solvers.stability'
__authors__ = ["Sampreet Kalita"]
__created__ = "2020-12-03"
__updated__ = "2023-07-10"

# dependencies
import logging
import numpy as np
import sympy as sp

# qom modules
from .base import validate_As_Coeffs
from ..io import Updater

class RHCSolver():
    r"""Class to solve for stability using the Routh-Hurwitz criterion.
    
    Initializes `As`, `Coeffs`, `params` and `updater`.

    Parameters
    ----------
    As : list or numpy.ndarray, optional
        Drift matrix.
    Coeffs : list or numpy.ndarray, optional
        Coefficients of the characteristic equation.
    params : dict
        Parameters for the solver. Available options are:
            ================    ====================================================
            key                 value
            ================    ====================================================
            'show_progress'     (*bool*) option to display the progress of the solver. Default is `False`.
            ================    ====================================================
    cb_update : callable, optional
        Callback function to update status and progress, formatted as `cb_update(status, progress, reset)`, where `status` is a string, `progress` is a float and `reset` is a boolean.

    .. note:: At least one of the parameters `As` and `Coeffs` (preferably `Coeffs`) should be non-`None`.
    """

    # attributes
    name = 'RHCSolver'
    """str : Name of the solver."""
    desc = "Routh Hurwitz Criterion Solver"
    """str : Description of the solver."""
    solver_defaults = {
        'show_progress': False
    }
    """dict : Default parameters of the solver."""

    def __init__(self, As=None, Coeffs=None, params:dict={}, cb_update=None):
        """Class constructor for RHCSolver."""

        # set constants
        self.As, self.Coeffs = validate_As_Coeffs(
            As=As,
            Coeffs=Coeffs
        )

        # set parameters
        self.set_params(params)

        # set updater
        self.updater = Updater(
            logger=logging.getLogger('qom.solvers.RHCSolver'),
            cb_update=cb_update
        )

    def set_params(self, params):
        """Method to validate and set the solver parameters.
        
        Parameters
        ----------
        params : dict
            Parameters of the solver.
        """

        # set solver parameters
        self.params = dict()
        for key in self.solver_defaults:
            self.params[key] = params.get(key, self.solver_defaults[key])

    def get_coeffs(self):
        r"""Method to obtain the coefficients (:math:`a_{i}`) of the characteristic equation for :math:`\det(\lambda I_{n} - A_{n \times n}) = 0` given by

        .. math::

            a_{0} \lambda^{n} + a_{1} \lambda^{n - 1} + ... + a_{n} = 0.

        Returns
        -------
        Coeffs : numpy.ndarray
            Coefficients of the characteristic equation.
        """

        # check inputs
        assert self.As is not None, "`As` should be non-`None` to obtain `Coeffs`."

        # extract frequently used variables
        show_progress = self.params['show_progress']
        _dim = (self.As.shape[0], self.As.shape[1] + 1)

        # initialize coefficients
        Coeffs = np.zeros(_dim, dtype=np.float_)

        # calculate coefficients
        for i in range(_dim[0]):
            # display progress
            if show_progress:
                self.updater.update_progress(
                    pos=i,
                    dim=_dim[0],
                    status="-" * 14 + "Obtaining Coefficients",
                    reset=False
                )

            # # convert to sympy matrix
            # _n              = self.As.shape[1]
            # _A              = sp.Matrix(self.As[i])
            # # eigenvalues
            # _lamb           = sp.symbols('\\lambda', complex=False)
            # # characteristic equation
            # _mat_eigenvalue = _lamb * sp.eye(_n) - _A
            # _expr_char      = _mat_eigenvalue.det(method='berkowitz').expand().collect(_lamb)

            # # set coefficients
            # _temp               = 0
            # for o in range(_n):
            #     Coeffs[i, o]= np.float_(_expr_char.coeff(_lamb**(_n - o)))
            #     _temp       += Coeffs[i, o] * _lamb**(_n - o)
            # Coeffs[i, _n]   = np.float_(_expr_char - _temp)

            # update coefficients
            Coeffs[i, :] = sp.Matrix(self.As[i]).charpoly().all_coeffs()

        # display completion
        if show_progress:
            self.updater.update_info(
                status="-" * 35 + "Coefficients Obtained"
            )

        return Coeffs

    def get_indices(self):
        r"""Method to obtain the indices where the sequence, :math:`\{T_{0}, T_{1}, ..., T_{n}\}` changes sign [1]_. Here, :math:`T_{k} = \det(M_{k})` are the determinants of the sub-matrices, where :math:`M_{k}` is the square sub-matrix of :math:`M` comprising of its first :math:`j` rows and columns, with :math:`T_{0} = a_{0}`.
        
        The matrix :math:`M` is defined as [1]_,

        .. math::
        
            M_{ij} = 
            \begin{cases} 
            a_{2i - j}, ~ \mathrm{if} ~ 0 \le 2 i - j \le n \\
            0, ~ \mathrm{otherwise}
            \end{cases}
        
        where the indices of :math:`M` are `1`-based.
        
        Returns
        -------
        Indices : numpy.ndarray
            Indices where the sequence changes sign as `0`s and `1`s for each drift matrix.
        """

        # if drift matrices are given
        if self.Coeffs is None and self.As is not None:
            self.Coeffs = self.get_coeffs()

        # extract frequently used variables
        show_progress = self.params['show_progress']
        _dim = self.Coeffs.shape
        _n = _dim[1] - 1

        # initialize variables
        Indices = np.zeros(_dim, dtype=np.int_)
        sequence = np.zeros(_dim[1], dtype=np.float_)

        # calculate coefficients
        for k in range(_dim[0]):
            # display progress
            if show_progress:
                self.updater.update_progress(
                    pos=k,
                    dim=_dim[0],
                    status="-" * 19 + "Obtaining Indices",
                    reset=False
                )

            # get M
            _M = np.zeros((_n, _n), dtype=np.float_)
            # handle 1-based indexing used in Ref. [1]
            for i in range(_n):
                for j in range(_n):
                    if 2 * i - j + 1 >= 0 and 2 * i - j + 1 <= _n:
                        _M[i][j] = self.Coeffs[k, 2 * i - j + 1]

            # set seq
            sequence[0] = self.Coeffs[k, 0]
            for i in range(1, _n + 1):
                sequence[i] = np.linalg.det(_M[:i, :i])

            # iterate
            for i in range(1, _n + 1):
                # add sign change index
                if np.sign(sequence[i] / sequence[i - 1]) == -1:
                    Indices[k, i] = 1

        # display completion
        if show_progress:
            self.updater.update_info(
                status="-" * 40 + "Indices Obtained"
            )

        return Indices
    
    def get_counts(self):
        """Method to obtain the number of positive real eigenvalues of the drift matrix.
        
        Returns
        -------
        counts : numpy.ndarray
            Number of positive real eigenvalues for each drift matrix.
        """

        # get counts from coefficients
        return np.sum(self.get_indices(), axis=1)
   
def get_counts_from_eigenvalues(As=None, Coeffs=None, params:dict={}, cb_update=None):
    """Function to obtain the number of positive real eigenvalues of the drift matrix.

    Parameters
    ----------
    As : list or numpy.ndarray, optional
        Drift matrix.
    Coeffs : list or numpy.ndarray, optional
        Coefficients of the characteristic equation.
    params : dict
        Parameters for the solver. Available options are:
            ==================  ====================================================
            key                 value
            ==================  ====================================================
            'show_progress'     (*bool*) option to display the progress of the solver.
            ==================  ====================================================
    cb_update : callable, optional
        Callback function to update status and progress, formatted as `cb_update(status, progress, reset)`, where `status` is a string, `progress` is a float and `reset` is a boolean.
    
    Returns
    -------
    counts : numpy.ndarray
        Number of positive real eigenvalues for each drift matrix.
    """

    # validate inputs
    As, Coeffs = validate_As_Coeffs(
        As=As,
        Coeffs=Coeffs
    )

    # set updater
    updater = Updater(
        logger=logging.getLogger(__name__),
        cb_update=cb_update
    )

    # if drift matrices is given
    if As is not None:
        _eigs, _ = np.linalg.eig(As)
    # if coefficients are given
    else:
        _eigs = np.zeros((len(Coeffs), len(Coeffs[0]) - 1), dtype=np.complex_)
        for i in range(len(Coeffs)):
            _eigs[i] = np.roots(Coeffs[i])

    # flag eigenvalues with positive real parts
    Indices = np.zeros_like(_eigs, dtype=np.int_)
    _condition = np.real(_eigs) > 0.0
    Indices[_condition] = 1

    # display completion
    if params.get('show_progress', False):
        updater.update_info(
            status="-" * 40 + "Indices Obtained"
        )

    # get counts
    return np.sum(Indices, axis=1)