#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module to handle matplotlib plots."""

__name__    = 'qom.ui.plotters.matplotlib'
__authors__ = ["Sampreet Kalita"]
__created__ = "2020-10-03"
__updated__ = "2023-07-10"

# dependencies
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.font_manager import FontProperties
import matplotlib.pyplot as plt
import numpy as np

# qom modules
from .base import BasePlotter

# TODO: Add segmented color bar for contour plots.

class MPLPlotter(BasePlotter):
    """Class to handle matplotlib plots.

    Initializes `axes`, `params` and `plots`.
        
    Parameters
    ----------
    axes : dict
        Axes for the plot containing one or more keys for the axes (`'X'`, 'Y' or 'Z'), each either a list of values, or a dictionary. Refer to :class:`qom.ui.plotters.base.BasePlotter` for currently supported keys.
    params : dict
        Parameters of the plot. Refer to :class:`qom.ui.plotters.base.BasePlotter` for all available options.
    """

    # attributes
    name = 'MPLPlotter'
    """str : Name of the plotter."""
    desc = "MatPlotLib Plotter"
    """str : Description of the plotter."""
    cbar_positions = {
        'left': lambda gs: gs[:, 0], 
        'top': lambda gs: gs[0, :], 
        'right': lambda gs: gs[:, -1], 
        'bottom': lambda gs: gs[-1, :]
    }
    """dict : Positions ofthe color bar."""
    cbar_positions_toggled = {
        'left': lambda gs: gs[:, 1:], 
        'top': lambda gs: gs[1:, :], 
        'right': lambda gs: gs[:, :-1], 
        'bottom': lambda gs: gs[:-1, :]
    }
    """dict : Toggled positions ofthe color bar."""

    def __init__(self, axes:dict, params:dict, cb_update=None):
        """Class constructor for MPLPlotter."""

        # initialize super class
        super().__init__(
            axes=axes,
            params=params,
            cb_update=cb_update
        )

        # set attributes
        self.plots = list()

        # extract frequently used variables
        _type = self.params['type']
        _font_dicts = self.params['font_dicts']
        _cbar_position = self.params['cbar']['position']

        # update fonts
        plt.rcParams['mathtext.fontset'] = self.params['font_math']

        # initialize figure
        _fig = plt.figure()
        self.mpl_spec = _fig.add_gridspec(ncols=3, nrows=3, width_ratios=[1, 8, 1], height_ratios=[1, 8, 1])
        # initialize and validate colorbar
        self.cbar = None
        if self.params['cbar']['show'] and _type not in self.types_1D:
            if _cbar_position not in self.cbar_positions:
                _cbar_position = 'right'
            gs = self.cbar_positions_toggled[_cbar_position](self.mpl_spec)
        else:
            gs = self.mpl_spec[:, :]

        _mpl_axes = _fig.add_subplot(gs, projection='3d' if _type in self.types_3D else None)
        # set current axes
        plt.sca(_mpl_axes)

        # update title
        plt.title(self.params['title'], fontdict=_font_dicts['title'], pad=12)

        # udpate ticks
        plt.ticklabel_format(axis='both', style='plain')

        # update x-axis
        self._update_axis(_mpl_axes, 'x', self.axes['X'])

        # 1D plot
        if _type in self.types_1D:
            # update y-axis
            self._update_axis(_mpl_axes, 'y', self.axes['V'])

            # initialize 1D plot
            self._init_1D()

            # values are given
            if 'V' in axes:
                self.update(
                    vs=self.axes['V'].val,
                    xs=self.axes['X'].val
                )

        # 2D plot
        elif _type in self.types_2D:
            # update y-axis
            self._update_axis(_mpl_axes, 'y', self.axes['Y'])

            # initializze 2D plot
            self._init_2D()

            # values are given
            if 'V' in axes:
                self.update(
                    vs=self.axes['V'].val
                )

        # 3D plot
        else:
            # update y-axis
            self._update_axis(_mpl_axes, 'y', self.axes['Y'])
            # update z-axis
            self._update_axis(_mpl_axes, 'z', self.axes['Z'] if 'density' in _type else self.axes['V'])

            # initializze 3D plot
            self._init_3D()

            # values are given
            if 'V' in axes:
                self.update(
                    vs=self.axes['V'].val
                )

    def _get_font_props(self, font_dict:dict):
        """Method to convert font dictionary to `FontProperties` object.
         
        Parameters
        ----------
        font_dict : dict
            Dictionary of font properties.

        Returns
        -------
        font_props : :class:`matplotlib.font_manager.FontProperties`
            Font properties.
        """

        # convert to FontProperties and return
        return FontProperties(
            family=font_dict['family'],
            style=font_dict['style'],
            variant=font_dict['variant'],
            weight=font_dict['weight'],
            stretch=font_dict['stretch'],
            size=font_dict['size'],
        )

    def _init_1D(self, dim=0, ax_twin=None):
        """Method to initialize 1D plots.
        
        Parameters
        ----------
        dim : int
            Dimension of the Y-axis.
        """

        # extract frequently used variables
        _type = self.params['type']
        _mpl_axes = plt.gca() if ax_twin is None else ax_twin
        _dim = len(self.plots)
        _colors, _sizes, _styles = self._get_colors_sizes_styles(dim)

        # line plots
        if 'line' in _type:
            # plots
            self.plots += [_mpl_axes.plot(list(), list(), color=_colors[i], linestyle=_styles[i], linewidth=_sizes[i])[0] for i in range(_dim, dim)]

        # scatter plots
        elif 'scatter' in _type:
            self.plots += [_mpl_axes.scatter(list(), list(), c=_colors[i], s=_sizes[i], marker=_styles[i]) for i in range(_dim, dim)]

        # legend
        if self.params['legend']['show'] and ax_twin is None:
            _l = plt.legend(labels=self.params['legend']['labels'][:dim], loc=self.params['legend']['location'], frameon=False)  
            plt.setp(_l.texts, fontproperties=self._get_font_props(self.params['font_dicts']['legend']))

    def _init_2D(self):
        """Method to initialize 2D plots."""

        # extract frequently used variables
        _type = self.params['type']
        _mpl_axes = plt.gca()
        _cmap = LinearSegmentedColormap.from_list(self.params['palette'], self.palette_colors)

        # update view
        _mpl_axes.set_facecolor('grey')

        # initailize values
        _xs, _ys = np.meshgrid(self.axes['X'].val, self.axes['Y'].val)
        _zeros = np.zeros((self.axes['Y'].dim, self.axes['X'].dim))
        _nan =  np.zeros((self.axes['Y'].dim, self.axes['X'].dim))
        _nan[:] = np.NaN

        # contour plot
        if _type == 'contour':
            self.plots = _mpl_axes.contour(_xs, _ys, _zeros, levels=self.params['bins'], cmap=_cmap)

        # contourf plot
        if _type == 'contourf':
            self.plots = _mpl_axes.contourf(_xs, _ys, _zeros, levels=self.params['bins'], cmap=_cmap)

        # pcolormesh plot
        if _type == 'pcolormesh':
            self.plots = _mpl_axes.pcolormesh(_xs, _ys, _nan, shading='gouraud', cmap=_cmap)

    def _init_3D(self):
        """Method to initialize 3D plots."""

        # extract frequently used variables
        _type = self.params['type']
        _mpl_axes = plt.gca()
        _cmap = LinearSegmentedColormap.from_list(self.params['palette'], self.palette_colors)

        # update view
        _mpl_axes.view_init(self.params['view']['elevation'], self.params['view']['rotation'])
        _mpl_axes.set_box_aspect(aspect=self.params['view']['aspect'])
        _pane_color = (1.0, 1.0, 1.0, 0.0)
        _mpl_axes.xaxis.set_pane_color(_pane_color)
        _mpl_axes.xaxis.set_rotate_label(False)
        _mpl_axes.xaxis.label.set_rotation(0)
        _mpl_axes.yaxis.set_pane_color(_pane_color)
        _mpl_axes.yaxis.set_rotate_label(False)
        _mpl_axes.yaxis.label.set_rotation(0)
        _mpl_axes.zaxis.set_pane_color(_pane_color)
        _mpl_axes.zaxis.set_rotate_label(False)
        _mpl_axes.zaxis.label.set_rotation(0)
        _grid_params = {
            'linewidth': 1,
            'color': (0.5, 0.5, 0.5, 0.2)
        }
        _mpl_axes.xaxis._axinfo['grid'].update(_grid_params)
        _mpl_axes.yaxis._axinfo['grid'].update(_grid_params)
        _mpl_axes.zaxis._axinfo['grid'].update(_grid_params)

        # initailize values
        _xs, _ys = np.meshgrid(self.axes['X'].val, self.axes['Y'].val)
        _zeros = np.zeros((self.axes['Y'].dim, self.axes['X'].dim))

        # density plot
        if 'density' in _type:
            # if unit sphere opted
            if 'unit' in _type:
                _line = np.linspace(-1, 1, self.axes['X'].dim)
                _thetas = np.linspace(-np.pi, np.pi, self.axes['X'].dim)
                _zeros = np.zeros(self.axes['X'].dim)
                self.plots = [_mpl_axes.plot(_line, _zeros, _zeros, color='k', linestyle='-', linewidth=0.5, alpha=0.5)[0]]
                self.plots += [_mpl_axes.plot(_zeros, _line, _zeros, color='k', linestyle='-', linewidth=0.5, alpha=0.5)[0]]
                self.plots += [_mpl_axes.plot(_zeros, _zeros, _line, color='k', linestyle='-', linewidth=0.5, alpha=0.5)[0]]
                self.plots += [_mpl_axes.plot(np.cos(_thetas), np.sin(_thetas), _zeros, color='k', linestyle='-', linewidth=0.75, alpha=0.75)[0]]
                self.plots += [_mpl_axes.plot(_zeros, np.cos(_thetas), np.sin(_thetas), color='k', linestyle='-', linewidth=0.75, alpha=0.75)[0]]
                self.plots += [_mpl_axes.plot(np.sin(_thetas), _zeros, np.cos(_thetas), color='k', linestyle='-', linewidth=0.75, alpha=0.75)[0]]
        # line plot
        if 'line' in _type:
            dim = self.axes['Y'].dim
            _colors, _sizes, _styles = self._get_colors_sizes_styles(dim)
            self.plots += [_mpl_axes.plot(_xs[i], _ys[i], _zeros[i], color=_colors[i], linestyle=_styles[i], linewidth=_sizes[i])[0] for i in range(len(self.plots), dim)]
        # scatter plot
        if 'scatter' in _type:
            dim = self.axes['Y'].dim
            _colors, _sizes, _styles = self._get_colors_sizes_styles(dim)
            self.plots += [_mpl_axes.scatter(_xs[i], _ys[i], _zeros[i], c=_colors[i], s=_sizes[i], marker=_styles[i]) for i in range(len(self.plots), dim)]
        # surface plot
        if 'surface' in _type:
            self.plots = _mpl_axes.plot_surface(_xs, _ys, _zeros, rstride=1, cstride=1, cmap=_cmap)

    def _get_colors_sizes_styles(self, dim):
        """Method to obtain the colors, sizes and styles for 1D plots.
        
        Parameters
        ----------
        dim : int
            Dimension of the Y-axis.

        Returns
        -------
        colors : list
            Colors for each plot.
        sizes : list
            Sizes for each plot.
        styles : list
            Styles for each plot.
        """

        # extract frequently used variables
        _type = self.params['type']
        _colors = self.params['colors']
        _sizes = self.params['sizes']
        _styles = self.params['styles']

        # udpate colors from palette if dimension mismatch or none
        if _colors is None or (type(_colors) is list and (len(_colors) == 0 or len(_colors) < dim)):
            # select extreme colors if two plots
            if dim == 2:
                _colors = [[self.palette_colors[0]], [self.palette_colors[-1]]] if 'scatter' in _type else [self.palette_colors[0], self.palette_colors[-1]]
            # else select colors serially
            else:
                _colors = [[self.palette_colors[i % self.params['bins']]] if 'scatter' in _type else self.palette_colors[i % self.params['bins']] for i in range(dim)]
        # select colors from palette if indices are given
        else:
            # select palette colors
            _colors = [[self.palette_colors[_colors[i] % self.params['bins']] if type(_colors[i]) is int else _colors[i]] if 'scatter' in _type else (self.palette_colors[_colors[i] % self.params['bins']] if type(_colors[i]) is int else _colors[i]) for i in range(dim)]

        # udpate sizes
        if _sizes is None or (type(_sizes) is list and (len(_sizes) == 0 or len(_sizes) < dim)):
            _sizes = [1.0 for _ in range(dim)]

        # udpate styles
        if _styles is None or (type(_styles) is list and (len(_styles) == 0 or len(_styles) < dim)):
            _styles = [BasePlotter.default_linestyles[i % len(BasePlotter.default_linestyles)] if 'line' in _type else BasePlotter.default_markers[i % len(BasePlotter.default_markers)] for i in range(dim)]

        return _colors, _sizes, _styles

    def _resize_plot(self, width:float=4.8, height:float=4.8):
        """Method to resize the plot.
        
        Parameters
        ----------
        width : float
            Width of the figure.
        height : float
            Height of the figure.
        """

        # extractfrequently used variables
        _cbar_position = self.params['cbar']['position']
        _min = min(width, height)
        if _min < 4.0:
            _min = 6.0
        
        # update 3D axes
        if self.params['type'] in self.types_3D:
            _mpl_axes = plt.gca()
            _axes = [_mpl_axes.xaxis, _mpl_axes.yaxis, _mpl_axes.zaxis]
            for _ax in _axes:
                _ax._axinfo['tick'].update({
                    'linewidth': {
                        True: _min / 5.0,
                        False: _min / 20.0
                    },
                    'inward_factor': _min / 20.0
                })
                _ax.set_tick_params(length=_min, width=_min / 5.0, which='major')
                _ax.set_tick_params(length=_min / 2.0, width=_min / 5.0, which='minor')
        # update all axes
        for _ax in plt.gcf().get_axes():
            # update spines
            for spine in ['top', 'bottom', 'left', 'right']:
                _ax.spines[spine].set_linewidth(_min / 4.0)

            # update tick lines
            _ax.tick_params(length=_min, width=_min / 5.0, which='major')
            _ax.tick_params(length=_min / 2.0, width=_min / 5.0, which='minor')

        # resize figure
        if self.cbar is not None:
            if _cbar_position == 'top' or _cbar_position == 'bottom':
                plt.gcf().set_size_inches(width, height + 0.5)
            else:
                plt.gcf().set_size_inches(width + 0.5, height)
            # update cbar axes
            self.cbar.outline.set_linewidth(_min / 5)
        else:
            plt.gcf().set_size_inches(width, height)

    def _update_1D(self, vs, xs, ax_twin=None):
        """Method to udpate 1D plots.
        
        Parameters
        ----------
        vs : list or numpy.ndarray
            V-axis values.
        xs : list or numpy.ndarray
            X-axis values.
        ax_twin : :class:`matplotlib.axes.Axes`
            Twin axis of the figure.
        """

        # validate parameters
        assert type(vs) is list or type(vs) is np.ndarray, "Parameter `vs` should be a list or NumPy array"
        assert type(xs) is list or type(xs) is np.ndarray, "Parameter `xs` should be a list or NumPy array"

        # frequently used variables
        _type = self.params['type']
        _mpl_axes = plt.gca() if ax_twin is None else ax_twin
        _offset = 0 if ax_twin is None else len(self.plots)

        # handle non-single plots
        if _offset + len(xs) != len(self.plots):
            self._init_1D(dim=_offset + len(xs), ax_twin=ax_twin)

        # handle multi-data points
        for i in range(len(self.plots) - _offset):
            _xs = list()
            _vs = list()
            # iterate each point
            for j in range(len(vs[i])):
                # if multi-data point
                if type(vs[i][j]) is list:
                    for k in range(len(vs[i][j])):
                        _xs.append(xs[i][j])
                        _vs.append(vs[i][j][k])
                # if single-data point
                else:
                    _xs.append(xs[i][j])
                    _vs.append(vs[i][j])

            # update lists
            xs[i] = _xs
            vs[i] = _vs
        
        # line plots
        if 'line' in _type:
            for j in range(len(self.plots) - _offset):
                self.plots[j + _offset].set_xdata(xs[j])
                self.plots[j + _offset].set_ydata(vs[j])

        # scatter plots
        if 'scatter' in _type:
            for j in range(len(self.plots) - _offset):
                XY = np.c_[xs[j], vs[j]]
                self.plots[j + _offset].set_offsets(XY)
                
        # handle nan values for limits
        _minis = []
        _maxis = []
        for j in range(len(vs)):
            # calculate minimum and maximum values
            if len(vs[j]) != 0:
                # handle NaN values
                _no_nan = [0 if np.isnan(y) or np.isinf(y) else y for y in vs[j]]

                # update limits
                _minis.append(np.min(_no_nan))
                _maxis.append(np.max(_no_nan))

        # get limits
        _mini, _maxi = np.min(_minis), np.max(_maxis)
        _mini, _maxi, _prec = self.get_limits(_mini, _maxi)

        # axis name
        ax_name = 'V' if ax_twin is None else 'V_twin'

        # ticks and tick labels
        _ticks = self.axes[ax_name].ticks
        _tick_labels = self.axes[ax_name].tick_labels
        if self.axes[ax_name].bound:
            _mini = self.axes[ax_name].limits[0]
            _maxi = self.axes[ax_name].limits[-1]
        else:
            _ticks = np.around(np.linspace(_mini, _maxi, len(_mpl_axes.get_yticks())), decimals=_prec + 1)
            _tick_labels = _ticks
            _mini = np.min(_ticks)
            _maxi = np.max(_ticks)
        _mpl_axes.set_yticks(_ticks)
        if self.axes[ax_name].ticks_minor is not None:
            _mpl_axes.set_yticks(self.axes[ax_name].ticks_minor, minor=True)
        _mpl_axes.set_yticklabels(_tick_labels)

        # update limits
        _mpl_axes.set_ylim(_mini, _maxi)

        return _mpl_axes

    def _update_2D(self, vs):
        """Method to udpate 2D plots.
        
        Parameters
        ----------
        vs : list or numpy.ndarray
            V-axis values.
        """

        # validate parameters
        assert type(vs) is list or type(vs) is np.ndarray, "Parameter `vs` should be a list or NumPy array"

        # frequently used variables
        _type = self.params['type']
        _mpl_axes = plt.gca()
        _rave = np.ravel(vs)

        # initialize values
        _no_nan = [0 if np.isnan(z) or np.isinf(z) else z for z in _rave]
        _mini, _maxi = np.min(_no_nan), np.max(_no_nan)

        # if bounded
        if self.axes['V'].bound:
            _mini = self.axes['V'].limits[0]
            _maxi = self.axes['V'].limits[-1]
            _, _, _prec = self.get_limits(_mini, _maxi)
        # generate limits
        else:
            _mini, _maxi, _prec = self.get_limits(_mini, _maxi)
        
        # get cbar ticks
        _cbar_ticks = self.params['cbar']['ticks']
        if _cbar_ticks is not None and type(_cbar_ticks[0]) is not str:
            _cbar_mini = np.min(_cbar_ticks)
            _cbar_maxi = np.max(_cbar_ticks)
        else:
            _cbar_mini = None
            _cbar_maxi = None

        # contour and contourf plots
        if 'contour' in _type:
            # remove QuadContourSet PathCollection
            for pc in self.plots.collections:
                pc.remove()
            _xs, _ys = np.meshgrid(self.axes['X'].val, self.axes['Y'].val)

            # contour plot
            if _type == 'contour':
                self.plots = _mpl_axes.contour(_xs, _ys, vs, levels=self.params['bins'], cmap=self.plots.get_cmap())
            # contourf plot
            if _type == 'contourf':
                self.plots = _mpl_axes.contourf(_xs, _ys, vs, levels=self.params['bins'], cmap=self.plots.get_cmap())

        # pcolormesh plot
        if _type == 'pcolormesh':
            self.plots.set_array(_rave)

        # set limits
        self.plots.set_clim(vmin=_mini if _cbar_mini is None else _cbar_mini, vmax=_maxi if _cbar_maxi is None else _cbar_maxi)

        # color bar
        if self.params['cbar']['show']:
            self.set_cbar(_mini, _maxi, _prec)

        return _mpl_axes

    def _update_3D(self, vs, xs, ys, zs):
        """Method to udpate 3D plots.
        
        Parameters
        ----------
        vs : list or numpy.ndarray
            V-axis values.
        xs : list or numpy.ndarray
            X-axis data.
        ys : list or numpy.ndarray
            Y-axis data.
        zs : list or numpy.ndarray
            Z-axis data.
        """

        # validate parameters
        assert type(vs) is list or type(vs) is np.ndarray, "Parameter `vs` should be a list or NumPy array"

        # frequently used variables
        _type = self.params['type']
        _mpl_axes = plt.gca()

        # initialize values
        _V = np.array(vs) if type(vs) is list else vs
        if 'density' in _type:
            _mini, _maxi, _prec = 0, 1, 1
        else:
            _mini, _maxi, _prec = self.get_limits(np.min(_V.ravel()), np.max(_V.ravel()))

        # get ticks and tick labels
        _ticks = self.axes['V'].ticks
        _tick_labels = self.axes['V'].tick_labels
        if self.axes['V'].bound:
            _mini = self.axes['V'].limits[0]
            _maxi = self.axes['V'].limits[-1]
        else:
            _ticks = np.around(np.linspace(_mini, _maxi, len(_mpl_axes.get_zticks())), decimals=_prec + 1)
            _tick_labels = _ticks
            _mini = np.min(_ticks)
            _maxi = np.max(_ticks)
        
        # get cbar ticks
        _cbar_ticks = self.params['cbar']['ticks']
        if _cbar_ticks is not None and type(_cbar_ticks[0]) is not str:
            _cbar_mini = np.min(_cbar_ticks)
            _cbar_maxi = np.max(_cbar_ticks)
        else:
            _cbar_mini = None
            _cbar_maxi = None

        # density plot
        if 'density' in _type:
            _cmap = LinearSegmentedColormap.from_list(self.params['palette'], self.palette_colors)
            _, _sizes, _styles = self._get_colors_sizes_styles(1)
            self.plots += [_mpl_axes.scatter(xs, ys, zs, c=vs, cmap=_cmap, s=_sizes[0], marker=_styles[0], alpha=0.5)]
        else:
            # update ticks and ticklabels
            _mpl_axes.set_zticks(_ticks)
            _mpl_axes.set_zticklabels(_tick_labels)
            # update minor ticks
            if self.axes['V'].ticks_minor is not None:
                _mpl_axes.set_zticks(self.axes['V'].ticks_minor, minor=True)
                _mpl_axes.set_zticklabels(['' for _ in self.axes['V'].ticks_minor], minor=True)
            # update limits
            _mpl_axes.set_zlim3d(_mini, _maxi)

            # line plot
            if 'line' in _type:
                for j in range(len(self.plots)):
                    _xs, _ys, _ = self.plots[j].get_data_3d()
                    self.plots[j].set_data_3d(_xs, _ys, _V[j])
            # scatter plot
            if 'scatter' in _type:
                for j in range(len(self.plots)):
                    self.plots[j].set_3d_properties(_V[j], 'z')
            # surface plot
            if 'surface' in _type:
                _cmap = self.plots.get_cmap()
                self.plots.remove()
                _X, _Y = np.meshgrid(self.axes['X'].val, self.axes['Y'].val)
                self.plots = _mpl_axes.plot_surface(_X, _Y, _V, rstride=1, cstride=1, cmap=_cmap, antialiased=False)

                # projections
                if _type == 'surface_cz':
                    _offset = _maxi  + 0.2 * (_maxi - _mini)
                    _proj_z = _mpl_axes.contour(_X, _Y, _V, zdir='z', levels=self.params['bins'], offset=_offset, cmap=_cmap, vmin=_mini if _cbar_mini is None else _cbar_mini, vmax=_maxi if _cbar_maxi is None else _cbar_maxi)

                # update colorbar
                if self.cbar is not None:
                    self.cbar.update_normal(self.plots)

                # update limits
                self.plots.set_clim(vmin=_mini if _cbar_mini is None else _cbar_mini, vmax=_maxi if _cbar_maxi is None else _cbar_maxi)

        # color bar
        if self.params['cbar']['show']:
            self.set_cbar(_mini, _maxi, _prec)
            self.cbar.ax.set_autoscale_on(True)

        return _mpl_axes

    def _update_axis(self, ax, ax_name:str, ax_data:dict):
        """Method to update an axis.
        
        Parameters
        ----------
        ax : :class:`matplotlib.axes.Axes`
            Axis of the plot.
        ax_name : str
            Name of the axis.
        ax_data : dict
            Data for the axis.
        """

        # frequently used variables
        _type = self.params['type']
        _font_dicts = self.params['font_dicts']
        _font_props = self._get_font_props(_font_dicts['tick'])
        _label_color = ax_data.label_color if type(ax_data.label_color) is str else self.palette_colors[ax_data.label_color]
        _tick_color = ax_data.tick_color if type(ax_data.tick_color) is str else self.palette_colors[ax_data.tick_color]
        _tick_position = ax_data.tick_position

        # labels
        getattr(ax, 'set_' + ax_name + 'label')(ax_data.label, color=_label_color, labelpad=ax_data.label_pad, fontdict=_font_dicts['label'])

        # scale
        getattr(ax, 'set_' + ax_name + 'scale')(ax_data.scale)

        # ticks
        suffix = '3d' if _type in self.types_3D else ''
        getattr(ax, 'set_' + ax_name + 'ticks')(ax_data.ticks)
        if ax_data.bound:
            getattr(ax.axes, 'set_' + ax_name + 'lim' + suffix)(ax_data.limits[0], ax_data.limits[1])

        # tick parameters
        _left = True if 'left' in _tick_position or 'both' in _tick_position else False
        _right = True if 'right' in _tick_position or 'both' in _tick_position else False
        _top = True if 'top' in _tick_position or 'both' in _tick_position else False
        _bottom = True if 'bottom' in _tick_position or 'both' in _tick_position else False
        _direction = 'in' if 'in' in _tick_position else 'out'
        ax.tick_params(axis=ax_name, which='major', direction=_direction, bottom=_bottom, left=_left, right=_right, top=_top, pad=ax_data.tick_pad)

        # minor ticks
        if ax_data.ticks_minor is not None:
            getattr(ax, 'set_' + ax_name + 'ticks')(ax_data.ticks_minor, minor=True)
            getattr(ax, 'set_' + ax_name + 'ticklabels')(['' for _ in ax_data.ticks_minor], minor=True)
            ax.tick_params(axis=ax_name, which='minor', direction=_direction, bottom=_bottom, left=_left, right=_right, top=_top, pad=ax_data.tick_pad)
        else:
            ax.minorticks_off()

        # tick labels
        getattr(ax, 'set_' + ax_name + 'ticklabels')(ax_data.tick_labels)
        plt.setp(getattr(ax, 'get_' + ax_name + 'ticklabels')(), color=_tick_color, fontproperties=_font_props)

    def add_scatter(self, vs, xs, color:str='k', size:float=1.0, style:str='.'):
        """Method to add a scatter plot.
        
        Parameters
        ----------
        vs : list or numpy.ndarray
            V-axis values.
        xs : list or numpy.ndarray
            X-axis data.
        color : str or int
            Color of the plot.
        size : int
            Size of the plot.
        style : str
            Marker style of the plot.
        """

        # get current axis
        ax = self.get_current_axis()
        # get color from palette
        if type(color) is int:
            color = self.palette_colors[color]

        # update axis
        ax.scatter(x=xs, y=vs, s=size, color=color, marker=style)

    def close(self):
        """Method to close the plotter.
        """
        
        plt.close()

    def get_current_axis(self):
        """Method to obtain the axes of the figure.
        
        Returns
        -------
        axes : :class:`matplotlib.axes.Axes`
            Axes of the figure.
        """

        return plt.gca()

    def get_current_figure(self):
        """Method to obtain the current figure.
        
        Returns
        -------
        fig : :class:`matplotlib.pyplot.figure`
            Current figure.
        """
        
        return plt.gcf()

    def save(self, filename:str):
        """Method to save the figure.

        Parameters
        ----------
        filename : str
            Name of the saved file.
        width : float
            Width of the figure.
        height : float
            Height of the figure.
        """

        # create directory
        self.updater.create_directory(
            file_path=filename
        )

        # resize plot
        self._resize_plot(
            width=self.params['width'],
            height=self.params['height']
        )

        # draw data
        plt.draw()
        plt.tight_layout()
        
        # save to file
        plt.savefig(filename, dpi=300)

    def set_cbar(self, mini:float=0, maxi:float=0, prec:int=2):
        """Method to set the colorbar for the figure.

        Parameters
        ----------
        mini : float
            Minimum value displayed. Default is 0.
        maxi : float
            Maximum value displayed. Default is 0.
        prec : int
            Precision upto which the values are displayed. Default is 2.
        """

        # extract frequently used variables
        _type = self.params['type']
        _cbar_position = self.params['cbar']['position']
        _orientation = 'vertical' if _cbar_position == 'right' or _cbar_position == 'left' else 'horizontal'
        _font_dicts = self.params['font_dicts']
        _ticks = self.params['cbar']['ticks']
        if _ticks is not None:
            _norm = Normalize(vmin=np.min(_ticks), vmax=np.max(_ticks))
        else:
            _ticks = np.around(np.linspace(mini, maxi, self.params['bins']), decimals=prec)
            _norm = Normalize(vmin=mini, vmax=maxi)
        _cmap = LinearSegmentedColormap.from_list(self.params['palette'], self.palette_colors)

        # clear if existed
        if self.cbar is not None:
            self.cbar.ax.clear()
            _cax = self.cbar.ax
        # add axis
        else:
            _cax = plt.gcf().add_subplot(self.cbar_positions[_cbar_position](self.mpl_spec))

        # set scalar mappable 
        if 'contour' in _type or 'density' in _type:
            _sm = plt.cm.ScalarMappable(cmap=_cmap, norm=_norm)
            _sm.set_array([])
        else:
            _sm = self.plots

        # initialize colorbar
        self.cbar = plt.colorbar(_sm, cax=_cax, ax=plt.gca(), orientation=_orientation, norm=_norm)

        # title
        self.cbar.ax.set_title(self.params['cbar']['title'], fontproperties=self._get_font_props(_font_dicts['title']), pad=12)

        # labels
        self.cbar.ax.set_xlabel(self.params['cbar']['x_label'], labelpad=_font_dicts['tick']['size'] + 12, fontproperties=self._get_font_props(_font_dicts['label']))
        self.cbar.ax.set_ylabel(self.params['cbar']['y_label'], labelpad=_font_dicts['tick']['size'] + 12, fontproperties=self._get_font_props(_font_dicts['label']))

        # ticks
        self.cbar.set_ticks(_ticks)
        self.cbar.ax.tick_params(axis='x', which='major', pad=12)
        self.cbar.ax.tick_params(axis='y', which='major', pad=12)

        # tick labels
        _tick_labels = self.params['cbar']['tick_labels']
        if _tick_labels is None:
            _tick_labels = _ticks
        if _cbar_position == 'top' or _cbar_position == 'bottom':
            self.cbar.ax.set_xticklabels(_tick_labels)
            plt.setp(self.cbar.ax.get_xticklabels(), fontproperties=self._get_font_props(_font_dicts['tick']), text=_tick_labels)
        else:
            self.cbar.ax.set_yticklabels(_tick_labels)
            plt.setp(self.cbar.ax.get_yticklabels(), fontproperties=self._get_font_props(_font_dicts['tick']))

    def show(self, hold:bool=True):
        """Method to display the figure.

        Parameters
        ----------
        hold : bool, default=True
            Option to hold the plot.
        """

        # resize plot
        self._resize_plot(
            width=self.params['width'],
            height=self.params['height']
        )

        # draw data
        plt.draw()
        plt.tight_layout()

        # display plot
        if hold:
            plt.show()
        else:
            plt.pause(1e-9)

    def update(self, vs, xs=None, ys=None, zs=None):
        """Method to update the figure.
        
        Parameters
        ----------
        vs : list or numpy.ndarray
            V-axis data.
        xs : list or numpy.ndarray, optional
            X-axis data.
        ys : list or numpy.ndarray, optional
            Y-axis data.
        zs : list or numpy.ndarray, optional
            Z-axis data.
        """

        # validate parameters
        assert type(vs) is list or type(vs) is np.ndarray, "Parameter `vs` should be a list or NumPy array"
        assert xs is None or type(xs) is list or type(xs) is np.ndarray, "Parameter `xs` should be a list or NumPy array"
        assert ys is None or type(ys) is list or type(ys) is np.ndarray, "Parameter `ys` should be a list or NumPy array"
        assert zs is None or type(zs) is list or type(zs) is np.ndarray, "Parameter `zs` should be a list or NumPy array"

        # extract frequently used variables
        _type = self.params['type']
        _dtypes_arrays = [list, np.ndarray]
        _dtypes_complex = [complex, np.complex64, np.complex128, np.complex_]

        # handle complex values
        if type(vs[0]) in _dtypes_complex or (type(vs[0]) in _dtypes_arrays and type(vs[0][0]) in _dtypes_complex):
            if 'imag' in self.params['component']:
                self.updater.update_info(
                    status="Plotting only Imaginary Parts of the Complex Values\t\n"
                )
                vs = np.imag(vs)
            else: 
                self.updater.update_info(
                    status="-----Plotting only Real Parts of the Complex Values\t\n"
                )
                vs = np.real(vs)

        # 1D plots
        if _type in self.types_1D:
            if len(xs) != len(vs): 
                xs = [xs for _ in range(len(vs))]
            elif type(xs[0]) is not list and type(xs[0]) is not np.ndarray:
                xs = [xs]
                vs = [vs]
            ax = self._update_1D(
                vs=vs,
                xs=xs
            )
        
        # 2D plots
        if _type in self.types_2D:
            ax = self._update_2D(
                vs=vs
            )

        # 3D plot
        if _type in self.types_3D:
            if xs is None or ys is None:
                xs, ys = np.meshgrid(self.axes['X'].val, self.axes['Y'].val)
            if zs is None:
                zs = np.zeros((self.axes['Y'].dim, self.axes['X'].dim))
            ax = self._update_3D(
                vs=vs,
                xs=xs,
                ys=ys,
                zs=zs
            )

        # annotations
        _annotations = self.params['annotations']
        if type(_annotations) is list and len(_annotations) > 0 and type(_annotations[0]) is dict:
            # add each annotation
            for item in _annotations:
                _color = item.get('color', 'k')
                if type(_color) is int:
                    _color = self.palette_colors[_color % self.params['bins']]
                ax.annotate(text=item.get('text', ''), xy=item.get('xy', (0.2, 0.8)), xycoords='figure fraction', color=_color, font_properties=self._get_font_props(
                    font_dict=self.params['font_dicts'].get(item.get('font_dict_type', 'label'), self.params['font_dicts']['label'])
                ), rotation=item.get('orientation', 'horizontal'), multialignment='center')

        # vertical background span
        _vspans = self.params['vertical_spans']
        if type(_vspans) is list and len(_vspans) > 0 and type(_vspans[0]) is dict:
            # add each span
            for item in _vspans:
                _color = item.get('color', 'k')
                if type(_color) is int:
                    _color = self.palette_colors[_color % self.params['bins']]
                ax.axvspan(xmin=item.get('limits', (0.0, 0.0))[0], xmax=item.get('limits', (0.0, 0.0))[1], color=_color, alpha=item.get('alpha', 0.25))

        return ax

    def update_twin_axis(self, vs, xs):
        """Method to create and update a twin axis of a 1D plot.
        
        Parameters
        ----------
        vs : list or numpy.ndarray
            V-axis data.
        xs : list or numpy.ndarray
            X-axis data.
        
        Returns
        ----------
        ax_twin : :class:`matplotlib.axes.Axes`
            The twin axis.
        """

        # frequently used variables
        ax_data = self.axes['V_twin']
        _font_dicts = self.params['font_dicts']
        _font_props = self._get_font_props(
            font_dict=_font_dicts['tick']
        )
        _label_color = ax_data.label_color if type(ax_data.label_color) is str else self.palette_colors[ax_data.label_color]
        _tick_color = ax_data.tick_color if type(ax_data.tick_color) is str else self.palette_colors[ax_data.tick_color]
        _tick_position = ax_data.tick_position

        # initialize twin axis
        ax_twin = plt.gca().twinx()

        # labels
        ax_twin.set_ylabel(ax_data.label, color=_label_color, labelpad=ax_data.label_pad, fontdict=_font_dicts['label'])

        # scale
        ax_twin.set_yscale(ax_data.scale)

        # tick parameters
        _left = True if 'left' in _tick_position or 'both' in _tick_position else False
        _right = True if 'right' in _tick_position or 'both' in _tick_position else False
        _top = True if 'top' in _tick_position or 'both' in _tick_position else False
        _bottom = True if 'bottom' in _tick_position or 'both' in _tick_position else False
        _direction = 'in' if 'in' in _tick_position else 'out'
        ax_twin.tick_params(axis='y', which='major', direction=_direction, bottom=_bottom, left=_left, right=_right, top=_top, pad=ax_data.tick_pad)

        # minor ticks
        if ax_data.ticks_minor is not None:
            ax_twin.set_yticks(ax_data.ticks_minor, minor=True)
            ax_twin.set_yticklabels(['' for _ in ax_data.ticks_minor], minor=True)
            ax_twin.tick_params(axis='y', which='minor', direction=_direction, bottom=_bottom, left=_left, right=_right, top=_top, pad=ax_data.tick_pad)
        else:
            ax_twin.minorticks_off()

        # tick labels
        ax_twin.set_yticklabels(ax_data.tick_labels)
        plt.setp(ax_twin.get_yticklabels(), color=_tick_color, fontproperties=_font_props)

        # reshape data points
        if len(xs) != len(vs): 
            xs = [xs for _ in range(len(vs))]
        elif type(xs[0]) is not list:
            xs = [xs]
            vs = [vs]
        
        # plot
        ax = self._update_1D(
            vs=vs,
            xs=xs,
            ax_twin=ax_twin
        )

        return ax