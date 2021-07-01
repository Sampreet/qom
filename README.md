# The Quantum Optomechanics Toolbox

[![Code Size](https://img.shields.io/github/repo-size/sampreet/qom?style=for-the-badge)](#)
[![Last Commit](https://img.shields.io/github/last-commit/sampreet/qom?style=for-the-badge)](#)

[![Open Issues](https://img.shields.io/github/issues-raw/sampreet/qom?style=flat-square)](https://github.com/Sampreet/qom/issues?q=is%3Aopen+is%3Aissue)
[![Closed Issues](https://img.shields.io/github/issues-closed-raw/sampreet/qom?style=flat-square)](https://github.com/Sampreet/qom/issues?q=is%3Aissue+is%3Aclosed)
[![Milestone](https://img.shields.io/github/milestones/progress/sampreet/qom/1?style=flat-square)](https://github.com/Sampreet/qom/milestones)

> A library of modules for computational quantum optomechanics!

The Quantum Optomechanics Toolbox (packaged as `qom`) is a wrapper-styled, scalable toolbox featuring multiple modules for the calculation of stationary as well as dynamical properties of many-body quantum optomechanical systems.
Its inheritable system classes can also be used to study other systems that follow the optomechanical model.
Backed by numerical libraries like NumPy and SciPy, and featuring the highly customizable visualizations offered by Matplotlib and Seaborn APIs, the toolbox aims to serve as an easy-to-use alternative to writing code explicitly and avoiding repetitive exercises for presentable visuals.

### Key Features!

* Automatically managed loops and parameter validation modules.
* Solver modules to calculate classical and quantum signatures.
* Inheritable optomechanical systems supporting callable properties.
* Configurable visualizations without the need for explicit plotting.

### Up Next!

- [ ] Support for Delay Differential Equations
- [ ] GUI module to run templated scripts
- [ ] Multithreaded looping
- [ ] Project website

## Installation

### Dependencies

The project requires `Python 3.8+` installed, preferably via the [Anaconda distribution](https://www.anaconda.com/products/individual).

### Installing from PyPI

To install the package and its requirements from the Python Package Index, execute: 

```bash
pip install -i https://test.pypi.org/simple/ qom
```

### Installing Locally

To install the package locally, download the repository as `.zip` and extract the contents.
Now, execute the following from *outside* the top-level directory, `ROOT_DIR`, inside which `setup.py` is located:

```bash
pip install -e ROOT_DIR
```

Once the package is installed, its modules can be imported.

## Basic Usage

The library features easy-to-use functions to calculate as well as visualize the trend of several quantum signatures.
Specialized examples on usage of the various components can be found in the [`examples`](./examples) folder.

### Loopers

The modules `XLooper`, `XYLooper` and `XYZLooper` loop over specific functions and parameters that are passed as arguments during initialization.
The `loop` method returns the results in the form of a dictionary of the axes (`X`, `Y` and `Z`) and the calculated values `V`.
The threshold values of the axes at which the calculations reach their minima or maxima can also be obtained using the `get_thresholds` method.

For example, the `qom.looper.XLooper` module can be implemented as:

```python
# initilize the looper with the function and the parameters
looper = XLooper(func, params)
# get resultant dictionary containing keys `X` and `V`.
results = looper.loop()
# obtain the threshold values of the inputs
thres = looper.get_thresholds()
```

Here, `func` is a function containing the steps of each iteration and `params` is a dictionary containing the parameters required for the looper, solver, system and plotter. 
The complete example can be found in the [XLooper notebook](./examples/qom_loopers_XLooper.ipynb).

### Solvers

Solvers constitute of a set of classes to tackle numerical computations of various forms. 
Each solver is associated with a particular method, measure or criterion. 

For example, the `qom.solvers.HLESolver` generates the time-varying solutions of the classical mode amplitudes and quantum correlations by solving the Heisenberg-Langevin equations and can be implemented as:

```python
# initialize the solver with the parameters
solver = HLESolver(solver_params)
# solve for the dynamics of modes and correlations
results = solver.solve(ode_func, iv)
# get modes and correlations
modes = solver.get_Modes(num_modes)
corrs = solver.get_Corrs(num_modes)
```

Here, `solver_params` is a dictionary containing the parameters required by `HLESolver`, `ode_func` is a function returning the rates of the modes and correlations, `iv` are their initial values and `num_modes` are the number of modes of the system.
The complete example can be found in the [HLESolver notebook](./examples/qom_solvers_HLESolver.ipynb).


### Systems

These classes cover some basic properties of optomechanical systems as well as wrap solvers for faster implementation.

For example, the `qom.systems.SOSMSystem` class can be used to interface a single-optical-single-mechanical system. Its built-in function `get_mean_optical_occupancy` returns the intracavity photon number and can be implemented as:

```python
# initialize the system with system parameters
system = MySystem(system_params)
# obtain mean occupancy of the optical mode
N_o = system.get_mean_optical_occupancy(system.params['lambda_l'], system.params['mu'], system.params['gamma_o'], system.params['P_l'], system.params['omega_m'])
```

Here, `MySystem` is a class inheriting `SOSMSystem`, initialized by `system_params`, which is a dictionary containing the parameters of the system.
The complete example can be found in the [SOSMSystem notebook](./examples/qom_systems_SOSMSystem.ipynb).

### UI

User-interface modules like `qom.ui.log` and `qom.ui.gui` provide console as well as graphical features to keep track of parameters and progress.
Plotters wrap independent packages of Python under an equivalent syntax. 
An implementation of `qom.ui.plotters.MPLPlotter` wrapping `matplotlib` is given below:

```python
# all axes
axes = {
    'X': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'V': [0, 1, 4, 9, 16, 25, 36, 49, 64, 81, 100]
}

# all parameters
params = {
    'plotter': {
        'type': 'line',
        'x_label': 'x',
        'y_label': '$x^{2}$'
    }
}

# initialize the plotter
plotter = MPLPlotter(axes, params['plotter'])
# display the plot
plotter.show(True)
```

### Utils

Utility functions provide an extra layer of ease over the other modules.
For example, the `qom.utils.wrappers` module contain various functions that wrap loopers and systems, together with an option to use plotter modules to visualize the results trimming several lines of code.

A complete API documentation is available in the [official website](https://sampreet.github.io/qom).

## Contributing

If you want to contribute to The Quantum Optomechanics Toolbox, check out the [contribution guidelines](./CONTRIBUTING.md).
Also, make sure you adhere to the [code of conduct](./CODE_OF_CONDUCT.md).