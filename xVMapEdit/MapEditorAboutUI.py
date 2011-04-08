# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MapEditorAbout.ui'
#
# Created: Fri Apr  8 16:40:08 2011
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MapEditorAboutDlg(object):
    def setupUi(self, MapEditorAboutDlg):
        MapEditorAboutDlg.setObjectName("MapEditorAboutDlg")
        MapEditorAboutDlg.setWindowModality(QtCore.Qt.ApplicationModal)
        MapEditorAboutDlg.resize(332, 219)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MapEditorAboutDlg.sizePolicy().hasHeightForWidth())
        MapEditorAboutDlg.setSizePolicy(sizePolicy)
        MapEditorAboutDlg.setMinimumSize(QtCore.QSize(0, 0))
        MapEditorAboutDlg.setMaximumSize(QtCore.QSize(100000, 100000))
        MapEditorAboutDlg.setModal(True)
        self.widget = QtGui.QWidget(MapEditorAboutDlg)
        self.widget.setGeometry(QtCore.QRect(10, 10, 313, 198))
        self.widget.setObjectName("widget")
        self.gridLayout_2 = QtGui.QGridLayout(self.widget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label = QtGui.QLabel(self.widget)
        self.label.setTextFormat(QtCore.Qt.AutoText)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(self.widget)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 2)
        self.label_3 = QtGui.QLabel(self.widget)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 2, 0, 1, 2)
        self.btnAboutQt = QtGui.QPushButton(self.widget)
        self.btnAboutQt.setObjectName("btnAboutQt")
        self.gridLayout_2.addWidget(self.btnAboutQt, 3, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self.widget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_2.addWidget(self.buttonBox, 4, 1, 1, 1)

        self.retranslateUi(MapEditorAboutDlg)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), MapEditorAboutDlg.accept)
        QtCore.QMetaObject.connectSlotsByName(MapEditorAboutDlg)

    def retranslateUi(self, MapEditorAboutDlg):
        MapEditorAboutDlg.setWindowTitle(QtGui.QApplication.translate("MapEditorAboutDlg", "About", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MapEditorAboutDlg", "<b><font size=4>xVector MMORPG Engine</font>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("MapEditorAboutDlg", "<font size=7><b><i>Map Editor</i></b></font>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("MapEditorAboutDlg", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Copyright © 2011 James Buchwald<br />Licensed under the GNU GPL, v2 or Later</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAboutQt.setText(QtGui.QApplication.translate("MapEditorAboutDlg", "&About Qt...", None, QtGui.QApplication.UnicodeUTF8))

import MapEditor_rc
