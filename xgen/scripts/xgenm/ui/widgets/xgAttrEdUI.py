from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *

import maya.cmds as cmds
import maya.OpenMaya as om


'''
    Wrapper widget for Maya's Attribute Editor
    
    This widget shows a dg node's Attribute Editor. In order to bridge the gap
    between Maya Qt and external Qt difference, we derive from QMainWindow.
    Maya recognize QMainWindow as a top level widget. A full UI path name will
    starts from the QMainWindow. So we don't need to assign object names to
    all parent QWidgets.
'''
class AttrEdUI(QMainWindow):
    
    # Name of the QMainWindow. Mandatory for Maya to recognize this widget
    windowName  = r''
    
    # Layout of the Property Sheet (Attribute Editor)
    psLayout    = r''
    
    # Current node of the Property Sheet (Attribute Editor)
    psNode      = r''
    psNodePtr   = om.MObjectHandle()
    
    # Whether we need to rebuild the Property Sheet (Attribute Editor)
    psRebuild   = False
    
    def __init__(self, name):
        ''' Constructor. Create a QMainWindow widget with the given name '''
        QMainWindow.__init__(self)

        # Maya recognizes this widget as a "Window". All layouts and controls
        # in the window are valid Maya UIs.
        # e.g. |myWindow|columnLayout|text
        self.windowName = name
        self.setObjectName(self.windowName)
        self.setAccessibleName(self.windowName)
        
        # By default, not attached to any nodes
        self.psLayout  = r''
        self.psNode    = r''
        self.psNodePtr = om.MObjectHandle()
        self.psRebuild = False

    def setNode(self, node):
        ''' Set the current dg node to show in Attribute Editor '''

        # Get the handle of the dg node
        nodePtr = om.MObject()
        if len(node) > 0:
            try:
                sl = om.MSelectionList()
                sl.add(node)
                sl.getDependNode(0, nodePtr)
            except:
                pass
        
        # Rebuild the Attribute Editor in the next refresh
        if self.psNodePtr != nodePtr or self.psNode != node:
            self.psRebuild = True
        
        # Set the current dg node name and handle
        self.psNode    = node
        self.psNodePtr = om.MObjectHandle(nodePtr)
        
    def refresh(self):
        ''' Update the Maya Attribute Editor '''
        
        if self.psRebuild:
            self.psRebuild = False
            self.__rebuildAttrEd()
            
    def __rebuildAttrEd(self):
        ''' Rebuild the Attribute Editor UI '''

        # Clean up the previous UI
        if len(self.psLayout) > 0:
            if cmds.layout(self.psLayout, q=True, ex=True):
                cmds.deleteUI(self.psLayout, layout=True)
            self.psLayout = r''
            
        # Make sure the default central widget exists
        if not self.centralWidget():
            centralWidget = QWidget()
            self.setCentralWidget(centralWidget)

        # No node to show ?
        if len(self.psNode) == 0:
            return
        
        # Node does not exist ?
        if not cmds.objExists(self.psNode):
            return
        
        # Set the current Maya window to the QMainWindow widget
        # All controls will be created in this widget
        cmds.setParent(self.windowName)
        
        # Create a default layout
        self.psLayout = cmds.formLayout()
        
        # Create the Attribute Editor in the layout
        cmds.createEditor(self.psLayout, self.psNode)
        
        # Stretch the Attribute Editor to the form border
        children = cmds.formLayout(self.psLayout, q=True, childArray=True)
        if children is not None and len(children) > 0:
            cmds.formLayout(self.psLayout, e=True, attachForm=[
                (children[0], r'top', 0), (children[0], r'left', 0),
                (children[0], r'bottom', 0), (children[0], r'right', 0)])
    
    
# ===========================================================================
# Copyright 2021 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
