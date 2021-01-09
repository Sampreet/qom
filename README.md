# The Quantum Optomechanics Toolbox

> A library of modules for computational quantum optomechanics!

## Key Features

* Automatically managed and optimized modules to implement loops.
* Solver modules to calculate classical as well as quantum signatures.
* Configurable visualizations without the need for explicit plotting.

## Basic Usage

The library features easy-to-use functions to easily calculate as well as visualize the trend of several quantum signatures.
For example, the `qom.looper.XLooper` module can be implemented as:

```python
XLooper(func, params).loop()
```

Here, `func` is a function containing the steps of each iteration and `params` is a dictionary containing the parameters required for the looper, solver, system and plotter.

Examples on usage of various modules can be found in the [`examples`](./examples) folder.

## Development

### Dependencies

The project requires `Python 3.7+` installed, preferably via the [Anaconda distribution](https://www.anaconda.com/products/individual).

*Some modules also use tensor-based calculations with the CPU/GPU libraries of `TensorFlow`, an installation guide for which can be found in [Anaconda's  Documentation](https://docs.anaconda.com/anaconda/user-guide/tasks/tensorflow/).*

### Structure of the Repository

```
ROOT_DIR/
|
│───docs/
│   └───...
|
│───examples/
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
│   │   ├───__init__.py
│   │   ├───foobar.py
│   │   └───...
│   │   
│   └───__init__.py
|
│───qom_legacy/
│   └───...
|
│───qom_tf/
│   └───...
|
│───tests/
│   └───...
│
├───.gitignore
├───CHANGELOG.md
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

