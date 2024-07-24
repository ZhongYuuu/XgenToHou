import maya
maya.utils.loadStringResourcesForModule(__name__)

from builtins import range
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from shiboken2 import wrapInstance, getCppPointer

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui

from xgenm.ui.util.xgUtil import CreateIcon
from xgenm.ui.util.xgUtil import DpiScale
from xgenm.ui.util.xgUtil import MayaCmdsTransaction
from xgenm.ui.util.xgIgSplineUtil import *
from xgenm.ui.widgets import *
from xgenm.ui.xgConsts import *
import sys

long_type = int if sys.version_info[0] >= 3 else long


# Definition of the columns of the Colliders

# Placeholder column is used to:
# - accommodate QTreeWidget's automatic indendation on the first column
# - store invisible data
TREE_COLUMN_PLACEHOLDER = 0
TREE_COLUMN_ENABLE = 1
TREE_COLUMN_OBJECT_NAME = 2
TREE_COLUMN_FLIP_NORMAL = 3
TREE_COLUMN_COUNT = 4

# Global variables
__inColliderAttrChangedCallback = False
__collidersControl = None


def AExgmModifierCollisionTemplate(nodeName):
    '''Construct the AE template for xgmModifierCollision node'''

    # Begin xgmModifierCollision Attribute Editor template
    cmds.editorTemplate(beginScrollLayout=True)

    # Common Attributes
    mel.eval(r'AExgmModifierBaseTemplate ' + nodeName)

    # Collision Modifier Attributes
    cmds.editorTemplate(
        beginLayout=maya.stringTable[u'y_xgenm_ui_ae_xgmModifierCollisionTemplate.kCollisionModifier' ],
        collapse=False
    )
    mel.eval(r'xgmCreateAEUiForFloatAttr "mask" "%s" "xgmModifierCollision"' %
             maya.stringTable[u'y_xgenm_ui_ae_xgmModifierCollisionTemplate.kMask' ])
    cmds.editorTemplate(addSeparator=True)

    cmds.editorTemplate(
        r'collisionDistance',
        label=maya.stringTable[u'y_xgenm_ui_ae_xgmModifierCollisionTemplate.kCollisionDistance' ],
        addControl=True
    )

    cmds.editorTemplate(
        r'AExgmModifierCollisionResolveTypeNew',
        r'AExgmModifierCollisionResolveTypeReplace',
        r'resolveType',
        callCustom=True
    )

    cmds.editorTemplate(
        r'deformationPreserved',
        label=maya.stringTable[u'y_xgenm_ui_ae_xgmModifierCollisionTemplate.kPreserveDeformation' ],
        addControl=True
    )
    cmds.editorTemplate(endLayout=True)

    # Collision Objects Attributes
    cmds.editorTemplate(
        beginLayout=maya.stringTable[u'y_xgenm_ui_ae_xgmModifierCollisionTemplate.kCollisionObjects' ],
        collapse=False
    )
    cmds.editorTemplate(
        r'AExgmModifierCollisionCollidersNew',
        r'AExgmModifierCollisionCollidersReplace',
        r'collider',
        callCustom=True
    )
    cmds.editorTemplate(addSeparator=True)
    cmds.editorTemplate(endLayout=True)

    # Add derived attributes
    mel.eval(r'AEdependNodeTemplate ' + nodeName)

    # Add dynamic attributes
    cmds.editorTemplate(addExtraControls=True)

    # End xgmModifierCollision Attribute Editor template
    cmds.editorTemplate(endScrollLayout=True)


class _CollidersControlItemDelegate(QItemDelegate):
    '''Delegation for specifying item height'''

    def sizeHint(self, option, index):
        size = super(_CollidersControlItemDelegate, self).sizeHint(option, index)
        size.setHeight(DpiScale(25))

        return size


