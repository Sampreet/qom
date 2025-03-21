# Changelog

## v1.1.0 - 2025/03/11 - 02 - Minor Fixes to Plotters
* Minor fixes to `qom.ui.plotters.matplotlib` module and `README`.

## v1.1.0 - 2025/03/11 - 01 - Minor Fixes to Docs
* Minor fixes to `docs` and `README`.

## v1.1.0 - 2025/03/11 - 00 - Bump NumPy Version
* Updated all modules to support NumPy 2.x.x.
* Added deprecation warning to `qom.solvers.stochastic.MCQTSolver` class.
* Updated `requirements` and `setup`.
* Updated documentation and `README`.

## v1.0.2 - 2024/06/23 - 00 - GUI Hotfix
* String support in axis values in `qom.loopers.base.BaseLooper` class.
* Updated `qom.solvers` package:
    * Added `required_params` in `deterministic` module.
    * Minor fixes to `measure` and `stability` modules.
    * Separate functions for operators and coefficients in `stochastic.MCQTSolver` class.
* Fixed `qom.ui.widgets` modules.
* Add Pauli operators in `qom.misc` module.
* Updated `CITATION` and `README`.

## v1.0.1 - 2023/10/04 - 00 - MCQT Solver and Two-mode Wigner
* Minor fixes to `qom.solvers.deterministic` module.
* Updated `qom.solvers.measure` module:
    * Added support for two-mode Wigner distribution.
    * Minor fixes to single-mode Wigner distribution.
* Added `qom.solvers.deterministic` module with the `MCQTSolver` class for Monte-Carlo quantum trajectories.
* Updated `qom.ui.plotters` package:
    * Added support for legend range selection in `base` module.
    * Added option to import legend from Y-axis data in `matplotlib` module.
    * Added option for z-order of scatter plots in `matplotlib` module.
* Added parallelization support for Monte-Carlo quantum trajectories solver in `qom.utils.solvers` module.
* Added `qom.misc` module for operators and state vectors.
* Minor fixes to `qom.io` module.
* Updated logging for all modules.
* Updated documentation.
* Updated `README`.

## v1.0.0 - 2023/07/20 - 00 - Updated README
* Updated `docs/source/index`.
* Removed `pyproject.toml`.
* Updated `README`.

## v1.0.0 - 2023/07/13 - 00 - Updated README
* Updated `docs/source/index`.
* Updated `README`.

## v1.0.0 - 2023/07/12 - 00 - Updated Documentation
* Updated docstrings in all modules.
* Added option to select DPI while saving plots.
* Minor fixes to `qom.loopers.base` module.
* Updated `README`.

## v1.0.0 - 2023/07/11 - 00 - Stable Numerics
* Updated `qom.loopers.BaseLooper` module:
    * Removed looper function arguments for value, logger and results. New format is `func(system_params)`.
    * Added option to prefix saved file with system parameters.
    * Support for broadcasting of X-axis results with uneven dimensions.
    * Removed multithreading and plotting support. Multiprocessing and plotting support are now available in `qom.utils.loopers` module.
    * Removed experimental features for calculating gradients.
    * Minor fixes and updated documentation.
    * Renamed to `qom.loopers.base`.
* Clubbed `qom.loopers.XLooper`,  `qom.loopers.XYLooper` and `qom.loopers.XYZLooper` into `qom.looper.axes` module with minor fixes.
* Revamped `qom.solvers.HLESolver` module:
    * Streamlined `set_results` and `solve` methods of `HLESolver` class.
    * Added methods `get_times`, `get_mode_intensities`, `get_mode_indices`, `get_corr_indices` to `HLESolver` class.
    * Added `SSHLESolver` class for steady state solutions.
    * Added `LLESolver` and `NLSESolver` classes for solving Lugiato-Lefever equations (LLEs) and Non-linear Schrodinger equations (NLSEs).
    * Renamed to `qom.solvers.deterministic`.
