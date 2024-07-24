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
class UIData(object):
    """A simple class to hold the data setting from UI.
    """
    def __init__(self):
        # default values
        self.loadDefaults()

        # keys for optionVar
        self.kNHairAttach   = 'xgIgMakeDynamic_NHairAttach'
        self.kNHairSnap     = 'xgIgMakeDynamic_NHairSnap'
        self.kNHairCollide  = 'xgIgMakeDynamic_NHairCollide'
        self.kNHairExact    = 'xgIgMakeDynamic_NHairExact'
        self.kDeletOrigin   = 'xgIgMakeDynamic_DeletOrigin'

    def loadDefaults(self):
        # default values
        self.value_nHair_attach  = True
        self.value_nHair_snap    = False
        self.value_nHair_collide = False
        self.value_nHair_exact   = True
        self.value_delete_origin = True

    def saveToMayaOptionVar(self):
        if cmds :
            cmds.optionVar(intValue   = (self.kNHairAttach,     self.value_nHair_attach))
            cmds.optionVar(intValue   = (self.kNHairSnap,       self.value_nHair_snap))
            cmds.optionVar(intValue   = (self.kNHairCollide,    self.value_nHair_collide))
            cmds.optionVar(intValue   = (self.kNHairExact,      self.value_nHair_exact))
            cmds.optionVar(intValue   = (self.kDeletOrigin,     self.value_delete_origin))

    def loadFromMayaOptionVar(self):
        if cmds :
            if cmds.optionVar(exists=self.kNHairAttach):
                self.value_nHair_attach = cmds.optionVar(query=self.kNHairAttach)
            if cmds.optionVar(exists=self.kNHairSnap):
                self.value_nHair_snap = cmds.optionVar(query=self.kNHairSnap)
            if cmds.optionVar(exists=self.kNHairCollide):
                self.value_nHair_collide = cmds.optionVar(query=self.kNHairCollide)
            if cmds.optionVar(exists=self.kNHairExact):
                self.value_nHair_exact = cmds.optionVar(query=self.kNHairExact)
            if cmds.optionVar(exists=self.kDeletOrigin):
                self.value_delete_origin = cmds.optionVar(query=self.kDeletOrigin)

