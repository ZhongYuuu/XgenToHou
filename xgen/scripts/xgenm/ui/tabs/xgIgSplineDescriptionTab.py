import maya
maya.utils.loadStringResourcesForModule(__name__)

from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *

import xgenm as xg
import xgenm.xgGlobal as xgg
from xgenm.ui.widgets import *
from xgenm.ui.util.xgIgSplineUtil import *
from xgenm.ui.util.xgUtil import DpiScale

import maya.OpenMaya as om


'''
    Description tab for Interactive Groom Splines
'''
class IgSplineDescriptionTabUI(QWidget):
    
    # Description Attributes UI
    descriptionAttrUI = None
    
    def __init__(self, parent):
        ''' Constructor '''
        QWidget.__init__(self, parent)
        
        # Create the Description Attributes UI
        self.descriptionAttrUI = AttrEdUI(r'xgenDescriptionAttributeWindow')

        # Frame Layout for the Description Attribute UI
        descriptionAttrFrameUI = ExpandUI(maya.stringTable[u'y_xgenm_ui_tabs_xgIgSplineDescriptionTab.kDescriptionAttributes'], True)
        descriptionAttrFrameUI.addWidget(self.descriptionAttrUI)

        # Main layout of the Description tab
        layout = QVBoxLayout()
        QLayoutItem.setAlignment(layout, QtCore.Qt.AlignTop)
        layout.setSpacing(DpiScale(0))
        layout.setContentsMargins(DpiScale(3), DpiScale(3), DpiScale(3), DpiScale(3))
        layout.addWidget(descriptionAttrFrameUI)
        self.setLayout(layout)
        
    def refresh(self):
        ''' Update the UI from the description '''
        
        self.descriptionAttrUI.setNode(self.__getDescriptionNodeName())
        self.descriptionAttrUI.refresh()
        
    def __getDescriptionNodeName(self):
        ''' Get the dg node name of the description '''
        
        # Get the MDagPath of the current spline description
        dagPath = getCurrentSplineDescriptionDagPath()
        if not dagPath.isValid():
            return r''
        
        return om.MFnDagNode(dagPath).name()
        
# ===========================================================================
# Copyright 2021 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
