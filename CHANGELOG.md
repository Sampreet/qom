# Changelog

## v0.4.8 - 2020/10/06 - 00 - Added 3D Plots
* Updated `qom/ui`:
    * Minor fixes to `figure` module.
    * Added `BasePlotter` module inside `plotters` module.
    * Updated 2D and 3D plotting methods in `PlotterMPL` module.
    * Initialized `PlotterPlotly` module.
* Minor changes to `qom/utils/axis` and `qom/utils/misc` modules.

## v0.4.6 - 2020/10/03 - 00 - Added Plotters
* Minor fixes to modules in `qom/loopers`.
* Updated `qom/ui`:
    * Updated `Plotter` class in `figure` module. 
    * Added `plotters` module to handle different types of plotters. 
* Added properties and handled attributes in `qom/utils/axis`.
* Updated `README`.

## v0.4.5 - 2020/09/29 - 00 - Attribute Handling
* Minor fixes to `measures` and `properties` modules in `qom/loopers`.
* Handled ticks and attribute fixes in `qom/ui/figure` module.
* Handled null attributes is `qom/utils/axis` module.

## v0.4.4 - 2020/09/27 - 02 - Minor Fixes
* Minor fixes to `examples/qom_loopers_properties` notebook.
* Updated `README` and `setup`.

## v0.4.3 - 2020/09/27 - 01 - Example Notebook
* Added `qom_loopers_properties` notebook in `examples`.
* Updated `qom/loopers`:
    * Handled attribute errors in `measures` module. 
    * Updated script and model attributes in `properties` module. 
* Updated `.gitignore` and `README`.

## v0.4.2 - 2020/09/27 - 00 - Restructured Modules
* Moved `qom/wrappers` to `qom/loopers`:
    * Removed limit function from `dynamics` module.
    * Removed threshold function from `measures` module. 
    * Removed threshold and gradient functions from `properties` module. 
* Renamed modules in `qom/measures`.
* Added `qom/numerics`:
    * Added `calculators` module for functions.
    * Added `solvers` module for equations.
* Updated font properties and added plot limits to `qom/ui/figure` module.
* Updated `qom/utils`:
    * Minor fixes to `axis` module.
    * Added `misc` module for miscellaneous utilities.
* Moved `qom/experimental` and `qom/legacy` to `qom_experimental` and `qom_legacy` with minor fixes to modules.
* Renamed `LICENSE`.
* Updated `README`, `requirements` and `setup`.

## v0.4.0 - 2020/09/23 - 00 - Revamped Modules
* Added `qom/experimental` module for experimental features:
    * Moved `qom/wrappers/dynamics_tf` to `qom/experimental/wrappers`.
    * Added logger initialization to `qom/experimental/wrappers/__init__`.
* Added `qom/legacy` module for legacy features:
    * Moved `qom/ui/figure` to `qom/legacy/ui`.
    * Moved `qom/wrappers/dynamics` to `qom/legacy/wrappers`.
    * Added logger initialization to `qom/legacy/wrappers/__init__`.
* Updated `qom/ui`:
    * Updated `figure` module for 1D and 2D plots.
    * Minor fixes to `log` module.
* Added `qom/utils` module for utility functions:
    * Added `axis` module for dynamic and static axes.
* Updated `qom/wrappers`:
    * Revamped `dynamics` module to handle multi-system models.
    * Added multi-line plots inside `measures` module and minor fixes.
    * Updated `properties` module to support dynamic and static axes.
* Updated `README`.
* Updated `setup`.

## v0.3.5 - 2020/09/04 - 00 - Added dynamics_tf Wrapper
* Updated `qom/ui`:
    * Minor fixes to `figure` module.
    * Added custom formatter for `log` module.
* Updated `qom/wrappers`:
    * Added `dynamics_tf` module implementing tensorflow-based integration.
    * Restructured `dynamics` module save/load blocks.
    * Minor fixes to `measures` and `properties` modules.
* Updated `setup`.

## v0.3.3 - 2020/08/24 - 00 - Added Difference Measures
* Updated `qom/measures`:
    * Added `diff` module for difference measures.
    * Added looped calculation in `corr` module.
* Updated `qom/wrappers`:
    * Removed looped calculation from `dynamics` module.
    * Updated calculation of average measures in `measures` module.
    * Minor fixes to `properties` module.
* Updated `README`.
* Updated `setup`.

## v0.3.2 - 2020/08/18 - 00 - Updated Wrappers
*  Updated `qom/measures`:
    * Added switch function in `corr` module.
    * Minor fixes to function parameters in `corr` module.
* Updated color options in `qom/ui/figure` module.
* Updated `qom/wrappers`:
    * Added switch functions to `dynamics` and `measures` modules.
    * Added cache options and updated parameters in `dynamics` module.
    * Revamped `measures` module functions.
    * Minor fixes to `properties` module.
* Updated `setup`.

## v0.3.0 - 2020/07/24 - 00 - Added Gradients
* Created UI modules.
    * Added support for multi-line plots to `qom/ui/figure`.
    * Minor fixes to `qom/ui/figure`.
* Updated wrapper modules.
    * Restructured `qom/warppers/properties`.
    * Added gradient functions to `qom/warppers/properties`.
* Updated `requirements`.
* Updated `setup`.

## v0.2.5 - 2020/06/24 - 00
* Created UI modules.
    * Created `qom/ui/figure` for plotting figures.
    * Moved `qom/wrappers/logs` to `qom/ui/logs`.
    * Removed `qom/wrappers/plot`.
* Updated wrapper modules.
    * Added `qom/wrappers/measures` to calculate measures from dynamics.
    * Added `qom/wrappers/properties` to calculate properties.
    * Updated `qom/wrappers/__init__` for UI initialization.
    * Minor fixes to `qom/wrappers/dynamics`.
* Updated `README`.

## v0.2.1 - 2020/06/15 - 00

* Added `qom/wrappers/cvar` for continuous variable calculations.
* Updated `qom/wrappers/dyna` to calculate initial values on function call.
* Minor fixes to `qom/wrappers/plot`. 

## v0.2.0 - 2020/06/09 - 01

* Restructured modules based on `PyPI` package documentation.
    * Created `setup` for installation.
    * Created `requirements` file.
    * Added MIT license.
* Renamed `modules/measures/quantum_correlations` to `qom/measures/corr`.
    * Removed object-oriented implementation.
    * Shortened module functions.
    * Implemented module logger.
* Renamed `controllers/solver_dynamics` to `qom/wrappers/dyna`.
    * Updated functions for measures and system dynamics.
    * Implemented module logger.
* Renamed `helpers/logger_console` to `qom/wrappers/logs`.
    * Added initialization of main logger and singleton usage.
* Renamed `helpers/plotter_2D` to `qom/wrappers/plot`.
    * Updated functions.

## v0.1.4 - 2020/06/09 - 00

* Updated `quantum_correlations` with rotated phase measure.
* Updated `plotter_2D` with contour plot.
* Updated `solver_dynamics` with cache option.

## v0.1.3 - 2020/05/01 - 00

* Added `solver_dynamics` wrapper for integration and calculation of measures.
* Updtaed `plotter_2D` with scatter plot.
* Created `controllers` folder to include control functions and wrappers.
* Renamed `properties` to `measures`.