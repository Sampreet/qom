#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Module to handle quantum correlation measure solver."""

__name__    = 'qom.solvers.QCMSolver'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-01-04'
__updated__ = '2021-07-31'

# dependencies
import logging
import numpy as np

# module logger
logger = logging.getLogger(__name__)

# TODO: Add `compute` wrapper.
# TODO: Add `get_sync_phase_rot`.
# TODO: Add `get_phase_match_*`.

class QCMSolver():
    r"""Class to handle quantum correlation measure solver.

    Initializes ``corrs`` and ``modes`` properties.

    Parameters
    ----------
    modes : list
        Classical mode amplitudes of the system.
    corrs : list
        Quantum correlations of the quadratures.
    
    References
    ----------   

    .. [1] S. L. Braunstein and P. van Loock, *Quantum Information with Continuous Variables*, Rev. Mod. Phys. **77**, 513 (2005).

    .. [2] S. Olivares, *Quantum Optics in Phase Space: A Tutorial on Gaussian States*, Eur. Phys. J. Special Topics **203**, 3 (2012).

    .. [3] A. Mari, A. Farace, N. Didier, V. Giovannetti and R. Fazio, *Measures of Quantum Synchronization in Continuous Variable Systems*, Phys. Rev. Lett. **111**, 103605 (2013).
    """

    # attributes
    code = 'qcm_solver'
    name = 'Quantum Correlations Measure Solver'

    def __init__(self, modes, corrs):
        """Class constructor for QCMSolver."""

        # set attributes
        self.modes = modes
        self.corrs = corrs

    def __get_invariants(self, pos_i: int, pos_j: int):
        """Helper function to calculate symplectic invariants for two modes given the correlation matrix of their quadratures.

        Parameters
        ----------
        pos_i : int
            Index of ith quadrature.
        pos_j : int
            Index of jth quadrature.

        Returns
        -------
        invariants : list
            Symplectic invariants.
        """

        # correlation matrix of ith mode
        A = np.matrix([ [   self.corrs[pos_i][pos_i],     self.corrs[pos_i][pos_i + 1]      ],
                        [   self.corrs[pos_i + 1][pos_i], self.corrs[pos_i + 1][pos_i + 1]  ]   ])
        # correlation matrix of jth mode
        B = np.matrix([ [   self.corrs[pos_j][pos_j],     self.corrs[pos_j][pos_j + 1]      ],
                        [   self.corrs[pos_j][pos_j + 1], self.corrs[pos_j + 1][pos_j + 1]  ]   ])
        # correlation matrix of intermodes
        C = np.matrix([ [   self.corrs[pos_i][pos_j],     self.corrs[pos_i][pos_j + 1]      ],
                        [   self.corrs[pos_i + 1][pos_j], self.corrs[pos_i + 1][pos_j + 1]  ]   ])
        # correlation matrix of the modes
        self.corrs_modes = np.matrix([[   self.corrs[pos_i][pos_i],     self.corrs[pos_i][pos_i + 1],     self.corrs[pos_i][pos_j],     self.corrs[pos_i][pos_j + 1]      ],
                                    [   self.corrs[pos_i + 1][pos_i], self.corrs[pos_i + 1][pos_i + 1], self.corrs[pos_i + 1][pos_j], self.corrs[pos_i + 1][pos_j + 1]  ],
                                    [   self.corrs[pos_j][pos_i],     self.corrs[pos_j][pos_i + 1],     self.corrs[pos_j][pos_j],     self.corrs[pos_j][pos_j + 1]      ],
                                    [   self.corrs[pos_j + 1][pos_i], self.corrs[pos_j + 1][pos_i + 1], self.corrs[pos_j + 1][pos_j], self.corrs[pos_j + 1][pos_j + 1]  ]   ])

        # symplectic invariants
        return [np.linalg.det(A), np.linalg.det(B), np.linalg.det(C), np.linalg.det(self.corrs_modes)]

    def __get_W(self, I_1, I_2, I_3, I_4):
        """Helper function for quantum discord calculation."""

        try: 
            if 4 * (I_1 * I_2 - I_4)**2 / (I_1 + 4 * I_4) / (1 + 4 * I_2) / I_3**2 <= 1.0:
                return ((2 * abs(I_3) + np.sqrt(4 * I_3**2 + (4 * I_2 - 1) * (4 * I_4 - I_1))) / (4 * I_2 - 1))**2
            return (I_1 * I_2 + I_4 - I_3**2 - np.sqrt((I_1 * I_2 + I_4 - I_3**2)**2 - 4 * I_1 * I_2 * I_4)) / 2 / I_2
        except ZeroDivisionError:
            logger.warning('Division by zero encountered in W function\n')
            return 0

    def get_discord_Gaussian(self, pos_i: int, pos_j: int):
        """Method to obtain Gaussian quantum discord [2]_ between two modes given the correlation matrix of their quadratures.

        Parameters
        ----------
        pos_i : int
            Index of ith quadrature.
        pos_j : int
            Index of jth quadrature.

        Returns
        -------
        D_G : float
            Gaussian quantum discord.
        """

        # symplectic invariants
        I_1, I_2, I_3, I_4 = self.__get_invariants(pos_i=pos_i, pos_j=pos_j)

        try:
            # sum of symplectic invariants
            sigma = I_1 + I_2 + 2 * I_3
            # symplectic eigenvalues
            mu_plus = 1 / np.sqrt(2) * np.sqrt(sigma + np.sqrt(sigma**2 - 4 * I_4))
            mu_minus = 1 / np.sqrt(2) * np.sqrt(sigma - np.sqrt(sigma**2 - 4 * I_4))
        except ValueError:
            logger.warning('Argument of sqrt is negative.\n')
            return 0

        # f function 
        f_func = lambda x: (x + 1 / 2) * np.log10(x + 1 / 2) - (x - 1 / 2) * np.log10(x - 1 / 2)
        # function values
        f_vals = list()
        for ele in [np.sqrt(I_2), mu_plus, mu_minus, np.sqrt(self.__get_W(I_1, I_2, I_3, I_4))]:
            f_vals.append(f_func(ele))
            
        # quantum discord value
        D_G = f_vals[0] - f_vals[1] - f_vals[2] + f_vals[3]
        
        # validate positive and not NaN
        D_G = D_G if D_G > 0.0 and D_G == D_G else 0.0

        return D_G

    def get_entanglement_logarithmic_negativity(self, pos_i: int, pos_j: int):
        """Function to calculate quantum entanglement via logarithmic negativity [1]_ between two modes given the correlation matrix of their quadratures.

        Parameters
        ----------
        pos_i : int
            Index of ith quadrature.
        pos_j : int
            Index of jth quadrature.

        Returns
        -------
        E_n : float
            Quantum entanglement value using logarithmic negativity.
        """

        # symplectic invariants
        I_1, I_2, I_3, I_4 = self.__get_invariants(pos_i=pos_i, pos_j=pos_j)
        
        try:
            # sum of symplectic invariants after positive partial transpose
            sigma = I_1 + I_2 - 2 * I_3
            # smallest symplectic eigenvalue
            mu_minus = 1 / np.sqrt(2) * np.sqrt(sigma - np.sqrt(sigma**2 - 4 * I_4))
        except ValueError:
            logger.warning('Argument of sqrt is negative\n')
            E_n = 0

        try:
            # quantum entanglement value using logarithmic negativity
            E_n = - 1 * (np.log(2 * mu_minus))
        except ValueError:
            logger.warning('Argument of ln is non-positive\n')
            E_n = 0
        else:
            E_n = max(0, E_n)
        
        return E_n

    def get_synchronization_complete(self, pos_i: int, pos_j: int):
        """Method to obtain the quantum complete synchronization measure [3]_ between two modes.

        Parameters
        ----------
        pos_i : int
            Index of ith quadrature.
        pos_j : int
            Index of jth quadrature.

        Returns
        -------
        S_complete : float
            Quantum complete synchronization measure.
        """

        # square difference between position quadratures
        q_minus_2 = 0.5 * (self.corrs[pos_i][pos_i] + self.corrs[pos_j][pos_j] - 2 * self.corrs[pos_i][pos_j])
        # square difference between momentum quadratures
        p_minus_2 = 0.5 * (self.corrs[pos_i + 1][pos_i + 1] + self.corrs[pos_j + 1][pos_j + 1] - 2 * self.corrs[pos_i + 1][pos_j + 1])

        try: 
            # quantum complete synchronization value
            return 1 / (q_minus_2 + p_minus_2)
        except ZeroDivisionError:
            logger.warning('Division by zero encountered\n')
            return 0

    def get_synchronization_phase(self, pos_i: int, pos_j: int):
        """Method to obtain the quantum phase synchronization measure [3]_ between two modes.

        Parameters
        ----------
        pos_i : int
            Index of ith quadrature.
        pos_j : int
            Index of jth quadrature.

        Returns
        -------
        S_phase : float
            Quantum phase synchronization measure.
        """

        # arguments of the modes
        arg_i = np.angle(self.modes[int(pos_i / 2)])
        arg_j = np.angle(self.modes[int(pos_j / 2)])

        # frequently used variables
        cos_i = np.cos(arg_i)
        cos_j = np.cos(arg_j)
        sin_i = np.sin(arg_i)
        sin_j = np.sin(arg_j)
        
        # transformation for ith mode momentum quadrature
        p_i_prime_2 = sin_i**2 * self.corrs[pos_i][pos_i] - sin_i * cos_i * self.corrs[pos_i][pos_i + 1] - cos_i * sin_i * self.corrs[pos_i + 1][pos_i] + cos_i**2 * self.corrs[pos_i + 1][pos_i + 1] 

        # transformation for jth mode momentum quadrature
        p_j_prime_2 = sin_j**2 * self.corrs[pos_j][pos_j] - sin_j * cos_j * self.corrs[pos_j][pos_j + 1] - cos_j * sin_j * self.corrs[pos_j + 1][pos_j] + cos_j**2 * self.corrs[pos_j + 1][pos_j + 1]

        # transformation for intermode momentum quadratures
        p_i_p_j_prime = sin_i * sin_j * self.corrs[pos_i][pos_j] - sin_i * cos_j * self.corrs[pos_i][pos_j + 1] - cos_i * sin_j * self.corrs[pos_i + 1][pos_j] + cos_i * cos_j * self.corrs[pos_i + 1][pos_j + 1]

        # square difference between momentum quadratures
        p_minus_prime_2 = 1 / 2 * (p_i_prime_2 + p_j_prime_2 - 2 * p_i_p_j_prime)

        # quantum phase synchronization value
        S_phase = 1 / 2 / p_minus_prime_2

        return S_phase