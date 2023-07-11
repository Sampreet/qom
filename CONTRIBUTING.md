# Contributing to The Quantum Optomechanics Toolbox

[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-1.2-4baaaa.svg?style=for-the-badge)](./CODE_OF_CONDUCT.md)

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
├───docs/
│   ├───images/
│   │   ├───foobar.png
│   │   └───...
│   │
│   ├───source/
│   │   ├───conf.py
│   │   ├───foobar.rst
│   │   └───...
│   │
│   ├───make.bat
│   └───Makefile
|
├───qom/
│   ├───loopers/
│   │   ├───__init__.py
│   │   ├───axes.py
│   │   └───base.py
│   │
│   ├───solvers/
│   │   ├───__init__.py
│   │   ├───base.py
│   │   ├───deterministic.py
│   │   ├───differential.py
│   │   ├───measure.py
│   │   └───stability.py
│   │
│   ├───systems/
│   │   ├───__init__.py
│   │   └───base.py
│   │
│   ├───ui/
│   │   ├───plotters/
│   │   │   ├───__init__.py
│   │   │   ├───base.py
│   │   │   └───matplotlib.py
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
│   │   ├───loopers.py
│   │   └───solvers.py
│   │
│   ├───__init__.py
│   └───io.py
|
├───.gitignore
├───CHANGELOG.md
├───CITATION.bib
├───CODE_OF_CONDUCT.md
├───CONTRIBUTING.md
├───LICENSE
├───MANIFEST.in
├───pyproject.toml
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