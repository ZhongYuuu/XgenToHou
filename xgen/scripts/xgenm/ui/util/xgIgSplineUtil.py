import maya
maya.utils.loadStringResourcesForModule(__name__)

from builtins import next
from builtins import range
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *


import os
import traceback
from contextlib import contextmanager

import xgenm as xg
import xgenm as xgen
import xgenm.xgGlobal as xgg

from xgenm.ui.util.xgUtil import DpiScale

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om
import maya.OpenMayaUI as omui

# Node IDs
XgmSplineDescription_id     = 0x5800032c
XgmSplineBaseNode_id        = 0x5800032d
XgmModifierSculptNode_id    = 0x58000841
XgmModifierGuide_id         = 0x58000843
XgmModifierSplineCache_id   = 0x58000844
XgmCurveToSpline_id         = 0x58000845
XgmModifierLinearWire_id    = 0x58000849

# Data IDs
XgmSplineData_id            = 0x5800032a

# Node nice names
gSplineNodeNiceNameTable = {
    r'xgmModifierCut'           : maya.stringTable[u'y_xgenm_ui_util_xgIgSplineUtil.kModifierCut'],
    r'xgmModifierCollision'     : maya.stringTable[u'y_xgenm_ui_util_xgIgSplineUtil.kModifierCollision'],
    r'xgmModifierSculpt'        : maya.stringTable[u'y_xgenm_ui_util_xgIgSplineUtil.kModifierSculpt'],
    r'xgmModifierNoise'         : maya.stringTable[u'y_xgenm_ui_util_xgIgSplineUtil.kModifierNoise'],
    r'xgmModifierGuide'         : maya.stringTable[u'y_xgenm_ui_util_xgIgSplineUtil.kModifierGuide'],
    r'xgmModifierLinearWire'    : maya.stringTable[u'y_xgenm_ui_util_xgIgSplineUtil.kModifierLinearWire'],
    r'xgmModifierScale'         : maya.stringTable[u'y_xgenm_ui_util_xgIgSplineUtil.kModifierScale'],
    r'xgmModifierDisplacement'  : maya.stringTable[u'y_xgenm_ui_util_xgIgSplineUtil.kModifierDisplacement' ],
    r'xgmSplineCache'           : maya.stringTable[u'y_xgenm_ui_util_xgIgSplineUtil.kModifierSplineCache'],
    r'xgmCurveToSpline'         : maya.stringTable[u'y_xgenm_ui_util_xgIgSplineUtil.kCurveToSpline' ],
    r'xgmModifierClump'         : maya.stringTable[u'y_xgenm_ui_util_xgIgSplineUtil.kModifierClump']
    }

def getSplineNodeNiceName(nodeType):
    ''' Get the Nice (UI) Name of the spline nodes '''
    global gSplineNodeNiceNameTable
    
    if nodeType in gSplineNodeNiceNameTable:
        return gSplineNodeNiceNameTable[nodeType]
    else:
        cmds.warning(r'Unlocalized XGen spline node type name %s' % nodeType)
        return nodeType
    
def getSplineModifierTypes():
    ''' Get a list of spline modifier node types '''

    return list(cmds.listNodeTypes(r'xgen/spline/modifier'))

