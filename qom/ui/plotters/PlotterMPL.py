#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to handle matplotlib plots."""

__name__    = 'qom.ui.plotters.PlotterMPL'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-10-03'
__updated__ = '2020-10-06'

# dependencies
from matplotlib.font_manager import FontProperties 
from matplotlib.lines import Line2D
import logging
import matplotlib.pyplot as plt
import numpy as np

# dev dependencies
from qom.ui.plotters.BasePlotter import BasePlotter
from qom.utils.axis import StaticAxis
from qom.utils.misc import get_limits

# module logger
logger = logging.getLogger(__name__)

# TODO: Add annotations.
# TODO: Options for `ticklabel_format`.
# TODO: Handle contour, contourf plots.
# TODO: Handle 3D.

class PlotterMPL(BasePlotter):
    """Class to handle matplotlib plots.

    Inherits :class:`qom.ui.plotters.BasePlotter`.
    """

    def __init__(self, plot_params, Axes):
        """Class constructor for MPLPlotter.
        
        Parameters
        ----------
            plot_params : dict
                Parameters of the plot.

            Axes : dict
                Axes used for the plot as :class:`qom.utils.axis.StaticAxis`.
        """
        super().__init__(plot_params, Axes)

        # set axes
        self.axes = plt.gca(projection='3d' if self.plot_type in self.plot_types_3D else None)

        # update math fonts
        plt.rcParams['mathtext.fontset'] = plot_params.get('font_math', 'cm')

        # update title
        plt.title(plot_params.get('title', ''), fontdict=self.font_dicts['label'])
        
        # update labels
        plt.xlabel(self.labels.get('X'), fontdict=self.font_dicts['label'])
        plt.ylabel(self.labels.get('Y'), fontdict=self.font_dicts['label'])

        # update tick properties
        _font_props = self.__get_font_props(self.font_dicts['tick'])
        plt.setp(self.axes.get_xticklabels(), fontproperties=_font_props)
        plt.setp(self.axes.get_yticklabels(), fontproperties=_font_props)
        plt.ticklabel_format(axis='both', style='plain')

        # default axis
        _default_axis = StaticAxis({
            'var': 'default_axis',
            'values': np.linspace(-1, 1, 5)
        })
        _multi_axis = StaticAxis({
            'var': 'multi_axis',
            'values': [0]
        })
        # common axis
        _X = Axes.get('X', _default_axis)

        # 1D plot
        if self.plot_type in self.plot_types_1D:
            # get axes
            _Z = Axes['Z'] if Axes.get('Z', None) is not None else _multi_axis
            # plot parameters
            _y_ticks = plot_params.get('y_ticks', np.linspace(-1, 1, 5).tolist())
            _colors = plot_params.get('colors', _Z.colors) 
            _legends = plot_params.get('legends', _Z.legends)
            _linestyles = plot_params.get('linestyles', _Z.linestyles)
            _sizes = plot_params.get('sizes', _Z.sizes)
            # initialize 1D plot
            self.__init_1D(_X, _y_ticks, _colors, _legends, _linestyles, _sizes)

        # 2D plot
        elif self.plot_type in self.plot_types_2D:
            # get axes
            _Y = Axes['Y'] if Axes.get('Y', None) is not None else _default_axis
            # plots parameters
            _show_cbar = plot_params.get('show_cbar', True)
            _cmap = self.cmaps.get(plot_params.get('color_grad', 'blr'), 'viridis')
            _shading = plot_params.get('shading', 'gouraud')
            # initializze 2D plot
            self.__init_2D(_X, _Y, _show_cbar, _cmap, _shading)

        # 3D plot
        else:
            _Y = Axes['Y'] if Axes.get('Y', None) is not None else _default_axis
            _Z = Axes['Z'] if Axes.get('Z', None) is not None else _default_axis
            # update axes
            self.axes.set_zlabel(self.labels.get('Z'), fontdict=self.font_dicts['label'])
            plt.setp(self.axes.get_zticklabels(), fontproperties=_font_props)
            # plot parameters
            _show_cbar = plot_params.get('show_cbar', True)
            _cmap = self.cmaps.get(plot_params.get('color_grad', 'blr'), 'viridis')
            # initializze 3D plot
            self.__init_3D(_X, _Y, _Z, _show_cbar, _cmap)

    def __get_font_props(self, font_dict):
        """Method to convert font dictionary to FontProperties.
         
        Parameters
        ----------
            font_dict : dict
                Dictionary of font properties.

        Returns
        -------
            font_props : :class:`matplotlib.font_manager.FontProperties`
                Font properties.
        """

        _font_props = FontProperties(
            family=font_dict['family'],
            style=font_dict['style'],
            variant=font_dict['variant'],
            weight=font_dict['weight'],
            stretch=font_dict['stretch'],
            size=font_dict['size'],
        )

        return _font_props

    def __init_1D(self, X, y_ticks, colors, legends, linestyles, sizes):
        """Method to initialize 1D plots.
        
        Parameters
        ----------
            X : :class:`qom.utils.axis.StaticAxis`
                X-axis.

            y_ticks : list
                Ticks for Y-axis.

            colors : list
                Colors for the plots.

            legends : list
                Legends for the plots.

            linestyles : list
                Linestyles for line plots.

            sizes : list
                Marker sizes for scatter plots.
        """

        # frequently used variables
        _dim = len(legends)

        # set values
        self.values = dict()
        self.values['X'] = X.values

        # update axes
        if type(X.values[0]) is not str:
            self.axes.set_xlim(X.values[0], X.values[-1])
        self.axes.set_xticks(X.ticks)
        self.axes.set_xticklabels(X.tick_labels)
        self.axes.set_ylim(min(y_ticks), max(y_ticks))
        self.axes.set_yticks(y_ticks)

        # line plots
        if self.plot_type == 'line' or self.plot_type == 'lines':
            # collection
            self.plot = [Line2D([], [], color=colors[i], linestyle=linestyles[i]) for i in range(_dim)]
            [self.axes.add_line(self.plot[i]) for i in range(_dim)]
            # heads
            self.head = [Line2D([], [], color=colors[i], linestyle=linestyles[i], marker='o') for i in range(_dim)]
            [self.axes.add_line(self.head[i]) for i in range(_dim)]

        # scatter plots
        elif self.plot_type == 'scatter' or self.plot_type == 'scatters':
            self.plot = [self.axes.scatter([], [], c=colors[i], s=sizes[i]) for i in range(_dim)]

        # update legends
        if _dim > 1:
            _l = plt.legend(legends, loc='best')            
            plt.setp(_l.texts, fontproperties=self.__get_font_props(self.font_dicts['label']))

    def __init_2D(self, X, Y, show_cbar, cmap, shading):
        """Method to initialize 2D plots.
        
        Parameters
        ----------
            X : :class:`qom.utils.axis.StaticAxis`
                X-axis.

            Y : :class:`qom.utils.axis.StaticAxis`
                Y-axis.

            show_cbar : bool
                Option to display colorbar.

            cmap : str or :class:`matplotlib.colorsColorMap`
                Color map for the plot.

            shading : str
                Shading of the plot:
                    'flat' : solid color.
                    'nearest' : centered color.
                    'gouraud' : Gouraud shaded.
                    'auto' : Choose 'flat' or 'nearest' depending on size
        """

        # set values
        self.values = dict()
        self.values['X'] = X.values
        self.values['Y'] = Y.values

        # update axes
        self.axes.set_xlim(X.values[0], X.values[-1])
        self.axes.set_xticks(X.ticks)
        self.axes.set_xticklabels(X.tick_labels)
        self.axes.set_ylim(Y.values[0], Y.values[-1])
        self.axes.set_yticks(Y.ticks)
        self.axes.set_yticklabels(Y.tick_labels)

        # initailize values
        _xs, _ys = np.meshgrid(X.values, Y.values)

        # contourf plot
        if self.plot_type == 'contourf':
            _zeros = np.zeros((len(Y.values), len(X.values)))
            self.plot = self.axes.contourf(_xs, _ys, _zeros, cmap=cmap)

        # pcolormesh plot
        if self.plot_type == 'pcolormesh':
            _nans = np.zeros((len(Y.values), len(X.values)))
            _nans[:] = np.NaN
            self.plot = self.axes.pcolormesh(_xs, _ys, _nans, shading=shading, cmap=cmap)

        # add color bar
        if show_cbar:
            self.cbar = plt.colorbar(self.plot)
            # labels
            self.cbar.set_label(self.labels['cbar'], fontproperties=self.__get_font_props(self.font_dicts['label']))
            # ticks
            plt.setp(self.cbar.ax.get_yticklabels(), fontproperties=self.__get_font_props(self.font_dicts['tick']))
        else:
            self.cbar = None

    def __init_3D(self, X, Y, Z, show_cbar, cmap):
        """Method to initialize 3D plots.
        
        Parameters
        ----------
            X : :class:`qom.utils.axis.StaticAxis`
                X-axis.

            Y : :class:`qom.utils.axis.StaticAxis`
                Y-axis.

            Z : :class:`qom.utils.axis.StaticAxis`
                Z-axis.

            show_cbar : bool
                Option to display colorbar.

            cmap : str or :class:`matplotlib.colorsColorMap`
                Color map for the plot.
        """

        # set values
        self.values = dict()
        self.values['X'] = X.values
        self.values['Y'] = Y.values

        # update axes
        self.axes.set_xlim(X.values[0], X.values[-1])
        self.axes.set_xticks(X.ticks)
        self.axes.set_xticklabels(X.tick_labels)
        self.axes.set_ylim(Y.values[0], Y.values[-1])
        self.axes.set_yticks(Y.ticks)
        self.axes.set_yticklabels(Y.tick_labels)
        _z_ticks = np.linspace(-1, 1, 5).tolist()
        if Z.var != 'default_axis':
            _z_ticks = Z.ticks
        self.axes.set_zticks(_z_ticks)

        # update view
        self.axes.view_init(32, 216)
        _pane_color = (1.0, 1.0, 1.0, 0.0)
        self.axes.xaxis.set_pane_color(_pane_color)
        self.axes.yaxis.set_pane_color(_pane_color)
        self.axes.zaxis.set_pane_color(_pane_color)
        self.axes.zaxis.set_rotate_label(False)
        self.axes.zaxis.label.set_rotation(96)
        _grid_params = {
            'linewidth': 1,
            'color': (0.5, 0.5, 0.5, 0.2)
        }
        self.axes.xaxis._axinfo['grid'].update(_grid_params)
        self.axes.yaxis._axinfo['grid'].update(_grid_params)
        self.axes.zaxis._axinfo['grid'].update(_grid_params)

        # initailize values
        _xs, _ys = np.meshgrid(X.values, Y.values)
        _zeros = np.zeros((len(Y.values), len(X.values)))

        # surface plot
        if 'surface' in self.plot_type:
            self.plot = self.axes.plot_surface(_xs, _ys, _zeros, rstride=1, cstride=1, cmap=cmap)

        # add color bar
        if show_cbar:
            self.cbar = plt.colorbar(self.plot)
            # labels
            self.cbar.set_label(self.labels['cbar'], fontproperties=self.__get_font_props(self.font_dicts['label']))
            # ticks
            plt.setp(self.cbar.ax.get_yticklabels(), fontproperties=self.__get_font_props(self.font_dicts['tick']))
        else:
            self.cbar = None

    def update(self, X=None, Y=None, Z=None, show_head=False):
        """Method to update plot.
        
        Parameters
        ----------
            X : list, optional
                X-axis data as :class:`qom.utils.axis.DynamicAxis`.
                
            Y : list, optional
                Y-axis data as :class:`qom.utils.axis.DynamicAxis`.
                
            Z : list, optional
                Z-axis data as :class:`qom.utils.axis.DynamicAxis`.

            show_head : boolean, optional
                Option to display the head for line-type plots. Default is False.
        """

        # single-line plot
        if self.plot_type == 'line':
            self.__update_1D([X.values], [Y.values], X.size[0], show_head)
        # multi-line plot
        if self.plot_type == 'lines':
            self.__update_1D(X.values, Y.values, X.size[1], show_head)
        # scatter plot
        if self.plot_type == 'scatter':
            self.__update_1D([X.values], [Y.values], None, show_head)
        # scatter plot
        if self.plot_type == 'scatters':
            self.__update_1D(X.values, Y.values, None, show_head)
        
        # 2D plot
        if self.plot_type == 'contourf':
            self.__update_2D(Z.values)
        if self.plot_type == 'pcolormesh':
            self.__update_2D(Z.values)

        # 3D plot
        if 'surface' in self.plot_type:
            self.__update_3D(Z.values)

    def __update_1D(self, xs, ys, dim, head):
        """Method to udpate 1D plots.
        
        Parameters
        ----------
            xs : list
                X-axis values.
                
            ys : list
                Y-axis values.
                
            dim : int
                Dimension of the X-axis.

            head : boolean
                Option to display the head for line-type plots.
        """
        
        # update line plots
        if self.plot_type == 'line' or self.plot_type == 'lines':
            for j in range(len(self.plot)):
                self.plot[j].set_xdata(xs[j])
                self.plot[j].set_ydata(ys[j])
                if head and len(xs[j]) != dim and len(xs[j]) != 0:
                    self.head[j].set_xdata(xs[j][-1:])
                    self.head[j].set_ydata(ys[j][-1:])
                else:
                    self.head[j].set_xdata([])
                    self.head[j].set_ydata([])

        # update scatter plots
        if self.plot_type == 'scatter' or self.plot_type == 'scatters':
            for j in range(len(self.plot)):
                XY = np.c_[xs[j], ys[j]]
                self.plot[j].set_offsets(XY)
                
        # handle nan values for limits
        _minis = []
        _maxis = []
        for j in range(len(ys)):
            # calculate minimum and maximum values
            if len(ys[j]) != 0:
                # handle NaN values
                _no_nan = [y if y == y else 0 for y in ys[j]]

                # update limits
                _minis.append(min(_no_nan))
                _maxis.append(max(_no_nan))

        # set limits
        _mini, _maxi = min(_minis), max(_maxis)
        self.axes.set_ylim(_mini, _maxi)
        self.axes.set_yticks(np.linspace(_mini, _maxi, len(self.axes.get_yticks())))

    def __update_2D(self, zs):
        """Method to udpate 2D plots.
        
        Parameters
        ----------
            zs : list
                Z-axis values.
        """
        
        # update pcolormesh plot
        _rave = np.ravel(zs)
        _cmap = self.plot.get_cmap()

        # handle NaN values
        _no_nan = [z if z == z else 0 for z in _rave]
        _mini, _maxi = min(_no_nan), max(_no_nan)
        _mini, _maxi, _ = get_limits(_mini, _maxi, res=1)

        # contourf plot
        if self.plot_type == 'contourf':
            # remove QuadContourSet PathCollection
            for pc in self.plot.collections:
                self.plot.collections.remove(pc)
            _xs, _ys = np.meshgrid(self.values['X'], self.values['Y'])
            self.plot = self.axes.contourf(_xs, _ys, zs, cmap=_cmap)

            # redraw color bar
            if self.cbar is not None:
                self.cbar.ax.clear()
                self.cbar = plt.colorbar(self.plot, cax=self.cbar.ax)
                # update label
                self.cbar.set_label(self.labels['cbar'], fontproperties=self.__get_font_props(self.font_dicts['label']))
                # update ticks
                plt.setp(self.cbar.ax.get_yticklabels(), fontproperties=self.__get_font_props(self.font_dicts['tick']))

        # pcolormesh plot
        if self.plot_type == 'pcolormesh':
            self.plot.set_array(_rave)

        # set limits
        self.plot.set_clim(vmin=_mini, vmax=_maxi)

        # color bar
        if self.cbar is not None:
            _ticks = np.linspace(_mini, _maxi, 11)
            self.cbar.set_ticks(_ticks)
            self.cbar.draw_all()

    def __update_3D(self, zs):
        """Method to udpate 3D plots.
        
        Parameters
        ----------
            zs : list
                Z-axis values.
        """
        _X, _Y = np.meshgrid(self.values['X'], self.values['Y'])
        _Z = np.array(zs)
        _mini, _maxi = min(_Z.ravel()), max(_Z.ravel())
        _mini, _maxi, _ = get_limits(_mini, _maxi, res=2)

        # surface plot
        if 'surface'in self.plot_type:
            _cmap = self.plot.get_cmap()
            self.plot.remove()
            self.plot = self.axes.plot_surface(_X, _Y, _Z, rstride=1, cstride=1, cmap=_cmap, antialiased=False)

            # projections
            if self.plot_type == 'surface_cz':
                _offset = _maxi + 0.2 * (_maxi - _mini)
                _proj_z = self.axes.contour(_X, _Y, _Z, zdir='z', levels=11, offset=_offset, cmap=_cmap)

            # update colorbar
            if self.cbar is not None:
                self.cbar.update_normal(self.plot)

        # set limits
        _ticks = np.linspace(_mini, _maxi, len(self.axes.get_zticks()))
        self.plot.set_clim(vmin=_mini, vmax=_maxi)
        self.axes.set_zlim(_mini, _maxi)
        self.axes.set_zticks(_ticks)

        # color bar
        if self.cbar is not None:
            _ticks = np.linspace(_mini, _maxi, 11)
            self.cbar.set_ticks(_ticks)
            self.cbar.ax.set_autoscale_on(True)
            self.cbar.draw_all()

    def show(self, hold=False):
        """Method to display plot.

        Parameters
        ----------
            hold : boolean, optional
                Option to hold the plot. Default is True.
        """

        # draw data
        plt.draw()

        # display plot
        if hold:
            plt.show()
        else:
            plt.pause(1e-9)