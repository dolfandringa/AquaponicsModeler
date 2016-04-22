# -*- coding: utf-8 -*-
"""
This module contais classes to package the model data necessary for plotting.

DataSeries is the main class of interest.

"""


class DataItem(object):

    """One line in a plot. It contains y-axis values and a title."""

    def __init__(self,  title,  values,  params):
        """Init the DataItem.

        Args:
            title (string): The title to be used in the legend.
            values (list): A list of y-axis values to for this line.
            params (list): A list of model parameters containing (title, value)

        """
        self.title = title
        self.values = values
        self.params = params


class DataSeries(object):

    """
    DataSeries contains series of data to plot in a single plot.

    The y-axis and x-axis scales should be identical for each dataItem.
    Each dataItem is represented by a line in the plot and legend.

    """

    def __init__(self, x_title,  y_title,  x_values, dataItems):
        """
        Init the Data Series.

        Args:
            x_title (string): The title for the x-axis
            y_title (string): The title for the y-axis
            x_values (list): A list of values for the x-axis.
            dataItems (list): A list of DataItem objects, one for each line.

        """
        self.dataItems = dataItems
        self.y_title = y_title
        self.x_title = x_title
        self.x_values = x_values


class PlotData(object):

    """PlotData contains data necessary to create plots from a model run."""

    def __init__(self, dataSeries, description):
        """
        Init the Plot Data.

        Args:
            dataSeries (list): A list of DataSeries items for this plot.
            description (string): A description to display below the plot.

        """
        self.dataSeries = dataSeries
        self.description = description
