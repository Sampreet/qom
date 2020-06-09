# Changelog

## 20200609 - 01 - v0.1.5

* Restructured modules based on ```PyPI``` package documentation.
* Renamed ```modules/measures/quantum_correlations``` to ```qom/measures/corr``` and removed object-oriented implementation.
* Renamed ```controllers/solver_dynamics``` to ```qom/wrappers/dyna``` and added .
* Renamed ```helpers/logger_console``` to ```qom/wrappers/logs``` with steam handling initialization.
* Renamed ```helpers/plotter_2D``` to ```qom/wrappers/plot```.
* Created ```setup``` for installation.
* Created ```requirements``` file.
* Added MIT license.

## 20200609 - 00 - v0.1.4

* Updated ```quantum_correlations``` with rotated phase measure.
* Updated ```plotter_2D``` with contour plot.
* Updated ```solver_dynamics``` with cache option.

## 20200501 - 00 - v0.1.3

* Added ```solver_dynamics``` wrapper for integration and calculation of measures.
* Updtaed ```plotter_2D``` with scatter plot.
* Created ```controllers``` folder to include control functions and wrappers.
* Renamed ```properties``` to ```measures```.