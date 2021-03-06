# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'interface.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(533, 525)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.grp_run = QtWidgets.QGroupBox(self.centralwidget)
        self.grp_run.setObjectName("grp_run")
        self.gridLayout = QtWidgets.QGridLayout(self.grp_run)
        self.gridLayout.setObjectName("gridLayout")
        self.inp_timestep = QtWidgets.QSpinBox(self.grp_run)
        self.inp_timestep.setMinimum(1)
        self.inp_timestep.setMaximum(3600)
        self.inp_timestep.setProperty("value", 10)
        self.inp_timestep.setObjectName("inp_timestep")
        self.gridLayout.addWidget(self.inp_timestep, 0, 1, 1, 1)
        self.lb_timestep = QtWidgets.QLabel(self.grp_run)
        self.lb_timestep.setObjectName("lb_timestep")
        self.gridLayout.addWidget(self.lb_timestep, 0, 0, 1, 1)
        self.btn_run = QtWidgets.QPushButton(self.grp_run)
        self.btn_run.setObjectName("btn_run")
        self.gridLayout.addWidget(self.btn_run, 2, 1, 1, 1)
        self.inp_runtime = QtWidgets.QSpinBox(self.grp_run)
        self.inp_runtime.setMinimum(1)
        self.inp_runtime.setMaximum(24)
        self.inp_runtime.setObjectName("inp_runtime")
        self.gridLayout.addWidget(self.inp_runtime, 1, 1, 1, 1)
        self.lb_runtime = QtWidgets.QLabel(self.grp_run)
        self.lb_runtime.setObjectName("lb_runtime")
        self.gridLayout.addWidget(self.lb_runtime, 1, 0, 1, 1)
        self.verticalLayout_2.addWidget(self.grp_run)
        self.grp_build = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.grp_build.sizePolicy().hasHeightForWidth())
        self.grp_build.setSizePolicy(sizePolicy)
        self.grp_build.setObjectName("grp_build")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.grp_build)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.bt_add_row = QtWidgets.QPushButton(self.grp_build)
        self.bt_add_row.setObjectName("bt_add_row")
        self.horizontalLayout.addWidget(self.bt_add_row)
        self.bt_del_row = QtWidgets.QPushButton(self.grp_build)
        self.bt_del_row.setObjectName("bt_del_row")
        self.horizontalLayout.addWidget(self.bt_del_row)
        self.gridLayout_2.addLayout(self.horizontalLayout, 1, 0, 1, 1)
        self.modelFrame = QtWidgets.QFrame(self.grp_build)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.modelFrame.sizePolicy().hasHeightForWidth())
        self.modelFrame.setSizePolicy(sizePolicy)
        self.modelFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.modelFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.modelFrame.setObjectName("modelFrame")
        self.modelLayout = QtWidgets.QVBoxLayout(self.modelFrame)
        self.modelLayout.setObjectName("modelLayout")
        self.gridLayout_2.addWidget(self.modelFrame, 2, 0, 1, 1)
        self.verticalLayout_2.addWidget(self.grp_build)
        MainWindow.setCentralWidget(self.centralwidget)
        self.lb_timestep.setBuddy(self.inp_timestep)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Aquaponics Model"))
        self.grp_run.setTitle(_translate("MainWindow", "Run Model"))
        self.lb_timestep.setText(_translate("MainWindow", "Time step (seconds)"))
        self.btn_run.setText(_translate("MainWindow", "Run Model"))
        self.lb_runtime.setText(_translate("MainWindow", "Run time (hours)"))
        self.grp_build.setTitle(_translate("MainWindow", "Build Model"))
        self.bt_add_row.setText(_translate("MainWindow", "Add Row"))
        self.bt_del_row.setText(_translate("MainWindow", "Remove Selected Rows"))

