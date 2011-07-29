# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TitleWidget.ui'
#
# Created: Mon Jul 25 18:40:11 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_TitleWidget(object):
    def setupUi(self, TitleWidget):
        TitleWidget.setObjectName(_fromUtf8("TitleWidget"))
        TitleWidget.resize(250, 300)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(TitleWidget.sizePolicy().hasHeightForWidth())
        TitleWidget.setSizePolicy(sizePolicy)
        self.verticalLayout = QtGui.QVBoxLayout(TitleWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.btnPublic = QtGui.QPushButton(TitleWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnPublic.sizePolicy().hasHeightForWidth())
        self.btnPublic.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.btnPublic.setFont(font)
        self.btnPublic.setFlat(True)
        self.btnPublic.setObjectName(_fromUtf8("btnPublic"))
        self.verticalLayout.addWidget(self.btnPublic)
        self.btnPrivate = QtGui.QPushButton(TitleWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnPrivate.sizePolicy().hasHeightForWidth())
        self.btnPrivate.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.btnPrivate.setFont(font)
        self.btnPrivate.setFlat(True)
        self.btnPrivate.setObjectName(_fromUtf8("btnPrivate"))
        self.verticalLayout.addWidget(self.btnPrivate)
        self.btnSettings = QtGui.QPushButton(TitleWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnSettings.sizePolicy().hasHeightForWidth())
        self.btnSettings.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.btnSettings.setFont(font)
        self.btnSettings.setFlat(True)
        self.btnSettings.setObjectName(_fromUtf8("btnSettings"))
        self.verticalLayout.addWidget(self.btnSettings)
        self.btnExit = QtGui.QPushButton(TitleWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnExit.sizePolicy().hasHeightForWidth())
        self.btnExit.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.btnExit.setFont(font)
        self.btnExit.setFlat(True)
        self.btnExit.setObjectName(_fromUtf8("btnExit"))
        self.verticalLayout.addWidget(self.btnExit)

        self.retranslateUi(TitleWidget)
        QtCore.QMetaObject.connectSlotsByName(TitleWidget)

    def retranslateUi(self, TitleWidget):
        TitleWidget.setWindowTitle(QtGui.QApplication.translate("TitleWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.btnPublic.setText(QtGui.QApplication.translate("TitleWidget", "Join Public Server", None, QtGui.QApplication.UnicodeUTF8))
        self.btnPrivate.setText(QtGui.QApplication.translate("TitleWidget", "Join Private Server", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSettings.setText(QtGui.QApplication.translate("TitleWidget", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.btnExit.setText(QtGui.QApplication.translate("TitleWidget", "Exit", None, QtGui.QApplication.UnicodeUTF8))

