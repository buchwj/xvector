# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PrivateServerWidget.ui'
#
# Created: Wed Jul 27 19:34:40 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_PrivateServerWidget(object):
    def setupUi(self, PrivateServerWidget):
        PrivateServerWidget.setObjectName(_fromUtf8("PrivateServerWidget"))
        PrivateServerWidget.resize(250, 130)
        self.formLayout = QtGui.QFormLayout(PrivateServerWidget)
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.HostLabel = QtGui.QLabel(PrivateServerWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.HostLabel.setFont(font)
        self.HostLabel.setObjectName(_fromUtf8("HostLabel"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.HostLabel)
        self.HostEdit = QtGui.QLineEdit(PrivateServerWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.HostEdit.setFont(font)
        self.HostEdit.setInputMethodHints(QtCore.Qt.ImhUrlCharactersOnly)
        self.HostEdit.setObjectName(_fromUtf8("HostEdit"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.HostEdit)
        self.PortLabel = QtGui.QLabel(PrivateServerWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.PortLabel.setFont(font)
        self.PortLabel.setObjectName(_fromUtf8("PortLabel"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.PortLabel)
        self.PortEdit = QtGui.QLineEdit(PrivateServerWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.PortEdit.setFont(font)
        self.PortEdit.setInputMethodHints(QtCore.Qt.ImhDigitsOnly)
        self.PortEdit.setObjectName(_fromUtf8("PortEdit"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.PortEdit)
        spacerItem = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.formLayout.setItem(2, QtGui.QFormLayout.LabelRole, spacerItem)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.BackButton = QtGui.QPushButton(PrivateServerWidget)
        self.BackButton.setObjectName(_fromUtf8("BackButton"))
        self.horizontalLayout.addWidget(self.BackButton)
        self.ConnectButton = QtGui.QPushButton(PrivateServerWidget)
        self.ConnectButton.setObjectName(_fromUtf8("ConnectButton"))
        self.horizontalLayout.addWidget(self.ConnectButton)
        self.formLayout.setLayout(3, QtGui.QFormLayout.SpanningRole, self.horizontalLayout)

        self.retranslateUi(PrivateServerWidget)
        QtCore.QMetaObject.connectSlotsByName(PrivateServerWidget)

    def retranslateUi(self, PrivateServerWidget):
        PrivateServerWidget.setWindowTitle(QtGui.QApplication.translate("PrivateServerWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.HostLabel.setText(QtGui.QApplication.translate("PrivateServerWidget", "Host:", None, QtGui.QApplication.UnicodeUTF8))
        self.PortLabel.setText(QtGui.QApplication.translate("PrivateServerWidget", "Port:", None, QtGui.QApplication.UnicodeUTF8))
        self.BackButton.setText(QtGui.QApplication.translate("PrivateServerWidget", "Back", None, QtGui.QApplication.UnicodeUTF8))
        self.ConnectButton.setText(QtGui.QApplication.translate("PrivateServerWidget", "Connect", None, QtGui.QApplication.UnicodeUTF8))

