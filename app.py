#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains the actual Qt app."""
from PyQt5 import QtWidgets,  QtCore
from PyQt5.Qt import QRect
import sys
import logging
from . import interface
from . import model
from .plotcanvas import PlotWindow
from .plotdata import DataSeries,  DataItem,  PlotData


logging.basicConfig(level=logging.INFO, stream=sys.stdout)


def run_model(chain,  timestep, runtime,  log):
    """
    Run the actual model and return the data series.

    Args:
        timestep (integer): The time steps (seconds) for the model.
            Minimum is 1 second, max is 3600s (1 hour)
        runtime (integer): The total time (hours) the model should run for.
            Minimum is 1 hour, maximum is 23 hours.
        chain (list): A list of :class:`model.BaseModelClass`) containing the
            chain model, which should contain objects inheriting from
            :class:`model.BaseModelClass`.
        log (logging.Logger): The logger to use for logging.

    Returns:
        list: A list with an item for the time series plus an item for
            each model component in <chain>, with the data series for that
            component.

    """
    runtime = runtime * 3600
    results = [[] for c in chain]
    results.append([])

    for t in range(0, runtime, timestep):
        results[0].append(t)
        log.debug("Stepping to time %i" % t)
        for i, c in enumerate(chain):
            results[i + 1].append(c.get_state())
        for c in reversed(chain):
            c.step(timestep)
    return results


def get_parameter_widget(name,  type):
    """
    Map a tuple with model parameter type information into a QtWidget set.

    Args:
        name (string): The name of the parameter.
        type (tuple): A tuple with parameter information. The first item is
            always the the second is the label to display and subsequent items
            might be needed to create the widget.

    Returns:
        list: A list with :class:`QtWidgets.QtWidget` for all widgets for this
            parameter.

    """

    if type[0] == model._PARAM_TYPES.MODEL:
        return []
    elif type[0] == model._PARAM_TYPES.INTEGER:
        label = QtWidgets.QLabel()
        label.setText(type[1])
        label.setObjectName('lab_%s' % name)
        widget = QtWidgets.QSpinBox()
        widget.setMaximum(99999)
        widget.setObjectName('w_%s' % name)
        label.setBuddy(widget)
        return [label,  widget]
    elif type[0] == model._PARAM_TYPES.FLOAT:
        label = QtWidgets.QLabel()
        label.setText(type[1])
        label.setObjectName('lab_%s' % name)
        widget = QtWidgets.QDoubleSpinBox()
        widget.setMaximum(99999)
        widget.setObjectName('w_%s' % name)
        label.setBuddy(widget)
        return [label,  widget]
    elif type[0] == model._PARAM_TYPES.TEXT:
        label = QtWidgets.QLabel()
        label.setText(type[1])
        label.setObjectName('lab_%s' % name)
        widget = QtWidgets.QLineEdit()
        widget.setObjectName('w_%s' % name)
        label.setBuddy(widget)
        return [label,  widget]


