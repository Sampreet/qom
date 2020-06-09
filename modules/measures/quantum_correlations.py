#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Modules to calculate quantum properties from quantum correlations."""

__authors__ = ['Sampreet Kalita']
__created__ = '2020-02-26'
__updated__ = '2020-05-01'

# dependencies
import numpy as np

from helpers import logger_console

class QuantumDiscord(object):
    """Class containing functions to calculate Quantum Discord.
    
    The class inherits object.

    Attributes
    ----------
    clh : :class:`logging.Logger`
        Logger to output status to console.
    """

    # initialize logger
    clh = logger_console.get_logger(__name__, 'short')

    def __init__(self):
        """Class constructor for QuantumDiscord."""

        # initialize parent class
        super().__init__()

    def calculate(self, Corr_mat, pos_i, pos_j):
        """Function to calculate Quantum Discord between two modes given the correlation matrix of their quadratures.

        Parameters
        ----------
        Corr_mat : list
            Matrix containing all correlations between quadratures.

        pos_i : *int*
            Position of ith mode in the correlation matrix.

        pos_j : *int*
            Position of jth mode in the correlation matrix.

        Returns
        -------
        qd : float
            Quantum Discord value.
        """

        # correlation matrix of ith mode
        A = np.matrix([ [   Corr_mat[pos_i][pos_i],     Corr_mat[pos_i][pos_i + 1]      ],
                        [   Corr_mat[pos_i + 1][pos_i], Corr_mat[pos_i + 1][pos_i + 1]  ]   ])
        # correlation matrix of jth mode
        B = np.matrix([ [   Corr_mat[pos_j][pos_j],     Corr_mat[pos_j][pos_j + 1]      ],
                        [   Corr_mat[pos_j][pos_j + 1], Corr_mat[pos_j + 1][pos_j + 1]  ]   ])
        # correlation matrix of intermodes
        C = np.matrix([ [   Corr_mat[pos_i][pos_j],     Corr_mat[pos_i][pos_j + 1]      ],
                        [   Corr_mat[pos_i + 1][pos_j], Corr_mat[pos_i + 1][pos_j + 1]  ]   ])
        # correlation matrix of the modes
        Corr_mat_modes = np.matrix([ [   Corr_mat[pos_i][pos_i],     Corr_mat[pos_i][pos_i + 1],     Corr_mat[pos_i][pos_j],     Corr_mat[pos_i][pos_j + 1]      ],
                                    [   Corr_mat[pos_i + 1][pos_i], Corr_mat[pos_i + 1][pos_i + 1], Corr_mat[pos_i + 1][pos_j], Corr_mat[pos_i + 1][pos_j + 1]  ],
                                    [   Corr_mat[pos_j][pos_i],     Corr_mat[pos_j][pos_i + 1],     Corr_mat[pos_j][pos_j],     Corr_mat[pos_j][pos_j + 1]      ],
                                    [   Corr_mat[pos_j + 1][pos_i], Corr_mat[pos_j + 1][pos_i + 1], Corr_mat[pos_j + 1][pos_j], Corr_mat[pos_j + 1][pos_j + 1]  ]   ])

        # symplectic invariants
        I_1 = np.linalg.det(A)
        I_2 = np.linalg.det(B)
        I_3 = np.linalg.det(C)
        I_4 = np.linalg.det(Corr_mat_modes)
        sigma = I_1 + I_2 + 2*I_3

        if sigma**2 < 4*I_4 or I_4 < 0:
            self.clh.warning('Argument of sqrt is negative\n')

        # symplectic eigenvalues
        mu_plus = 1/np.sqrt(2)*np.sqrt(sigma + np.sqrt(sigma**2 - 4*I_4))
        mu_minus = 1/np.sqrt(2)*np.sqrt(sigma - np.sqrt(sigma**2 - 4*I_4))

        # Quantum Discord value
        return self.f(np.sqrt(I_2)) - self.f(mu_plus) - self.f(mu_minus) + self.f(np.sqrt(self.W(I_1, I_2, I_3, I_4)))

    def f(self, x):
        """Helper function for Quantum Discord calculation."""

        if x + 1/2 <= 0 or x - 1/2 <= 0:
            self.clh.warning('Argument of log in f function is non-positive\n')

        return (x + 1/2)*np.log10(x + 1/2) - (x - 1/2)*np.log10(x - 1/2)

    def W(self, I_1, I_2, I_3, I_4):
        """Helper function for Quantum Discord calculation."""

        if (I_1 + 4*I_4)/(1 + 4*I_2)/I_3**2 == 0 or (4*I_2 - 1) == 0 or I_2 == 0:
            self.clh.warning('Division by zero encountered in W function\n')
        
        if 4*(I_1*I_2 - I_4)**2/(I_1 + 4*I_4)/(1 + 4*I_2)/I_3**2 <= 1.0:
            return ((2*np.abs(I_3) + np.sqrt(4*I_3**2 + (4*I_2 - 1)*(4*I_4 - I_1)))/(4*I_2 - 1))**2
        return (I_1*I_2 + I_4 - I_3**2 - np.sqrt((I_1*I_2 + I_4 - I_3**2)**2 - 4*I_1*I_2*I_4))/2/I_2

