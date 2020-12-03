#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to handle Routh-Hurwitz criterion.

References:
[1] E. X. DeJesus and C. Kaufman, **Routh-Hurwitz Criterion in the Examination of Eigenvalues of a System of Nonlinear Ordinary Differential Equations**, Phys. Rev. A *35* (12), 5288 (1987)."""

__name__    = 'qom.numerics.RHCriterion'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-12-03'
__updated__ = '2020-12-03'

# dependencies
import logging
import numpy as np
import sympy as sp

# module logger
logger = logging.getLogger(__name__)

class RHCriterion():
    """Class to handle Routh-Hurwitz criterion.

    References:
    [1] E. X. DeJesus and C. Kaufman, **Routh-Hurwitz Criterion in the Examination of Eigenvalues of a System of Nonlinear Ordinary Differential Equations**, Phys. Rev. A *35* (12), 5288 (1987).
    
    Properties
    ----------
        order : int
            Order of the characteristic equation.

        coeffs : list
            Coefficients of the characteristic equation.
            
        seq : list
            Sequence of determinants of the sub-matrices.
    """

    @property
    def order(self):
        """Property order.

        Returns
        -------
            order : int
                Order of the characteristic equation.
        """

        return self.__order
    
    @order.setter
    def order(self, order):
        """Setter for order.

        Parameters
        ----------
            order : int
                Order of the characteristic equation.
        """

        self.__order = order

    @property
    def coeffs(self):
        """Property coeffs.

        Returns
        -------
            coeffs : list
                Coefficients of the characteristic equation.
        """

        return self.__coeffs
    
    @coeffs.setter
    def coeffs(self, coeffs):
        """Setter for coeffs.

        Parameters
        ----------
            coeffs : list
                Coefficients of the characteristic equation.
        """

        self.__coeffs = coeffs

    @property
    def seq(self):
        """Property seq.

        Returns
        -------
            seq : list
                Sequence of determinants of the sub-matrices.
        """

        return self.__seq
    
    @seq.setter
    def seq(self, seq):
        """Setter for seq.

        Parameters
        ----------
            seq : list
                Sequence of determinants of the sub-matrices.
        """

        self.__seq = seq

    def __init__(self, A):
        """Class constructor for RHCriterion.

        Initializes `order` and `coeffs` properties.

        Parameters
        ----------
            A : `numpy.matrix` or list
               Drift matrix. 
        """

        # validate shape
        _shape = np.shape(A)
        assert _shape[0] == _shape[1], 'A should be a square matrix.'

        # set order
        self.order = _shape[0]

        # convert to sympy matrix
        _A = sp.Matrix(A)
        # eigenvalues
        _lamb = sp.symbols('\\lambda', complex=True)
        # eigenvalue equation
        _mat_eig = _lamb * sp.eye(self.order) - _A
        # characteristic equation
        _eqn_chr = _mat_eig.det(method='berkowitz').expand().collect(_lamb)

        # set coefficients
        self.coeffs = list()
        _temp = 0
        for o in range(self.order):
            self.coeffs.append(_eqn_chr.coeff(_lamb**(self.order - o)))
            _temp += self.coeffs[o] * _lamb**(self.order - o)
        self.coeffs.append(_eqn_chr - _temp)
        # convert to numpy constants
        for i in range(len(self.coeffs)):
            self.coeffs[i] = np.complex(sp.re(self.coeffs[i]), sp.im(self.coeffs[i]))

        # set Ts
        self.__set_Ts()

    def __set_Ts(self):
        """Method to set the determinants of the sub-matrices."""

        # get M
        _M = np.zeros((self.order, self.order), dtype=np.complex)
        for i in range(self.order):
            for j in range(self.order):
                if 2 * i - j >= 0 and 2 * i - j <= self.order:
                    _M[i][j] = self.coeffs[2 * i - j]

        # set seq
        self.seq = list()
        self.seq.append(self.coeffs[0])
        for i in range(1, self.order + 1):
            _sub_mat = _M[:i, :i]
            self.seq.append(np.linalg.det(_sub_mat))

    def check(self):
        """Method to check Routh-Hurwitz criterion.

        Returns
        -------
            idxs : list
                Indices of the sequence where the element changes sign.
        """

        # initialize values
        _prev_sign = np.sign(self.seq[0])
        idxs = list()

        # iterate
        for i in range(1, self.order + 1):
            _curr_sign = np.sign(self.seq[i] / self.seq[i - 1])
            if _curr_sign != _prev_sign:
                _prev_sign = _curr_sign
                idxs.append(i)

        # return
        return idxs