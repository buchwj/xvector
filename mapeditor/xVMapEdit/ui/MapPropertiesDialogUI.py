# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MapPropertiesDialog.ui'
#
# Created: Sat Jul 23 23:13:11 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MapPropertiesDialog(object):
    def setupUi(self, MapPropertiesDialog):
        MapPropertiesDialog.setObjectName(_fromUtf8("MapPropertiesDialog"))
        MapPropertiesDialog.resize(288, 260)
        MapPropertiesDialog.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(MapPropertiesDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tabWidget = QtGui.QTabWidget(MapPropertiesDialog)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.GeneralTab = QtGui.QWidget()
        self.GeneralTab.setObjectName(_fromUtf8("GeneralTab"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.GeneralTab)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.mapNameLabel = QtGui.QLabel(self.GeneralTab)
        self.mapNameLabel.setObjectName(_fromUtf8("mapNameLabel"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.mapNameLabel)
        self.MapNameEdit = QtGui.QLineEdit(self.GeneralTab)
        self.MapNameEdit.setObjectName(_fromUtf8("MapNameEdit"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.MapNameEdit)
        self.backgroundImageLabel = QtGui.QLabel(self.GeneralTab)
        self.backgroundImageLabel.setObjectName(_fromUtf8("backgroundImageLabel"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.backgroundImageLabel)
        self.BackgroundImageEdit = QtGui.QLineEdit(self.GeneralTab)
        self.BackgroundImageEdit.setObjectName(_fromUtf8("BackgroundImageEdit"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.BackgroundImageEdit)
        self.northBorderLabel = QtGui.QLabel(self.GeneralTab)
        self.northBorderLabel.setObjectName(_fromUtf8("northBorderLabel"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.northBorderLabel)
        self.NorthBorderEdit = QtGui.QLineEdit(self.GeneralTab)
        self.NorthBorderEdit.setObjectName(_fromUtf8("NorthBorderEdit"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.NorthBorderEdit)
        self.eastBorderLabel = QtGui.QLabel(self.GeneralTab)
        self.eastBorderLabel.setObjectName(_fromUtf8("eastBorderLabel"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.eastBorderLabel)
        self.EastBorderEdit = QtGui.QLineEdit(self.GeneralTab)
        self.EastBorderEdit.setObjectName(_fromUtf8("EastBorderEdit"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.EastBorderEdit)
        self.southBorderLabel = QtGui.QLabel(self.GeneralTab)
        self.southBorderLabel.setObjectName(_fromUtf8("southBorderLabel"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.southBorderLabel)
        self.SouthBorderEdit = QtGui.QLineEdit(self.GeneralTab)
        self.SouthBorderEdit.setObjectName(_fromUtf8("SouthBorderEdit"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.SouthBorderEdit)
        self.westBorderLabel = QtGui.QLabel(self.GeneralTab)
        self.westBorderLabel.setObjectName(_fromUtf8("westBorderLabel"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.LabelRole, self.westBorderLabel)
        self.WestBorderEdit = QtGui.QLineEdit(self.GeneralTab)
        self.WestBorderEdit.setObjectName(_fromUtf8("WestBorderEdit"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.FieldRole, self.WestBorderEdit)
        self.verticalLayout_2.addLayout(self.formLayout)
        self.tabWidget.addTab(self.GeneralTab, _fromUtf8(""))
        self.DimensionsTab = QtGui.QWidget()
        self.DimensionsTab.setObjectName(_fromUtf8("DimensionsTab"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.DimensionsTab)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.formLayout_2 = QtGui.QFormLayout()
        self.formLayout_2.setLabelAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
        self.widthLabel = QtGui.QLabel(self.DimensionsTab)
        self.widthLabel.setObjectName(_fromUtf8("widthLabel"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.widthLabel)
        self.WidthSpin = QtGui.QSpinBox(self.DimensionsTab)
        self.WidthSpin.setMinimum(1)
        self.WidthSpin.setMaximum(2000000)
        self.WidthSpin.setObjectName(_fromUtf8("WidthSpin"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.FieldRole, self.WidthSpin)
        self.heightLabel = QtGui.QLabel(self.DimensionsTab)
        self.heightLabel.setObjectName(_fromUtf8("heightLabel"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.LabelRole, self.heightLabel)
        self.HeightSpin = QtGui.QSpinBox(self.DimensionsTab)
        self.HeightSpin.setMinimum(1)
        self.HeightSpin.setMaximum(2000000)
        self.HeightSpin.setSingleStep(1)
        self.HeightSpin.setObjectName(_fromUtf8("HeightSpin"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.FieldRole, self.HeightSpin)
        self.depthLabel = QtGui.QLabel(self.DimensionsTab)
        self.depthLabel.setObjectName(_fromUtf8("depthLabel"))
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.LabelRole, self.depthLabel)
        self.DepthSpin = QtGui.QSpinBox(self.DimensionsTab)
        self.DepthSpin.setMinimum(2)
        self.DepthSpin.setMaximum(2000000)
        self.DepthSpin.setObjectName(_fromUtf8("DepthSpin"))
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.FieldRole, self.DepthSpin)
        self.playerDepthLabel = QtGui.QLabel(self.DimensionsTab)
        self.playerDepthLabel.setObjectName(_fromUtf8("playerDepthLabel"))
        self.formLayout_2.setWidget(3, QtGui.QFormLayout.LabelRole, self.playerDepthLabel)
        self.PlayerDepthSpin = QtGui.QSpinBox(self.DimensionsTab)
        self.PlayerDepthSpin.setMinimum(2)
        self.PlayerDepthSpin.setMaximum(2000000)
        self.PlayerDepthSpin.setObjectName(_fromUtf8("PlayerDepthSpin"))
        self.formLayout_2.setWidget(3, QtGui.QFormLayout.FieldRole, self.PlayerDepthSpin)
        self.verticalLayout_3.addLayout(self.formLayout_2)
        self.tabWidget.addTab(self.DimensionsTab, _fromUtf8(""))
        self.verticalLayout.addWidget(self.tabWidget)
        self.buttonBox = QtGui.QDialogButtonBox(MapPropertiesDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(MapPropertiesDialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), MapPropertiesDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), MapPropertiesDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(MapPropertiesDialog)

    def retranslateUi(self, MapPropertiesDialog):
        MapPropertiesDialog.setWindowTitle(QtGui.QApplication.translate("MapPropertiesDialog", "Map Properties", None, QtGui.QApplication.UnicodeUTF8))
        self.mapNameLabel.setWhatsThis(QtGui.QApplication.translate("MapPropertiesDialog", "The name of this map.  This may be displayed at the top of the client and should be human-readable.", None, QtGui.QApplication.UnicodeUTF8))
        self.mapNameLabel.setText(QtGui.QApplication.translate("MapPropertiesDialog", "Map Name:", None, QtGui.QApplication.UnicodeUTF8))
        self.backgroundImageLabel.setWhatsThis(QtGui.QApplication.translate("MapPropertiesDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans Serif\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">(Optional) The name of an image file to show behind the map.  This file must be in the <span style=\" font-style:italic;\">Backgrounds</span> folder of your server\'s resources.  Leave blank to use the default black background.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.backgroundImageLabel.setText(QtGui.QApplication.translate("MapPropertiesDialog", "Background Image:", None, QtGui.QApplication.UnicodeUTF8))
        self.northBorderLabel.setWhatsThis(QtGui.QApplication.translate("MapPropertiesDialog", "(Optional) The filename of the map which lies along the north border of this map.  The specified map must have the same width as this map.  Leave blank to use none.", None, QtGui.QApplication.UnicodeUTF8))
        self.northBorderLabel.setText(QtGui.QApplication.translate("MapPropertiesDialog", "North Border:", None, QtGui.QApplication.UnicodeUTF8))
        self.eastBorderLabel.setWhatsThis(QtGui.QApplication.translate("MapPropertiesDialog", "(Optional) The filename of the map which lies along the east border of this map.  The specified map must have the same height as this map.  Leave blank to use none.", None, QtGui.QApplication.UnicodeUTF8))
        self.eastBorderLabel.setText(QtGui.QApplication.translate("MapPropertiesDialog", "East Border", None, QtGui.QApplication.UnicodeUTF8))
        self.southBorderLabel.setWhatsThis(QtGui.QApplication.translate("MapPropertiesDialog", "(Optional) The filename of the map which lies along the south border of this map.  The specified map must have the same width as this map.  Leave blank to use none.", None, QtGui.QApplication.UnicodeUTF8))
        self.southBorderLabel.setText(QtGui.QApplication.translate("MapPropertiesDialog", "South Border:", None, QtGui.QApplication.UnicodeUTF8))
        self.westBorderLabel.setWhatsThis(QtGui.QApplication.translate("MapPropertiesDialog", "(Optional) The filename of the map which lies along the west border of this map.  The specified map must have the same height as this map.  Leave blank to use none.", None, QtGui.QApplication.UnicodeUTF8))
        self.westBorderLabel.setText(QtGui.QApplication.translate("MapPropertiesDialog", "West Border:", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.GeneralTab), QtGui.QApplication.translate("MapPropertiesDialog", "&General", None, QtGui.QApplication.UnicodeUTF8))
        self.widthLabel.setWhatsThis(QtGui.QApplication.translate("MapPropertiesDialog", "The width of this map, in tiles.  Must be greater than zero.", None, QtGui.QApplication.UnicodeUTF8))
        self.widthLabel.setText(QtGui.QApplication.translate("MapPropertiesDialog", "Width:", None, QtGui.QApplication.UnicodeUTF8))
        self.heightLabel.setWhatsThis(QtGui.QApplication.translate("MapPropertiesDialog", "The height of this map, in tiles.  Must be greater than zero.", None, QtGui.QApplication.UnicodeUTF8))
        self.heightLabel.setText(QtGui.QApplication.translate("MapPropertiesDialog", "Height:", None, QtGui.QApplication.UnicodeUTF8))
        self.depthLabel.setWhatsThis(QtGui.QApplication.translate("MapPropertiesDialog", "The number of layers which this map consists of.  Must be at least 2.", None, QtGui.QApplication.UnicodeUTF8))
        self.depthLabel.setText(QtGui.QApplication.translate("MapPropertiesDialog", "Depth:", None, QtGui.QApplication.UnicodeUTF8))
        self.playerDepthLabel.setWhatsThis(QtGui.QApplication.translate("MapPropertiesDialog", "The layer at which objects (such as players, items, and NPCs) are shown.  Layers are numbered starting from 0.  Layers below the player depth will be obscured by any objects; likewise, the objects will be obscured by the layers above this.  Must be at least 2.", None, QtGui.QApplication.UnicodeUTF8))
        self.playerDepthLabel.setText(QtGui.QApplication.translate("MapPropertiesDialog", "Player Depth:", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.DimensionsTab), QtGui.QApplication.translate("MapPropertiesDialog", "&Dimensions", None, QtGui.QApplication.UnicodeUTF8))