def __createCollidersControl():
    '''Create a QTreeWidget for Colliders'''

    # Get QWidget of the current Maya layout.
    parentPtr = long_type(omui.MQtUtil.getCurrentParent())
    parentWidget = wrapInstance(parentPtr, QWidget)

    treeUI = QTreeWidget(parentWidget)
    treeUI.setItemDelegate(_CollidersControlItemDelegate())
    treeUI.setObjectName(r'CollidersControl')
    treeUI.setUniformRowHeights(True)
    treeUI.setExpandsOnDoubleClick(False)
    treeUI.setEditTriggers(QAbstractItemView.NoEditTriggers)
    treeUI.setDragDropMode(QAbstractItemView.InternalMove)
    treeUI.setAllColumnsShowFocus(True)
    treeUI.setColumnCount(TREE_COLUMN_COUNT)
    treeUI.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    treeUI.setSelectionMode(QAbstractItemView.ExtendedSelection)

    # Set header view
    headerView = treeUI.header()
    headerView.setFixedHeight(DpiScale(25))
    headerView.setStretchLastSection(False)
    headerView.setSectionResizeMode(TREE_COLUMN_PLACEHOLDER, QHeaderView.Fixed)
    headerView.setSectionResizeMode(TREE_COLUMN_ENABLE, QHeaderView.Fixed)
    headerView.setSectionResizeMode(TREE_COLUMN_OBJECT_NAME, QHeaderView.Stretch)
    headerView.setSectionResizeMode(TREE_COLUMN_FLIP_NORMAL, QHeaderView.Fixed)
    headerView.hideSection(TREE_COLUMN_PLACEHOLDER)
    headerView.resizeSection(TREE_COLUMN_ENABLE, DpiScale(60))
    headerView.resizeSection(TREE_COLUMN_FLIP_NORMAL, DpiScale(80))
    headerView.setStyleSheet(TreeWidgetHeaderFlatStyle)

    # Set header text
    headerItem = QTreeWidgetItem()
    headerItem.setText(TREE_COLUMN_ENABLE, maya.stringTable[u'y_xgenm_ui_ae_xgmModifierCollisionTemplate.kColliderEnable' ])
    headerItem.setTextAlignment(TREE_COLUMN_ENABLE, QtCore.Qt.AlignCenter)
    headerItem.setText(TREE_COLUMN_OBJECT_NAME, maya.stringTable[u'y_xgenm_ui_ae_xgmModifierCollisionTemplate.kColliderObjectName' ])
    headerItem.setTextAlignment(TREE_COLUMN_OBJECT_NAME, QtCore.Qt.AlignCenter)
    headerItem.setText(TREE_COLUMN_FLIP_NORMAL, maya.stringTable[u'y_xgenm_ui_ae_xgmModifierCollisionTemplate.kColliderFlipNormal' ])
    headerItem.setTextAlignment(TREE_COLUMN_FLIP_NORMAL, QtCore.Qt.AlignCenter)
    treeUI.setHeaderItem(headerItem)

    # Save the parent layout so we don't lose it
    treeUI.setProperty(r'xgenCollidersControlFullName', cmds.setParent(q=True))

    # Set background color for treewidget
    # Enable alternating colors: dark(default) - 54, 54, 54  bright - 64, 64, 64
    palette = treeUI.palette()
    treeUI.setAlternatingRowColors(True)
    palette.setColor(palette.AlternateBase, QColor(64, 64, 64))   
    treeUI.setPalette(palette)

    return omui.MQtUtil.addWidgetToMayaLayout(
        long_type(getCppPointer(treeUI)[0]), parentPtr)


def __findCollidersControl():
    '''Find colliders control'''

    treeUIPtr = long_type(omui.MQtUtil.findControl(r'CollidersControl'))
    treeUI = wrapInstance(treeUIPtr, QTreeWidget)

    return treeUI


def __getNextColliderLogicalIndex(nodeAttr):
    '''Get next available logical index for collider connection'''

    indices = cmds.getAttr(nodeAttr, multiIndices=True)
    nextIndex = max(indices) + 1 if indices else 0

    return nextIndex


