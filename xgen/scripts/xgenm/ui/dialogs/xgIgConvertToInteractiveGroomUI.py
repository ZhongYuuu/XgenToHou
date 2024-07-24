import maya
maya.utils.loadStringResourcesForModule(__name__)

from builtins import object
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from shiboken2 import wrapInstance

import xgenm as xg
import xgenm.xgGlobal as xgg
if xgg.Maya:
    import maya.cmds as cmds
    import maya.mel as mel
    import maya
    import maya.utils as utils
    from maya import OpenMayaUI as omui

from xgenm.ui.util.xgUtil import DpiScale
import sys

long_type = int if sys.version_info[0] >= 3 else long

# Class to hold the UI data
class UIData(object):
    """A simple class to hold the data setting from UI.
    """
    def __init__(self):
        # default values
        self.loadDefaults()

        # keys for optionVar
        self.kAddOutNamePrefix = 'xgIgConvert_addOutNamePrefix'
        self.kOutNamePrefix    = 'xgIgConvert_outNamePrefix'

    def saveToMayaOptionVar(self):
        if cmds :
            cmds.optionVar(intValue    = (self.kAddOutNamePrefix, self.addOutNamePrefix))
            cmds.optionVar(stringValue = (self.kOutNamePrefix, self.outNamePrefix))


    def loadFromMayaOptionVar(self):
        if cmds :
            if cmds.optionVar(exists=self.kAddOutNamePrefix):
                self.addOutNamePrefix = cmds.optionVar(query=self.kAddOutNamePrefix)
            if cmds.optionVar(exists=self.kOutNamePrefix):
                self.outNamePrefix = cmds.optionVar(query=self.kOutNamePrefix)

    def loadDefaults(self):
        # default values
        self.addOutNamePrefix = False
        self.outNamePrefix    = ""


# UI
class ConvertToInteractiveGroomWindow(QMainWindow):
    """A window for configuring converting to interactive groom.
    """

    def __init__(self, parent):
        QMainWindow.__init__(self)

        # Main window used as a parent widget here
        self.setParent(parent)

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Window)
        self.hide()

        self.__uiData = UIData()
        self.__uiData.loadFromMayaOptionVar()

        # Window title
        self.setWindowTitle(maya.stringTable[ u'y_xgenm_ui_dialogs_xgIgConvertToInteractiveGroomUI.kConvertToInteractiveGroomWindowTitle'  ])

        # Create menus
        #self.__createMenus()

        # Fixed size
        self.setFixedSize(DpiScale(480), DpiScale(100))

        # Set Central widget with grid layout
        centralWidget = QWidget()
        gridLayout = QGridLayout()
        centralWidget.setLayout(gridLayout)
        self.setCentralWidget(centralWidget)

        # Check box - whether add name prefix
        self.outPrefixChkBoxUI = QCheckBox(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgConvertToInteractiveGroomUI.kOutNamePrefixCheckbox' ])
        self.connect(self.outPrefixChkBoxUI, QtCore.SIGNAL("clicked()"), self.__onClickOutNamePrefix)
        gridLayout.addWidget(self.outPrefixChkBoxUI, 0, 0, 1, 1)

        # text field - prefix name
        self.outPrefixUI = QLineEdit()
        gridLayout.addWidget(self.outPrefixUI, 1, 0, 1, 1)

        #----------------------------------------
        # UIs for two button
        #----------------------------------------
        buttonHeight = DpiScale(26)
        buttonRowWidget = QWidget()
        buttonRowHLayout = QHBoxLayout()
        buttonRowHLayout.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))
        buttonRowHLayout.setSpacing(DpiScale(3))
        buttonRowWidget.setLayout(buttonRowHLayout)

        # "Convert" button
        self.ui_convertButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_dialogs_xgIgConvertToInteractiveGroomUI.kConvertButton'  ])
        self.ui_convertButton.setFixedHeight(buttonHeight)
        self.connect(self.ui_convertButton, QtCore.SIGNAL("clicked()"), self.__onClickConvertButton)
        buttonRowHLayout.addWidget(self.ui_convertButton)

        # "Cancel" button
        self.ui_cancelButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_dialogs_xgIgConvertToInteractiveGroomUI.kCancel'  ])
        self.ui_cancelButton.setFixedHeight(buttonHeight)
        self.connect(self.ui_cancelButton, QtCore.SIGNAL("clicked()"), self.__onClickCancelButton)
        buttonRowHLayout.addWidget(self.ui_cancelButton)

        gridLayout.addWidget(buttonRowWidget, 2, 0, 1, 2)


        self.__updateDataToUI()

    def __onClickOutNamePrefix(self):
        self.__uiData.addOutNamePrefix = self.outPrefixChkBoxUI.isChecked()
        if self.__uiData.addOutNamePrefix:
            self.outPrefixUI.setEnabled(True)
        else:
            self.outPrefixUI.setEnabled(False)

    def __onClickConvertButton(self):
        self.__updateUIToData()
        self.__uiData.saveToMayaOptionVar()
        try:
            if self.__uiData.addOutNamePrefix:
                cmds.xgmGroomConvert(prefix=self.__uiData.outNamePrefix)
            else:
                cmds.xgmGroomConvert()
        except:
            pass
        self.close()

    def __onClickCancelButton(self):
        self.close()


    def __updateDataToUI(self):
        if self.__uiData.addOutNamePrefix:
            self.outPrefixChkBoxUI.setCheckState(QtCore.Qt.Checked)
            self.outPrefixUI.setEnabled(True)
        else:
            self.outPrefixChkBoxUI.setCheckState(QtCore.Qt.Unchecked)
            self.outPrefixUI.setEnabled(False)

        self.outPrefixUI.setText(self.__uiData.outNamePrefix)

    def __updateUIToData(self):
        self.__uiData.addOutNamePrefix = self.outPrefixChkBoxUI.isChecked()
        self.__uiData.outNamePrefix = self.outPrefixUI.text()

    def run(self):
        self.__updateDataToUI()
        self.show()

def createXgIgConvertToInteractiveGroomWindow():
    """Function to create the window for converting to interacive groom setting.
    """
    # Main window used as a parent widget here
    mayaMainWindowPtr = omui.MQtUtil.mainWindow()
    mayaMainWindow = wrapInstance(long_type(mayaMainWindowPtr), QWidget)
    wnd = ConvertToInteractiveGroomWindow(mayaMainWindow)
    wnd.run()
# ===========================================================================
# Copyright 2021 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
