#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to handle matplotlib plots."""

__name__    = 'qom.ui.plotters.MPLPlotter'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-10-03'
__updated__ = '2021-02-24'

# dependencies
from matplotlib.colors import Normalize
from matplotlib.font_manager import FontProperties 
from matplotlib.lines import Line2D
from typing import Union
import logging
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# qom modules
from .BasePlotter import BasePlotter

# module logger
logger = logging.getLogger(__name__)

# data types
t_list = Union[list, np.ndarray]

# TODO: Add annotations.
# TODO: Options for 3D plot parameters.
# TODO: Options for `ticklabel_format` and padding.

class MPLPlotter(BasePlotter):
    """Class to handle matplotlib plots.

    Inherits :class:`qom.ui.plotters.BasePlotter`.
        
    Parameters
    ----------
    axes : dict
        Axes for the plot.
    params : dict
        Parameters of the plot.
    """

    def __init__(self, axes: dict, params: dict):
        """Class constructor for MPLPlotter."""

        # initialize super class
        super().__init__(axes, params)

        # extract frequently used variables
        _type = self.params['type']
        _mpl_axes = plt.gca(projection='3d' if _type in self.types_3D else None)
        _font_dicts = self.params['font_dicts']

        # update fonts
        plt.rcParams['mathtext.fontset'] = _font_dicts['math']

        # update title
        _mpl_axes.set_title(self.params['title'], fontdict=_font_dicts['label'], pad=12)

        # udpate ticks
        plt.ticklabel_format(axis='both', style='plain')

        # update x-axis
        self.__update_axis(_mpl_axes, 'x', self.axes['X'])

        # 1D plot
        if _type in self.types_1D:
            # update y-axis
            self.__update_axis(_mpl_axes, 'y', self.axes['V'])

            # initialize 1D plot
            self.__init_1D()

        # 2D plot
        elif _type in self.types_2D:
            # update y-axis
            self.__update_axis(_mpl_axes, 'y', self.axes['Y'])

            # initializze 2D plot
            self.__init_2D()

        # 3D plot
        else:
            # update y-axis
            self.__update_axis(_mpl_axes, 'y', self.axes['Y'])
            # update z-axis
            self.__update_axis(_mpl_axes, 'z', self.axes['V'])

            # initializze 3D plot
            self.__init_3D()

    def __get_font_props(self, font_dict: dict):
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

        # convert to FontProperties
        _font_props = FontProperties(
            family=font_dict['family'],
            style=font_dict['style'],
            variant=font_dict['variant'],
            weight=font_dict['weight'],
            stretch=font_dict['stretch'],
            size=font_dict['size'],
        )

        # return
        return _font_props

    def __init_1D(self):
        """Method to initialize 1D plots."""

        # extract frequently used variables
        _type = self.params['type']
        _mpl_axes = plt.gca(projection=None)
        _palette = self.params['palette']
        _colors = self.axes['Y'].colors
        _styles = self.axes['Y'].styles
        _dim = len(self.axes['Y'].legends)

        # handle dimension for single-value plot
        if _type == 'line' or _type == 'scatter':
            _dim = 1

        # udpate colors
        if _colors is None:
            _colors = self.get_palette(_palette, self.bins, False)
            self.axes['Y'].colors = _colors

        # line plots
        if 'line' in _type:
            # plots
            self.plots = [Line2D([], [], color=_colors[i], linestyle=_styles[i]) for i in range(_dim)]
            [_mpl_axes.add_line(self.plots[i]) for i in range(_dim)]
            # heads
            self.heads = [Line2D([], [], color=_colors[i], linestyle=_styles[i], marker='o') for i in range(_dim)]
            [_mpl_axes.add_line(self.heads[i]) for i in range(_dim)]

        # scatter plots
        elif 'scatter' in _type:
            self.plots = [_mpl_axes.scatter([], [], c=_colors[i], s=self.axes['Y'].sizes[i], marker=_styles[i]) for i in range(_dim)]

        # legends
        if self.params['legend']['show']:
            _l = plt.legend(self.axes['Y'].legends, loc=self.params['legend']['location'])            
            plt.setp(_l.texts, fontproperties=self.__get_font_props(self.params['font_dicts']['label']))

    def __init_2D(self):
        """Method to initialize 2D plots."""

        # extract frequently used variables
        _type = self.params['type']
        _mpl_axes = plt.gca(projection=None)
        _font_dicts = self.params['font_dicts']
        _cmap = self.params['cmap']

        # initailize values
        _xs, _ys = np.meshgrid(self.axes['X'].val, self.axes['Y'].val)
        _zeros = np.zeros((self.axes['Y'].dim, self.axes['X'].dim))
        _nan =  np.zeros((self.axes['Y'].dim, self.axes['X'].dim))
        _nan[:] = np.NaN

        # contour plot
        if _type == 'contour':
            self.plots = _mpl_axes.contour(_xs, _ys, _zeros, levels=self.bins, cmap=_cmap)

        # contourf plot
        if _type == 'contourf':
            self.plots = _mpl_axes.contourf(_xs, _ys, _zeros, levels=self.bins, cmap=_cmap)

        # pcolormesh plot
        if _type == 'pcolormesh':
            self.plots = _mpl_axes.pcolormesh(_xs, _ys, _nan, shading='gouraud', cmap=_cmap)

        # color bar
        self.cbar = None

    def __init_3D(self):
        """Method to initialize 3D plots."""

        # extract frequently used variables
        _type = self.params['type']
        _mpl_axes = plt.gca(projection='3d')
        _cmap = self.params['cmap']

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
            self.plots =_mpl_axes.plot_surface(_xs, _ys, _zeros, rstride=1, cstride=1, cmap=_cmap)

        # color bar
        self.cbar = None

    def __update_1D(self, xs: t_list, vs: t_list, head: bool):
        """Method to udpate 1D plots.
        
        Parameters
        ----------
        xs : list or numpy.ndarray
            X-axis values.
        vs : list or numpy.ndarray
            Y-axis values.
        head : boolean
            Option to display the head for line-type plots.
        """

        # frequently used variables
        _type = self.params['type']
        _mpl_axes = plt.gca(projection=None)
        _dim = len(xs[0])
        
        # line plots
        if 'line' in _type:
            for j in range(len(self.plots)):
                self.plots[j].set_xdata(xs[j])
                self.plots[j].set_ydata(vs[j])
                _idx_nan = np.argwhere(np.isnan(vs[j]))
                _idx_nan = _idx_nan[0][0] if len(_idx_nan) != 0 else -1
                if head and _idx_nan < _dim - 1 and _idx_nan != -1:
                    self.heads[j].set_xdata(xs[j][_idx_nan - 1 : _idx_nan])
                    self.heads[j].set_ydata(vs[j][_idx_nan - 1 : _idx_nan])
                else:
                    self.heads[j].set_xdata([])
                    self.heads[j].set_ydata([])

        # scatter plots
        if 'scatter' in _type:
            for j in range(len(self.plots)):
                XY = np.c_[xs[j], vs[j]]
                self.plots[j].set_offsets(XY)
                
        # handle nan values for limits
        _minis = []
        _maxis = []
        for j in range(len(vs)):
            # calculate minimum and maximum values
            if len(vs[j]) != 0:
                # handle NaN values
                _no_nan = [y if y == y else 0 for y in vs[j]]

                # update limits
                _minis.append(min(_no_nan))
                _maxis.append(max(_no_nan))

        # get limits
        _mini, _maxi = min(_minis), max(_maxis)
        _mini, _maxi, _prec = super().get_limits(_mini, _maxi)

        # ticks and tick labels
        _ticks = self.axes['V'].ticks
        _tick_labels = self.axes['V'].tick_labels
        if self.axes['V'].bound == 'none':
            _ticks = np.around(np.linspace(_mini, _maxi, len(_mpl_axes.get_yticks())), decimals=_prec)
            _tick_labels = _ticks
        _mini = min(_ticks)
        _maxi = max(_ticks)
        _mpl_axes.set_yticks(_ticks)
        _mpl_axes.set_yticklabels(_tick_labels)

        # update limits
        _mpl_axes.set_ylim(_mini, _maxi)

    def __update_2D(self, vs: t_list):
        """Method to udpate 2D plots.
        
        Parameters
        ----------
        vs : list or numpy.ndarray
            V-axis values.
        """

        # frequently used variables
        _type = self.params['type']
        _mpl_axes = plt.gca(projection=None)
        _font_dicts = self.params['font_dicts']
        _cmap = self.params['cmap']
        _rave = np.ravel(vs)

        # initialize values
        _no_nan = [z if z == z else 0 for z in _rave]
        _mini, _maxi = min(_no_nan), max(_no_nan)

        # handle color bar limits
        if self.params['cbar']['show'] and self.params['cbar']['ticks'] is not None:
            _mini = self.params['cbar']['ticks'][0]
            _maxi = self.params['cbar']['ticks'][-1]
            _prec = np.ceil(-np.log10(_mini))
        else:
            _mini, _maxi, _prec = super().get_limits(_mini, _maxi)

        # contour and contourf plots
        if 'contour' in _type:
            # remove QuadContourSet PathCollection
            for pc in self.plots.collections:
                pc.remove()
            _xs, _ys = np.meshgrid(self.axes['X'].val, self.axes['Y'].val)

            # contour plot
            if _type == 'contour':
                self.plots = _mpl_axes.contour(_xs, _ys, vs, levels=self.bins, cmap=_cmap)
            # contourf plot
            if _type == 'contourf':
                self.plots = _mpl_axes.contourf(_xs, _ys, vs, levels=self.bins, cmap=_cmap)

        # pcolormesh plot
        if _type == 'pcolormesh':
            self.plots.set_array(_rave)

        # set limits
        self.plots.set_clim(vmin=_mini, vmax=_maxi)

        # color bar
        if self.params['cbar']['show']:
            self.set_cbar(_mini, _maxi, _prec)

    def __update_3D(self, vs: t_list):
        """Method to udpate 3D plots.
        
        Parameters
        ----------
        vs : list or numpy.ndarray
            Z-axis or V-axis values.
        """

        # frequently used variables
        _type = self.params['type']
        _mpl_axes = plt.gca(projection='3d')
        _font_dicts = self.params['font_dicts']
        _cmap = self.params['cmap']

        # initialize values
        _X, _Y = np.meshgrid(self.axes['X'].val, self.axes['Y'].val)
        _Z = np.array(vs) if type(vs) is list else vs
        _mini, _maxi = min(_Z.ravel()), max(_Z.ravel())
        _mini, _maxi, _prec = super().get_limits(_mini, _maxi)

        # surface plot
        if 'surface'in _type:
            _cmap = self.plots.get_cmap()
            self.plots.remove()
            self.plots = _mpl_axes.plot_surface(_X, _Y, _Z, rstride=1, cstride=1, cmap=_cmap, antialiased=False)

            # projections
            if _type == 'surface_cz':
                _offset = _maxi + 0.2 * (_maxi - _mini)
                _proj_z = _mpl_axes.contour(_X, _Y, _Z, zdir='z', levels=self.bins, offset=_offset, cmap=_cmap)

            # update colorbar
            if self.cbar is not None:
                self.cbar.update_normal(self.plots)

        # update ticks and tick labels
        _ticks = self.axes['V'].ticks
        _tick_labels = self.axes['V'].tick_labels
        if self.axes['V'].bound == 'none':
            _ticks = np.linspace(_mini, _maxi, len(_mpl_axes.get_zticks()))
            _tick_labels = _ticks
        _mini = min(_ticks)
        _maxi = max(_ticks)
        _mpl_axes.set_zticks(_ticks)
        _mpl_axes.set_zticklabels(_tick_labels)

        # update limits
        self.plots.set_clim(vmin=_mini, vmax=_maxi)
        _mpl_axes.set_zlim(_mini, _maxi)

        # color bar
        if self.params['cbar']['show']:
            self.set_cbar(_mini, _maxi, _prec)
            self.cbar.ax.set_autoscale_on(True)

    def __update_axis(self, ax, ax_name: str, ax_data: dict):
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
        _font_dicts = self.params['font_dicts']
        _font_props = self.__get_font_props(_font_dicts['tick'])

        # labels
        getattr(ax, 'set_' + ax_name + 'label')(ax_data.label, labelpad=12, fontdict=_font_dicts['label'])

        # ticks
        getattr(ax, 'set_' + ax_name + 'lim')(min(ax_data.ticks), max(ax_data.ticks))
        getattr(ax, 'set_' + ax_name + 'ticks')(ax_data.ticks)
        ax.tick_params(axis=ax_name, which='major', pad=12)

        # tick labels
        getattr(ax, 'set_' + ax_name + 'ticklabels')(ax_data.tick_labels)
        plt.setp(getattr(ax, 'get_' + ax_name + 'ticklabels')(), fontproperties=_font_props)

    def gca(self):
        """Method to obtain the axes of the figure.
        
        Returns
        -------
        axes : :class:`matplotlib.axes.Axes`
            Axes of the figure.
        """

        # frequently used variables
        _type = self.params['type']

        return plt.gca(projection='3d' if _type in self.types_3D else None)

    def gcf(self):
        """Method to obtain the current figure.
        
        Returns
        -------
        fig : :class:`matplotlib.pyplot.figure`
            Current figure.
        """
        
        return plt.gcf()

    def gta(self):
        """Method to obtain a twin axes of the figure.
        
        Returns
        ----------
        axes : :class:`matplotlib.axes.Axes`
            Axes of the figure.
        """

        # frequently used variables
        _type = self.params['type']
        _font_dicts = self.params['font_dicts']
        _font_props = self.__get_font_props(_font_dicts['tick'])

        # initialize twin axis
        ax_twin = plt.twinx()

        # labels
        ax_twin.set_ylabel('a', labelpad=12, fontdict=_font_dicts['label'])

        # ticks
        plt.setp(ax_twin.get_yticklabels(), fontproperties=_font_props)
        ax_twin.tick_params(axis='y', which='major', pad=12)

        return ax_twin

    def set_cbar(self, mini: float=0, maxi: float=0, prec: int=2):
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

        # frequently used variables
        _orientation = self.params['cbar']['orientation']
        _font_dicts = self.params['font_dicts']
        _cax = None

        # clear if existed
        if self.cbar is not None:
            self.cbar.ax.clear()
            _cax = self.cbar.ax

        # set scalar mappable 
        if 'contour' in self.params['type']:
            _sm = plt.cm.ScalarMappable(cmap=self.params['cmap'], norm=Normalize(vmin=mini, vmax=maxi))
            _sm.set_array([])
        else:
            _sm = self.plots

        # initialize
        self.cbar = plt.colorbar(_sm, cax=_cax, orientation=_orientation)

        # title
        self.cbar.ax.set_title(self.params['cbar']['title'], fontproperties=self.__get_font_props(_font_dicts['label']), pad=12)

        # labels
        self.cbar.ax.set_xlabel(self.params['cbar']['x_label'], labelpad=_font_dicts['tick']['size'] + 12, fontproperties=self.__get_font_props(_font_dicts['label']))
        self.cbar.ax.set_ylabel(self.params['cbar']['y_label'], labelpad=_font_dicts['tick']['size'] + 12, fontproperties=self.__get_font_props(_font_dicts['label']))

        # ticks
        _ticks = self.params['cbar']['ticks']
        if _ticks is None:
            _ticks = np.around(np.linspace(mini, maxi, self.bins), decimals=prec)
        self.cbar.set_ticks(_ticks)

        # tick labels
        _tick_labels = self.params['cbar']['tick_labels']
        if _tick_labels is None:
            _tick_labels = _ticks
        self.cbar.set_ticklabels(_tick_labels)
        plt.setp(self.cbar.ax.get_yticklabels(), fontproperties=self.__get_font_props(_font_dicts['tick']))
        plt.setp(self.cbar.ax.get_xticklabels(), fontproperties=self.__get_font_props(_font_dicts['tick']))
        self.cbar.ax.tick_params(axis='x', which='major', pad=12)
        self.cbar.ax.tick_params(axis='y', which='major', pad=12)

        # draw colorbar
        self.cbar.draw_all()

    def update(self, xs: t_list=None, ys: t_list=None, zs: t_list=None, vs: t_list=None, head: bool=False):
        """Method to update the figure.
        
        Parameters
        ----------
        xs : list or numpy.ndarray, optional
            X-axis data.
        ys : list or numpy.ndarray, optional
            Y-axis data.
        zs : list or numpy.ndarray, optional
            Z-axis data.
        vs : list or numpy.ndarray, optional
            V-axis data.
        head : bool, optional
            Option to display the head for line-type plots. Default is False.
        """

        # extract frequently used variables
        _type = self.params['type']

        # single-line plot
        if _type == 'line' or _type == 'scatter':
            self.__update_1D([xs], [vs], head)
        # multi-line plot
        if _type == 'lines' or _type == 'scatters':
            self.__update_1D(xs, vs, head)
        
        # 2D plots
        if _type in self.types_2D:
            self.__update_2D(vs)

        # 3D plot
        if 'surface' in _type:
            self.__update_3D(vs)

    def show(self, hold: bool=False):
        """Method to display the figure.

        Parameters
        ----------
        hold : bool, optional
            Option to hold the plot. Default is False.
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