class QuantumEntanglement(object):
    """Class containing functions to calculate Quantum Entanglement.
    
    The class inherits object.

    Attributes
    ----------
    clh : :class:`logging.Logger`
        Logger to output status to console.
    """

    # initialize logger
    clh = logger_console.get_logger(__name__, 'short')

    def __init__(self):
        """Class constructor for QuantumEntanglement."""

        # initialize parent class
        super().__init__()

    def calculate_log_neg(self, Corr_mat, pos_i, pos_j):
        """Function to calculate Quantum Entanglement via logarithmic negativity between two modes given the correlation matrix of their quadratures.

        Parameters
        ----------
        Corr_mat : list
            Matrix containing all correlations between quadratures.

        pos_i : *int*
            Position of ith mode in the correlation matrix.

        pos_j : *int*
            Position of jth mode in the correlation matrix.

        Returns
        -------
        qe_log_neg : float
            Quantum Entanglement value using logarithmic negativity.
        """

        # correlation matrix of ith mode
        A = np.matrix([ [   Corr_mat[pos_i][pos_i],     Corr_mat[pos_i][pos_i + 1]      ],
                        [   Corr_mat[pos_i + 1][pos_i], Corr_mat[pos_i + 1][pos_i + 1]  ]   ])
        # correlation matrix of jth mode
        B = np.matrix([ [   Corr_mat[pos_j][pos_j],     Corr_mat[pos_j][pos_j + 1]      ],
                        [   Corr_mat[pos_j][pos_j + 1], Corr_mat[pos_j + 1][pos_j + 1]  ]   ])
        # correlation matrix of intermodes
        C = np.matrix([ [   Corr_mat[pos_i][pos_j],     Corr_mat[pos_i][pos_j + 1]      ],
                        [   Corr_mat[pos_i + 1][pos_j], Corr_mat[pos_i + 1][pos_j + 1]  ]   ])
        # correlation matrix of the modes
        Corr_mat_modes = np.matrix([ [   Corr_mat[pos_i][pos_i],     Corr_mat[pos_i][pos_i + 1],     Corr_mat[pos_i][pos_j],     Corr_mat[pos_i][pos_j + 1]      ],
                                    [   Corr_mat[pos_i + 1][pos_i], Corr_mat[pos_i + 1][pos_i + 1], Corr_mat[pos_i + 1][pos_j], Corr_mat[pos_i + 1][pos_j + 1]  ],
                                    [   Corr_mat[pos_j][pos_i],     Corr_mat[pos_j][pos_i + 1],     Corr_mat[pos_j][pos_j],     Corr_mat[pos_j][pos_j + 1]      ],
                                    [   Corr_mat[pos_j + 1][pos_i], Corr_mat[pos_j + 1][pos_i + 1], Corr_mat[pos_j + 1][pos_j], Corr_mat[pos_j + 1][pos_j + 1]  ]   ])

        # symplectic invariants
        I_1 = np.linalg.det(A)
        I_2 = np.linalg.det(B)
        I_3 = np.linalg.det(C)
        I_4 = np.linalg.det(Corr_mat_modes)

        # sum of symplectic invariants after positive partial transpose
        sigma = I_1 + I_2 - 2*I_3

        if sigma**2 < 4*I_4 or I_4 < 0:
            self.clh.warning('Argument of sqrt is negative\n')

        # smallest symplectic eigenvalue
        mu_minus = 1 / np.sqrt(2) * np.sqrt(sigma - np.sqrt(sigma**2 - 4*I_4))

        if mu_minus <= 0:
            self.clh.warning('Argument of ln is non-positive\n')

        # Quantum Entanglement value using logarithmic negativity
        return max(0, -1*(np.log(2 * mu_minus)))

