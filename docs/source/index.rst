.. Quantum Optomechanics Toolbox documentation master file, created by
   sphinx-quickstart on Fri Dec 4 15:06:12 2020.

Welcome to the ``qom-v1.0.2`` Documentation!
============================================

The Quantum Optomechanics Toolbox (packaged as ``qom``) is a wrapper-styled, scalable toolbox featuring multiple modules for the calculation of stationary as well as dynamical properties of linearized quantum optomechanical systems.
Backed by numerical libraries like NumPy and SciPy, and featuring the highly customizable visualizations offered by Matplotlib and Seaborn APIs, the toolbox aims to serve as an easy-to-use alternative to writing code explicitly and avoiding repetitive exercises for presentable visuals.

.. note::
   The toolbox is not under active maintenance since 2023 and addition of newer features are not planned for the near future.
   However, the current CPU-based modules fully support the simulation of linearized quantum optomechanical systems and their related analysis.
   For the simulation of more general systems, ``QuTiP`` (``> v5.0``) provides a much faster interface.

Key Features
------------

* Run automatically-managed loops in parallel and pool results.
* Solve for stability and classical/quantum signatures seamlessly.
* Configure plots across plotting libraries with a common syntax.

What's New in v1.0!
-------------------

* Non-linear Schrodinger equation solver with integration support.
* Attractor detection and bifurcation for non-linear dynamical systems.
* Huge performance boost with NumPy-based vectorization.
* Faster Monte-Carlo quantum trajectories solver for low-dimensional Hilbert spaces (deprecated since ``qom-v1.0.2``).

.. list-table::
   :widths: 50 50
   :header-rows: 1

   * - Dynamical Stability
     - Quantum Correlations
   * - .. image:: ../images/00_00_sz.png
     - .. image:: ../images/00_01_en.png
   * - Runtimes for the calculation of dynamical stability of the steady state using the Routh-Hurwitz criteria.
     - Runtimes for the calculation of average entanglement from the dynamical values of modes and correlations.

Examples
--------

.. list-table::
   :widths: 50 50
   :header-rows: 1

   * - Classical Amplitudes
     - Quantum Fluctuations
   * - .. image:: ../images/01_00_classical.gif
     - .. image:: ../images/01_01_quantum.gif
   * - The classical mean values of the optical and mechanical modes are obtained using the rate equations of the modes.
     - The variances of the quantum fluctuation quadratures are obtained using the rate equation for the correlation matrix.

.. list-table::
   :widths: 50 50
   :header-rows: 1

   * - Fixed Point
     - Limit Cycle
   * - .. image:: ../images/02_00_fixed_point.gif
     - .. image:: ../images/02_01_limit_cycle.gif
   * - An optomechanical system settling to a steady state.
     - Self-sustained oscillations in an optomechanical system.

.. list-table::
   :widths: 50 50
   :header-rows: 1

   * - Dynamical Stability
     - Optical Bistability
   * - .. image:: ../images/03_00_sz.gif
     - .. image:: ../images/03_01_ob.gif
   * - Dynamical stability obtained from the steady state drift matrix.
     - Bistability obtained from the steady state optical occupancies.

.. list-table::
   :widths: 50 50
   :header-rows: 1

   * - Optomechanical Entanglement
     - Mechanical Synchronization
   * - .. image:: ../images/04_00_en.png
     - .. image:: ../images/04_01_sp.png
   * - Quantum entanglement between the optical and mechanical modes of an optomechanical system.
     - Quantum phase synchronization between the mechanical modes of two coupled identical systems.

.. list-table::
   :widths: 50 50
   :header-rows: 1

   * - Wigner Distributions
     - Optomechanical Solitons
   * - .. image:: ../images/05_00_wigner.gif
     - .. image:: ../images/05_01_soliton.gif
   * - Wigner distribution depicting the evolution of mechanical squeezing in a modulated optomechanical system.
     - Soliton propagation in an array of optomechanical systems at different phase lags between the input solitons.

A set of notebooks and scripts to demonstrate the usage of the toolbox can be found in the `examples repository <https://github.com/sampreet/qom-examples>`_.

Installation
============

Dependencies
------------

`The Quantum Optomechanics Toolbox <https://github.com/sampreet/qom>`_ requires ``Python 3.8+``, preferably installed via the `Anaconda distribution <https://www.anaconda.com/download>`_.
Once ``Anaconda`` is set up, create and activate a new ``conda`` environment using:

.. code-block:: bash

   conda create -n qom python
   conda activate qom

The toolbox primarily relies on ``numpy`` (for fast numerical algebra), ``scipy`` (for numerical methods), ``sympy`` (for symbolic algebra), ``seaborn`` (for color palettes) and ``matplotlib`` (for plotting results).
These libraries can be installed using:

.. code-block:: bash

   conda install matplotlib numpy scipy sympy seaborn

.. note:: To run the GUI modules, ``pyqt`` should be installed separately.

Once the dependencies are installed, the toolbox can be installed via PyPI or locally.

The documentation of the latest release is available `here <https://sampreet.github.io/qom-docs>`_.

Installing via PyPI
-------------------

To install the packages via the Python Package Index (PyPI), execute: 

.. code-block:: bash

   pip install git+https://github.com/sampreet/qom.git

Installing Locally
------------------

To install the package locally, download `the repository <https://github.com/sampreet/qom>`_ as ``.zip`` and extract the contents.
Now, execute the following from *outside* the top-level directory, ``ROOT_DIR``, inside which ``setup.py`` is located (refer to the `file structure <https://github.com/sampreet/qom/blob/master/CONTRIBUTING.md>`_):

.. code-block:: bash

   pip install -e ROOT_DIR

Citing
======

Please cite `S. Kalita and A. K. Sarma, *The QOM Toolbox: An object-oriented Python framework for cavity optomechanical systems*, Proceedings of Eighth International Congress on Information and Communication Technology **3**, Springer Singapore (2023) <https://github.com/sampreet/qom/blob/master/CITATION.bib>`_ if you use our work in your research.

Available Modules
=================

.. toctree::
   :maxdepth: 3
   
   qom.loopers
   qom.solvers
   qom.systems
   qom.ui
   qom.utils
   qom.io
   qom.misc

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
