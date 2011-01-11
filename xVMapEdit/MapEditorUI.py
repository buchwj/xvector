# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MapEditor.ui'
#
# Created: Mon Jan 10 19:02:09 2011
#      by: PyQt4 UI code generator 4.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MapEditorWindow(object):
    def setupUi(self, MapEditorWindow):
        MapEditorWindow.setObjectName(_fromUtf8("MapEditorWindow"))
        MapEditorWindow.resize(800, 600)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MapEditorWindow.sizePolicy().hasHeightForWidth())
        MapEditorWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtGui.QWidget(MapEditorWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.ResourceScroll = QtGui.QScrollArea(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ResourceScroll.sizePolicy().hasHeightForWidth())
        self.ResourceScroll.setSizePolicy(sizePolicy)
        self.ResourceScroll.setMinimumSize(QtCore.QSize(0, 0))
        self.ResourceScroll.setSizeIncrement(QtCore.QSize(32, 0))
        self.ResourceScroll.setFrameShape(QtGui.QFrame.StyledPanel)
        self.ResourceScroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.ResourceScroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.ResourceScroll.setWidgetResizable(True)
        self.ResourceScroll.setObjectName(_fromUtf8("ResourceScroll"))
        self.ResourceArea = QtGui.QWidget()
        self.ResourceArea.setGeometry(QtCore.QRect(0, 0, 160, 547))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ResourceArea.sizePolicy().hasHeightForWidth())
        self.ResourceArea.setSizePolicy(sizePolicy)
        self.ResourceArea.setMinimumSize(QtCore.QSize(160, 0))
        self.ResourceArea.setMaximumSize(QtCore.QSize(160, 16777215))
        self.ResourceArea.setObjectName(_fromUtf8("ResourceArea"))
        self.ResourceScroll.setWidget(self.ResourceArea)
        self.horizontalLayout.addWidget(self.ResourceScroll)
        self.mdiArea = QtGui.QMdiArea(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mdiArea.sizePolicy().hasHeightForWidth())
        self.mdiArea.setSizePolicy(sizePolicy)
        self.mdiArea.setViewMode(QtGui.QMdiArea.TabbedView)
        self.mdiArea.setObjectName(_fromUtf8("mdiArea"))
        self.horizontalLayout.addWidget(self.mdiArea)
        MapEditorWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MapEditorWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menu_File = QtGui.QMenu(self.menubar)
        self.menu_File.setObjectName(_fromUtf8("menu_File"))
        self.menu_Edit = QtGui.QMenu(self.menubar)
        self.menu_Edit.setObjectName(_fromUtf8("menu_Edit"))
        self.menu_Help = QtGui.QMenu(self.menubar)
        self.menu_Help.setObjectName(_fromUtf8("menu_Help"))
        self.menu_Window = QtGui.QMenu(self.menubar)
        self.menu_Window.setObjectName(_fromUtf8("menu_Window"))
        self.menuMap = QtGui.QMenu(self.menubar)
        self.menuMap.setObjectName(_fromUtf8("menuMap"))
        MapEditorWindow.setMenuBar(self.menubar)
        self.toolBar = QtGui.QToolBar(MapEditorWindow)
        self.toolBar.setAllowedAreas(QtCore.Qt.TopToolBarArea)
        self.toolBar.setFloatable(False)
        self.toolBar.setObjectName(_fromUtf8("toolBar"))
        MapEditorWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.action_Contents = QtGui.QAction(MapEditorWindow)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/ActionIcons/res/help-browser.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_Contents.setIcon(icon)
        self.action_Contents.setObjectName(_fromUtf8("action_Contents"))
        self.action_About = QtGui.QAction(MapEditorWindow)
        self.action_About.setObjectName(_fromUtf8("action_About"))
        self.action_Copy = QtGui.QAction(MapEditorWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/ActionIcons/res/edit-copy.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_Copy.setIcon(icon1)
        self.action_Copy.setObjectName(_fromUtf8("action_Copy"))
        self.actionC_ut = QtGui.QAction(MapEditorWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/ActionIcons/res/edit-cut.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionC_ut.setIcon(icon2)
        self.actionC_ut.setObjectName(_fromUtf8("actionC_ut"))
        self.action_Paste = QtGui.QAction(MapEditorWindow)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/ActionIcons/res/edit-paste.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_Paste.setIcon(icon3)
        self.action_Paste.setObjectName(_fromUtf8("action_Paste"))
        self.action_New = QtGui.QAction(MapEditorWindow)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(_fromUtf8(":/ActionIcons/res/document-new.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_New.setIcon(icon4)
        self.action_New.setObjectName(_fromUtf8("action_New"))
        self.action_Open = QtGui.QAction(MapEditorWindow)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(_fromUtf8(":/ActionIcons/res/document-open.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_Open.setIcon(icon5)
        self.action_Open.setObjectName(_fromUtf8("action_Open"))
        self.action_Save = QtGui.QAction(MapEditorWindow)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(_fromUtf8(":/ActionIcons/res/document-save.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_Save.setIcon(icon6)
        self.action_Save.setObjectName(_fromUtf8("action_Save"))
        self.action_SaveAs = QtGui.QAction(MapEditorWindow)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(_fromUtf8(":/ActionIcons/res/document-save-as.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_SaveAs.setIcon(icon7)
        self.action_SaveAs.setObjectName(_fromUtf8("action_SaveAs"))
        self.action_Quit = QtGui.QAction(MapEditorWindow)
        self.action_Quit.setObjectName(_fromUtf8("action_Quit"))
        self.actionNone = QtGui.QAction(MapEditorWindow)
        self.actionNone.setEnabled(False)
        self.actionNone.setObjectName(_fromUtf8("actionNone"))
        self.action_Properties = QtGui.QAction(MapEditorWindow)
        self.action_Properties.setObjectName(_fromUtf8("action_Properties"))
        self.actionClose = QtGui.QAction(MapEditorWindow)
        self.actionClose.setObjectName(_fromUtf8("actionClose"))
        self.action_Undo = QtGui.QAction(MapEditorWindow)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(_fromUtf8(":/ActionIcons/res/edit-undo.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_Undo.setIcon(icon8)
        self.action_Undo.setObjectName(_fromUtf8("action_Undo"))
        self.action_Redo = QtGui.QAction(MapEditorWindow)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(_fromUtf8(":/ActionIcons/res/edit-redo.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_Redo.setIcon(icon9)
        self.action_Redo.setObjectName(_fromUtf8("action_Redo"))
        self.menu_File.addAction(self.action_New)
        self.menu_File.addAction(self.action_Open)
        self.menu_File.addAction(self.action_Save)
        self.menu_File.addAction(self.action_SaveAs)
        self.menu_File.addAction(self.actionClose)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.action_Quit)
        self.menu_Edit.addAction(self.action_Undo)
        self.menu_Edit.addAction(self.action_Redo)
        self.menu_Edit.addSeparator()
        self.menu_Edit.addAction(self.action_Copy)
        self.menu_Edit.addAction(self.actionC_ut)
        self.menu_Edit.addAction(self.action_Paste)
        self.menu_Help.addAction(self.action_Contents)
        self.menu_Help.addSeparator()
        self.menu_Help.addAction(self.action_About)
        self.menu_Window.addAction(self.actionNone)
        self.menuMap.addAction(self.action_Properties)
        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.menu_Edit.menuAction())
        self.menubar.addAction(self.menuMap.menuAction())
        self.menubar.addAction(self.menu_Window.menuAction())
        self.menubar.addAction(self.menu_Help.menuAction())

        self.retranslateUi(MapEditorWindow)
        QtCore.QMetaObject.connectSlotsByName(MapEditorWindow)

    def retranslateUi(self, MapEditorWindow):
        MapEditorWindow.setWindowTitle(QtGui.QApplication.translate("MapEditorWindow", "xVector Engine Map Editor", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_File.setTitle(QtGui.QApplication.translate("MapEditorWindow", "&File", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_Edit.setTitle(QtGui.QApplication.translate("MapEditorWindow", "&Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_Help.setTitle(QtGui.QApplication.translate("MapEditorWindow", "&Help", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_Window.setTitle(QtGui.QApplication.translate("MapEditorWindow", "&Window", None, QtGui.QApplication.UnicodeUTF8))
        self.menuMap.setTitle(QtGui.QApplication.translate("MapEditorWindow", "&Map", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MapEditorWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Contents.setText(QtGui.QApplication.translate("MapEditorWindow", "&Contents", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Contents.setShortcut(QtGui.QApplication.translate("MapEditorWindow", "F1", None, QtGui.QApplication.UnicodeUTF8))
        self.action_About.setText(QtGui.QApplication.translate("MapEditorWindow", "&About", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Copy.setText(QtGui.QApplication.translate("MapEditorWindow", "&Copy", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Copy.setShortcut(QtGui.QApplication.translate("MapEditorWindow", "Ctrl+C", None, QtGui.QApplication.UnicodeUTF8))
        self.actionC_ut.setText(QtGui.QApplication.translate("MapEditorWindow", "Cu&t", None, QtGui.QApplication.UnicodeUTF8))
        self.actionC_ut.setShortcut(QtGui.QApplication.translate("MapEditorWindow", "Ctrl+X", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Paste.setText(QtGui.QApplication.translate("MapEditorWindow", "&Paste", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Paste.setShortcut(QtGui.QApplication.translate("MapEditorWindow", "Ctrl+V", None, QtGui.QApplication.UnicodeUTF8))
        self.action_New.setText(QtGui.QApplication.translate("MapEditorWindow", "&New...", None, QtGui.QApplication.UnicodeUTF8))
        self.action_New.setShortcut(QtGui.QApplication.translate("MapEditorWindow", "Ctrl+N", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Open.setText(QtGui.QApplication.translate("MapEditorWindow", "&Open...", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Open.setShortcut(QtGui.QApplication.translate("MapEditorWindow", "Ctrl+O", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Save.setText(QtGui.QApplication.translate("MapEditorWindow", "&Save", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Save.setShortcut(QtGui.QApplication.translate("MapEditorWindow", "Ctrl+S", None, QtGui.QApplication.UnicodeUTF8))
        self.action_SaveAs.setText(QtGui.QApplication.translate("MapEditorWindow", "S&ave As...", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Quit.setText(QtGui.QApplication.translate("MapEditorWindow", "&Quit", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNone.setText(QtGui.QApplication.translate("MapEditorWindow", "None", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Properties.setText(QtGui.QApplication.translate("MapEditorWindow", "&Properties...", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Properties.setShortcut(QtGui.QApplication.translate("MapEditorWindow", "Ctrl+M", None, QtGui.QApplication.UnicodeUTF8))
        self.actionClose.setText(QtGui.QApplication.translate("MapEditorWindow", "&Close", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Undo.setText(QtGui.QApplication.translate("MapEditorWindow", "&Undo", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Undo.setShortcut(QtGui.QApplication.translate("MapEditorWindow", "Ctrl+Z", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Redo.setText(QtGui.QApplication.translate("MapEditorWindow", "&Redo", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Redo.setShortcut(QtGui.QApplication.translate("MapEditorWindow", "Ctrl+Y", None, QtGui.QApplication.UnicodeUTF8))

import MapEditor_rc
