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
from xgenm.ui.widgets.xgIgValueSliderUI import *
from xgenm.ui.widgets.xgExpandUI import *
from xgenm.ui.util.xgUtil import DpiScale
import traceback
import sys

long_type = int if sys.version_info[0] >= 3 else long

# Class to hold the UI data
class UIOptionsData(object):
    """A simple class to hold the data setting from UI.
    """
    def __init__(self):
        # default values
        self.loadDefaults()

        # keys for optionVar
        self.keyDeleteCurves          = 'xgIgCurveToGuide_DeleteCurves'
        self.keyPreserveDynamicLink   = 'xgIgCurveToGuide_PreserveDynamicLink'

    def loadDefaults(self):
        # default values
        self.value_delete_curves    = False
        self.value_preserve_dynamic_link = True

    def saveToMayaOptionVar(self):
        if cmds :
            cmds.optionVar(intValue   = (self.keyDeleteCurves,            self.value_delete_curves))
            cmds.optionVar(intValue   = (self.keyPreserveDynamicLink,     self.value_preserve_dynamic_link))

    def loadFromMayaOptionVar(self):
        if cmds :
            if cmds.optionVar(exists=self.keyDeleteCurves):
                self.value_delete_curves = cmds.optionVar(query=self.keyDeleteCurves)
            if cmds.optionVar(exists=self.keyPreserveDynamicLink):
                self.value_preserve_dynamic_link = cmds.optionVar(query=self.keyPreserveDynamicLink)

