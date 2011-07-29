# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MetaserverWidget.ui'
#
# Created: Wed Jul 27 16:25:48 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MetaserverWidget(object):
    def setupUi(self, MetaserverWidget):
        MetaserverWidget.setObjectName(_fromUtf8("MetaserverWidget"))
        MetaserverWidget.resize(339, 374)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MetaserverWidget.sizePolicy().hasHeightForWidth())
        MetaserverWidget.setSizePolicy(sizePolicy)
        self.verticalLayout = QtGui.QVBoxLayout(MetaserverWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.ServerList = QtGui.QListView(MetaserverWidget)
        self.ServerList.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.ServerList.setObjectName(_fromUtf8("ServerList"))
        self.verticalLayout.addWidget(self.ServerList)
        self.scrollArea = QtGui.QScrollArea(MetaserverWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setMinimumSize(QtCore.QSize(0, 120))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 325, 114))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.DescriptionLabel = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.DescriptionLabel.setText(_fromUtf8(""))
        self.DescriptionLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.DescriptionLabel.setWordWrap(True)
        self.DescriptionLabel.setObjectName(_fromUtf8("DescriptionLabel"))
        self.verticalLayout_2.addWidget(self.DescriptionLabel)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.BackButton = QtGui.QPushButton(MetaserverWidget)
        self.BackButton.setObjectName(_fromUtf8("BackButton"))
        self.horizontalLayout.addWidget(self.BackButton)
        self.ConnectButton = QtGui.QPushButton(MetaserverWidget)
        self.ConnectButton.setEnabled(False)
        self.ConnectButton.setObjectName(_fromUtf8("ConnectButton"))
        self.horizontalLayout.addWidget(self.ConnectButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(MetaserverWidget)
        QtCore.QMetaObject.connectSlotsByName(MetaserverWidget)

    def retranslateUi(self, MetaserverWidget):
        MetaserverWidget.setWindowTitle(QtGui.QApplication.translate("MetaserverWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.BackButton.setText(QtGui.QApplication.translate("MetaserverWidget", "Back", None, QtGui.QApplication.UnicodeUTF8))
        self.ConnectButton.setText(QtGui.QApplication.translate("MetaserverWidget", "Connect", None, QtGui.QApplication.UnicodeUTF8))

