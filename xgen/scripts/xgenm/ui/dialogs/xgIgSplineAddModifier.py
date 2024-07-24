import maya
maya.utils.loadStringResourcesForModule(__name__)

from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *

import xgenm as xg
import xgenm as xgen
import xgenm.xgGlobal as xgg
from xgenm.ui.util.xgIgSplineUtil import *
from xgenm.ui.util.xgUtil import CreateIcon
from xgenm.ui.util.xgUtil import DpiScale

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om


'''
    A modal dialog to add a modifier to the modifier chain of the current
    description. 
'''
class IgSplineAddModifierUI(QDialog):
    
    modifierListUI = None
    buttonsUI      = None
    nodeTypes      = []
    
    def __init__(self, x, y):
        ''' Create a dialog at (x,y) '''
        QDialog.__init__(self)

        self.nodeTypes = []
        
        # Dialog properties
        self.setGeometry(x, y, DpiScale(580), DpiScale(330))
        self.setSizeGripEnabled(True)
        self.setWindowTitle(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgSplineAddModifier.kAddModifierWindow'])

        # Modifier List
        self.__createModifierListUI()

        # OK and Cancel buttons
        self.__createButtonsUI()
        
        # Main Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(DpiScale(10), DpiScale(10), DpiScale(10), DpiScale(10))
        layout.setSpacing(DpiScale(0))
        layout.addWidget(self.modifierListUI)
        layout.addWidget(self.buttonsUI)
        self.setLayout(layout)

    def __createModifierListUI(self):
        ''' Create the UI widgets for the modifiers '''

        # If in localized mode, build tab in horizontal layout to
        # accomodate japanese text better.
        isLocalized = cmds.about(uiLanguageIsLocalized=True)
        
        # A QListWidget to show the modifiers
        self.modifierListUI = QListWidget()
        self.modifierListUI.setSelectionMode(QAbstractItemView.MultiSelection)
        self.modifierListUI.setMovement(QListView.Static)
        self.modifierListUI.setResizeMode(QListView.Adjust)
        self.modifierListUI.setWordWrap(True)
        
        if isLocalized:
            self.modifierListUI.setViewMode(QListView.ListMode)
            self.modifierListUI.setWrapping(True)
            self.modifierListUI.setFlow(QListView.LeftToRight)
            self.modifierListUI.setIconSize(QSize(DpiScale(50),DpiScale(50)))
        else:
            self.modifierListUI.setViewMode(QListView.IconMode)
            self.modifierListUI.setGridSize(QSize(DpiScale(64),DpiScale(80)))
            
        # Add spline modifiers
        for nodeType in getSplineModifierTypes():
            # Temporary hide the xgmSplineCache modifier
            if nodeType == r'xgmSplineCache':
                continue

            # UI Nice Name and Icon of the modifier
            niceName = getSplineNodeNiceName(nodeType)
            icon     = CreateIcon(getSplineModifierIcon(nodeType))
            
            # Create the list widget item for the modifier
            item = QListWidgetItem(icon, niceName)
            item.setToolTip(niceName)
            item.setData(QtCore.Qt.UserRole, nodeType)
            
            if isLocalized:
                item.setSizeHint(QSize(DpiScale(110),DpiScale(50)))
                item.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            
            # Add to the list
            self.modifierListUI.addItem(item)
            
    def __createButtonsUI(self):
        ''' Create the UI widgets for the buttons '''
        
        # OK Button
        okButton = QPushButton(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgSplineAddModifier.kOK'])
        okButton.setFixedWidth(DpiScale(90))
        okButton.setAutoRepeat(False)
        okButton.setToolTip(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgSplineAddModifier.kOKButtonAnnot' ])
        okButton.setDefault(True)
        
        # Cancel Button
        cancelButton = QPushButton(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgSplineAddModifier.kCancel'])
        cancelButton.setFixedWidth(DpiScale(90))
        cancelButton.setToolTip(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgSplineAddModifier.kCancelButtonAnnot' ])

        # Connect Signals
        okButton.clicked.connect(self.__onOKButtonClicked)
        cancelButton.clicked.connect(self.reject)
        
        # A widget to hold the buttons
        self.buttonsUI = QWidget()
        layout = QHBoxLayout()
        QLayoutItem.setAlignment(layout, QtCore.Qt.AlignCenter)
        layout.addWidget(okButton)
        layout.addWidget(cancelButton)
        self.buttonsUI.setLayout(layout)
        
    def __onOKButtonClicked(self):
        ''' Invoked when the OK button is clicked '''
        
        # Collect the user selection
        for item in self.modifierListUI.selectedItems():
            self.nodeTypes.append(str(item.data(QtCore.Qt.UserRole)))
        self.accept()
        
    def getNodeTypes(self):
        ''' Return the result of the user selection '''
        
        return self.nodeTypes

        
# ===========================================================================
# Copyright 2021 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
