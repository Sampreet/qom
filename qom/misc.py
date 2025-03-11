#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Module containing different operators."""

__name__    = 'qom.misc'
__authors__ = ["Sampreet Kalita"]
__created__ = "2023-08-13"
__updated__ = "2025-03-11"

# dependencies
from copy import deepcopy
import numpy as np
import scipy.sparse as sp

def op_annihilation(N):
    """Function to obtain an annihilation operator.

    Parameters
    ----------
    N : int
        Dimension of the Hilbert space.

    Returns
    ----------
    op : numpy.ndarray
        Annihilation operator.    
    """

    # data
    data = np.sqrt(np.arange(1, N, dtype=np.complex128))
    # column indices
    indices = np.arange(1, N, dtype=np.int32)
    # pointers to column indices
    indptr = np.arange(N + 1, dtype=np.int32)
    indptr[-1] = N - 1
    # return annihilation operator
    return sp.csr_matrix((data, indices, indptr), shape=(N, N)).toarray()

def op_creation(N):
    """Function to obtain a creation operator.

    Parameters
    ----------
    N : int
        Dimension of the Hilbert space.

    Returns
    ----------
    op : numpy.ndarray
        Creation operator.
    """

    # return Hermitian congugate of annihilation operator
    return dagger(op_annihilation(N))

def op_identity(N):
    """Function to obtain an identity operator.

    Parameters
    ----------
    N : int
        Dimension of the Hilbert space.

    Returns
    ----------
    op : numpy.ndarray
        Identity operator.
    """

    # data
    data = np.ones(N, dtype=np.complex128)
    # column indices
    indices = np.arange(0, N, dtype=np.int32)
    # pointers to column indices
    indptr = np.arange(N + 1, dtype=np.int32)
    indptr[-1] = N
    # return identity operator
    return sp.csr_matrix((data, indices, indptr), shape=(N, N)).toarray()

def op_sigma_x():
    """Function to obtain the Pauli-X operator.

    Parameters
    ----------
    A : numpy.ndarray
        Operator for which the Hermitian conjugate is to be obtained.

    Returns
    ----------
    op : numpy.ndarray
        Pauli-X operator.
    """

    return np.array([[0, 1], [1, 0]], dtype=np.complex128)

def op_sigma_y():
    """Function to obtain the Pauli-Y operator.

    Parameters
    ----------
    A : numpy.ndarray
        Operator for which the Hermitian conjugate is to be obtained.

    Returns
    ----------
    op : numpy.ndarray
        Pauli-Y operator.
    """

    return np.array([[0, -1j], [1j, 0]], dtype=np.complex128)

def op_sigma_z():
    """Function to obtain the Pauli-Z operator.

    Parameters
    ----------
    A : numpy.ndarray
        Operator for which the Hermitian conjugate is to be obtained.

    Returns
    ----------
    op : numpy.ndarray
        Pauli-Z operator.
    """

    return np.array([[1, 0], [0, -1]], dtype=np.complex128)

def dagger(A):
    """Function to obtain the Hermitian conjugate of an operator.

    Parameters
    ----------
    A : numpy.ndarray
        Operator for which the Hermitian conjugate is to be obtained.

    Returns
    ----------
    op : numpy.ndarray
        Hermitian conjugate of the operator.
    """

    # return conjugate transpose
    return deepcopy(np.conjugate(A.T))

def expect(A, psi):
    """Function to obtain the expectation value of an operator.

    Parameters
    ----------
    A : numpy.ndarray
        Operator for which the expectation value is to be obtained.
    psi : numpy.ndarray
        State vector for the operator.

    Returns
    ----------
    expect : float
        Expectation value of the operator.
    """

    # obtain expection value
    _data = (dagger(psi) * A * psi).data
    # handle null
    if len(_data) == 0:
        return 0.0
    # return expectation value
    return np.real(_data[0])

def state_fock(N, n):
    """Function to obtain a Fock state with an initial number of quanta.

    Parameters
    ----------
    N : int
        Dimension of the Hilbert space.
    n : int
        Initial number of quanta in the state.

    Returns
    ----------
    fock : numpy.ndarray
        Fock state with given quanta.
    """

    # validate dimension
    assert N > n, "Hilbert space dimension insufficient"

    # data
    data = np.array([1], dtype=np.complex128)
    # row indices
    indices = np.array([n], dtype=np.int32)
    # pointers to row indices
    indptr = np.array([0, 1], dtype=np.int32)
    # return fock state
    return sp.csc_matrix((data, indices, indptr), shape=(N, 1)).toarray()

def tensor(A, B):
    """Function to obtain the tensor product of two operators.
    
    Parameters
    ----------
    A : numpy.ndarray
        First operator.
    B : numpy.ndarray
        Second operator.
        
    Returns
    -------
    op : numpy.ndarray
        Tensor product of the operators.
    """

    # return Kronecker product
    return np.kron(A, B)

