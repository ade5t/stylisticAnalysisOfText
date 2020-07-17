# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'plugin_window.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!

import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore


class Ui_PluginWindow(object):
    def setupUi(self, PluginWindow):
        PluginWindow.setObjectName("PluginWindow")
        PluginWindow.setWindowModality(QtCore.Qt.ApplicationModal)
        PluginWindow.resize(482, 600)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(PluginWindow.sizePolicy().hasHeightForWidth())
        PluginWindow.setSizePolicy(sizePolicy)
        PluginWindow.setMinimumSize(QtCore.QSize(482, 600))
        PluginWindow.setMaximumSize(QtCore.QSize(482, 600))
        self.font = QtGui.QFont("Arial", 10)
        self.font_header = QtGui.QFont("Arial", 10)
        self.font_header.setBold(True)
        self.centralwidget = QtWidgets.QWidget(PluginWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setFont(self.font)
        self.gridLayout.addWidget(self.pushButton, 1, 0, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setFont(self.font)
        self.gridLayout.addWidget(self.pushButton_2, 1, 1, 1, 1)
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setFocusPolicy(QtCore.Qt.NoFocus)
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.tableWidget.verticalHeader().setVisible(False)
        self.gridLayout.addWidget(self.tableWidget, 0, 0, 1, 2)
        PluginWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(PluginWindow)
        QtCore.QMetaObject.connectSlotsByName(PluginWindow)

        self.pushButton_2.clicked.connect(PluginWindow.exit)
        self.pushButton.clicked.connect(PluginWindow.start_plugin_window)

    def retranslateUi(self, PluginWindow):
        _translate = QtCore.QCoreApplication.translate
        PluginWindow.setWindowTitle(_translate("PluginWindow", "Выбор плагинов"))
        self.pushButton.setText(_translate("PluginWindow", "Запуск"))
        self.pushButton_2.setText(_translate("PluginWindow", "Отмена"))
