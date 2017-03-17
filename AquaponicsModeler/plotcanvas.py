# -*- coding: utf-8 -*-
"""This module contains the plot window for the application."""
from PyQt5 import QtWidgets,  QtCore
from PyQt5.Qt import QWidget
import logging

from matplotlib.backends import backend_qt5agg
import matplotlib.pyplot as plt

FigureCanvas = backend_qt5agg.FigureCanvasQTAgg
NavigationToolbar = backend_qt5agg.NavigationToolbar2QT


class PlotWindow(QWidget):

    """The main plot window."""

    def __init__(self):
        """Init the plot window."""

        QWidget.__init__(self)

        self.log = logging.getLogger('aquaponics.plotcanvas.PlotWindow')
        self.setWindowTitle("Plots")

        self.canvas = None
        self.toolbar = None

        #  HLayout to divide between plot area and list widget
        self.hlayout = QtWidgets.QHBoxLayout()
        self.setLayout(self.hlayout)

        #  VLayout to divide between plot canvas and toolbar
        widget = QtWidgets.QWidget(self)
        self.vlayout = QtWidgets.QVBoxLayout(self)
        self.vlayout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(self.vlayout)
        self.hlayout.addWidget(widget)

        groupbox = QtWidgets.QGroupBox(self)
        groupbox.setObjectName("plotHistory")
        groupbox.setTitle("Plot History")
        groupbox_layout = QtWidgets.QVBoxLayout(groupbox)
        groupbox_layout.setContentsMargins(0, 10, 0, 0)
        groupbox_layout.setSpacing(0)
        self.plotList = QtWidgets.QListWidget()
        self.plotList.itemClicked.connect(self.restoreFigure)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum,
                                           QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setWidthForHeight(False)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.plotList.sizePolicy().hasHeightForWidth())
        self.plotList.setMaximumSize(QtCore.QSize(150, 16777215))
        self.plotList.setSizePolicy(sizePolicy)
        groupbox_layout.addWidget(self.plotList)
        self.hlayout.addWidget(groupbox)

    def restoreFigure(self, item):
        """
        Restore a previously created plot to the canvas and toolbar widgets.

        Args:
            item (QListWidgetItem): The item that was clicked in self.plotList.

        """
        fig = item.listWidget().row(item)
        data = item.data(QtCore.Qt.UserRole)
        self.log.debug('Restoring plot %i with data %s.' % (fig, data))
        self.plot(data, restore=True)

    def delFigure(self):
        """Remove the current figure form the canvas and toolbar widgets."""
        if self.canvas is not None:
            self.vlayout.removeWidget(self.canvas)
        if self.toolbar is not None:
            self.vlayout.removeWidget(self.toolbar)

    def addFigure(self):
        """Add a new figure to the canvas, plotList and toolbar widgets."""

        self.fig = plt.figure()
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas,  self)
        self.vlayout.addWidget(self.toolbar)
        self.vlayout.addWidget(self.canvas)

    def plot(self,  data,  restore=False):
        """
        Plot data on the canvas using Matplotlib.

        Args:
            data (PlotData): A PlotData instance with the data to be plotted.
                It contains a list of DataSeries items with one instance
                for each subplot (only 2 supported now). Each subplot has a
                constant x-axis and y-axis scale but can contain multiple
                dataItems, each resulting in a separate line in the plot.
            restore (bool): This tells the plot function whether we are
                restoring an old figure or adding a new one. In the first case
                the figure is not added to self.plotList as it is there
                already.

        """
        self.delFigure()
        self.addFigure()

        numplots = self.plotList.count()
        if restore is False:
            item = QtWidgets.QListWidgetItem("%s" % (numplots + 1, ))
            item.setData(QtCore.Qt.UserRole, data)
            self.plotList.insertItem(numplots, item)
            item.setSelected(True)
        num_series = len(data.dataSeries)
        gs = plt.GridSpec(num_series * 2 + 1, 3)
        for i, series in enumerate(data.dataSeries):
            colors = ['g', 'r', 'c', 'm', 'y', 'k', 'b']
            sp = self.fig.add_subplot(gs[i * 2:i * 2 + 2, :-1])
            sp.set_xlabel(series.x_title)
            sp.set_ylabel(series.y_title)
            x = series.x_values

            items = []

            for i, d in enumerate(series.dataItems):
                vals = d.values
                numvals = len(vals)
                label = d.title
                self.log.debug('Got %i items in series item %i' % (numvals, i))
                item, = sp.plot(x, vals, '%s-' % colors.pop(),  label=label)
                items.append(item)
            sp.legend(handles=items, loc='upper left', borderaxespad=0.,
                      bbox_to_anchor=(1.05, 1), prop={'size': 8})

        plt.figtext(0.02, 0.02,  data.description)
        plt.tight_layout()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        self.canvas.update()
