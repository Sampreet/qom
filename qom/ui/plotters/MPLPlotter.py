#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to handle matplotlib plots."""

__name__    = 'qom.ui.plotters.MPLPlotter'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-10-03'
__updated__ = '2020-10-23'

# dependencies
from matplotlib.colors import Normalize
from matplotlib.font_manager import FontProperties 
from matplotlib.lines import Line2D
import logging
import matplotlib.pyplot as plt
import numpy as np

# dev dependencies
from qom.ui.axes.StaticAxis import StaticAxis
from qom.ui.plotters.BasePlotter import BasePlotter

# module logger
logger = logging.getLogger(__name__)

# TODO: Change attributes to properties.
# TODO: Add annotations.
# TODO: Options for lower and upper bounds.
# TODO: Options for `ticklabel_format`.

class MPLPlotter(BasePlotter):
    """Class to handle matplotlib plots.

    Inherits :class:`qom.ui.plotters.BasePlotter`.
    """

    plot = []
    head = []

    def __init__(self, plot_params, Axes):
        """Class constructor for MPLPlotter.
        
        Parameters
        ----------
            plot_params : dict
                Parameters of the plot.

            Axes : dict
                Axes used for the plot as :class:`qom.utils.axis.StaticAxis`.
        """

        # initialize super class
        super().__init__(plot_params, Axes)

        # extract frequently used variables
        _type = self.plot_params['type']
        _mpl_axes = plt.gca(projection='3d' if _type in self.plot_types_3D else None)
        _font_dicts = self.plot_params['font_dicts']

        # update math fonts
        plt.rcParams['mathtext.fontset'] = _font_dicts['math']

        # update title
        plt.title(self.plot_params['title'], fontdict=_font_dicts['label'])
        
        # update labels
        plt.xlabel(self.axes['X'].label, labelpad=12, fontdict=_font_dicts['label'])
        plt.ylabel(self.axes['Y'].label, labelpad=12, fontdict=_font_dicts['label'])

        # update tick properties
        _font_props = self.__get_font_props(_font_dicts['tick'])
        plt.setp(_mpl_axes.get_xticklabels(), fontproperties=_font_props)
        plt.setp(_mpl_axes.get_yticklabels(), fontproperties=_font_props)
        plt.ticklabel_format(axis='both', style='plain')

        # update ticks
        _mpl_axes.set_xlim(min(self.axes['X'].ticks), max(self.axes['X'].ticks))
        _mpl_axes.set_xticks(self.axes['X'].ticks)
        _mpl_axes.set_xticklabels(self.axes['X'].tick_labels)
        _mpl_axes.set_ylim(min(self.axes['Y'].ticks), max(self.axes['Y'].ticks))
        _mpl_axes.set_yticks(self.axes['Y'].ticks)
        _mpl_axes.set_yticklabels(self.axes['Y'].tick_labels)

        # 1D plot
        if _type in self.plot_types_1D:
            # initialize 1D plot
            self.__init_1D()

        # 2D plot
        elif _type in self.plot_types_2D:
            # initializze 2D plot
            self.__init_2D()

        # 3D plot
        else:
            # update axes
            _mpl_axes.set_zlabel(self.axes['Z'].label, labelpad=12, fontdict=_font_dicts['label'])
            plt.setp(_mpl_axes.get_zticklabels(), fontproperties=_font_props)
            _mpl_axes.set_zlim(min(self.axes['Z'].ticks), max(self.axes['Z'].ticks))
            _mpl_axes.set_zticks(self.axes['Z'].ticks)
            _mpl_axes.set_zticklabels(self.axes['Z'].tick_labels)
            # initializze 3D plot
            self.__init_3D()

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

    def __init_1D(self):
        """Method to initialize 1D plots."""

        # extract frequently used variables
        _type = self.plot_params['type']
        _mpl_axes = plt.gca(projection=None)
        _dim = len(self.axes['Z'].legends)
        if _type == 'line' or _type == 'scatter':
            _dim = 1

        # line plots
        if _type == 'line' or _type == 'lines':
            # collection
            self.plot = [Line2D([], [], color=self.axes['Z'].colors[i], linestyle=self.axes['Z'].styles[i]) for i in range(_dim)]
            [_mpl_axes.add_line(self.plot[i]) for i in range(_dim)]
            # heads
            self.head = [Line2D([], [], color=self.axes['Z'].colors[i], linestyle=self.axes['Z'].styles[i], marker='o') for i in range(_dim)]
            [_mpl_axes.add_line(self.head[i]) for i in range(_dim)]

        # scatter plots
        elif _type == 'scatter' or _type == 'scatters':
            self.plot = [_mpl_axes.scatter([], [], c=self.axes['Z'].colors[i], s=self.axes['Z'].sizes[i]) for i in range(_dim)]

        # update legends
        if self.plot_params['legend']['show']:
            _l = plt.legend(self.axes['Z'].legends, loc='best')            
            plt.setp(_l.texts, fontproperties=self.__get_font_props(self.plot_params['font_dicts']['label']))

    def __init_2D(self):
        """Method to initialize 2D plots."""

        # extract frequently used variables
        _type = self.plot_params['type']
        _mpl_axes = plt.gca(projection=None)
        _cmap = self.plot_params['cmap']
        _font_dicts = self.plot_params['font_dicts']

        # initailize values
        _xs, _ys = np.meshgrid(self.axes['X'].val, self.axes['Y'].val)
        _zeros = np.zeros((self.axes['Y'].dim, self.axes['X'].dim))

        # contour plot
        if _type == 'contour':
            # _zeros[0] = 1
            self.plot = _mpl_axes.contour(_xs, _ys, _zeros, levels=11, cmap=self.plot_params['cmap'])

        # contourf plot
        if _type == 'contourf':
            self.plot = _mpl_axes.contourf(_xs, _ys, _zeros, cmap=_cmap)

        # pcolormesh plot
        if _type == 'pcolormesh':
            _nan =  np.zeros((self.axes['Y'].dim, self.axes['X'].dim))
            _nan[:] = np.NaN
            self.plot = _mpl_axes.pcolormesh(_xs, _ys, _nan, shading='gouraud', cmap=_cmap)

        # add color bar
        if self.plot_params['cbar']['show']:
            if 'contour' in _type:
                _sm = plt.cm.ScalarMappable(cmap=_cmap, norm=Normalize(vmin=0, vmax=0))
                _sm.set_array([])
            else:
                _sm = self.plot
            self.cbar = plt.colorbar(_sm)
            # labels
            self.cbar.ax.set_xlabel(self.plot_params['cbar']['label'], labelpad=_font_dicts['tick']['size'] + 12, fontproperties=self.__get_font_props(_font_dicts['label']))
            # ticks
            _ticks = self.plot_params['cbar']['ticks']
            if _ticks is None:
                _ticks = np.linspace(0, 1, 6)
            self.cbar.set_ticks(_ticks)
            plt.setp(self.cbar.ax.get_yticklabels(), fontproperties=self.__get_font_props(_font_dicts['tick']))
        else:
            self.cbar = None

    def __init_3D(self):
        """Method to initialize 3D plots."""

        # extract frequently used variables
        _type = self.plot_params['type']
        _mpl_axes = plt.gca(projection='3d')
        _cmap = self.plot_params['cmap']
        _font_dicts = self.plot_params['font_dicts']

        # update view
        _mpl_axes.view_init(32, 216)
        _pane_color = (1.0, 1.0, 1.0, 0.0)
        _mpl_axes.xaxis.set_pane_color(_pane_color)
        _mpl_axes.yaxis.set_pane_color(_pane_color)
        _mpl_axes.zaxis.set_pane_color(_pane_color)
        _mpl_axes.zaxis.set_rotate_label(False)
        _mpl_axes.zaxis.label.set_rotation(96)
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

        # surface plot
        if 'surface' in _type:
            self.plot =_mpl_axes.plot_surface(_xs, _ys, _zeros, rstride=1, cstride=1, cmap=_cmap)

        # add color bar
        if self.plot_params['cbar']['show']:
            self.cbar = plt.colorbar(self.plot)
            # labels
            self.cbar.ax.set_xlabel(self.plot_params['cbar']['label'], labelpad=_font_dicts['tick']['size'] + 12, fontproperties=self.__get_font_props(_font_dicts['label']))
            # ticks
            plt.setp(self.cbar.ax.get_yticklabels(), fontproperties=self.__get_font_props(_font_dicts['tick']))
            _ticks = self.plot_params['cbar']['ticks']
            if _ticks is not None:
                self.cbar.set_ticks(_ticks)
        else:
            self.cbar = None

    def update(self, xs=None, ys=None, zs=None, head=False):
        """Method to update plot.
        
        Parameters
        ----------
            xs : list or numpy.ndarray, optional
                X-axis data.
                
            ys : list or numpy.ndarray, optional
                Y-axis data.
                
            zs : list or numpy.ndarray, optional
                Z-axis data.

            head : boolean, optional
                Option to display the head for line-type plots. Default is False.
        """

        # extract frequently used variables
        _type = self.plot_params['type']

        # single-line plot
        if _type == 'line' or _type == 'scatter':
            self.__update_1D([xs], [ys], head)
        # multi-line plot
        if _type == 'lines' or _type == 'scatters':
            self.__update_1D(xs, ys, head)
        
        # 2D plots
        if _type in self.plot_types_2D:
            self.__update_2D(zs)

        # 3D plot
        if 'surface' in _type:
            self.__update_3D(zs)

    def __update_1D(self, xs, ys, head):
        """Method to udpate 1D plots.
        
        Parameters
        ----------
            xs : list or numpy.ndarray
                X-axis values.
                
            ys : list or numpy.ndarray
                Y-axis values.

            head : boolean
                Option to display the head for line-type plots.
        """

        # frequently used variables
        _type = self.plot_params['type']
        _mpl_axes = plt.gca(projection=None)
        _dim = len(xs[0])
        
        # update line plots
        if _type == 'line' or _type == 'lines':
            for j in range(len(self.plot)):
                self.plot[j].set_xdata(xs[j])
                self.plot[j].set_ydata(ys[j])
                _idx_nan = np.argwhere(np.isnan(ys[j]))
                _idx_nan = _idx_nan[0][0] if len(_idx_nan) != 0 else -1
                if head and _idx_nan < _dim - 1 and _idx_nan != -1:
                    self.head[j].set_xdata(xs[j][_idx_nan - 1 : _idx_nan])
                    self.head[j].set_ydata(ys[j][_idx_nan - 1 : _idx_nan])
                else:
                    self.head[j].set_xdata([])
                    self.head[j].set_ydata([])

        # update scatter plots
        if _type == 'scatter' or _type == 'scatters':
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
        _mini, _maxi, _prec = super().get_limits(_mini, _maxi, res=1)
        _ticks = self.axes['Y'].ticks
        _tick_labels = self.axes['Y'].tick_labels
        if self.axes['Y'].bound == 'none':
            _ticks = np.linspace(_mini, _maxi, len(_mpl_axes.get_yticks()))
            _tick_labels = _ticks
        _mini = min(_ticks)
        _maxi = max(_ticks)
        _mpl_axes.set_ylim(_mini, _maxi)
        _mpl_axes.set_yticks(_ticks)
        _mpl_axes.set_yticklabels(_tick_labels)

    def __update_2D(self, zs):
        """Method to udpate 2D plots.
        
        Parameters
        ----------
            zs : list or numpy.ndarray
                Z-axis values.
        """

        # frequently used variables
        _type = self.plot_params['type']
        _mpl_axes = plt.gca(projection=None)
        _cmap = self.plot_params['cmap']
        _font_dicts = self.plot_params['font_dicts']
        _rave = np.ravel(zs)

        # handle NaN values
        _no_nan = [z if z == z else 0 for z in _rave]
        _mini, _maxi = min(_no_nan), max(_no_nan)
        _mini, _maxi, _ = super().get_limits(_mini, _maxi, res=1)

        # contour and contourf plots
        if 'contour' in _type:
            # remove QuadContourSet PathCollection
            for pc in self.plot.collections:
                pc.remove()
            _xs, _ys = np.meshgrid(self.axes['X'].val, self.axes['Y'].val)

            # contour plot
            if _type == 'contour':
                self.plot = _mpl_axes.contour(_xs, _ys, zs, levels=11, cmap=_cmap)
            # contourf plot
            if _type == 'contourf':
                self.plot = _mpl_axes.contourf(_xs, _ys, zs, levels=11, cmap=_cmap)

            # redraw color bar
            if self.cbar is not None:
                self.cbar.ax.clear()
                _sm = plt.cm.ScalarMappable(cmap=_cmap, norm=Normalize(vmin=_mini, vmax=_maxi))
                _sm.set_array([])
                self.cbar = plt.colorbar(_sm, cax=self.cbar.ax)
                # update label
                self.cbar.ax.set_xlabel(self.plot_params['cbar']['label'], labelpad=_font_dicts['tick']['size'] + 12, fontproperties=self.__get_font_props(_font_dicts['label']))
                # update ticks
                plt.setp(self.cbar.ax.get_yticklabels(), fontproperties=self.__get_font_props(_font_dicts['tick']))

        # pcolormesh plot
        if _type == 'pcolormesh':
            self.plot.set_array(_rave)

        # set limits
        self.plot.set_clim(vmin=_mini, vmax=_maxi)

        # color bar
        if self.cbar is not None:
            _ticks = self.plot_params['cbar']['ticks']
            if _ticks is None:
                _ticks = np.linspace(_mini, _maxi, len(self.cbar.get_ticks()))
            self.cbar.set_ticks(_ticks)
            self.cbar.draw_all()

    def __update_3D(self, zs):
        """Method to udpate 3D plots.
        
        Parameters
        ----------
            zs : list or numpy.ndarray
                Z-axis values.
        """

        # frequently used variables
        _type = self.plot_params['type']
        _mpl_axes = plt.gca(projection='3d')
        _cmap = self.plot_params['cmap']
        _font_dicts = self.plot_params['font_dicts']

        _X, _Y = np.meshgrid(self.axes['X'].val, self.axes['Y'].val)
        _Z = np.array(zs) if type(zs) is list else zs
        _mini, _maxi = min(_Z.ravel()), max(_Z.ravel())
        _mini, _maxi, _ = super().get_limits(_mini, _maxi, res=1)

        # surface plot
        if 'surface'in _type:
            _cmap = self.plot.get_cmap()
            self.plot.remove()
            self.plot = _mpl_axes.plot_surface(_X, _Y, _Z, rstride=1, cstride=1, cmap=_cmap, antialiased=False)

            # projections
            if _type == 'surface_cz':
                _offset = _maxi + 0.2 * (_maxi - _mini)
                _proj_z = _mpl_axes.contour(_X, _Y, _Z, zdir='z', levels=11, offset=_offset, cmap=_cmap)

            # update colorbar
            if self.cbar is not None:
                self.cbar.update_normal(self.plot)

        # set limits
        _ticks = self.axes['Z'].ticks
        _tick_labels = self.axes['Z'].tick_labels
        if self.axes['Z'].bound == 'none':
            _ticks = np.linspace(_mini, _maxi, len(_mpl_axes.get_zticks()))
            _tick_labels = _ticks
        _mini = min(_ticks)
        _maxi = max(_ticks)
        self.plot.set_clim(vmin=_mini, vmax=_maxi)
        _mpl_axes.set_zlim(_mini, _maxi)
        _mpl_axes.set_zticks(_ticks)
        _mpl_axes.set_zticklabels(_tick_labels)

        # color bar
        if self.cbar is not None:
            _ticks = self.plot_params['cbar']['ticks']
            if _ticks is None:
                _ticks = np.linspace(_mini, _maxi, len(_mpl_axes.get_zticks()))
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
        plt.tight_layout()
        # plt.subplots_adjust(top=0.99, bottom=0.06, left=0.06, right=0.99)

        # display plot
        if hold:
            plt.show()
        else:
            plt.pause(1e-9)