def __OnCollidersButtonAddPressed(*args):
    '''Callback to be used when add collider button is pressed'''
    treeUI = __findCollidersControl()

    nodeAttr = treeUI.headerItem().text(TREE_COLUMN_PLACEHOLDER)

    colliders = []
    for i in range(treeUI.topLevelItemCount()):
        colliders.append(treeUI.topLevelItem(i).text(TREE_COLUMN_PLACEHOLDER))

    # Expand set selection
    # cmds.select(replace=True, noExpand=False)

    objectsSelectedInScene = cmds.ls(selection=True, objectsOnly=True)

    # Filter out objects with no mesh child
    shapesSelectedInScene = cmds.listRelatives(
        *objectsSelectedInScene,
        shapes=True,
        noIntermediate=True,
        type=r'mesh',
        path=True
    )

    # Avoid adding existing colliders
    existingMeshSet = set([__getConnectedMesh(collider) for collider in colliders])

    if shapesSelectedInScene:
        shapesToAdd = [
            shape for shape in shapesSelectedInScene if
                cmds.listRelatives(shape, parent=True)[0] not in existingMeshSet
        ]

        for shape in shapesToAdd:
            index = __getNextColliderLogicalIndex(nodeAttr)
            fromAttr = r'%s.worldMesh' % shape
            toAttr = r'%s[%d].colliderMesh' % (nodeAttr, index)
            cmds.connectAttr(fromAttr, toAttr)


def __disconnectPlug(plug):
    '''Disconnect incoming connection from plug'''

    connections = cmds.listConnections(
        plug,
        source=True,
        plugs=True
    )
    if connections:
        cmds.disconnectAttr(connections[0], plug)


def __disconnectCollider(collider):
    '''Disconnect specified collider'''

    __disconnectPlug(r'%s.colliderMesh' % collider)
    __disconnectPlug(r'%s.colliderMatrix' % collider)


def __OnCollidersButtonRemovePressed(*args):
    '''Callback to be used when remove collider button is pressed'''

    treeUI = __findCollidersControl()

    colliders = []
    for i in range(treeUI.topLevelItemCount()):
        colliders.append(treeUI.topLevelItem(i).text(TREE_COLUMN_PLACEHOLDER))

    collidersSelectedInModifier = set(
        [item.text(TREE_COLUMN_PLACEHOLDER) for item in treeUI.selectedItems()]
    )

    objectsSelectedInScene = set(cmds.ls(selection=True, objectsOnly=True))

    for collider in colliders:
        if (
            collider in collidersSelectedInModifier or
            __getConnectedMesh(collider) in objectsSelectedInScene
        ):
            __disconnectCollider(collider)


class _ClickableCheckBoxItemWidget(CheckBoxItemWidget):
    '''Centered checkbox widget with the added ability of specific a state changed callback'''

    def __init__(self, parent):
        super(_ClickableCheckBoxItemWidget, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, False)

    def setStateChangedCallback(self, onStateChanged):
        self.widget.stateChanged.connect(onStateChanged)


def __OnCheckBoxStateChanged(colliderAttr, childAttr):
    '''Callback to be used when checkbox state changes'''

    def wrapped(state):
        # Only setAttr when not in callback, in case of infinite loop
        if not globals()[r'__inColliderAttrChangedCallback']:
            cmds.setAttr(
                r"%s.%s" % (colliderAttr, childAttr),
                True if state == QtCore.Qt.Checked else False
            )

    return wrapped


def __getConnectedMesh(collider):
    '''Get connected mesh from a collider'''

    connections = cmds.listConnections(
        r'%s.colliderMesh' % collider,
        source=True,
        type=r'mesh',
        shapes=False
    )

    return connections[0] if connections else None


def __getCollidersList(nodeAttr):
    '''Gather infomation to be used for displaying in the colliders list'''

    colliders = []
    indices = cmds.getAttr(nodeAttr, multiIndices=True)
    indices = indices if indices else []
    for index in indices:
        colliderAttr = r'%s[%d]' % (nodeAttr, index)
        enabled = cmds.getAttr(r'%s.colliderEnabled' % colliderAttr)
        normalFlipped = cmds.getAttr(r'%s.colliderNormalFlipped' % colliderAttr)
        connectedMesh = __getConnectedMesh(colliderAttr)

        # colliderMesh connection should always be valid, else we might be in an
        # intermediate state
        if connectedMesh:
            colliders.append((index, colliderAttr, enabled, connectedMesh, normalFlipped))

    return colliders


