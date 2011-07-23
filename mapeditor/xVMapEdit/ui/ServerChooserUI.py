# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ServerChooser.ui'
#
# Created: Fri Jul 22 14:14:01 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ServerChooserDialog(object):
    def setupUi(self, ServerChooserDialog):
        ServerChooserDialog.setObjectName(_fromUtf8("ServerChooserDialog"))
        ServerChooserDialog.resize(295, 349)
        self.verticalLayout = QtGui.QVBoxLayout(ServerChooserDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.InstructionsLabel = QtGui.QLabel(ServerChooserDialog)
        self.InstructionsLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.InstructionsLabel.setWordWrap(True)
        self.InstructionsLabel.setObjectName(_fromUtf8("InstructionsLabel"))
        self.verticalLayout.addWidget(self.InstructionsLabel)
        self.ResourcesList = QtGui.QListView(ServerChooserDialog)
        self.ResourcesList.setObjectName(_fromUtf8("ResourcesList"))
        self.verticalLayout.addWidget(self.ResourcesList)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.buttonOK = QtGui.QPushButton(ServerChooserDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonOK.sizePolicy().hasHeightForWidth())
        self.buttonOK.setSizePolicy(sizePolicy)
        self.buttonOK.setObjectName(_fromUtf8("buttonOK"))
        self.horizontalLayout.addWidget(self.buttonOK)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(ServerChooserDialog)
        QtCore.QObject.connect(self.buttonOK, QtCore.SIGNAL(_fromUtf8("clicked()")), ServerChooserDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(ServerChooserDialog)

    def retranslateUi(self, ServerChooserDialog):
        ServerChooserDialog.setWindowTitle(QtGui.QApplication.translate("ServerChooserDialog", "Select Resources...", None, QtGui.QApplication.UnicodeUTF8))
        self.InstructionsLabel.setText(QtGui.QApplication.translate("ServerChooserDialog", "Please select which server\'s resources to use when editing maps.", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonOK.setText(QtGui.QApplication.translate("ServerChooserDialog", "&OK", None, QtGui.QApplication.UnicodeUTF8))