class NHairGuideWindow(QMainWindow):
    """Window for the nHair Guide workflow
    """

    def __init__(self, parent, guideModifierNode):
        QMainWindow.__init__(self, parent)

        # An ui data
        self.uiData = UIData()
        self.uiData.loadFromMayaOptionVar()

        # Start with not show
        self.hide()

        # Modal
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        # Store some nodes here
        self.__guideModifierNode = guideModifierNode

        # Window title
        self.setWindowTitle(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgNHairGuideUI.kNHairGuideWindowTitle' ])

        # Fixed window size
        self.setFixedSize(DpiScale(485), DpiScale(180))

        # Create menus
        self.__createMenus()

        # Form Central widget
        #
        # Centeral widget -
        #              VBOX -
        #                  QFrame+Grid -
        #                       "Attach curves to selected surfaces"
        #                       "Snap curve base to surface"
        #                       "Collide With Mesh"
        #                       "Exact shape match"
        #                       "Delete Original Guide Data"
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
        # UIs for 'nHair Options'
        #----------------------------------------

        self.ui_nhair_attachCurve = QCheckBox(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgNHairGuideUI.kNHairAttachCurve' ])
        self.ui_nhair_snapCurve   = QCheckBox(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgNHairGuideUI.kNHairSnapCurve' ])
        self.ui_nhair_collide     = QCheckBox(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgNHairGuideUI.kNHairCollide' ])
        self.ui_nhair_exact       = QCheckBox(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgNHairGuideUI.kNHairExact' ])
        self.ui_delete_origin     = QCheckBox(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgNHairGuideUI.kDeleteOriginGuide' ])

        self.connect(self.ui_nhair_attachCurve, QtCore.SIGNAL("clicked()"), self.__onClickAttachCurve)

        frameGridLayout.setColumnMinimumWidth(0, DpiScale(150))
        frameGridLayout.addWidget(self.ui_nhair_attachCurve, 0, 1, 1, 2)
        frameGridLayout.addWidget(self.ui_nhair_snapCurve, 1, 1, 1, 2)
        frameGridLayout.addWidget(self.ui_nhair_collide, 2, 1, 1, 2)
        frameGridLayout.addWidget(self.ui_nhair_exact, 3, 1, 1, 2)
        frameGridLayout.addWidget(self.ui_delete_origin, 4, 1, 1, 2)

        #----------------------------------------
        # UIs for two button
        #----------------------------------------

        buttonHeight  = 26

        # "Apply" button
        self.ui_applyButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_dialogs_xgIgNHairGuideUI.kApplyAndClose'  ])
        self.ui_applyButton.setFixedHeight(DpiScale(buttonHeight))
        self.connect(self.ui_applyButton, QtCore.SIGNAL("clicked()"), self.__onClickApplyButton)
        buttonHLayout.addWidget(self.ui_applyButton, 0, QtCore.Qt.AlignBottom)

        # "Cancel" button
        self.ui_cancelButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_dialogs_xgIgNHairGuideUI.kCancel'  ])
        self.ui_cancelButton.setFixedHeight(DpiScale(buttonHeight))
        self.connect(self.ui_cancelButton, QtCore.SIGNAL("clicked()"), self.__onClickCancelButton)
        buttonHLayout.addWidget(self.ui_cancelButton, 0, QtCore.Qt.AlignBottom)

        # Data -> UI
        self.__updateDataToUI()

    def __createMenus(self):
        # Edit menu
        editMenu = self.menuBar().addMenu(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgNHairGuideUI.kEdit' ])
        editMenu.addAction(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgNHairGuideUI.kResetSettings' ], self.__onMenuResetSettings)

        # Help menu
        helpMenu = self.menuBar().addMenu(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgNHairGuideUI.kHelp' ])
        helpMenu.addAction(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgNHairGuideUI.kHelpMenu' ], self.__onMenuHelp)

    def __onMenuResetSettings(self):
        self.__resetUI()

    def __onMenuHelp(self):
        # Navigate to an online help web page
        cmds.showHelp(r'MakeGuidesDynamic')

    def __onClickAttachCurve(self):
        self.uiData.value_nHair_attach = self.ui_nhair_attachCurve.isChecked()
        if self.uiData.value_nHair_attach:
            self.ui_nhair_snapCurve.setEnabled(True)
            self.ui_nhair_collide.setEnabled(True)
        else:
            self.ui_nhair_snapCurve.setEnabled(False)
            self.ui_nhair_collide.setEnabled(False)

    # data -> UI
    def __updateDataToUI(self):
        if self.uiData.value_nHair_attach:
            self.ui_nhair_attachCurve.setCheckState(QtCore.Qt.Checked)
        else:
            self.ui_nhair_attachCurve.setCheckState(QtCore.Qt.Unchecked)
        if self.uiData.value_nHair_snap:
            self.ui_nhair_snapCurve.setCheckState(QtCore.Qt.Checked)
        else:
            self.ui_nhair_snapCurve.setCheckState(QtCore.Qt.Unchecked)
        if self.uiData.value_nHair_collide:
            self.ui_nhair_collide.setCheckState(QtCore.Qt.Checked)
        else:
            self.ui_nhair_collide.setCheckState(QtCore.Qt.Unchecked)
        if self.uiData.value_nHair_exact:
            self.ui_nhair_exact.setCheckState(QtCore.Qt.Checked)
        else:
            self.ui_nhair_exact.setCheckState(QtCore.Qt.Unchecked)
        if self.uiData.value_delete_origin:
            self.ui_delete_origin.setCheckState(QtCore.Qt.Checked)
        else:
            self.ui_delete_origin.setCheckState(QtCore.Qt.Unchecked)

        self.__onClickAttachCurve()

    # UI -> data
    def __updateUIToData(self):
        self.uiData.value_nHair_attach  = self.ui_nhair_attachCurve.isChecked()
        self.uiData.value_nHair_snap    = self.ui_nhair_snapCurve.isChecked()
        self.uiData.value_nHair_collide = self.ui_nhair_collide.isChecked()
        self.uiData.value_nHair_exact   = self.ui_nhair_exact.isChecked()
        self.uiData.value_delete_origin = self.ui_delete_origin.isChecked()

    def __resetUI(self):
        self.uiData.loadDefaults()
        self.__updateDataToUI()

    # Click "Create" button
    def __onClickApplyButton(self):
        # Save UI data
        self.__updateUIToData()
        self.uiData.saveToMayaOptionVar()

        # Use all existing guides to create nHair system
        try:
            cmds.xgmMakeGuideDynamic(
                        self.__guideModifierNode,
                        create=(
                            self.uiData.value_nHair_attach,
                            self.uiData.value_nHair_snap,
                            self.uiData.value_nHair_collide,
                            self.uiData.value_nHair_exact,
                            self.uiData.value_delete_origin))
        except:
            stackTrace = traceback.format_exc()
            print(stackTrace)
            cmds.inViewMessage(msg=maya.stringTable[u'y_xgenm_ui_dialogs_xgIgNHairGuideUI.kMakeGuideDynamicFailed' ], pos="botCenter", fade=True)
        else:
            cmds.inViewMessage(msg=maya.stringTable[u'y_xgenm_ui_dialogs_xgIgNHairGuideUI.kMakeGuideDynamicSucceeded' ], pos="botCenter", fade=True)

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

def createXgIgNHairGuideWindow(guideModifierNode):
    """Function to create the NHair Guide window
    """
    # Main window used as a parent widget here
    mayaMainWindowPtr = omui.MQtUtil.mainWindow()
    mayaMainWindow = wrapInstance(long_type(mayaMainWindowPtr), QWidget)

    wnd = NHairGuideWindow(mayaMainWindow, guideModifierNode)
    wnd.run()

# ===========================================================================
# Copyright 2021 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
