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
    Base Node tab for Interactive Groom Splines
'''
class IgSplineBaseTabUI(QWidget):
    
    # Base Node Attributes UI
    baseAttrUI = None
    
    def __init__(self, parent):
        ''' Constructor '''
        QWidget.__init__(self, parent)
        
        # Create the Base Node Attributes UI
        self.baseAttrUI = AttrEdUI(r'xgenBaseAttributeWindow')

        # Frame Layout for the Base Node Attribute UI
        baseAttrFrameUI = ExpandUI(maya.stringTable[u'y_xgenm_ui_tabs_xgIgSplineBaseTab.kBaseAttributes'], True)
        baseAttrFrameUI.addWidget(self.baseAttrUI)

        # Main layout of the Base Node tab
        layout = QVBoxLayout()
        QLayoutItem.setAlignment(layout, QtCore.Qt.AlignTop)
        layout.setSpacing(DpiScale(0))
        layout.setContentsMargins(DpiScale(3), DpiScale(3), DpiScale(3), DpiScale(3))
        layout.addWidget(baseAttrFrameUI)
        self.setLayout(layout)
        
    def refresh(self):
        ''' Update the UI from the description '''
        
        self.baseAttrUI.setNode(self.__getBaseNodeName())
        self.baseAttrUI.refresh()
        
    def __getBaseNodeName(self):
        ''' Get the dg node name of the base node '''
        
        # Get the MDagPath of the current spline description
        dagPath = getCurrentSplineDescriptionDagPath()
        if not dagPath.isValid():
            return r''
        
        # Starting with the xgmSplineDescription.outSplineData plug
        plug = om.MFnDagNode(dagPath).findPlug(r'outSplineData')
        if plug.isNull():
            return r''
        
        node = findUpstreamBaseNode(plug)
        if node.isNull():
            return r''
        
        dgNode = om.MFnDependencyNode(node)
        return dgNode.name()

# ===========================================================================
# Copyright 2021 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
