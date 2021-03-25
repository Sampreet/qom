# The Quantum Optomechanics Toolbox

> A library of modules for computational quantum optomechanics!

## Key Features

* Automatically managed loops and parameter validation modules.
* Solver modules to calculate classical and quantum signatures.
* Inheritable optomechanical systems supporting callable properties.
* Configurable visualizations without the need for explicit plotting.

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
The complete example can be found in the [`XLooper Example`](./examples/qom_loopers_XLooper.ipynb) notebook.

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
The complete example can be found in the [`HLESolver Example`](./examples/qom_solvers_HLESolver.ipynb) notebook.


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
The complete example can be found in the [`SOSMSystem Example`](./examples/qom_systems_SOSMSystem.ipynb) notebook.

### UI

#### Plotters

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

## Development

### Dependencies

The project requires `Python 3.7+` installed, preferably via the [Anaconda distribution](https://www.anaconda.com/products/individual).

*Some modules also use tensor-based calculations with the CPU/GPU libraries of `TensorFlow`, an installation guide for which can be found in [Anaconda's  Documentation](https://docs.anaconda.com/anaconda/user-guide/tasks/tensorflow/).*

### Structure of the Repository

```
ROOT_DIR/
|
│───docs/
│   ├───source/
│   │   ├───conf.py
│   │   ├───foobar.rst
│   │   └───...
│   │   
│   ├───make.bat
│   └───Makefile
|
│───examples/
│   ├───foo_bar.ipynb
│   └───...
|
│───qom/
│   ├───loopers/
│   │   ├───__init__.py
│   │   ├───FooBarLooper.py
│   │   └───...
│   │   
│   ├───solvers/
│   │   ├───__init__.py
│   │   ├───FooBarSolver.py
│   │   └───...
│   │   
│   ├───systems/
│   │   ├───__init__.py
│   │   ├───FooBarSystem.py
│   │   └───...
│   │   
│   ├───ui/
│   │   ├───axes/
│   │   │   ├───__init__.py
│   │   │   ├───FooBarAxis.py
│   │   │   └───...
│   │   │
│   │   ├───plotters/
│   │   │   ├───__init__.py
│   │   │   ├───FooBarPlotter.py
│   │   │   └───...
│   │   │
│   │   ├───widgets/
│   │   │   ├───icons/
│   │   │   │   ├───foo_bar.png
│   │   │   │   └───...
│   │   │   │
│   │   │   ├───stylesheets/
│   │   │   │   ├───foo_bar.ss
│   │   │   │   └───...
│   │   │   │
│   │   │   ├───__init__.py
│   │   │   ├───FooBarWidget.py
│   │   │   └───...
│   │   │
│   │   ├───__init__.py
│   │   ├───gui.py
│   │   └───log.py
│   │   
│   └───__init__.py
|
│───qom_tf/
│   └───...
│
├───.gitignore
├───CHANGELOG.md
├───MANIFEST.in
├───README.md
├───requirements.txt
└───setup.py
```

### Installing in Editable Mode

To install the package in editable mode, execute the following from *outside* the top-level directory, `ROOT_DIR`, inside which `setup.py` is located:

```bash
pip install -e ROOT_DIR
```

### Building the Documentation

To auto-generate and build the API documentation, navigate to the `ROOT_DIR/docs` folder and execute:

```bash
sphinx-apidoc -o source ../qom
make html
```