* Renamed `qom.solvers.ODESolver` module to `qom.solvers.differential` with minor fixes to `ODESolver` class.
* Updated `qom.solvers.QCMSolver` module:
    * Updated constructor and added validation checks for `QCMSolver` class. Current constructor supports multiple mode and correlation arrays.
    * Added `get_measures` method in `QCMSolver` to batch-calculate measures for significant speedup.
    * Added method for entanglement calculation using matrices (currently default) and updated helper methods for batch mode in `QCMSolver`.
    * Added functions to calculate classical correlation measures (`get_average_amplitude_difference`, `get_average_phase_difference` and `get_correlation_Pearson`) and Lyapunov exponents (`get_Lyapunov_exponents`), detect bistability and multistability zones (`get_stability_zone`), obtain system measures (`get_system_measures`) and generate single-mode Wigner probability distributions (`get_Wigner_distributions_single_mode`).
    * Renamed to `qom.solvers.measure`.
* Updated `qom.solvers.RHCSolver` module:
    * Updated constructor and added validation checks for `RHCSolver` class. Current constructor supports multiple drift matrix or coefficient arrays.
    * Sped up SymPy-dependent methods and added `get_counts` method to `RHCSolver` class.
    * Added support for calculation of instability counts using eigenvalues of the drift matrix in `get_counts_from_eigenvalues` function.
    * Renamed to `qom.solvers.stability`.
* Removed `SOSMSystem`, `SODMSystem`, `DOSMSystem`, `DODMSystem` and `SOMASystem` modules. Only the `BaseSystem` class in the `base` module can be used for interfacing user-defined systems. The many-body dynamics solvers earlier available in the `SOMASystem` module are now available in the `qom.solvers.deterministic` module.
* Revamped `qom.systems.BaseSystem` module:
    * Moved all solver methods of `BaseSystem` class to `qom.solvers.deterministic` module and measure calculation methods to `qom.solvers.measure` module.
    * Minor fixes and speedups to ODE functions in `BaseSystem` class.
    * Updated documentation with more formatting options for user-defined functions.
    * Renamed to `qom.systems.base`.
* Updated `qom.ui.plotters` package:
    * Minor fixes to `BasePlotter` and `MPLPlotter` modules.
    * Added support for label colors and additional scatter plots in `MPLPlotter` module.
    * Updated documentations and renamed `BasePlotter` and `MPLPlotter` modules to `base` and `matplotlib`.
* Clubbed `qom.ui.axes.BaseAxis` and `qom.ui.axes.MultiAxis` modules into `qom.ui.plotters.base`.
* Removed `qom.ui.axes.DynamicAxis` and `qom.ui.axes.StaticAxis`.
* Updated `qom.utils.looper` module:
    * Removed solver functions and streamlined multiprocessing functions.
    * Renamed to `qom.utils.loopers`.
* Added `qom.utils.solvers` module to handle solver options.
* Added `qom.io` module with support for IO operations.
* Updated documentation for numerical packages and added demos.
* Added `CITATION.bib` and `pyproject.toml`.
* Updated `requirements`, `setup` and `README`.

## v0.9.0 - 2023/01/29 - 00 - Minor Fixes
* Updated documentation of `qom.systems.BaseSystem` and `qom.ui.axes.BaseAxis` modules.
* Minor fixes for 3D plot linewidths in `qom.ui.plotters.MPLPlotter` module.
* Minor fixes to parellel instances in `qom.utils.looper` module.
* Minor updates to docsources.

## v0.9.0 - 2022/11/08 - 00 - Multiprocessing Support
* Updated `qom.loopers.BaseLooper` module:
    * Added process variables to support object multiprocessing.
    * Removed multiprocessor mode from `loop` method.
    * Updated params for saving/loading data.
    * Exception handling for single value.
* Revamped progress outputs for `qom.loopers`, `qom.solvers` and `qom.systems` modules.
* Updated `qom.systems.BaseSystem` module:
    * Support for constant drift and noise matrices.
    * Revamped progress outputs and restructured IVP parameters.
* Support for unformatted output in `qom.ui.log` module.
* Minor fixes to `qom.ui.plotters.BasePlotter` module.
* Updated option for palette colors and minor fixes in `qom.ui.plotters.MPLPlotter` module.
* Updated `qom.utils.looper` module:
    * Added `run_loopers_in_parallel` function to multiprocess `wrap_looper` function and merge results. Removed `merge_xy_loopers` function.
    * Added support for multiprocessing in `wrap_looper` function.
* Updated `README` and `setup`.

