# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'NewMapDialog.ui'
#
# Created: Fri Jan 07 14:45:14 2011
#      by: PySide uic UI code generator
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_NewMapDialog(object):
    def setupUi(self, NewMapDialog):
        NewMapDialog.setObjectName("NewMapDialog")
        NewMapDialog.resize(257, 192)
        self.buttonBox = QtGui.QDialogButtonBox(NewMapDialog)
        self.buttonBox.setGeometry(QtCore.QRect(30, 150, 211, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.groupBox = QtGui.QGroupBox(NewMapDialog)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 231, 131))
        self.groupBox.setObjectName("groupBox")
        self.lblMapName = QtGui.QLabel(self.groupBox)
        self.lblMapName.setGeometry(QtCore.QRect(20, 30, 61, 16))
        self.lblMapName.setObjectName("lblMapName")
        self.txtMapName = QtGui.QLineEdit(self.groupBox)
        self.txtMapName.setGeometry(QtCore.QRect(80, 26, 131, 20))
        self.txtMapName.setObjectName("txtMapName")
        self.lblWidth = QtGui.QLabel(self.groupBox)
        self.lblWidth.setGeometry(QtCore.QRect(20, 60, 46, 13))
        self.lblWidth.setObjectName("lblWidth")
        self.spnWidth = QtGui.QSpinBox(self.groupBox)
        self.spnWidth.setGeometry(QtCore.QRect(80, 52, 61, 22))
        self.spnWidth.setMinimum(1)
        self.spnWidth.setMaximum(99999)
        self.spnWidth.setProperty("value", 16)
        self.spnWidth.setObjectName("spnWidth")
        self.spnHeight = QtGui.QSpinBox(self.groupBox)
        self.spnHeight.setGeometry(QtCore.QRect(80, 82, 61, 22))
        self.spnHeight.setMinimum(1)
        self.spnHeight.setMaximum(99999)
        self.spnHeight.setProperty("value", 16)
        self.spnHeight.setObjectName("spnHeight")
        self.lblHeight = QtGui.QLabel(self.groupBox)
        self.lblHeight.setGeometry(QtCore.QRect(20, 89, 46, 13))
        self.lblHeight.setObjectName("lblHeight")

        self.retranslateUi(NewMapDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), NewMapDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), NewMapDialog.reject)
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