def __updateCollidersControl(nodeAttr, treeUI):
    '''Update the colliders control'''

    cmds.setUITemplate(r'attributeEditorTemplate', pushTemplate=True)

    treeUI.clear()

    # Store nodeAttr in header's placeholder column
    treeUI.headerItem().setText(TREE_COLUMN_PLACEHOLDER, nodeAttr)

    for collider in __getCollidersList(nodeAttr):
        index, colliderAttr, enabled, objectName, normalFlipped = collider

        item = QTreeWidgetItem()
        treeUI.addTopLevelItem(item)

        colliderAttr = r'%s[%d]' % (nodeAttr, index)
        item.setText(TREE_COLUMN_PLACEHOLDER, colliderAttr)

        checkBoxWidget = _ClickableCheckBoxItemWidget(treeUI)
        checkBoxWidget.setCheckState(QtCore.Qt.Checked if enabled else QtCore.Qt.Unchecked)
        checkBoxWidget.setStateChangedCallback(
            __OnCheckBoxStateChanged(colliderAttr, r'colliderEnabled')
        )

        # Set background color for checkboxwidget
        palette = checkBoxWidget.palette()
        palette.setColor(palette.Base, QColor(16, 16, 16))
        checkBoxWidget.setPalette(palette)

        treeUI.setItemWidget(item, TREE_COLUMN_ENABLE, checkBoxWidget)

        item.setText(TREE_COLUMN_OBJECT_NAME, objectName)

        checkBoxWidget = _ClickableCheckBoxItemWidget(treeUI)
        checkBoxWidget.setCheckState(QtCore.Qt.Checked if normalFlipped else QtCore.Qt.Unchecked)
        checkBoxWidget.setStateChangedCallback(
            __OnCheckBoxStateChanged(colliderAttr, r'colliderNormalFlipped')
        )
        # Set background color for checkboxwidget
        palette = checkBoxWidget.palette()
        palette.setColor(palette.Base, QColor(16, 16, 16))
        checkBoxWidget.setPalette(palette)

        treeUI.setItemWidget(item, TREE_COLUMN_FLIP_NORMAL, checkBoxWidget)

    cmds.setUITemplate(popTemplate=True)


def __OnColliderAttrChanged(nodeAttr, treeUI):
    '''Callback to be used when collider attr changes'''

    def wrapped():
        globals()[r'__inColliderAttrChangedCallback'] = True
        __updateCollidersControl(nodeAttr, treeUI)
        globals()[r'__inColliderAttrChangedCallback'] = False

    return wrapped


def AExgmModifierCollisionCollidersNew(nodeAttr):
    '''Create the UI template for Collision Objects Attributes'''

    cmds.setUITemplate(r'attributeEditorTemplate', pushTemplate=True)

    # Form layout
    cmds.formLayout(r'collidersForm', numberOfDivisions=100)

    buttonWidth = 138
    buttonHeight = 25
    margin = 5

    # Button - "Add Selected Objects"
    cmds.button(
        r'uiColliderButtonAdd',
        label=maya.stringTable[u'y_xgenm_ui_ae_xgmModifierCollisionTemplate.kButtonAddColliders' ],
        width=buttonWidth,
        height=buttonHeight,
        command=__OnCollidersButtonAddPressed
    )

    # Button - "Remove Selected Objects"
    cmds.button(
        r'uiColliderButtonRemove',
        label=maya.stringTable[u'y_xgenm_ui_ae_xgmModifierCollisionTemplate.kButtonRemoveColliders' ],
        width=buttonWidth,
        height=buttonHeight,
        command=__OnCollidersButtonRemovePressed
    )

    collidersControl = __createCollidersControl()

    # Save control name for usage in AExgmModifierCollisionCollidersReplace()
    globals()[r'__collidersControl'] = collidersControl

    cmds.formLayout(
        r'collidersForm',
        edit=True,
        attachForm=[
            (r'uiColliderButtonAdd', r'top', margin),
            (r'uiColliderButtonAdd', r'left', margin),
            (r'uiColliderButtonRemove', r'top', margin),
            (collidersControl, r'left', margin),
            (collidersControl, r'bottom', margin),
            (collidersControl, r'right', margin),
        ],
        attachControl=[
            (r'uiColliderButtonRemove', r'left', margin, r'uiColliderButtonAdd'),
            (collidersControl, r'top', margin, r'uiColliderButtonAdd'),
        ],
        attachNone=[
            (r'uiColliderButtonAdd', r'bottom'),
            (r'uiColliderButtonAdd', r'right'),
            (r'uiColliderButtonRemove', r'bottom'),
            (r'uiColliderButtonRemove', r'right'),
        ]
    )

    # End Form Layout
    cmds.setParent(r'..')

    cmds.setUITemplate(popTemplate=True)

    # Update UI and wire controls
    AExgmModifierCollisionCollidersReplace(nodeAttr)


