# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MapEditorAbout.ui'
#
# Created: Mon Jan 10 19:02:28 2011
#      by: PyQt4 UI code generator 4.8.2
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
        MapEditorAboutDlg.resize(269, 234)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MapEditorAboutDlg.sizePolicy().hasHeightForWidth())
        MapEditorAboutDlg.setSizePolicy(sizePolicy)
        MapEditorAboutDlg.setMinimumSize(QtCore.QSize(0, 0))
        MapEditorAboutDlg.setMaximumSize(QtCore.QSize(100000, 100000))
        MapEditorAboutDlg.setModal(True)
        self.buttonBox = QtGui.QDialogButtonBox(MapEditorAboutDlg)
        self.buttonBox.setGeometry(QtCore.QRect(30, 190, 211, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.label = QtGui.QLabel(MapEditorAboutDlg)
        self.label.setGeometry(QtCore.QRect(10, 10, 161, 16))
        self.label.setTextFormat(QtCore.Qt.AutoText)
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(MapEditorAboutDlg)
        self.label_2.setGeometry(QtCore.QRect(64, 32, 151, 41))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(MapEditorAboutDlg)
        self.label_3.setGeometry(QtCore.QRect(34, 80, 201, 31))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.layoutWidget = QtGui.QWidget(MapEditorAboutDlg)
        self.layoutWidget.setGeometry(QtCore.QRect(106, 120, 61, 61))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.gridLayout = QtGui.QGridLayout(self.layoutWidget)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_5 = QtGui.QLabel(self.layoutWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setMinimumSize(QtCore.QSize(24, 24))
        self.label_5.setMaximumSize(QtCore.QSize(24, 24))
        self.label_5.setText(_fromUtf8(""))
        self.label_5.setPixmap(QtGui.QPixmap(_fromUtf8(":/ResourceIcons/res/AnimationsIcon.png")))
        self.label_5.setScaledContents(False)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 0, 1, 1, 1)
        self.label_6 = QtGui.QLabel(self.layoutWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        self.label_6.setMinimumSize(QtCore.QSize(24, 24))
        self.label_6.setMaximumSize(QtCore.QSize(24, 24))
        self.label_6.setText(_fromUtf8(""))
        self.label_6.setPixmap(QtGui.QPixmap(_fromUtf8(":/ResourceIcons/res/ItemsIcon.png")))
        self.label_6.setScaledContents(False)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 1, 0, 1, 1)
        self.label_7 = QtGui.QLabel(self.layoutWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy)
        self.label_7.setMinimumSize(QtCore.QSize(24, 24))
        self.label_7.setMaximumSize(QtCore.QSize(24, 24))
        self.label_7.setText(_fromUtf8(""))
        self.label_7.setPixmap(QtGui.QPixmap(_fromUtf8(":/ResourceIcons/res/NPCsIcon.png")))
        self.label_7.setScaledContents(False)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout.addWidget(self.label_7, 1, 1, 1, 1)
        self.label_4 = QtGui.QLabel(self.layoutWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setMinimumSize(QtCore.QSize(24, 24))
        self.label_4.setMaximumSize(QtCore.QSize(24, 24))
        self.label_4.setText(_fromUtf8(""))
        self.label_4.setPixmap(QtGui.QPixmap(_fromUtf8(":/ResourceIcons/res/TilesIcon.png")))
        self.label_4.setScaledContents(False)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 1)

        self.retranslateUi(MapEditorAboutDlg)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), MapEditorAboutDlg.accept)
        QtCore.QMetaObject.connectSlotsByName(MapEditorAboutDlg)

    def retranslateUi(self, MapEditorAboutDlg):
        MapEditorAboutDlg.setWindowTitle(QtGui.QApplication.translate("MapEditorAboutDlg", "About", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MapEditorAboutDlg", "<b><font size=4>xVector MMORPG Engine</font>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("MapEditorAboutDlg", "<font size=7><b><i>Map Editor</i></b></font>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("MapEditorAboutDlg", "<center>Copyright © 2010 James Buchwald<br />Licensed under the GNU GPL, v2 or Later</center>", None, QtGui.QApplication.UnicodeUTF8))

import MapEditor_rc