## v0.8.6 - 2022/09/06 - 00 - Wigner and LLE Support
* Minor fixes to `qom.solvers.ODESolver` module.
* Added single-mode Wigner function in `qom.systems.BaseSystem` module.
* Added LLE dynamics solver function in `qom.system.SOMASystem` module.
* Updated `qom.ui.plotters` package:
    * Fixed limits and ticks for plots and colorbar.
    * Updated outline size with figure size.
    * Added option for vertical patches with `vspan` key.
* Minor fixes to `qom.ui.widgets.SystemWidget` and `qom.utils.looper` modules.
* Updated `README` and `setup`.

## v0.8.5 - 2022/05/17 - 00 - Twin Axis Support
* Minor fixes to progress methods in `qom.loopers`, `qom.solvers` and `qom.systems`.
* Added option for label and tick color in `qom.ui.axes`.
* Added support for twin axis in `qom.ui.plotters`.
* Updated `README` and `setup`.

## v0.8.4 - 2022/05/27 - 00 - Updated 3D Plots
* Minor fixes to `qom.loopers.BaseLooper` and `qom.solvers.RHCSolver` modules.
* Updated `qom.ui.plotters` package:
    * Added 3D line, scatter and density plots with support for unit sphere.
    * Updated color selection to support extreme colors for dual plots.
    * Added support for multi-line annotations.
* Updated `README` and `setup`.

## v0.8.3 - 2022/04/24 - 00 - Revamped Loopers and UI
* Updated `qom.loopers` package:
    * Updated structure and updated public methods to supersede looper parameters.
    * Added function to check directories and save/load results.
    * Fixed progress and threshold function.
    * Updated documentation.
* Minor updates to `qom.solver` package methods.
* Minor changes in `qom.systems.BaseSystem` module for optical steady state method.
* Revamped `qom.ui.axes` package with more options for labels and ticks.
* Updated `qom.ui.plotters` package:
    * Removed axes formatting from `BasePlotter` module.
    * Added option for minor ticks, tick position and tick limits  in `MPLPlotter` module.
    * Added option to add annotations and change view for 3D plots.
* Minor fixes to `qom.ui.log` and `qom.utils.looper` modules.
* Updated `README` and `requirements` and `setup`.

## v0.8.2 - 2022/01/09 - 00 - Updated Loopers and Bugfixes
* Added support for custom parameters in `qom.loopers` modules.
* Added default time parameters in `qom.solvers.HLESover` module.
* Fixed dimension mismatch in `qom.ui.axes.MultiAxis` module.
* Updated `qom.ui.plotters` package:
    * Added option to choose real or imaginary components in `BasePlotter` and `MPLPlotter` modules.
    * Fixed dimension mismatch and scale in `MPLPlotter` module.
* Minor fixes to `qom.ui.log` and `qom.utils.looper` modules.
* Updated `README` and `setup`.

## v0.8.1 - 2021/12/20 - 00 - Updated Stability Zone
* Minor updates to `qom.loopers.BaseLooper` module.
* Updated stability zone calculation in `qom.systems.BaseSystem` module.
* Updated legend for `qom.ui.axes.MultiAxis` module.
* Templated function to obtain scripts in `qom.ui.widgets.SystemWidget` module.
* Updated `README` and `setup`.

## v0.8.0 - 2021/09/28 - 00 - Updated Lyapunov Exponents
* Updated Lyapunov exponents in `qom.systems.BaseSystem` module.
* Minor fixes to `qom.utils.looper` module.
* Updated `CONTRIBUTING` and `README`.

## v0.8.0 - 2021/09/25 - 00 - Added Classical Differences
* Updated `docs` and fixed documentation of modules.
* Added file-path and results-saving functions in `qom.loopers.BaseLooper` module.
* Updated `qom.systems.BaseSystem` module:
    * Added classical amplitude and phase difference methods.
    * Updated Pearson correlation coefficient method.
    * Handled mode amplitude calculation without correlations.
* Handled infinity and NaN values in `qom.ui.plotters.MPLPlotter` module.
* Added wrapper-merger function to `qom.utils.loopers` module and updated system-functions.
* Updated requirements for `pyqt` in `README`, `requirements` and `setup`.

## v0.8.0 - 2021/09/09 - 00 - Improved Callables
* Removed multi-value appending from `qom.loopers.BaseLooper` module.
* Updated `qom.systems` package:
    * Updated all callables and added stability zone calculation in `BaseSystem` module.
    * Improved mode dynamics calculation in `SOMASystem` module.
    * Removed stability zone calculation from `SOSMSystem` module.
