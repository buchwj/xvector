# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'NewMapDialog.ui'
#
# Created: Thu Apr  7 18:41:47 2011
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

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
        self.widget = QtGui.QWidget(self.groupBox)
        self.widget.setGeometry(QtCore.QRect(0, 30, 231, 95))
        self.widget.setObjectName("widget")
        self.formLayout = QtGui.QFormLayout(self.widget)
        self.formLayout.setObjectName("formLayout")
        self.lblMapName = QtGui.QLabel(self.widget)
        self.lblMapName.setObjectName("lblMapName")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.lblMapName)
        self.txtMapName = QtGui.QLineEdit(self.widget)
        self.txtMapName.setWhatsThis("")
        self.txtMapName.setObjectName("txtMapName")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.txtMapName)
        self.lblWidth = QtGui.QLabel(self.widget)
        self.lblWidth.setObjectName("lblWidth")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.lblWidth)
        self.spnWidth = QtGui.QSpinBox(self.widget)
        self.spnWidth.setWhatsThis("")
        self.spnWidth.setMinimum(1)
        self.spnWidth.setMaximum(99999)
        self.spnWidth.setProperty("value", 16)
        self.spnWidth.setObjectName("spnWidth")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.spnWidth)
        self.lblHeight = QtGui.QLabel(self.widget)
        self.lblHeight.setObjectName("lblHeight")
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.lblHeight)
        self.spnHeight = QtGui.QSpinBox(self.widget)
        self.spnHeight.setWhatsThis("")
        self.spnHeight.setMinimum(1)
        self.spnHeight.setMaximum(99999)
        self.spnHeight.setProperty("value", 16)
        self.spnHeight.setObjectName("spnHeight")
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.spnHeight)

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