def getSplineModifierIcon(nodeType):
    ''' Get the path to the spline modifier icon '''
    
    # e.g. xgmModifierSculpt -> sculpt
    iconName = None
    if nodeType.startswith(r'xgmModifier'):
        if nodeType == r'xgmModifierLinearWire':
            iconName = r'controlWires'
        elif nodeType == r'xgmModifierScale':
            iconName = r'tool_scaleGuideCurve'
        elif nodeType == r'xgmModifierCut':
            iconName = r'fx_cut'
        elif nodeType == r'xgmModifierCollision':
            iconName = r'collision'
        elif nodeType == r'xgmModifierGuide':
            iconName = r'tool_guidesAsCurves'
        elif nodeType == r'xgmModifierDisplacement':
            iconName = r'planeAnim'
        elif nodeType == r'xgmModifierClump':
            iconName = r'clumping'
        else:
            iconName = nodeType[11].lower() + nodeType[12:]
    elif nodeType == r'xgmSplineCache':
        iconName = r'xgSave'
    elif nodeType == r'xgmCurveToSpline':
        iconName = r'tool_curvesToGuides'
    else:
        iconName = nodeType

    # e.g. icons/fx_sculpt.png 
    path = r'%sfx_%s.png' % (xg.iconDir(), iconName)
    if os.path.exists(path):
        return path
    else:
        path = r'%s%s.png' % (xg.iconDir(), iconName)
        if os.path.exists(path):
            return path
        else:
            return xg.iconDir() + r'xgLogo.png'

def getCurrentSplineDescriptionDagPath():
    ''' Get the MDagPath object of the current spline description '''
    global XgmSplineDescription_id

    # Get the current spline description
    description = xgg.DescriptionEditor.currentDescription()
    
    # No current description ?
    if len(description) == 0:
        return om.MDagPath()
    
    # Query the MDagPath from Maya by partial path
    dagPath = om.MDagPath()
    try:
        sl = om.MSelectionList()
        sl.add(description)
        sl.getDagPath(0, dagPath)
    except:
        pass
    
    # We need the shape node
    dagPath.extendToShape()
    
    # Check the node type
    dagNode = om.MFnDagNode(dagPath)
    if dagNode.typeId().id() != XgmSplineDescription_id:
        return om.MDagPath()
    
    return dagPath

def isSplineBaseNode(node):
    ''' Returns True if the node is type of xgmSplineBase '''

    # Not a dg node ?
    if not node.hasFn(om.MFn.kDependencyNode):
        return False

    # Check for type id
    return om.MFnDependencyNode(node).typeId().id() == XgmSplineBaseNode_id

def isSplineModifierNode(node):
    ''' Returns True if the node is a modifier '''
    
    # Not a dg node ?
    if not node.hasFn(om.MFn.kDependencyNode):
        return r''
    
    # Get the classification of the node
    dgNode = om.MFnDependencyNode(node)
    classification = om.MFnDependencyNode.classification(dgNode.typeName())
    
    # Modifiers should be classified as 'xgen/spline/modifier'
    return r'xgen/spline/modifier' in str(classification)

def isSplineModifierSculptNode(node):
    ''' Returns True if the node is type of xgmModifierSculpt '''

    # Not a dg node ?
    if not node.hasFn(om.MFn.kDependencyNode):
        return False

    # Check for type id
    return om.MFnDependencyNode(node).typeId().id() == XgmModifierSculptNode_id

def isSplineModifierGuideNode(node):
    ''' Returns True if the node is type of xgmModifierGuide '''

    # Not a dg node ?
    if not node.hasFn(om.MFn.kDependencyNode):
        return False

    # Check for type id
    return om.MFnDependencyNode(node).typeId().id() == XgmModifierGuide_id

def isSplineModifierLinearWireNode(node):
    ''' Returns True if the node is type of xgmModifierLinearWire '''

    # Not a dg node ?
    if not node.hasFn(om.MFn.kDependencyNode):
        return False

    # Check for type id
    return om.MFnDependencyNode(node).typeId().id() == XgmModifierLinearWire_id

def isSplineModifierCacheNode(node):
    ''' Returns True if the node is type of xgmSplineCache '''

    # Not a dg node ?
    if not node.hasFn(om.MFn.kDependencyNode):
        return False

    # Check for type id
    return om.MFnDependencyNode(node).typeId().id() == XgmModifierSplineCache_id

def isCurveToSplineNode(node):
    ''' Returns True if the node is type of xgmCurveToSpline '''

    # Not a dg node ?
    if not node.hasFn(om.MFn.kDependencyNode):
        return False

    # Check for type id
    return om.MFnDependencyNode(node).typeId().id() == XgmCurveToSpline_id