* Minor fixes to styles and sizes in `qom.ui.axes` and `qom.ui.plotters` modules.
* Handled template directory error in `qom.ui.widgets.LooperWidget` module.
* Compacted functions in `qom.utils.looper` module.

## v0.8.0 - 2021/09/04 - 00 - Updated Systems
* Updated `qom.systems` package:
    * Updated LE and RHC methods in `qom.systems.BaseSystem` module.
    * Updated solver parameters in `qom.systems.SOMASystem` module.
    * Added optical stability zone calculation in `qom.systems.SOSMSystem` module.
* Minor fixes to parameter widgets in `qom.ui.widgets` modules.
* Updated `README`.

## v0.8.0 - 2021/08/30 - 00 - Bugfixes and Improvements
* Added stationary measure calculation and minor fixes to `qom.solvers` modules.
* Added required parameters and fixed multi-plots in `qom.ui.plotters` modules.
* Updated footer layout and combo box selection functions in `qom.ui.widgets` modules.
* Added stationary measure calculation in `qom.utils.looper` module.

## v0.8.0 - 2021/08/29 - 00 - Updated Widgets
* Minor fixes to `qom.solvers.HLESolver` module.
* Added attributes for required parameters and UI defaults in `qom.systems` modules.
* Fixed scatter plot markers in `qom.ui.axes` and `qom.ui.plotters` subpackages.
* Updated function and parameter selection in `qom.ui.widgets` modules.
* Reverted to system class calls in `qom.utils.looper` module.
* Updated `README`.

## v0.8.0 - 2021/08/29 - 00 - Updated Widgets
* Minor fixes to `qom.solvers.HLESolver` module.
* Added attributes for required parameters and UI defaults in `qom.systems` modules.
* Fixed scatter plot markers in `qom.ui.axes` and `qom.ui.plotters` subpackages.
* Updated function and parameter selection in `qom.ui.widgets` modules.
* Reverted to system class calls in `qom.utils.looper` module.
* Updated `README`.

## v0.8.0 - 2021/08/28 - 00 - Revamped Systems
* Minor fixes to `qom.solvers.HLESolver` module.
* Removed predefined function arguments and added validations for required and optional functions in `qom.systems.BaseSystem` and `qom.systems.SOMASystem` modules.
* Minor fixes to bounds in `qom.ui.axes` and `qom.ui.plotters` subpackages.
* Rearranged widgets and fixes to callables in `qom.ui.widgets` subpackage.
* Updated `qom.utils.looper` module to match revamped system functions.

## v0.8.0 - 2021/08/26 - 00 - Version Upgrade
* Minor fixes to attributes and callback updaters in `qom.loopers` modules.
* Added attributes and callback updaters to `qom.solvers.HLESolver` and `qom.solvers.ODESover` modules.
* Added callback updaters and minor fixes to `qom.systems` modules.
* Added attributes and fixed plot updaters in `qom.ui.plotters.MPLPlotter` module.
* Revamped layout and functions `qom.ui.widgets` subpackage and updated `qom.ui.gui` module.
* Minor fixes to `qom.ui.looper` module.
* Updated `README` and `setup`.

## v0.7.9 - 2021/08/24 - 00 - Updated ODESolver
* Added tolerance and stiffness in `qom.solvers.ODESolver` module.
* Minor fixes to `qom.systems.Basesystem` and `qom.systems.SOMASystem` modules.
* Minor fixes to surface plots in `qom.ui.plotters.MPLPlotter` module.
* Updated `README`.

## v0.7.9 - 2021/08/23 - 00 - Minor Fixes
* Updated `docs` with `qom.systems.SOMASystem`.
* Update update callback functions for `qom.loopers` modules.
* Minor fixes to `qom.ui.widgets` subpackage and `qom.ui.gui` module.
* Minor fixes to `qom.utils.looper` module.

## v0.7.9 - 2021/08/20 - 00 - Templated GUI
* Added progress callback and minor fixes to `qom.loopers` modules.
* Minor fixes to `qom.solvers.HLESolver` module.
* Updated `qom.solvers` subpackage:
    * Added RHC calculator and fixed optical methods in `BaseSystem` module.
    * Added `SOMASystem` module for single optomechanical array systems.
