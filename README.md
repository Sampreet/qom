# The Quantum Optomechanics Toolbox

> A library of modules for computational quantum optomechanics.

## Key Features

* Calculate quantum properties and quantum measures with automatically managed loops.
* Configure numerous plot parameters without getting into plotting syntax.
* 

## Usage

### Looping Through Properties

Create a model for the quantum system following the schematic below:

```python
# demo class
class Model:
    """Class containing the model.

    Attributes
    ----------
        name : str
            Name of the model
        
        code : str
            Short code for the model

        params : dict
            Base parameters for the model.
    """
    
    # demo attributes
    name = 'My Model Class'
    code = 'mmc'
    params = {
        'x': 2.0
    }

    # demo property function
    def square(self):
        """Function to obtain square value.
            
        Returns
        -------
            y : float
                Square of the parameter.
        """

        return self.params['x']**2
```

Now, add the following to loop through property `square`:

```python
# dev dependencies
from qom.loopers import dynamics

# data for modules
script_data = {
    # property parameters
    'prop_params': {
        # function in the library
        'func': 'properties_1D',
        # function in the model
        'code': 'square',
        # name of the function
        'name': 'Square',
        # variable in the x-axis
        'X': {
            'var': 'x',
            'min': -5,
            'max': 5,
            'steps': 1001
        }
    },
    # option to show plot
    'plot': True,
    # plot parameters
    'plot_params': {
        # option to show progress on plot
        'progress': True, 
        # plot title
        'title': 'Square Function',
        # axis labels
        'x_label': '$x$',
        'y_label': '$x^{2}$',
        # line plot
        'type': 'line'
    }
}

# calculate properties
properties.calculate(Model(), script_data)
```

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


