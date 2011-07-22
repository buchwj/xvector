# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'NewMapDialog.ui'
#
# Created: Fri Jul 22 16:39:05 2011
#      by: PyQt4 UI code generator 4.8.3
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
        NewMapDialog.resize(274, 242)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(NewMapDialog.sizePolicy().hasHeightForWidth())
        NewMapDialog.setSizePolicy(sizePolicy)
        self.verticalLayout = QtGui.QVBoxLayout(NewMapDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(NewMapDialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.layoutWidget = QtGui.QWidget(self.groupBox)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 30, 231, 143))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.formLayout = QtGui.QFormLayout(self.layoutWidget)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.formLayout.setFormAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.formLayout.setMargin(0)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.lblMapName = QtGui.QLabel(self.layoutWidget)
        self.lblMapName.setObjectName(_fromUtf8("lblMapName"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.lblMapName)
        self.txtMapName = QtGui.QLineEdit(self.layoutWidget)
        self.txtMapName.setWhatsThis(_fromUtf8(""))
        self.txtMapName.setObjectName(_fromUtf8("txtMapName"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.txtMapName)
        self.lblWidth = QtGui.QLabel(self.layoutWidget)
        self.lblWidth.setObjectName(_fromUtf8("lblWidth"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.lblWidth)
        self.spnWidth = QtGui.QSpinBox(self.layoutWidget)
        self.spnWidth.setWhatsThis(_fromUtf8(""))
        self.spnWidth.setMinimum(1)
        self.spnWidth.setMaximum(99999)
        self.spnWidth.setProperty(_fromUtf8("value"), 16)
        self.spnWidth.setObjectName(_fromUtf8("spnWidth"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.spnWidth)
        self.lblHeight = QtGui.QLabel(self.layoutWidget)
        self.lblHeight.setObjectName(_fromUtf8("lblHeight"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.lblHeight)
        self.spnHeight = QtGui.QSpinBox(self.layoutWidget)
        self.spnHeight.setWhatsThis(_fromUtf8(""))
        self.spnHeight.setMinimum(1)
        self.spnHeight.setMaximum(99999)
        self.spnHeight.setProperty(_fromUtf8("value"), 16)
        self.spnHeight.setObjectName(_fromUtf8("spnHeight"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.spnHeight)
        self.lblDepth = QtGui.QLabel(self.layoutWidget)
        self.lblDepth.setObjectName(_fromUtf8("lblDepth"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.lblDepth)
        self.spnDepth = QtGui.QSpinBox(self.layoutWidget)
        self.spnDepth.setMinimum(5)
        self.spnDepth.setMaximum(99999999)
        self.spnDepth.setObjectName(_fromUtf8("spnDepth"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.spnDepth)
        self.playerDepthLabel = QtGui.QLabel(self.layoutWidget)
        self.playerDepthLabel.setObjectName(_fromUtf8("playerDepthLabel"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.playerDepthLabel)
        self.playerDepthSpin = QtGui.QSpinBox(self.layoutWidget)
        self.playerDepthSpin.setMaximum(4)
        self.playerDepthSpin.setProperty(_fromUtf8("value"), 2)
        self.playerDepthSpin.setObjectName(_fromUtf8("playerDepthSpin"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.playerDepthSpin)
        self.verticalLayout.addWidget(self.groupBox)
        self.buttonBox = QtGui.QDialogButtonBox(NewMapDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

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
        self.lblDepth.setText(QtGui.QApplication.translate("NewMapDialog", "Depth:", None, QtGui.QApplication.UnicodeUTF8))
        self.playerDepthLabel.setWhatsThis(QtGui.QApplication.translate("NewMapDialog", "Depth at which objects (such as players, items, and NPCS) are drawn.  Objects will obscure tiles at lower depths than this, and tiles at higher depths will obscure the objects.", None, QtGui.QApplication.UnicodeUTF8))
        self.playerDepthLabel.setText(QtGui.QApplication.translate("NewMapDialog", "Player Depth:", None, QtGui.QApplication.UnicodeUTF8))