* Minor fixes to `qom.ui.plotters` modules and `qom.ui.axes.MultiAxis` module.
* Updated `qom.ui.gui` module and templated `qom.ui.widgets` modules.
* Renamed `qom.utils.wrappers` to `qom.utils.looper`.
* Updated `README` and `setup`.

## v0.7.8 - 2021/08/02 - 01 - Minor Fixes
* Updated `docs` configuration and source static files.
* Fixed indexing issue in `qom.solvers.QCMSolver` module.
* Added number of iterations for Lyapunov exponents in `qom.systems.BaseSystem` module.
* Fixed legend display in `qom.ui.axes` and `qom.ui.plotters` subpackages.
* Updated `README`.

## v0.7.8 - 2021/08/02 - 00 - Added Lyapunov Exponents
* Remodelled `docs` with class-based documentation support.
* Removed all notebooks from `examples`.
* Restructured `qom/loopers` modules:
    * Updated documentation, axis scaling, properties and parameters for `BaseLooper`.
    * Revised parameters and removed plotter options for `loop` methods in `XLooper`, `XYLooper` and `XYZLooper`.
* Updated `qom/solvers` modules:
    * Merged methods and modified workflows for `HLESolver` and `ODESolver`.
    * Minor fixes and reference additions for `QCMSOlver` and `RHCSolver`.
* Restructured `qom/systems` modules:
    * Added Lyapunov exponents, modified solver integrations and resolved parameters for `BaseSystem`.
    * Minor fixes to attributes in `DODMSystem`, `DOSMSystem`, `SODMSystem` and `SOSMSystem`.
* Updated documentation and minor fixes to `qom.ui.axes` and `qom.ui.plotters` modules.
* Added Lyapunov exponents-based functions and minor fixes to `qom.utils.wrappers` module.
* Updated `docs` with new appearance and class-based pages. 
* Updated `README` and `setup`.

## v0.7.7 - 2021/07/09 - 00 - Bugfixes
* Fixed copy bug in `qom/loopers/XYLooper` and `qom/loopers/XYZLooper` modules.
* Fixed Lyapunov equation bug in `qom/systems/BaseSystem` module.
* Added looper function handling in `qom/utils/wrappers` module.

## v0.7.7 - 2021/07/06 - 00 - Minor Fixes
* Fixed stationary method in `qom/systems/BaseSystem` module.

## v0.7.7 - 2021/07/04 - 00 - Fixed Multithread
* Fixed multithreading and wrapping in `qom/loopers/BaseLooper` module.
* Added maximum eigenvalue and minor fixes in `qom/systems/BaseSystem` module.
* Updated `qom/utils/log` with thread IDs for logging.
* Updated maximum eigenvalue and minor fixes in `qom/utils/wrappers` module.
* Updated `setup` and `README`.

## v0.7.6 - 2021/07/01 - 00 - Updated Loopers
* Updated `examples` for updated loopers.
* Updated `qom/loopers`:
    * Minor fixes to cached filename and rearrangement in `BaseLooper` module.
    * Added deep copy of parameters in `XYLooper` and `XYZLooper` modules.
* Rearranged methods in `qom/solvers/ODESolver` module.
* Updated drift matrix template in `qom/systems/BaseSystem` module.
* Fixed milti-instance logging in `qom/ui/log` module.
* Added dynamics wrapper in `qom/utils/wrappers` module.
* Updated `setup` and `README`.

## v0.7.5 - 2021/06/10 - 01 - Removed GitHub Pages
* Removed `_config.yml` files.

## v0.7.5 - 2021/06/10 - 00 - PyPI Packaging
* Updated link to `CODE_OF_CONDUCT` in `CONTRIBUTING`.
* Added `LICENSE` for BSD licensing.
* Updated `requirements` and `setup`.
* Updated `README`.

## v0.7.3 - 2021/06/09 - 01 - Removed TF Modules
* Updated documentation configuration in `docs`.
* Removed `qom_tf` package.
* Added `CODE_OF_CONDUCT` for GitHub pages configuration.
* Updated `CONTRIBUTING`.
* Updated `README`.
* Removed TensorFlow dependencies from `requirements`.

## v0.7.3 - 2021/06/09 - 00 - Updated README
* Updated documentation.
* Added `_config.yml` for GitHub pages configuration.
* Added `CONTRIBUTING`.
* Updated `README`.

## v0.7.3 - 2021/06/01 - 00 - Fixed System Import
* Fixed initialization import of `qom/systems/BaseSystem` module.

