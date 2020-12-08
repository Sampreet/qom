#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to handle Routh-Hurwitz criterion.

References:

[1] E. X. DeJesus and C. Kaufman, *Routh-Hurwitz Criterion in the Examination of Eigenvalues of a System of Nonlinear Ordinary Differential Equations*, Phys. Rev. A **35** (12), 5288 (1987)."""

__name__    = 'qom.numerics.RHCriterion'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-12-03'
__updated__ = '2020-12-05'

# dependencies
import logging
import numpy as np
import sympy as sp

# module logger
logger = logging.getLogger(__name__)

class RHCriterion():
    r"""Class to handle Routh-Hurwitz criterion.

    Initializes `coeffs`, `n` and `seq` properties. At least one of the parameters, preferably "coeffs", should be non-None.

    An eigenvalue equation in :math:`\lambda` is obtained by equating :math:`\det(\lambda I_{n} - A_{n \times n})` to zero.

    Parameters
    ----------
    A : list or numpy.matrix, optional
        Drift matrix. 
    coeffs : list, optional
        Coefficients of the characteristic equation.
    """

    @property
    def coeffs(self):
        r"""list: Coefficients of the characteristic equation given by,

        .. math::
            a_{0} \lambda^{n} + a_{1} \lambda^{n - 1} + ... + a_{n} = 0
        """

        return self.__coeffs
    
    @coeffs.setter
    def coeffs(self, coeffs):
        self.__coeffs = coeffs

    @property
    def n(self):
        """int: Order of the characteristic equation."""

        return self.__n
    
    @n.setter
    def n(self, n):
        self.__n = n

    @property
    def seq(self):
        r"""list: Sequence of terms :math:`T_{k} = \det(M_{k})`, where :math:`M_{k}` is the square sub-matrix of :math:`M` comprising of its first :math:`k` rows and columns, with :math:`T_{0} = 1`.
        
        The matrix :math:`M` is defined as [1],

        .. math::
            M_{ij} = 
            \begin{cases} 
            a_{2i - j}, ~ \mathrm{if} ~ 0 \le 2 i - j \le n \\
            0, ~ \mathrm{otherwise}
            \end{cases}
        """

        return self.__seq
    
    @seq.setter
    def seq(self, seq):
        self.__seq = seq

    def __init__(self, A=None, coeffs=None):
        """Class constructor for RHCriterion."""

        # validate parameters
        assert A is not None or coeffs is not None, 'At least one of the parameters "A" and "coeffs" should be non-None'

        # if drift matrix
        if A is not None:
            # validate shape
            _shape = np.shape(A)
            assert _shape[0] == _shape[1], 'A should be a square matrix.'
            # set order
            self.n = _shape[0]

            # convert to sympy matrix
            _A = sp.Matrix(A)
            # eigenvalues
            _lamb = sp.symbols('\\lambda', complex=True)
            # eigenvalue equation
            _mat_eig = _lamb * sp.eye(self.n) - _A
            # characteristic equation
            _eqn_chr = _mat_eig.det(method='berkowitz').expand().collect(_lamb)

            # set coefficients
            self.coeffs = list()
            _temp = 0
            for o in range(self.n):
                self.coeffs.append(_eqn_chr.coeff(_lamb**(self.n - o)))
                _temp += self.coeffs[o] * _lamb**(self.n - o)
            self.coeffs.append(_eqn_chr - _temp)
            # convert to numpy constants
            for i in range(len(self.coeffs)):
                self.coeffs[i] = np.complex(sp.re(self.coeffs[i]), sp.im(self.coeffs[i]))
        # if coefficients
        if coeffs is not None:
            # set order
            self.n = len(coeffs) - 1
            # set coefficients
            self.coeffs = coeffs

        # set Ts
        self._set_Ts()

    def _set_Ts(self):
        """Method to set the determinants of the sub-matrices."""

        # get M
        _M = np.zeros((self.n, self.n), dtype=np.complex)
        for i in range(self.n):
            for j in range(self.n):
                if 2 * i - j >= 0 and 2 * i - j <= self.n:
                    _M[i][j] = self.coeffs[2 * i - j]

        # set seq
        self.seq = list()
        self.seq.append(self.coeffs[0])
        for i in range(1, self.n + 1):
            _sub_mat = _M[:i, :i]
            self.seq.append(np.linalg.det(_sub_mat))

    def get_indices(self):
        r"""Method to obtain the indices where the sequence, :math:`\{T_{0}, T_{1}, ..., T_{n}\}` changes sign. 

        Returns
        -------
        idxs : list
            Indices where the sequence changes sign.
        """

        # initialize values
        idxs = list()

        # iterate
        for i in range(1, self.n + 1):
            if np.sign(self.seq[i] / self.seq[i - 1]) == -1:
                idxs.append(i)

        # return
        return idxs