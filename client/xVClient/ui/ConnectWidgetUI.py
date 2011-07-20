# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ConnectWidget.ui'
#
# Created: Wed Jul 13 22:47:35 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ConnectWidget(object):
    def setupUi(self, ConnectWidget):
        ConnectWidget.setObjectName(_fromUtf8("ConnectWidget"))
        ConnectWidget.resize(226, 138)
        self.verticalLayout = QtGui.QVBoxLayout(ConnectWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.HostLabel = QtGui.QLabel(ConnectWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.HostLabel.setFont(font)
        self.HostLabel.setObjectName(_fromUtf8("HostLabel"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.HostLabel)
        self.lineEdit = QtGui.QLineEdit(ConnectWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lineEdit.setFont(font)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.lineEdit)
        self.portLabel = QtGui.QLabel(ConnectWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.portLabel.setFont(font)
        self.portLabel.setObjectName(_fromUtf8("portLabel"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.portLabel)
        self.portLineEdit = QtGui.QLineEdit(ConnectWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.portLineEdit.setFont(font)
        self.portLineEdit.setObjectName(_fromUtf8("portLineEdit"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.portLineEdit)
        spacerItem = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.formLayout.setItem(2, QtGui.QFormLayout.LabelRole, spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(ConnectWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.buttonBox.setFont(font)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.SpanningRole, self.buttonBox)
        self.verticalLayout.addLayout(self.formLayout)

        self.retranslateUi(ConnectWidget)
        QtCore.QMetaObject.connectSlotsByName(ConnectWidget)

    def retranslateUi(self, ConnectWidget):
        ConnectWidget.setWindowTitle(QtGui.QApplication.translate("ConnectWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.HostLabel.setText(QtGui.QApplication.translate("ConnectWidget", "Host:", None, QtGui.QApplication.UnicodeUTF8))
        self.portLabel.setText(QtGui.QApplication.translate("ConnectWidget", "Port:", None, QtGui.QApplication.UnicodeUTF8))