class QuantumSynchronization(object):
    """Class containing functions to calculate Quantum Synchronization.
    
    The class inherits object.

    Attributes
    ----------
    clh : :class:`logging.Logger`
        Logger to output status to console.
    """

    # initialize logger
    clh = logger_console.get_logger(__name__, 'short')

    def __init__(self):
        """Class constructor for QuantumSynchronization."""

        # initialize parent class
        super().__init__()

    def calculate_comp_sync(self, Corr_mat, pos_i, pos_j):
        """Function to calculate Quantum Complete Synchronization between two modes given the correlation matrix of their quadratures.

        Parameters
        ----------
        Corr_mat : list
            Matrix containing all correlations between quadratures.

        pos_i : *int*
            Position of ith mode in the correlation matrix.

        pos_j : *int*
            Position of jth mode in the correlation matrix.

        Returns
        -------
        qs_c : float
            Quantum Complete Synchronization value.
        """

        # square difference between position quadratures
        q_minus_2 = 0.5*(Corr_mat[pos_i][pos_i] + Corr_mat[pos_j][pos_j] - 2*Corr_mat[pos_i][pos_j])
        # square difference between momentum quadratures
        p_minus_2 = 0.5*(Corr_mat[pos_i + 1][pos_i + 1] + Corr_mat[pos_j + 1][pos_j + 1] - 2*Corr_mat[pos_i + 1][pos_j + 1])

        # Complete Synchronization value
        return 1/(q_minus_2 + p_minus_2)

    def calculate_phase_sync(self, Corr_mat, pos_i, pos_j, mode_i, mode_j):
        """Function to calculate Quantum Phase Synchronization between two modes given the correlation matrix of their quadratures.

        Parameters
        ----------
        Corr_mat : list
            Matrix containing all correlations between quadratures.

        pos_i : *int*
            Position of ith mode in the correlation matrix.

        pos_j : *int*
            Position of jth mode in the correlation matrix.

        mode_i : np.complex
            Value of the ith mode.

        mode_j : np.complex
            Value of the jth mode.

        Returns
        -------
        qs_p : float
            Quantum Phase Synchronization value.
        """

        # amplitudes
        amp_i = np.abs(mode_i)
        amp_j = np.abs(mode_j)

        # arguments
        arg_i = np.angle(mode_i)
        arg_j = np.angle(mode_j)
        
        # transformation for ith mode momentum quadrature
        p_i_prime_2 = (np.sin(arg_i))**2*Corr_mat[pos_i][pos_i] - (np.sin(arg_i))*(np.cos(arg_i))*Corr_mat[pos_i][pos_i + 1] - (np.cos(arg_i))*(np.sin(arg_i))*Corr_mat[pos_i + 1][pos_i] + (np.cos(arg_i))**2*Corr_mat[pos_i + 1][pos_i + 1] 

        # transformation for jth mode momentum quadrature
        p_j_prime_2 = (np.sin(arg_j))**2*Corr_mat[pos_j][pos_j] - (np.sin(arg_j))*(np.cos(arg_j))*Corr_mat[pos_j][pos_j + 1] - (np.cos(arg_j))*(np.sin(arg_j))*Corr_mat[pos_j + 1][pos_j] + (np.cos(arg_j))**2*Corr_mat[pos_j + 1][pos_j + 1]

        # transformation for intermode momentum quadratures
        p_i_p_j_prime = (np.sin(arg_i))*(np.sin(arg_j))*Corr_mat[pos_i][pos_j] - (np.sin(arg_i))*(np.cos(arg_j))*Corr_mat[pos_i][pos_j + 1] - (np.cos(arg_i))*(np.sin(arg_j))*Corr_mat[pos_i + 1][pos_j] + (np.cos(arg_i))*(np.cos(arg_j))*Corr_mat[pos_i + 1][pos_j + 1]

        # square difference between momentum quadratures
        p_minus_prime_2 = 1/2*(p_i_prime_2 + p_j_prime_2 - 2*p_i_p_j_prime)

        # Quantum Phase Synchronization value
        return 1/2/p_minus_prime_2

    def calculate_rotated_phase_diff(self, mat_Corr, pos_i, pos_j, mode_i, mode_j):
        """Function to calculate Quantum Phase Synchronization between two modes given the correlation matrix of their quadratures.

        Parameters
        ----------
        mat_Corr : list
            Matrix containing all correlations between quadratures.

        pos_i : *int*
            Position of ith mode in the correlation matrix.

        pos_j : *int*
            Position of jth mode in the correlation matrix.

        mode_i : np.complex
            Value of the ith mode.

        mode_j : np.complex
            Value of the jth mode.

        Returns
        -------
        qs_p : float
            Quantum Phase Synchronization value.
        """

        # amplitudes
        amp_i = np.abs(mode_i)
        amp_j = np.abs(mode_j)

        # arguments
        arg_i = np.angle(mode_i)
        arg_j = np.angle(mode_j)

        # calculate rotated quadratures
        corr = np.cos(arg_i)*np.cos(arg_j)*mat_Corr[pos_i + 1][pos_j + 1] - np.cos(arg_i)*np.sin(arg_j)*mat_Corr[pos_i + 1][pos_j] - np.sin(arg_i)*np.cos(arg_j)*mat_Corr[pos_i][pos_j + 1] + np.sin(arg_i)*np.sin(arg_j)*mat_Corr[pos_i][pos_j]

        # Quantum Phase Synchronization value
        return corr