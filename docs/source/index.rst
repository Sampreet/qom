.. Quantum Optomechanics Toolbox documentation master file, created by
   sphinx-quickstart on Fri Dec  4 15:06:12 2020.

Welcome to the ``qom-v0.9.0`` Documentation!
============================================

The Quantum Optomechanics Toolbox (packaged as ``qom``) is a wrapper-styled, scalable toolbox featuring multiple modules for the calculation of stationary as well as dynamical properties of many-body quantum optomechanical systems. 
Its inheritable system classes can also be used to study other systems that follow the optomechanical model.
Backed by numerical libraries like NumPy and SciPy, and featuring the highly customizable visualizations offered by Matplotlib and Seaborn APIs, the toolbox aims to serve as an easy-to-use alternative to writing code explicitly and avoiding repetitive exercises for presentable visuals.

Key Features
------------

* Automatically managed loops and parameter validation modules.
* Solver modules to calculate classical and quantum signatures.
* Inheritable optomechanical systems supporting callable properties.
* Configurable visualizations without the need for explicit plotting.

Available Modules
-----------------

.. toctree::
   :maxdepth: 3
   
   qom.loopers
   qom.solvers
   qom.systems
   qom.ui
   qom.utils

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
