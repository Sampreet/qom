# Contributing to The Quantum Optomechanics Toolbox

Feel free to contribute to the code by forking this repository in your profile.
All pull requests from subsequent branches will be reviewed.
If you encountered any bugs while using the package, kindly report them in the [issues](https://github.com/Sampreet/qom/issues) page.
Your contribution will be accordingly acknowledged.

## Development

### Structure of the Repository

The repository follows the following template:

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
│   ├───utils/
│   │   ├───__init__.py
│   │   ├───foo_bar.py
│   │   └───...
│   │   
│   └───__init__.py
|
│───qom_tf/
│   └───...
│
├───.gitignore
├───_config.yml
├───CHANGELOG.md
├───CONTRIBUTING.md
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