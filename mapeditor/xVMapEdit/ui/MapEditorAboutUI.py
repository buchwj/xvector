# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MapEditorAbout.ui'
#
# Created: Sun Jun  5 15:43:30 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MapEditorAboutDlg(object):
    def setupUi(self, MapEditorAboutDlg):
        MapEditorAboutDlg.setObjectName(_fromUtf8("MapEditorAboutDlg"))
        MapEditorAboutDlg.setWindowModality(QtCore.Qt.ApplicationModal)
        MapEditorAboutDlg.resize(371, 217)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MapEditorAboutDlg.sizePolicy().hasHeightForWidth())
        MapEditorAboutDlg.setSizePolicy(sizePolicy)
        MapEditorAboutDlg.setMinimumSize(QtCore.QSize(0, 0))
        MapEditorAboutDlg.setMaximumSize(QtCore.QSize(100000, 100000))
        MapEditorAboutDlg.setModal(True)
        self.layoutWidget = QtGui.QWidget(MapEditorAboutDlg)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 351, 198))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.gridLayout_2 = QtGui.QGridLayout(self.layoutWidget)
        self.gridLayout_2.setMargin(0)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label = QtGui.QLabel(self.layoutWidget)
        self.label.setTextFormat(QtCore.Qt.AutoText)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(self.layoutWidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 2)
        self.label_3 = QtGui.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Abyssinica SIL"))
        font.setPointSize(6)
        self.label_3.setFont(font)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 2, 0, 1, 2)
        self.btnAboutQt = QtGui.QPushButton(self.layoutWidget)
        self.btnAboutQt.setObjectName(_fromUtf8("btnAboutQt"))
        self.gridLayout_2.addWidget(self.btnAboutQt, 3, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self.layoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 4, 1, 1, 1)

        self.retranslateUi(MapEditorAboutDlg)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), MapEditorAboutDlg.accept)
        QtCore.QMetaObject.connectSlotsByName(MapEditorAboutDlg)

    def retranslateUi(self, MapEditorAboutDlg):
        MapEditorAboutDlg.setWindowTitle(QtGui.QApplication.translate("MapEditorAboutDlg", "About", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MapEditorAboutDlg", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">xVector MMORPG Engine</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("MapEditorAboutDlg", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:18pt; font-weight:600; font-style:italic;\">Map Editor</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("MapEditorAboutDlg", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\';\">Copyright © 2011 James Buchwald<br />Licensed under the GNU GPL, v2 or Later</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAboutQt.setText(QtGui.QApplication.translate("MapEditorAboutDlg", "&About Qt...", None, QtGui.QApplication.UnicodeUTF8))

import MapEditor_rc