def isOverrideModifierNode(node):
    ''' Returns True if the node is type of xgmSplineCache or xgmCurveToSpline '''

    return isSplineModifierCacheNode(node) or isCurveToSplineNode(node)

def isSplineDescriptionNode(node):
    ''' Returns True if the node is type of xgmSplineDescription '''

    # Not a dg node ?
    if not node.hasFn(om.MFn.kDependencyNode):
        return False

    # Check for type id
    return om.MFnDependencyNode(node).typeId().id() == XgmSplineDescription_id

def isDestinationSplinePlug(plug):
    ''' Returns True if the plug is typeof xgmSplineData and connected '''
    global XgmSplineData_id
    
    # Not a destination plug ?
    if not plug.isDestination():
        return False
    
    # Not typeof xgmSplineData ?
    splineType = om.MTypeId(XgmSplineData_id)
    if not om.MFnAttribute(plug.attribute()).accepts(splineType):
        return False

    return True

def getUniquePlugName(plug):
    ''' Get the unique name of a MPlug '''

    # Null plug ?
    if plug.isNull():
        return r''

    # Get the MObject of the node
    node = plug.node()

    # Determine the unique name of the MPlug
    if node.hasFn(om.MFn.kDagNode):
        # MPlug.name() might return an ambigious name when the name of
        # the dag node is not unique.
        name = plug.name()
        return om.MFnDagNode(node).partialPathName() + name[name.index(r'.'):]
    else:
        return plug.name()

def findUpstreamSplinePlug(outPlug):
    ''' Find the plug connecting to the upstream spline node (at most 1) '''
    
    # Not a dg node ?
    if not outPlug.node().hasFn(om.MFn.kDependencyNode):
        return om.MPlug()
    
    # Get the owner dg node
    dgNode = om.MFnDependencyNode(outPlug.node())
    
    # Prefer inSplineData and outSplineData plugs
    inPlug = om.MPlug()
    try:
        inPlug = dgNode.findPlug(r'inSplineData')
    except:
        pass
    if not inPlug.isNull():
        # inSplineData plug take precedence
        if inPlug.isArray() and outPlug.isElement():
            # Look for a matching multi child
            for i in range(0, inPlug.numConnectedElements()):
                plug = inPlug.connectionByPhysicalIndex(i)
                if plug.logicalIndex() == outPlug.logicalIndex():
                    return plug
        elif inPlug.isDestination():
            # Just find the source regardless of type or multi
            return inPlug
    else:
        # A generic approach : Iterate the affecting plugs
        dgIt = om.MItDependencyGraph(outPlug, om.MFn.kInvalid,
            om.MItDependencyGraph.kUpstream,
            om.MItDependencyGraph.kDepthFirst,
            om.MItDependencyGraph.kPlugLevel)
        next(dgIt) # Skip root plug (outPlug)
        while not dgIt.isDone():
            plug = dgIt.previousPlug()
            if plug.node() == outPlug.node() and isDestinationSplinePlug(plug):
                # The input plug is a destination plug type of xgmSplineData
                if plug.isElement() and outPlug.isElement():
                    # Looking for a matching multi child
                    if plug.logicalIndex() == outPlug.logicalIndex():
                        return plug
                else:
                    # Either input or output is not a multi plug
                    return plug
            else:
                # Only looking for input plugs of this node
                dgIt.prune()
            next(dgIt)

    return om.MPlug()

def findUpstreamBaseNode(outPlug):
    ''' Find the upstream base node (at most 1) '''
    global XgmSplineBaseNode_id
    
    # Recursively iterate the dg graph for the node chain until we find
    # a base node.
    dgNode = om.MFnDependencyNode()
    plug   = outPlug
    while not plug.isNull():
        # Go upstream
        destinationPlug = findUpstreamSplinePlug(plug)
        plug = destinationPlug.source()

        # Check node type
        if not plug.isNull():
            dgNode.setObject(plug.node())
            if dgNode.typeId().id() == XgmSplineBaseNode_id:
                return plug.node()

    return om.MObject()