## v0.7.3 - 2021/05/25 - 00 - Added Looper Wrapper
* Directory creation and minor fixes to `qom/loopers/BaseLooper`.
* Minor fixes to `qom/systems/BaseSystem` an `qom/ui/axes/MultiAxis`.
* Fixed figure overlap in `qom/ui/plotters/MPLPlotter`.
* Added `wrap_looper` in `qom/utils/wrappers` to wrap `qom/loopers` classes.
* Updated `README`.

## v0.7.2 - 2021/05/21 - 00 - Added RHC Wrapper
* Added support for parameter indexing in `qom/loopers` modules.
* Added function to wrap RHCSolver in `qom/systems/BaseSystem` module.

## v0.7.1 - 2021/05/19 - 00 - Added ODE Wrapper
* Minor fixes to handle constants in `qom/solvers` modules.
* Added function to wrap ODEs in `qom/systems/BaseSystem` module.
* Minor fixes to `qom/ui/plotters/MPLPlotter` module. 

## v0.7.0 - 2021/05/14 - 00 - Stationary Measures
* Added stationary measure functions in `qom/systems/BaseSystem` module.

## v0.6.9 - 2021/05/12 - 00 - Updated Loopers and Plotters
* Updated `qom/loopers` module:
    * Added wrapper method to `qom/loopers/BaseLooper` module.
    * Added plot size option in `loop` methods.
* Added resize option in `qom/ui/plotters/MPLPlotter` module.

## v0.6.8 - 2021/03/25 - 00 - Added Examples
* Added notebooks to demonstrate `loopers`, `solvers` and `systems`.
* Added threshold method in `qom/loopers/BaseLooper` module.
* Added detection of number of modes in `qom/solvers/HLESolver` module.
* Minor fixes to `qom/systems/BaseSystem` module.
* Updated `qom/ui/plotters/MPLPlotter` module methods.
* Updated usage in `README`.

## v0.6.7 - 2021/03/04 - 00 - Updated Plotters
* Updated `qom/ui/plotters` module:
    * Updated palettes in `BasePlotter` module.
    * Added colorbar position support in `MPLPlotter`.
* Updated `README`.

## v0.6.6 - 2021/02/24 - 00 - Refined Plotters
* Minor fixes to `qom/systems/BaseSystem` module.
* Updated `qom/ui/plotters` module:
    * Restructured and added palettes in `BasePlotter` module.
    * Modified colorbar in `MPLPlotter` module supporting horizontal orientation.
* Updated `README`.

## v0.6.5 - 2021/02/12 - 00 - Initialized UI
* Updated `qom/solvers`:
    * Updated `HLESolver` module result calculations and fixed cache.
    * Added standalone integrator in `ODESolver` module.
    * Handled exceptions in `QCMSolver` module.
    * Updated module display name and code names.
* Updated `qom/systems/BaseSystem` module:
    * Added single-time validation-check methods to speed up loops.
    * Added methods to select mode amplitudes and correlation elements.
    * Added measure and eigenvalue calculation methods.
* Minor fixes to `qom/systems/SOSMSystem` and `qom/ui/axes/MultiAxis` modules.
* Updated `qom/ui/plotters`:
    * Added support for all seaborn palettes in `BasePlotter` module.
    * Added option to get axes in `MPLPlotter` module.
* Added `qom/ui/widgets`:
    * Added icons and stylesheets for light and dark themes.
    * Added separate widgets for constituent modules.
* Added `gui` module to read folder data and compile widgets.
* Removed `qom_legacy`.
* Added `MANIFEST` to pack resources.
* Updated `README`, `requirements` and `setup`.

## v0.6.3 - 2021/01/13 - 00 - Updated Solvers
* Updated `qom/solvers`:
    * Updates to `HLESolver` module properties and parameters.
    * Added new APIs and minor fixes in `ODESolver` module.
* Added solver method and cache options in `qom/systems/BaseSystem` module.

## v0.6.2 - 2021/01/12 - 00 - Updated ODE Solvers
* Updated `qom/solvers`:
    * Updated ODE solving methods in `HLESolver` module.
    * Added methods for integration steps and parameters in `ODESolver` module.
    * Minor updates to `QCMSolver` module.
* Updated methods for dynamics in `qom/systems/BaseSystem` module.

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