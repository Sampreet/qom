# The Quantum Optomechanics Toolbox

> A library of modules for computational quantum optomechanics.

## Key Features

* Calculation of several quantum properties and quantum measures.
* Automatically managed and optimized wrappers implementing loops.
* Configurable visualizations without the requirement for plotting explicitly.

## Usage

The library features easy-to-use functions to easily calculate as well as visualize the trend of several quantum signatures.
For example, the `qom.looper.properties` module can be implemented as:

```python
Values, Thresholds, Axes = properties.calculate(my_model, script_data)
```

Here, `my_model` is a python class describing the system and `script_data` is a dictionary containing the data for calculation of the properties and the parameters for visualization of the results.

Examples on usage of various modules can be found in the [`examples`](./examples) folder.

## Development

### Dependencies

The project requires `Python 3.7+` installed for the specific operating system, preferably via the [Anaconda distribution](https://www.anaconda.com/products/individual).

*Note: Some modules use tensor-based calculations with the CPU/GPU libraries of `TensorFlow`, an installation guide for which can be found in [Anaconda's  Documentation](https://docs.anaconda.com/anaconda/user-guide/tasks/tensorflow/).*

### Structure

The repository follows the following structure:

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
│   ├───foo/
│   │   ├───__init__.py
│   │   ├───bar.py
│   │   └───...
│   │   
│   └───__init__.py
|
│───qom_experimental/
│   ├───foo/
│   │   ├───__init__.py
│   │   ├───bar.py
│   │   └───...
│   │   
│   └───__init__.py
|
│───qom_legacy/
│   ├───foo/
│   │   ├───__init__.py
│   │   ├───bar.py
│   │   └───...
│   │   
│   └───__init__.py
|
│───tests/
│   └───...
│
├───.gitignore
├───CHANGELOG.md
├───LICENSE
├───README.md
├───requirements.txt
└───setup.py
```