def isSculptGroupOwnerEnabled(node, ownerId):
    ''' Return True if all the owner sculpt groups and the modifier is enabled '''

    # Check if the whole sculpt modifier node is muted
    dgNode = om.MFnDependencyNode(node)
    if dgNode.findPlug(r'mute').asBool():
        return False

    # Get the "tweakGroups" plug
    groupArrayPlug = dgNode.findPlug(r'tweakGroups')

    # Get the "tweakGroupEnable" attribute
    enableAttribute = dgNode.attribute(r'tweakGroupEnable')

    # Get the "tweakGroupOwnerId" attribute
    ownerIdAttribute = dgNode.attribute(r'tweakGroupOwnerId')

    # Loop until the root group
    while ownerId != -1:
        # Get the "tweakGroups[ownerId]" plug
        groupPlug = groupArrayPlug.elementByLogicalIndex(ownerId)

        # Get the "tweakGroups[ownerId].tweakGroupEnable" plug
        enablePlug = groupPlug.child(enableAttribute)

        # Is owner enabled ?
        if not enablePlug.asBool():
            return False

        # Go up
        ownerId = groupPlug.child(ownerIdAttribute).asInt()

    # Survive !
    return True

def isActiveSculptLayer(descriptionNode, sculptModifierNode, logicalIndex):
    ''' Return True if the specified layer is globally active '''

    # Get the MDagPath to the current active description
    dagPath = xgg.IgSplineEditor.getCurrentDescriptionPath()

    # Reject if the description is not active
    if not dagPath.isValid() or dagPath.node() != descriptionNode:
        return False

    # Track the activeSculpt plug of the current description
    dgNode = om.MFnDependencyNode(descriptionNode)
    plug   = dgNode.findPlug(r'activeSculpt')

    # Reject if the sculpt modifier is not active
    if not plug.isDestination() or plug.source().node() != sculptModifierNode:
        return False

    # Get the current active layer of the sculpt modifier
    dgNode.setObject(sculptModifierNode)
    physicalIndex = dgNode.findPlug(r'activeTweak').asInt() - 1

    # Get the tweaks array plug
    plug = dgNode.findPlug(r'tweaks')

    # Reject if the physical index is invalid ?
    if physicalIndex >= plug.numElements():
        return False
    
    # Reject if the sculpt layer is not active
    if plug.elementByPhysicalIndex(physicalIndex).logicalIndex() != logicalIndex:
        return False

    # Survive !
    return True

def currentSplineDescription(shape=False):
    ''' Return the current spline description '''

    if xgg.IgSplineEditor:
        return xgg.IgSplineEditor.currentDescription(shape=shape)
    elif xgg.DescriptionEditor: # Legacy. XGEN_TODO: deleteme
        return xgg.DescriptionEditor.currentDescription()
    return r''

def addSculptLayer():
    if xgg.IgSplineEditor:
        xgg.IgSplineEditor.newLayerRequested.emit()

'''
    A widget with a center-aligned QCheckBox
'''
class CheckBoxItemWidget(QWidget):
    
    widget = None
    layout = None
    
    def __init__(self, parent):
        ''' Constructor '''
        QWidget.__init__(self, parent)
        
        # Create the internal QCheckBox widget
        self.widget = QCheckBox(self)
        
        # Create the layout to center the check box
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(DpiScale(0), DpiScale(0), DpiScale(0), DpiScale(0))
        QLayoutItem.setAlignment(self.layout, QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.widget)
        self.setLayout(self.layout)
        
        # Widget is transparent to events
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents,True)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

    def setCheckState(self, state):
        ''' Set the check state to the QCheckBox '''
        self.widget.setCheckState(state)


    




    
# ===========================================================================
# Copyright 2021 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
