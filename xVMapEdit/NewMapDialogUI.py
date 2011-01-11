# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'NewMapDialog.ui'
#
# Created: Mon Jan 10 19:03:49 2011
#      by: PyQt4 UI code generator 4.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_NewMapDialog(object):
    def setupUi(self, NewMapDialog):
        NewMapDialog.setObjectName(_fromUtf8("NewMapDialog"))
        NewMapDialog.resize(257, 192)
        self.buttonBox = QtGui.QDialogButtonBox(NewMapDialog)
        self.buttonBox.setGeometry(QtCore.QRect(30, 150, 211, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.groupBox = QtGui.QGroupBox(NewMapDialog)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 231, 131))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.lblMapName = QtGui.QLabel(self.groupBox)
        self.lblMapName.setGeometry(QtCore.QRect(20, 30, 61, 16))
        self.lblMapName.setObjectName(_fromUtf8("lblMapName"))
        self.txtMapName = QtGui.QLineEdit(self.groupBox)
        self.txtMapName.setGeometry(QtCore.QRect(80, 26, 131, 20))
        self.txtMapName.setWhatsThis(_fromUtf8(""))
        self.txtMapName.setObjectName(_fromUtf8("txtMapName"))
        self.lblWidth = QtGui.QLabel(self.groupBox)
        self.lblWidth.setGeometry(QtCore.QRect(20, 60, 46, 13))
        self.lblWidth.setObjectName(_fromUtf8("lblWidth"))
        self.spnWidth = QtGui.QSpinBox(self.groupBox)
        self.spnWidth.setGeometry(QtCore.QRect(80, 52, 61, 22))
        self.spnWidth.setWhatsThis(_fromUtf8(""))
        self.spnWidth.setMinimum(1)
        self.spnWidth.setMaximum(99999)
        self.spnWidth.setProperty(_fromUtf8("value"), 16)
        self.spnWidth.setObjectName(_fromUtf8("spnWidth"))
        self.spnHeight = QtGui.QSpinBox(self.groupBox)
        self.spnHeight.setGeometry(QtCore.QRect(80, 82, 61, 22))
        self.spnHeight.setWhatsThis(_fromUtf8(""))
        self.spnHeight.setMinimum(1)
        self.spnHeight.setMaximum(99999)
        self.spnHeight.setProperty(_fromUtf8("value"), 16)
        self.spnHeight.setObjectName(_fromUtf8("spnHeight"))
        self.lblHeight = QtGui.QLabel(self.groupBox)
        self.lblHeight.setGeometry(QtCore.QRect(20, 89, 46, 13))
        self.lblHeight.setObjectName(_fromUtf8("lblHeight"))

        self.retranslateUi(NewMapDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), NewMapDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), NewMapDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(NewMapDialog)

    def retranslateUi(self, NewMapDialog):
        NewMapDialog.setWindowTitle(QtGui.QApplication.translate("NewMapDialog", "New Map", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("NewMapDialog", "Options", None, QtGui.QApplication.UnicodeUTF8))
        self.lblMapName.setWhatsThis(QtGui.QApplication.translate("NewMapDialog", "This is the name of the map which will be visible to players while they are on it.", None, QtGui.QApplication.UnicodeUTF8))
        self.lblMapName.setText(QtGui.QApplication.translate("NewMapDialog", "Map Name:", None, QtGui.QApplication.UnicodeUTF8))
        self.lblWidth.setWhatsThis(QtGui.QApplication.translate("NewMapDialog", "This is the width of the map, in tiles.", None, QtGui.QApplication.UnicodeUTF8))
        self.lblWidth.setText(QtGui.QApplication.translate("NewMapDialog", "Width:", None, QtGui.QApplication.UnicodeUTF8))
        self.lblHeight.setWhatsThis(QtGui.QApplication.translate("NewMapDialog", "This is the height of the map, in tiles.", None, QtGui.QApplication.UnicodeUTF8))
        self.lblHeight.setText(QtGui.QApplication.translate("NewMapDialog", "Height:", None, QtGui.QApplication.UnicodeUTF8))