def AExgmModifierCollisionCollidersReplace(nodeAttr):
    '''Replace UI content when AE needs to get updated'''

    treeUI = __findCollidersControl()
    __updateCollidersControl(nodeAttr, treeUI)

    cmds.scriptJob(
        attributeChange=[
            nodeAttr,
            __OnColliderAttrChanged(nodeAttr, treeUI)
        ],
        disregardIndex=True,
        allChildren=True,
        replacePrevious=True,
        parent=globals()[r'__collidersControl']
    )


def __smoothFactorSliderDragged(newValue):
    cmds.setAttr(
        r'collision.sigma',
        newValue
    )


def __OnCollisionSigmaChanged():
    newValue = cmds.getAttr(r'collision.sigma')
    cmds.intSliderGrp(
        r'sigma',
        edit = True,
        value = newValue
    )


def AExgmModifierCollisionResolveTypeNew(nodeAttr):
    '''Create the UI template for Collision Objects Attributes'''

    cmds.setUITemplate(r'attributeEditorTemplate', pushTemplate=True)

    # Form layout
    cmds.formLayout(r'collisionForm', numberOfDivisions=100)

    cmds.intSliderGrp(
        r'sigma',
        label = maya.stringTable[u'y_xgenm_ui_ae_xgmModifierCollisionTemplate.kSmoothFactor' ],
        field = True,
        minValue = 0,
        maxValue = 3,
        value = 1,
        fieldStep = 1
    )

    cmds.formLayout(
        r'collisionForm',
        edit=True,
        attachForm=[
            (r'sigma', r'right', 0),
            (r'sigma', r'left', 0),
        ],
        attachControl=[
        ]
    )

    cmds.setParent(r'..')

    cmds.setUITemplate(popTemplate=True)

    # Update UI and wire controls
    AExgmModifierCollisionResolveTypeReplace(nodeAttr)
    

def AExgmModifierCollisionResolveTypeReplace(nodeAttr):
    '''Replace UI content when AE needs to get updated'''

    resolveAttrValue = cmds.getAttr(nodeAttr)
    if resolveAttrValue:
        radioGrpIdx = 2
    else:
        radioGrpIdx = 1

    flexibleCmd = r'cmds.setAttr("%s", 0); cmds.intSliderGrp("sigma", edit=True, enable=1)'
    stiffCmd = r'cmds.setAttr("%s", 1); cmds.intSliderGrp("sigma", edit=True, enable=0)'

    cmds.intSliderGrp(
        r'sigma',
        edit = True,
        dragCommand = __smoothFactorSliderDragged
    )

    resolveAttrValue = cmds.getAttr(nodeAttr)
    if resolveAttrValue:
        cmds.intSliderGrp(r'sigma', edit=True, enable=0)
        
    else:
        cmds.intSliderGrp(r'sigma', edit=True, enable=1)

    cmds.scriptJob(
        attributeChange = [
            r'collision.sigma',
            __OnCollisionSigmaChanged
            ]
        )


# ===========================================================================
# Copyright 2021 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