class AquaponicsModeler(QtWidgets.QMainWindow,  interface.Ui_MainWindow):

    """The graphical interface to the aquaponics modeler."""

    def __init__(self, log,   parent=None):
        """Instantiate the application."""
        super(AquaponicsModeler,  self).__init__(parent)
        self.log = log
        self.setupUi(self)
        self.bt_add_row.clicked.connect(self.addRow)
        self.bt_del_row.clicked.connect(self.deleteSelectedRows)
        self.btn_run.clicked.connect(self.runModel)
        self.plotWindow = PlotWindow()
        self.plotWindow.setGeometry(QRect(0, 0, 600, 400))

    def showErrorMessage(self,  message):
        """Popup a message box with an error message."""
        msgbx = QtWidgets.QMessageBox()
        msgbx.setText(message)
        msgbx.setIcon(QtWidgets.QMessageBox.Critical)
        msgbx.exec_()

    def plotResults(self,  results,  chain):
        """Plot the results of a model run with matplotlib."""
        x = [r / 60 for r in results[0]]
        pumpSeries = DataSeries(x_title='Time (min)',
                                y_title='State (on/off)',
                                x_values=x, dataItems=[])
        containerSeries = DataSeries(x_title='Time (min)',
                                     y_title='Contents (L)',
                                     x_values=x, dataItems=[])
        self.log.debug("Got %i items for time axis" % len(x))

        items = []
        names = []
        for i, c in enumerate(chain):
            params = c.__class__.getParameters()
            paramValues = [(k, str(getattr(c, k))) for k in params.keys()]
            num = 1
            name = "%s%i" % (c, num)
            while name in names:
                num += 1
                name = "%s%i" % (c, num)
            names.append(name)
            item = DataItem(title=name,
                            values=results[i + 1],
                            params=paramValues)
            if isinstance(c, model.Pump):
                self.log.debug('Adding a series with %i items to pumpSeries.'
                               % len(item.values))
                pumpSeries.dataItems.append(item)
            elif isinstance(c, model.Container):
                self.log.debug('Adding a series with %i' % len(item.values) +
                               ' items to containerSeries.')
                containerSeries.dataItems.append(item)
            items.append(item)
        desc = "Model components: %s" % ", ".join([i.title for i in items])
        data = PlotData(dataSeries=[containerSeries, pumpSeries],
                        description=desc)

        self.plotWindow.plot(data)
        self.plotWindow.show()

    def runModel(self):
        """Run the actual model."""
        chain = []
        for i in range(0, self.modelLayout.count()):
            row = self.modelLayout.itemAt(i).widget().layout()
            typewidget = row.itemAt(1).widget()
            componentType = typewidget.itemData(typewidget.currentIndex())
            if componentType is None:
                self.showErrorMessage("The component in row %i doesn't have " +
                                      "a type yet. Please select one." %
                                      (i + 1))
                return
            self.log.debug('Component %i is of type %s' %
                           (i,  componentType.__name__))

            values = {}
            params = componentType.getParameters()
            if 'previous' in params.keys():
                if i == 0:
                    self.showErrorMessage("The %s component at row %i can't be"
                                          "the first component. It needs a "
                                          "source of water. Try adding a pump."
                                          % (componentType.__name__,  (i + 1)))
                    return
                else:
                    values['previous'] = chain[i - 1]

            for j in range(2, row.count()):
                w = row.itemAt(j).widget()
                name = w.objectName()
                self.log.debug('Checking widget %s' % name)
                if name[:2] == 'w_':
                    name = name[2:]
                    if hasattr(w, 'value'):
                        v = w.value()
                    elif hasattr(w,  'text'):
                        v = w.text()
                    else:
                        self.log.error("Unable to fetch value for widget %s %s"
                                       % (name,  w))
                        v = None
                    values[name] = v
            self.log.debug('Got parameter values %s' % values)
            component = componentType(**values)
            chain.append(component)
        if len(chain) == 0:
                self.showErrorMessage("No model components have been defined "
                                      "yet. Please add rows.")
                return
        self.log.debug('Got chain %s' % chain)
        timestep = self.inp_timestep.value()
        runtime = self.inp_runtime.value()
        self.log.debug('Got timestep %i and runtime %i' % (timestep, runtime))
        results = run_model(chain,  timestep,  runtime,  self.log)
        self.plotResults(results, chain)

    def addRow(self):
        """Add a row to the list of components."""
        count = self.modelLayout.count()  # The number of rows already there

        """The initial widgets (dropbox for component type and checkbox
        to select the row"""
        checkbox = QtWidgets.QCheckBox()
        typebox = QtWidgets.QComboBox()
        typebox.addItem("-- choose a component--", None)
        typebox.currentIndexChanged.connect(self.updateModelComponent)
        for i, t in enumerate(model.get_components()):
            typebox.addItem(t.__name__, t)

        #  The frame widget and layout holding this row.
        frame = QtWidgets.QFrame(self.modelFrame)
        frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        frame.setFrameShadow(QtWidgets.QFrame.Raised)
        frame.setObjectName("componentFrame%i" % count)
        modelComponent = QtWidgets.QHBoxLayout(frame)
        modelComponent.setAlignment(QtCore.Qt.AlignLeft)
        modelComponent.setObjectName("modelComponent%i" % count)

        #  Add the component widgets to the frame
        modelComponent.addWidget(checkbox)
        modelComponent.addWidget(typebox)
        #  Add the frame to the application
        self.modelLayout.addWidget(frame)

    def updateModelComponent(self):
        """
        Action to perform when the component type dropbox changes.

        It removes all parameter widgets for the respective row and adds the
        parameter widgets for the new component type.

        """
        sender = self.sender()
        layout = sender.parent().layout()
        index = layout.indexOf(sender)
        rem_items = []
        for i in range(index + 1,  layout.count()):
            """First loop over the widgets before removing them as the index
            will change once removed."""
            item = layout.itemAt(i)
            if item is None:
                continue
            self.log.debug('item at at %s: %s' % (i,  item.widget()))
            rem_items.append(item)
        for i in rem_items:
            # Now remove the items.
            layout.removeItem(i)
            widget = i.widget()
            widget.deleteLater()

        #  get the component type
        component = sender.itemData(sender.currentIndex())
        self.log.debug('Changed model component to %s' % component)
        #  get the model parameters for the type
        params = component.getParameters()
        for k, v in params.items():
            #  add all parameters to the layout
            if k == 'previous':
                continue
            else:
                for w in get_parameter_widget(k, v):
                    layout.addWidget(w)
                    self.log.debug('adding widget %s %s' % (k, w))

    def deleteSelectedRows(self):
        """
        Action to perform when the remove row button is clicked.

        All component rows for which the checkbox was clicked are removed.

        """
        layout = self.modelLayout
        self.log.debug('Number of component rows: %s' % (layout.count()))
        remove_rows = []
        for r in range(0, layout.count()):
            row_item = layout.itemAt(r)
            if row_item is None:
                self.log.warn('Widget at row %s is of type None' % r)
                continue
            row = row_item.widget()
            self.log.debug('Item at row %s: %s' % (r,  row))
            componentLayout = row.layout()
            item = componentLayout.itemAt(0)
            if item is None:
                self.log.debug('Widget at row %s and position 0 is None' % r)
                continue
            widget = item.widget()
            self.log.debug('Widget at row %s and position 0: %s' %
                           (r,  widget))
            if isinstance(widget,  QtWidgets.QCheckBox) and widget.isChecked():
                self.log.debug('Removing widgets for row %s' % r)
                remove_rows.append(row_item)
                items = [componentLayout.itemAt(c)
                         for c in range(0, componentLayout.count())]
                for c, item in enumerate(items):
                    if item is None:
                        continue
                    self.log.debug('item at at %s %s: %s' %
                                   (r,  c,  item.widget()))
                    componentLayout.removeItem(item)
                    widget = item.widget()
                    widget.deleteLater()
            else:
                self.log.debug('Leaving row %s alone' % r)

        for row in remove_rows:
            """Remove the actual rows (Frames that used to contain the widgets
            for the component)"""
            self.log.debug('Removing row %s' % row.widget())
            layout.removeItem(row)
            row.widget().deleteLater()
        self.log.debug('Rows remaning: %i' % layout.count())


def main():
    """Run the actual application."""
    log = logging.getLogger("aquaponics.interface")
    app = QtWidgets.QApplication(sys.argv)
    form = AquaponicsModeler(log)
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()

__all__ = ['AquaponicsModeler', 'run_model', 'get_parameter_widget', 'main']
