# Changelog

## v0.2.5 - 2020/06/24 - 00
* Created UI modules.
    * Created ```qom/ui/figure``` for plotting figures.
    * Moved ```qom/wrappers/logs``` to ```qom/ui/logs```.
    * Removed ```qom/wrappers/plot```.
* Updated wrapper modules.
    * Added ```qom/wrappers/measures``` to calculate measures from dynamics.
    * Added ```qom/wrappers/properties``` to calculate properties.
    * Updated ```qom/wrappers/__init__``` for UI initialization.
    * Minor fixes to ```qom/wrappers/dynamics```.
* Updated ```README```.

## v0.2.1 - 2020/06/15 - 00

* Added ```qom/wrappers/cvar``` for continuous variable calculations.
* Updated ```qom/wrappers/dyna``` to calculate initial values on function call.
* Minor fixes to ```qom/wrappers/plot```. 

## v0.2.0 - 2020/06/09 - 01

* Restructured modules based on ```PyPI``` package documentation.
    * Created ```setup``` for installation.
    * Created ```requirements``` file.
    * Added MIT license.
* Renamed ```modules/measures/quantum_correlations``` to ```qom/measures/corr```.
    * Removed object-oriented implementation.
    * Shortened module functions.
    * Implemented module logger.
* Renamed ```controllers/solver_dynamics``` to ```qom/wrappers/dyna```.
    * Updated functions for measures and system dynamics.
    * Implemented module logger.
* Renamed ```helpers/logger_console``` to ```qom/wrappers/logs```.
    * Added initialization of main logger and singleton usage.
* Renamed ```helpers/plotter_2D``` to ```qom/wrappers/plot```.
    * Updated functions.

## v0.1.4 - 2020/06/09 - 00

* Updated ```quantum_correlations``` with rotated phase measure.
* Updated ```plotter_2D``` with contour plot.
* Updated ```solver_dynamics``` with cache option.

## v0.1.3 - 2020/05/01 - 00

* Added ```solver_dynamics``` wrapper for integration and calculation of measures.
* Updtaed ```plotter_2D``` with scatter plot.
* Created ```controllers``` folder to include control functions and wrappers.
* Renamed ```properties``` to ```measures```.