class CurveToGuideWindow(QMainWindow):
    """Window for the Curve to Guide workflow
    """

    def __init__(self, parent, modifierNode, isGuide):
        QMainWindow.__init__(self, parent)

        self.isGuide = isGuide

        # An ui data
        self.uiData = UIOptionsData()
        self.uiData.loadFromMayaOptionVar()

        # Start with not show
        self.hide()

        # Modal
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        # Store some nodes here
        self.__modifierNode = modifierNode

        # Window title
        if self.isGuide:
            self.setWindowTitle(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgCurveToGuideUI.kCurveAsGuideWindowTitle' ])
        else:
            self.setWindowTitle(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgCurveToGuideUI.kCurveAsWireWindowTitle' ])

        # Fixed window size
        self.setFixedSize(DpiScale(485), DpiScale(120))

        # Create menus
        self.__createMenus()

        # Form Central widget
        #
        # Centeral widget -
        #              VBOX -
        #                  QFrame+Grid -
        #                       "Delete Curves"
        #                       "Preserve Dynamic Link"
        #                  HBOX -
        #                      "Apply and Close", "Cancel"
        #

        spacing = DpiScale(5)
        margin  = DpiScale(3)

        # central widget(rootVLayout)
        centeralWidget = QWidget()
        self.setCentralWidget(centeralWidget)
        rootVLayout = QVBoxLayout()
        centeralWidget.setLayout(rootVLayout)
        rootVLayout.setSpacing(spacing)
        rootVLayout.setContentsMargins(margin,margin,margin,margin)

        # rootVLayout | QFrame(Grid)
        frameWidget = QFrame()
        frameWidget.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        rootVLayout.addWidget(frameWidget)
        frameGridLayout = QGridLayout()
        frameWidget.setLayout(frameGridLayout)
        frameGridLayout.setSpacing(spacing)
        frameGridLayout.setContentsMargins(margin,margin,margin,margin)

        # rootVLayout | HBOX
        # "Apply and Close" and "Cancel" buttons
        widgetCreateCancelButtons = QWidget()
        rootVLayout.addWidget(widgetCreateCancelButtons)
        buttonHLayout = QHBoxLayout()
        widgetCreateCancelButtons.setLayout(buttonHLayout)
        buttonHLayout.setSpacing(spacing)
        buttonHLayout.setContentsMargins(margin,margin,margin,margin)

        #----------------------------------------
        # UIs for Options
        self.ui_delete_curves = QCheckBox(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgCurveToGuideUI.kDeleteCurves' ])
        self.ui_preserve_dynamic_link  = QCheckBox(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgCurveToGuideUI.kPreserveDynamicLink' ])

        self.connect(self.ui_delete_curves, QtCore.SIGNAL("clicked()"), self.__onDeleteCurves)
        self.connect(self.ui_preserve_dynamic_link, QtCore.SIGNAL("clicked()"), self.__onPreserveDynamicLink)

        frameGridLayout.setColumnMinimumWidth(0, DpiScale(150))
        frameGridLayout.addWidget(self.ui_delete_curves, 0, 1, 1, 2)
        frameGridLayout.addWidget(self.ui_preserve_dynamic_link, 1, 1, 1, 2)

        #----------------------------------------
        # UIs for two button
        #----------------------------------------

        buttonHeight  = 26

        # "Apply" button
        self.ui_applyButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_dialogs_xgIgCurveToGuideUI.kApplyAndClose'  ])
        self.ui_applyButton.setFixedHeight(DpiScale(buttonHeight))
        self.connect(self.ui_applyButton, QtCore.SIGNAL("clicked()"), self.__onClickApplyButton)
        buttonHLayout.addWidget(self.ui_applyButton, 0, QtCore.Qt.AlignBottom)

        # "Cancel" button
        self.ui_cancelButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_dialogs_xgIgCurveToGuideUI.kCancel'  ])
        self.ui_cancelButton.setFixedHeight(DpiScale(buttonHeight))
        self.connect(self.ui_cancelButton, QtCore.SIGNAL("clicked()"), self.__onClickCancelButton)
        buttonHLayout.addWidget(self.ui_cancelButton, 0, QtCore.Qt.AlignBottom)

        # Data -> UI
        self.__updateDataToUI()

    def __createMenus(self):
        # Edit menu
        editMenu = self.menuBar().addMenu(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgCurveToGuideUI.kEdit' ])
        editMenu.addAction(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgCurveToGuideUI.kResetSettings' ], self.__onMenuResetSettings)

        # Help menu
        helpMenu = self.menuBar().addMenu(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgCurveToGuideUI.kHelp' ])
        if self.isGuide:
            helpMenu.addAction(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgCurveToGuideUI.kCurveAsGuideWindowHelp' ], self.__onMenuHelp)
        else:
            helpMenu.addAction(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgCurveToGuideUI.kCurveAsWireWindowHelp' ], self.__onMenuHelp)

    def __onMenuResetSettings(self):
        self.__resetUI()

    def __onMenuHelp(self):
        # Navigate to an online help web page
        cmds.showHelp(r'CreateInteractiveGroomSplines')

    def __onDeleteCurves(self):
        self.uiData.value_delete_curves = self.ui_delete_curves.isChecked()
        if self.uiData.value_delete_curves:
            self.ui_delete_curves.setEnabled(True)
            self.ui_preserve_dynamic_link.setEnabled(False)
            self.uiData.value_preserve_dynamic_link = False
        else:
            self.ui_preserve_dynamic_link.setEnabled(True)

    def __onPreserveDynamicLink(self):
        self.uiData.value_preserve_dynamic_link = self.ui_preserve_dynamic_link.isChecked()
        if self.uiData.value_preserve_dynamic_link:
            self.ui_preserve_dynamic_link.setEnabled(True)
            self.ui_delete_curves.setEnabled(False)
            self.uiData.value_delete_curves = False
        else:
            self.ui_delete_curves.setEnabled(True)

    # data -> UI
    def __updateDataToUI(self):
        if self.uiData.value_delete_curves:
            self.ui_delete_curves.setCheckState(QtCore.Qt.Checked)
            self.ui_preserve_dynamic_link.setEnabled(False)
        else:
            self.ui_delete_curves.setCheckState(QtCore.Qt.Unchecked)

        if self.uiData.value_preserve_dynamic_link:
            self.ui_preserve_dynamic_link.setCheckState(QtCore.Qt.Checked)
            self.ui_delete_curves.setEnabled(False)
        else:
            self.ui_preserve_dynamic_link.setCheckState(QtCore.Qt.Unchecked)

        self.__onPreserveDynamicLink()

    # UI -> data
    def __updateUIToData(self):
        self.uiData.value_delete_curves  = self.ui_delete_curves.isChecked()
        self.uiData.value_preserve_dynamic_link  = self.ui_preserve_dynamic_link.isChecked()

    def __resetUI(self):
        self.uiData.loadDefaults()
        self.__updateDataToUI()

    # Click "Create" button
    def __onClickApplyButton(self):
        # Save UI data
        self.__updateUIToData()
        self.uiData.saveToMayaOptionVar()

        try:
            cmds.xgmMakeGuideDynamic(
                        createFromCurves = True,
                        deleteCurves = self.uiData.value_delete_curves,
                        preserveDynamicLink = self.uiData.value_preserve_dynamic_link)
        except:
            stackTrace = traceback.format_exc()
            print(stackTrace)

        self.close()

    # Click "Cancel" button
    def __onClickCancelButton(self):
        self.close()

    # On exit
    def closeEvent(self, event):
        pass

    # On show
    def showEvent(self, event):
        pass

    def run(self):
        self.show()

def createXgIgCurveToGuideWindow(modifierNode, isGuide):
    """Function to create the "Use Selected Curve as Guide Option" window
    """
    # Main window used as a parent widget here
    mayaMainWindowPtr = omui.MQtUtil.mainWindow()
    mayaMainWindow = wrapInstance(long_type(mayaMainWindowPtr), QWidget)

    wnd = CurveToGuideWindow(mayaMainWindow, modifierNode, isGuide)
    wnd.run()
# ===========================================================================
# Copyright 2021 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
