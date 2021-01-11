# Changelog

## v0.6.1 - 2021/01/11 - 00 - SciPy Integration APIs
* Updated `qom/solvers`:
    * Updated displaying and solving in `HLESolver` module.
    * Added new `scipy.integrate` API wrappers in `ODESolver` module.
* Minor updates to `qom/systems/BaseSystem` module.
* Dependency fixes to all modules.

## v0.6.0 - 2021/01/09 - 00 - Minor Fixes
* Minor fixes to `qom/loopers/BaseLooper` module.
* Added log in `qom/solvers/HLESolver` module.
* Updated `README`.

## v0.6.0 - 2021/01/08 - 00 - Minor Fixes
* Fixed axis value rounding in `qom/loopers/BaseLooper` module.
* Added file compression in `qom/solvers/HLESolver` module.

## v0.6.0 - 2021/01/07 - 00 - Updated Solvers
* Fixed axis values in `qom/loopers/BaseLooper` module and minor updates.
* Updated `qom/solvers`:
    * Added option to save dynamics in `HLESolver` module.
    * Minor updates to `ODESolver` module.
    * Added correlation element method to `QCMSolver` module.
* Added dynamics range in `qom/systems/BaseSystem` module.
* Updated `README`.

## v0.6.0 - 2021/01/06 - 00 - Clean-up and Revamp
* Updated documentation in `docs`.
* Updated `qom/examples/qom_loopers_XLooper` notebook.
* Updated `qom/loopers`:
    * Moved `dynamics`, `measures` and `properties` modules to `qom_legacy/loopers`.
    * Minor updates and fixes to other modules.
* Moved `qom/measures` and `qom/numerics` to `qom_legacy`.
* Updated `qom/solvers`:
    * Updated `HLESolver` module to handle number of modes.
    * Minor updates and fixes to other modules.
* Updated `qom/systems`:
    * Added option to plot via `BaseSystem` module.
    * Minor fixes to other modules.
* Updated `qom/ui`:
    * Moved `Figure` module to `qom_legacy/ui`.
    * Minor updates and fixes to modules in `axes` and `plotters`.
* Moved `qom/utils` to `qom_legacy`.
* Renamed `qom_experimental/wrappers` to `qom_tf/loopers`.
* Added dynamics calculation methods to `qom/systems/BaseSystem` module.
* Removed `LICENSE`.
* Updated `README`.

## v0.5.9 - 2021/01/05 - 00 - Updated Measures
* Updated `qom/solvers`:
    * Minor fixes to `ODESolver` and `HLESolver` modules.
    * Added discord and entanglement methods to `QCMSolver` module.
* Added dynamics calculation methods to `qom/systems/BaseSystem` module.

## v0.5.8 - 2021/01/04 - 00 - Templated Measure Solvers
* Minor fixes to `qom/loopers/BaseLooper`.
* Updated `qom/solvers`:
    * Added `ODESolver` to solve ODEs.
    * Added `HLESolver` to solve Heisenberg-Langevin equations.
    * Added `QCMSolver` for quantum correlation measures.

## v0.5.7 - 2021/01/01 - 00 - Interfaced Gradients
* Updated `qom/loopers`:
    * Added `XYZLooper` for 3D looping.
    * Updated `BaseLooper`, `XLooper` and `XYLooper` with gradient options.
* Moved `qom/numerics/RHCriterion` to `qom/solvers/RHCSolver`.
* Updated `qom/ui`:
    * Minor fixes to `axes` modules.
    * Updated `BasePlotter` and `MPLPlotter` with V-axis.
    * Fixes to `Figure` and `log` modules.

## v0.5.6 - 2020/12/21 - 01 - Templated Loopers
* Updated `qom/loopers`:
    * Added `BaseLooper` with multithreading and multiprocessing methods.
    * Added `XLooper`, `XYLooper` and `XZLooper` for 1D and 2D looping.
    * Removed `init_log` method from `__init__`.
* Updated `qom/systems` modules.

## v0.5.5 - 2020/12/21 - 00 - Minor Fixes
* Fixed `qom/numerics/RHCriterion` module with 0-based indexing.
* Updated `qom/systems/BaseSystem` module data types.

## v0.5.5 - 2020/12/08 - 00 - Updated Modules
* Added support for coefficient initialization in `qom/numerics/RHCriterion` module.
* Updated `qom/systems/BaseSystem` with option to select basic or cubic solutions for mean optical amplitude and occupancy.

## v0.5.4 - 2020/12/04 - 00 - Added Sphinx Docs
* Added Sphinx API documentation sources and builders to `docs`.
* Updated documentation of all packages to NumPy style docstrings.
* Initialized optomechanical systems in `qom/systems` package.
* Changed all occurences of `model` to `system`.

## v0.5.3 - 2020/12/03 - 00 - Routh-Hurwitz Criterion
* Added `qom/numerics/RHCriterion` module.
* Fixed axis error in `qom/ui/plotters/BasePlotter` module.
* Minor changes to `qom/ui/Figure` module.

## v0.5.2 - 2020/12/02 - 00 - Exception Handling
* Minor fixes to `qom/loopers/dynamics` and `qom/loopers/measures` modules.
* Exception handling in modules under `qom/ui`.

## v0.5.1 - 2020/11/17 - 00 - Intermediate Commit
* Updated `qom/loopers/measures` and `qom/loopers/properties` modules.
* Minor fixes to `qom/ui/plotters`.

## v0.5.0 - 2020/10/23 - 00 - Minor Fixes
* Updated `examples/qom_looper_properties`.
* Renamed `qom/ui/figure` to `qom/ui/Figure`.
* Minor fixes to `qom/ui/plotters`.

## v0.5.0 - 2020/10/22 - 00 - Revamped Figure
* Updated `qom/ui/loopers` modules with axis classes.
* Added axis classes to `qom/ui/axes`:
    * `DynamicAxis` handles variable axis.
    * `MultiAxis` handles multi 1D plots.
    * `StaticAxis` handles the static axes.
* Updated `qom/ui/plotters`:
    * Changed `BasePlotter` to handle axis classes.
    * Added `MPLPlotter` to handle `matplotlib` and axis classes.
    * Moved previous versions to `qom_legacy/ui/plotters`.
* Renamed `Plotter` to `Figure` class in `qom/ui/figure` module.
* Moved `qom/utils/axis` module to `qom_legacy/utils`.
* Updated `examples/qom_loopers_properties`.

## v0.4.9 - 2020/10/19 - 00 - Minor Fixes
* Minor fixes to `qom/ui/plotters` and `qom/utils`.
* Initialized axes classes in `qom_experimental/ui/axes`.

## v0.4.9 - 2020/10/09 - 00 - Added Contour Plot
* Updated `qom/ui/plotters`:
    * Minor fixes to `BasePlotter` object.
    * Added support for contour plot in `PlotterMPL` object.
* Minor changes to `qom/utils/misc` modules.

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