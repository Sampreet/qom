# Quantum Optomechanics

> A Python-based repository of *library modules* for computational Quantum Optomechanics.

## Development

### Dependencies

#### Python

The project requires ```Python 3.7+``` installed using the [Anaconda Distribution](https://www.anaconda.com/distribution/#download-section) for the specific operating system.

#### PyCUDA

Some modules require CUDA-capable hardware for parallelized calculations and hence require the installation of CUDA. For Anaconda-based Python installation, ```PyCUDA```, along with its dependencies can be installed by executing the following command in the terminal:

```
conda install pycuda
```

A complete guide for installation of all dependencies is available in my [GPU-Accelerated Deep Learning guide](https://github.com/Sampreet/install-guides/blob/master/languages/python/GPU-accelerated-deep-learning-Keras-Tensorflow-Theano-PyCUDA.md) with the packages mentioned replaced by the latest VS Community and Anaconda packages. A separate python environment for ```PyCUDA``` is preferable.

#### Tensorflow

Some modules use tensor-based calculations with ```Tensorflow```, which can be installed by executing the following command in the terminal:

```
conda install tensorflow
```

For CUDA-capable devices, the GPU version of ```Tensorflow``` can be installed using:

```
conda install tensorflow-gpu
```

A complete guide for installation of ```Tensorflow``` can be found in [Anaconda's  Documentation](https://docs.anaconda.com/anaconda/user-guide/tasks/tensorflow/). A separate python environment for ```Tensorflow``` is preferable.

### Project Structure

The repository follows the following structure:

```
ROOT_DIR/
|
│───docs/
│   ├───__init__.py
│   └───...
|
│───examples/
│   ├───__init__.py
│   └───...
|
│───qom/
│   │
│   ├───experimental/
│   │   ├───__init__.py
│   │   └───...
│   │
│   ├───legacy/
│   │   ├───__init__.py
│   │   └───...
│   │
│   ├───measures/
│   │   ├───__init__.py
│   │   └───...
│   │
│   ├───ui/
│   │   ├───__init__.py
│   │   └───...
│   │
│   ├───wrappers/
│   │   ├───__init__.py
│   │   └───...
│   │   
│   └───__init__.py
|
│───tests/
│   │───__init__.py
│   └───...
│
├───.gitignore
├───CHANGELOG.md
├───LICENSE.txt
├───README.md
├───requirements.txt
└───setup.py
```


