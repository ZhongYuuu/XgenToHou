import maya
maya.utils.loadStringResourcesForModule(__name__)

pysideVersion = r'-1'

import PySide2, PySide2.QtCore, PySide2.QtGui, PySide2.QtWidgets
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from shiboken2 import wrapInstance
pysideVersion = PySide2.__version__

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om
import maya.OpenMayaUI as omui

import xgenm as xg
import xgenm.xgGlobal as xgg
import xgenm.xgLog as xglog
from xgenm.ui.widgets import *
from xgenm.ui.xgConsts import *
from xgenm.ui.xgIgSplineEditorTreeModel import IgSplineEditorTreeModel
from xgenm.ui.xgIgSplineEditorTreeView import IgSplineEditorTreeView
from xgenm.ui.util.xgIgSplineUtil import *
from xgenm.ui.util.xgUtil import *
import sys

import traceback

long_type = int if sys.version_info[0] >= 3 else long

'''
    XGen Interactive Groom Spline Editor
'''
class IgSplineEditor(QWidget):

    # Child widgets
    menuBar     = None
    tabBar      = None
    treeView    = None
    treeModel   = None

    # Current description (MDagPath to shape)
    descriptionDagPath      = None

    # Signals
    newModifierRequested        = QtCore.Signal(str)
    newLayerRequested           = QtCore.Signal()
    newGroupRequested           = QtCore.Signal()
    deleteRequested             = QtCore.Signal()
    duplicateRequested          = QtCore.Signal()
    moveRequested               = QtCore.Signal(int)
    currentDescriptionChanged   = QtCore.Signal()

    def __init__(self, parent=None):
        ''' Constructor '''
        QWidget.__init__(self, parent)
        self.descriptionDagPath = om.MDagPath()

        # Create child widgets
        self.__createMenuBar()
        self.__createTabBar()
        self.__createTreeView()
        self.__connectSignals()

        # Create the main layout
        layout = QVBoxLayout()
        QLayoutItem.setAlignment(layout, Qt.AlignTop)

        # Layout child widgets
        layout.addWidget(self.menuBar)
        layout.addWidget(self.tabBar)
        layout.addWidget(self.treeView)
        self.setLayout(layout)

        # QWidget properties
        self.setMinimumWidth(DpiScale(450))

    def __createMenuBar(self):
        ''' Create the menu bar on the top of the widget '''
        self.menuBar = QMenuBar()
        self.menuBar.setNativeMenuBar(False)

        # Edit menu
        editMenu = self.menuBar.addMenu(maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kEditMenu'])
        editMenu.addAction(
            maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kEditMenuGroup'],
            lambda: self.newGroupRequested.emit())
        editMenu.addSeparator()
        editMenu.addAction(
            maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kEditMenuDuplicate'],
            lambda: self.duplicateRequested.emit())
        editMenu.addSeparator()
        editMenu.addAction(
            maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kEditMenuDelete'],
            lambda: self.deleteRequested.emit())

        # Create menu
        createMenu = self.menuBar.addMenu(maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kCreateMenu'])
        createMenu.addAction(
            maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kCreateMenuInteractiveGroomSplines'],
            lambda: self.__doCreateSplineDescription())
        createMenu.addSeparator()
        self.__createAddModifierMenu(
            createMenu.addMenu(maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kCreateMenuAddModifier']))
        createMenu.addAction(
            maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kCreateMenuAddSculptLayer'],
            lambda: self.newLayerRequested.emit())

        # Select menu
        selectMenu = self.menuBar.addMenu(maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kSelectMenu' ])
        selectMenu.addAction(
            maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kCreateMenuSelectSplineOnFace' ],
            lambda: cmds.XgmSplineSelectReplaceBySelectedFaces())
        selectMenu.addAction(
            maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kCreateMenuFreezeSelected' ],
            lambda: cmds.XgmSplineSelectConvertToFreeze())

        # Descriptions menu
        descriptionsMenu = self.menuBar.addMenu(maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kDescriptionsMenu'])
        descriptionsMenu.addAction(
            maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kDescriptionsMenuTransfer'],
            lambda: self.__doTransferSplineDescription())

        # Descriptions -> Preset menu
        presetMenu = descriptionsMenu.addMenu(maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kPresetMenu' ])
        presetMenu.addAction(
            maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kPresetMenuImport' ],
            cmds.XgmSplinePresetImport)
        presetMenu.addAction(
            maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kPresetMenuExport' ],
            cmds.XgmSplinePresetExport)

        # Descriptions -> Cache menu
        cacheMenu = descriptionsMenu.addMenu(maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kCacheMenu'])
        cacheMenu.addAction(
            CreateIcon(r':/createCache.png'),
            maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kCacheMenuCreateNewCache'],
            lambda: cmds.XgmSplineCacheCreate())
        cacheMenu.addAction(
            CreateIcon(r':/importCache.png'),
            maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kCacheMenuImportCache'],
            lambda: cmds.XgmSplineCacheImport())
        cacheMenu.addAction(
            CreateIcon(r':/exportCache.png'),
            maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kCacheMenuExportCache'],
            lambda: cmds.XgmSplineCacheExport())
        cacheMenu.addSeparator()
        cacheMenu.addAction(
            CreateIcon(r':/disableAllCaches.png'),
            maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kCacheMenuDisableAllCache'],
            lambda: cmds.XgmSplineCacheDisableSelectedCache())
        cacheMenu.addAction(
            CreateIcon(r':/enableAllCaches.png'),
            maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kCacheMenuEnableAllCache'],
            lambda: cmds.XgmSplineCacheEnableSelectedCache())
        cacheMenu.addSeparator()
        cacheMenu.addAction(
            CreateIcon(r':/replaceCache.png'),
            maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kCacheMenuReplaceCache'],
            lambda: cmds.XgmSplineCacheReplace())
        cacheMenu.addAction(
            CreateIcon(r':/deleteCache.png'),
            maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kCacheMenuDeleteCache'],
            lambda: cmds.XgmSplineCacheDelete())
        cacheMenu.addAction(
            CreateIcon(r':/deleteCacheHistory.png'),
            maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kCacheMenuDeleteNodesAheadOfCache'],
            lambda: cmds.XgmSplineCacheDeleteNodesAhead())

        # Help menu
        helpMenu = self.menuBar.addMenu(maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kHelpMenu'])
        helpMenu.addAction(
            maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kHelpMenuHelpOnXGen'],
            lambda: cmds.showHelp(r'InteractiveGroomEditor'))

    def __createTabBar(self):
        ''' Create a utility tab bar under the menu bar '''
        self.tabBar = QWidget()

        # Container for buttons on the left
        container = ToolBarUI(QSize(20, 20), 2)

        # Add Modifier button
        button = container.addButton(r':/newLayerEmpty.png',
            maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kTabAddModifierTip'],
            lambda: None)
        text   = maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kTabAddModifier']
        button.setText(text)
        button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        button.setMinimumSize(ToolButtonSizeHint(button, TabToolButtonSize, rightText=text))
        button.setStyleSheet(ToolButtonPushFlatStyle)

        # Attach a menu to the button with a list of modifiers
        buttonMenu = QMenu()
        self.__createAddModifierMenu(buttonMenu)
        button.setPopupMode(QToolButton.InstantPopup)
        button.myMenu = buttonMenu # Keep a reference to the QMenu
        button.setMenu(buttonMenu)

        # Add Sculpt Layer button
        button = container.addButton(r':/newLayerEmpty.png',
            maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kTabAddSculptLayerTip'],
            lambda: self.newLayerRequested.emit())
        text   = maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kTabAddSculptLayer']
        button.setText(text)
        button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        button.setMinimumSize(ToolButtonSizeHint(button, TabToolButtonSize, rightText=text))
        button.setStyleSheet(ToolButtonPushFlatStyle)

        # Stretchable space
        container.layout().setSizeConstraint(QLayout.SetNoConstraint)
        container.layout().addSpacing(DpiScale(20))
        container.layout().addStretch()

        # Move up button
        button = container.addButton(r':/moveLayerUp.png',
            maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kTabMoveUpTip'],
            lambda: self.moveRequested.emit(1))
        button.setMinimumSize(ToolButtonSizeHint(button, TabToolButtonSize))
        button.setStyleSheet(ToolButtonFlatStyle)

        # Move down button
        button = container.addButton(r':/moveLayerDown.png',
            maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kTabMoveDownTip'],
            lambda: self.moveRequested.emit(-1))
        button.setMinimumSize(ToolButtonSizeHint(button, TabToolButtonSize))
        button.setStyleSheet(ToolButtonFlatStyle)

        # Add Sculpt Group button
        button = container.addButton(r':/folder-new.png',
            maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kTabAddSculptGroupTip'],
            lambda: self.newGroupRequested.emit())
        button.setMinimumSize(ToolButtonSizeHint(button, TabToolButtonSize))
        button.setStyleSheet(ToolButtonFlatStyle)

        # Delete button
        button = container.addButton(r':/trash.png',
            maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kTabDeleteTip'],
            lambda: self.deleteRequested.emit())
        button.setMinimumSize(ToolButtonSizeHint(button, TabToolButtonSize))
        button.setStyleSheet(ToolButtonFlatStyle)

        # Create the layout
        layout = QHBoxLayout()
        layout.setSpacing(DpiScale(0))
        layout.setContentsMargins(DpiScale(0), DpiScale(0), DpiScale(0), DpiScale(0))

        # Layout the widgets
        layout.addWidget(container)
        self.tabBar.setLayout(layout)

    def __createAddModifierMenu(self, menu):
        ''' Populate the menu to show a list of available modifiers '''

        for nodeType in getSplineModifierTypes():

            # UI Nice Name and Icon of the modifier
            niceName = getSplineNodeNiceName(nodeType)
            icon     = CreateIcon(getSplineModifierIcon(nodeType))
            
            # Add a menu item for the specific modifier
            menu.addAction(icon, niceName,
                lambda nodeType=nodeType: self.newModifierRequested.emit(nodeType))

    def __createTreeView(self):
        ''' Create the main tree widget '''
        self.treeModel = IgSplineEditorTreeModel()
        self.treeView  = IgSplineEditorTreeView(self.treeModel)

    def __connectSignals(self):
        ''' Connect signals between child widgets '''
        self.newModifierRequested.connect(self.treeModel.addModifier)
        self.newLayerRequested.connect(self.treeModel.addLayer)
        self.newGroupRequested.connect(self.treeModel.addGroup)
        self.duplicateRequested.connect(self.treeModel.duplicateItem)
        self.moveRequested.connect(self.treeModel.moveItem)
        self.deleteRequested.connect(self.treeModel.deleteItem)

    def __doCreateSplineDescription(self):
        ''' Create an XGen spline description from the selection '''

        # Check for the current selection before calling the command
        selectedMeshes = mel.eval(r'listRelatives -children -type mesh -noIntermediate `ls -sl`')

        # Check for shape or component selections
        if not selectedMeshes:
            selectedMeshes = mel.eval(r'ls -sl -o -type mesh')

        if not selectedMeshes:
            xglog.XGTip(maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kCreateNoMeshSelected'])
            return

        # Show the UI
        try:
            cmds.XgmCreateInteractiveGroomSplinesOption()
        except:
            traceback.print_exc()

    def __doTransferSplineDescription(self):
        ''' Transfer an XGen spline description '''

        # Check for the current selection before calling the command
        selectedObjects = mel.eval(r'ls -sl')
        selectedMeshes = mel.eval(r'listRelatives -shapes -type mesh -noIntermediate `ls -sl`')
        selectedDescriptions = mel.eval(r'listRelatives -shapes -type xgmSplineDescription -noIntermediate `ls -sl`')
        selectedMeshesShape = mel.eval(r'ls -sl -type mesh')
        selectedDescriptionsShape = mel.eval(r'ls -sl -type xgmSplineDescription')
        
        bInvalidSelectedObjects = not selectedObjects or len(selectedObjects) != 2
        bInvalidSelectedMeshes = (not selectedMeshes or len(selectedMeshes) != 1) and (not selectedMeshesShape or len(selectedMeshesShape) != 1)
        bInvalidSelectedDescriptions = (not selectedDescriptions or len(selectedDescriptions) != 1) and (not selectedDescriptionsShape or len(selectedDescriptionsShape) != 1)
        if (bInvalidSelectedObjects or bInvalidSelectedMeshes or bInvalidSelectedDescriptions):
            xglog.XGTip(maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kTransferNoSelection'])
            return

        # Execute the command
        try:
            cmds.xgmGroomTransfer()
        except:
            traceback.print_exc()

    def detachMe(self):
        ''' Remove the widget from its parent's children list '''
        self.setParent(None)

    def refresh(self):
        ''' Refresh the content of the editor '''
        self.treeModel.refresh()

    def currentDescription(self, shape=False):
        ''' Return the name of the current descripton '''
        if (self.descriptionDagPath.isValid()
                and om.MObjectHandle(self.descriptionDagPath.node()).isValid()):
            if shape:
                # Return the name of the shape node
                return self.descriptionDagPath.partialPathName()
            else:
                # Return the name of the transform node
                dagPath = om.MDagPath(self.descriptionDagPath)
                dagPath.pop()
                return dagPath.partialPathName()
        # No current description
        return r''

    def getCurrentDescriptionPath(self):
        ''' Return the MDagPath of the current description shape '''
        return self.descriptionDagPath

    def setCurrentDescription(self, path):
        ''' Set the current description by the specified full path '''

        # Get the MDagPath to the description shape node
        dagPath = om.MDagPath()
        try:
            sl = om.MSelectionList()
            sl.add(path)
            sl.getDagPath(0, dagPath)
        except:
            dagPath = om.MDagPath()

        # Not a valid path ?
        if not dagPath.isValid():
            return

        # Not a spline description shape ?
        if not isSplineDescriptionNode(dagPath.node()):
            return

        # No changes ?
        if self.descriptionDagPath == dagPath:
            return

        # Set the current description to the specified path
        self.descriptionDagPath = dagPath
        self.currentDescriptionChanged.emit()


'''
    Create Interactive Groom Spline Editor Window. This is the global method
    that is exposed to xgui module. e.g. xgui.createIgSplineEditor()

    restore is True when the method is invoked as workspace callback script.
'''
def createIgSplineEditor(restore=False):
    # Constants
    igSplineDockControlName  = r'XGenIgSplineDockWidget'
    igSplineEditorObjectName = r'XGenIgSplineEditorWidget'
    igIntialWidthValue = r'workspacesWidePanelInitialWidth'

    # One-time initialization of the main widget
    if xgg.IgSplineEditor is None:
        # Create the main interactive groom spline editor widget
        with MayaWaitCursor():
            xgg.IgSplineEditor = IgSplineEditor()
            xgg.IgSplineEditor.setObjectName(igSplineEditorObjectName)
            xgg.IgSplineEditor.refresh()

        # This will happen when someone manually delete the main widget without
        # deleting the owner dock control. Most likely for debugging purpose.
        if not restore:
            # We don't want to raise a control with invalid content so we
            # delete previous control.
            if cmds.workspaceControl(igSplineDockControlName, q=True, ex=True):
                cmds.deleteUI(igSplineDockControlName)

    # Use workspaceControl command to hold the main widget
    if restore:
        # Get the layout of the parent workspace control and the main widget
        parent = omui.MQtUtil.getCurrentParent()
        widget = omui.MQtUtil.findControl(igSplineEditorObjectName)

        # Add the main widget to the workspace control layout
        omui.MQtUtil.addWidgetToMayaLayout(long_type(widget), long_type(parent))

        # Maya workspace control should never delete its content widget when
        # retain flag is true. But it still deletes in certain cases. We avoid
        # deleting the global widget by removing it from its parent's children.
        # destroyed signal is emitted right before deleting children.
        parentWidget = wrapInstance(long_type(parent), QWidget)
        if parentWidget:
            parentWidget.destroyed.connect(xgg.IgSplineEditor.detachMe)
    else:
        # Create the workspace control from Maya menu
        if cmds.workspaceControl(igSplineDockControlName, q=True, ex=True):
            # Raise the workspace control if exists
            cmds.workspaceControl(igSplineDockControlName, e=True, vis=True, r=True, 
                initialWidth=cmds.optionVar( q=igIntialWidthValue ),
                minimumWidth=cmds.optionVar( q=igIntialWidthValue ))
        else:
            # Create the workspace control
            LEcomponent = mel.eval(r'getUIComponentDockControl("Channel Box / Layer Editor", false);')
            cmds.workspaceControl(igSplineDockControlName, vis=True,
                requiredPlugin=r'xgenToolkit', tabToControl=(LEcomponent, -1),
                label=maya.stringTable[u'y_xgenm_ui_xgIgSplineEditor.kIgSplineEditorDockTitle'],
                uiScript=r'''# Load xgenToolkit plug-in and create the main widget
def xguiWorkspaceBootstrap():
    import maya.cmds as cmds
    if not cmds.pluginInfo('xgenToolkit', q=True, loaded=True):
        cmds.loadPlugin('xgenToolkit')
xguiWorkspaceBootstrap()
del xguiWorkspaceBootstrap
xgui.createIgSplineEditor(restore=True)''',
                initialWidth=cmds.optionVar( q=igIntialWidthValue ),
                minimumWidth=cmds.optionVar( q=igIntialWidthValue )
)
            cmds.workspaceControl(igSplineDockControlName, e=True, r=True)
# ===========================================================================
# Copyright 2021 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
