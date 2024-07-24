import maya
maya.utils.loadStringResourcesForModule(__name__)

from builtins import next
from builtins import range
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *

pysideVersion = '-1'
import PySide2
pysideVersion = PySide2.__version__

import xgenm as xg
import xgenm.xgGlobal as xgg
import xgenm.xgLog as xglog
from xgenm.ui.dialogs.xgIgSplineAddModifier import IgSplineAddModifierUI
from xgenm.ui.dialogs.xgIgSplineDeleteSharedModifier import IgSplineDeleteSharedModifierUI
from xgenm.ui.widgets import *
from xgenm.ui.xgConsts import *
from xgenm.ui.util.xgUtil import CreateIcon
from xgenm.ui.util.xgUtil import DpiScale
from xgenm.ui.util.xgUtil import MayaCmdsTransaction
from xgenm.ui.util.xgUtil import ToolButtonSizeHint
from xgenm.ui.util.xgIgSplineUtil import *

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om
import maya.OpenMayaUI as omui


'''
    Modifiers tab for Interactive Groom Splines
'''
class IgSplineModifierTabUI(QWidget):
    
    # Modifiers UI
    modifiersUI = None
    
    # Modifier Attributes UI
    modifierAttrUI = None

    def __init__(self, parent):
        ''' Constructor '''
        QWidget.__init__(self, parent)
        
        # --------------------------
        # | Modifiers              |
        # |------------------------|
        # | Modifier Attributes    |
        # --------------------------
        
        # Create the Modifiers UI
        self.modifiersUI = IgSplineModifiersUI()
        self.modifiersUI.setContentsMargins(DpiScale(8), DpiScale(0), DpiScale(8), DpiScale(0))
        
        # Frame Layout for the Modifiers UI
        modifiersFrameUI = ExpandUI(maya.stringTable[u'y_xgenm_ui_tabs_xgIgSplineModifierTab.kModifiers'], True)
        modifiersFrameUI.addWidget(self.modifiersUI)

        # Create the Modifier Attributes UI
        self.modifierAttrUI = IgSplineModifierAttrUI()
        self.modifierAttrUI.setContentsMargins(DpiScale(0), DpiScale(0), DpiScale(0), DpiScale(0))
        
        # Frame Layout for the Modifier Attribute UI
        modifierAttrFrameUI = ExpandUI(maya.stringTable[u'y_xgenm_ui_tabs_xgIgSplineModifierTab.kModifierAttributes'], True)
        modifierAttrFrameUI.addWidget(self.modifierAttrUI)

        # Connect Modifiers UI and Modifier Attributes UI together
        self.modifiersUI.modifierSelectionChanged.connect(self.__onCurrentModifierChanged)

        # Splitter between Modifiers UI and Modifier Attributes UI
        splitter = QSplitter(QtCore.Qt.Vertical)
        splitter.addWidget(modifiersFrameUI)
        splitter.addWidget(modifierAttrFrameUI)
        splitter.setSizes([DpiScale(50), DpiScale(800)])
        
        # Main layout of the Modifiers tab
        layout = QVBoxLayout()
        QLayoutItem.setAlignment(layout, QtCore.Qt.AlignTop)
        layout.setSpacing(DpiScale(0))
        layout.setContentsMargins(DpiScale(3), DpiScale(3), DpiScale(3), DpiScale(3))
        layout.addWidget(splitter)
        self.setLayout(layout)
        
    def refresh(self):
        ''' Update the UI from the description '''
        self.modifiersUI.refresh()
        self.modifierAttrUI.refresh()
        
    def __onCurrentModifierChanged(self, node):
        ''' Invoked when the current modifier has been changed '''
        self.modifierAttrUI.setNode(node)
    
'''
    Modifiers UI for Interactive Groom Splines
'''
class IgSplineModifiersUI(QWidget):
    
    # Toolbar
    toolbarUI = None
    
    # Modifiers List
    treeUI = None
    
    # Flags
    isUpdating = False
    
    # Script Jobs
    scriptJobs = []
    
    # Signals
    modifierSelectionChanged = QtCore.Signal(str)
    
    # Definition of the columns of the Modifiers List
    TREE_COLUMN_ENABLE     = 0
    TREE_COLUMN_LOCK       = 1
    TREE_COLUMN_REFRESH    = 2
    TREE_COLUMN_NAME       = 3
    TREE_COLUMN_ACTIVE     = 4
    TREE_COLUMN_COUNT      = 5
    
    # Roles
    TREE_ROLE_NAME         = QtCore.Qt.UserRole + 1
    
    # Icons
    TREE_ICON_NONE         = CreateIcon(r'')
    TREE_ICON_EYE          = CreateIcon(r':/eye.png')
    TREE_ICON_LOCK         = CreateIcon(r'xgLock.png')
    TREE_ICON_REFRESH      = CreateIcon(r':/clockwise.png')
    TREE_ICON_ACTIVE       = CreateIcon(r'xgActiveSculpt.png')
    TREE_ICON_EXPIRED      = CreateIcon(r':/SP_MessageBoxWarning.png')
    TREE_ICON_ON           = CreateIcon(r'xgVisOn.png')
    TREE_ICON_OFF          = CreateIcon(r'')
    TREE_ICON_ACTIVE_GREEN = CreateIcon(r'xgActiveGreen.png')

    # Brushes
    TREE_BRUSH_DISABLED    = QBrush(QColor(102,102,102))

    def __init__(self):
        ''' Constructor '''
        QWidget.__init__(self)
        
        # --------------------------
        # |                Toolbar |
        # |------------------------|
        # |  Modifier A            |
        # |  Modifier B            |
        # --------------------------
        
        # Create the Toolbar UI
        self.__createToolbar()
        
        # Create the Modifier List UI
        self.__createModifierList()
        
        # Main layout of the Modifiers UI
        layout = QVBoxLayout()
        QLayoutItem.setAlignment(layout, QtCore.Qt.AlignTop)
        layout.setSpacing(DpiScale(0))
        layout.setContentsMargins(DpiScale(3), DpiScale(3), DpiScale(3), DpiScale(3))
        layout.addWidget(self.toolbarUI)
        layout.addWidget(self.treeUI)
        self.setLayout(layout)
        
    def __createToolbar(self):
        ''' Create the Toolbar on the top of the widget '''
        buttonDescs = [
            (r'moveLayerUp',
             r':/moveLayerUp.png',
                maya.stringTable[u'y_xgenm_ui_tabs_xgIgSplineModifierTab.kMoveSelectedModifierUp'],
                lambda: self.__moveModifier(1)),
            (r'moveLayerDown',
             r':/moveLayerDown.png',
                maya.stringTable[u'y_xgenm_ui_tabs_xgIgSplineModifierTab.kMoveSelectedModifierDown'],
                lambda: self.__moveModifier(-1)),
            (r'newLayerEmpty',
             r':/newLayerEmpty.png',
                maya.stringTable[u'y_xgenm_ui_tabs_xgIgSplineModifierTab.kAddNewModifier'],
                lambda: self.__addModifier()),
            (r'smallTrash',
             r':/smallTrash.png',
                maya.stringTable[u'y_xgenm_ui_tabs_xgIgSplineModifierTab.kDeleteSelectedModifier'],
                lambda: self.__deleteModifier()),
            (r'refresh',
             r':/refresh.png',
                maya.stringTable[u'y_xgenm_ui_tabs_xgIgSplineModifierTab.kRefreshModifiers'],
                lambda: self.refresh()),
            (r'xgMenu',
             r'xgMenu.png',
                maya.stringTable[u'y_xgenm_ui_tabs_xgIgSplineModifierTab.kOpenModifierMenu'],
                lambda: self.__showContextMenu(QCursor.pos()))
            ]
        
        # Create the buttons on the Toolbar
        buttons = []
        for (toolName, icon, annot, slot) in buttonDescs:
            button = QToolButton()
            button.setFixedSize(DpiScale(24), DpiScale(24))
            button.setAutoRaise(True)
            button.setAccessibleName(toolName)
            button.setIcon(CreateIcon(icon))
            button.setIconSize(QSize(DpiScale(20), DpiScale(20)))
            button.setToolTip(annot)
            button.setStyleSheet(ToolButtonFlatStyle)
            button.clicked.connect(slot)
            buttons.append(button)
        
        # Main layout of the Toolbar, right-aligned
        layout = QHBoxLayout()
        layout.setSpacing(DpiScale(0))
        layout.setContentsMargins(DpiScale(0), DpiScale(0), DpiScale(0), DpiScale(0))
        layout.addStretch()
        for button in buttons:
            layout.addWidget(button)
        
        # Main widget to hold the buttons
        self.toolbarUI = QWidget()
        self.toolbarUI.setLayout(layout)
        self.toolbarUI.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed)
        
    def __createModifierList(self):
        ''' Create the Modifier List widget'''
        
        # Main widget to list the modifiers
        self.treeUI = QTreeWidget()
        self.treeUI.setRootIsDecorated(False)
        self.treeUI.setUniformRowHeights(True)
        self.treeUI.setExpandsOnDoubleClick(False)
        self.treeUI.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.treeUI.setDragDropMode(QAbstractItemView.InternalMove)
        self.treeUI.setAllColumnsShowFocus(True)
        self.treeUI.setColumnCount(self.TREE_COLUMN_COUNT)
        self.treeUI.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        if pysideVersion == '1.2.0' :
            self.treeUI.header().setResizeMode(QHeaderView.Fixed)
            self.treeUI.header().setResizeMode(self.TREE_COLUMN_NAME, QHeaderView.Stretch)
        else:
            self.treeUI.header().setSectionResizeMode(QHeaderView.Fixed)
            self.treeUI.header().setSectionResizeMode(self.TREE_COLUMN_NAME, QHeaderView.Stretch)

        self.treeUI.header().setDefaultSectionSize(DpiScale(20))
        self.treeUI.header().setStretchLastSection(False)
        
        # Remove the padding on the headers...
        self.treeUI.header().setStyleSheet(r'''
QHeaderView::section:horizontal
{
    border: 1px solid #2B2B2B;
    border-right-style: none;
    padding: 1px;
}
QHeaderView::section:horizontal::last
{
    border-right-style: solid;
}''')

        # Set the header text and icons
        header = QTreeWidgetItem()
        header.setIcon(self.TREE_COLUMN_ENABLE, self.TREE_ICON_EYE)
        header.setIcon(self.TREE_COLUMN_LOCK, self.TREE_ICON_LOCK)
        header.setText(self.TREE_COLUMN_NAME, maya.stringTable[u'y_xgenm_ui_tabs_xgIgSplineModifierTab.kName'])
        header.setTextAlignment(self.TREE_COLUMN_NAME, QtCore.Qt.AlignCenter)
        header.setIcon(self.TREE_COLUMN_ACTIVE, self.TREE_ICON_ACTIVE)
        self.treeUI.setHeaderItem(header)
        
        # Connect signals
        self.treeUI.currentItemChanged.connect(self.__onCurrentItemChanged)
        self.treeUI.itemClicked.connect(self.__onItemClicked)
        self.treeUI.itemDoubleClicked.connect(self.__onItemDoubleClicked)
        self.treeUI.itemPressed.connect(self.__onItemPressed)
        self.treeUI.itemChanged.connect(self.__onItemChanged)
        self.treeUI.customContextMenuRequested.connect(self.__onCustomContextMenuRequested)
        model = self.treeUI.model()
        model.rowsInserted.connect(self.__onRowsInserted)

        # Hide not implemented columns
        self.treeUI.hideColumn(self.TREE_COLUMN_LOCK)
        self.treeUI.hideColumn(self.TREE_COLUMN_REFRESH)
        
    def refresh(self):
        ''' Update the UI from the description '''
        
        # Save the current modifier dg node name
        prevModifier = self.__getCurrentModifier()
        
        try:
            self.isUpdating = True
            self.__refreshTreeUI()
        finally:
            self.isUpdating = False
    
        # Restore the previous modifier selection
        if len(prevModifier) > 0:
            matchItems = self.treeUI.findItems(prevModifier,
                QtCore.Qt.MatchFlag.MatchExactly, self.TREE_COLUMN_NAME)
            if len(matchItems) > 0:
                self.treeUI.setCurrentItem(matchItems[0])
        
        # If nothing is selected, select the first item
        if not self.treeUI.currentItem() and self.treeUI.topLevelItemCount() > 0:
            item = self.treeUI.topLevelItem(0)
            self.treeUI.setCurrentItem(item)
            
        # Update the highlight text color
        self.__updateTreeUIPalette(self.treeUI.currentItem())
        
        # Rehook the refresh callbacks
        self.__hookNodeConnectionChanges()
        
        # Signal the selection change
        currentModifier = self.__getCurrentModifier()
        if prevModifier != currentModifier:
            self.modifierSelectionChanged.emit(currentModifier)
            
    def __hookNodeConnectionChanges(self):
        ''' Register callbacks when the node or connection change '''

        # Kill any existing script jobs
        for jobId in self.scriptJobs:
            try:
                if cmds.scriptJob(exists=jobId):
                    cmds.scriptJob(kill=jobId)
            except:
                pass
        self.scriptJobs = []
        
        # Register script jobs for the nodes in the chain
        refreshCmd = r'xgg.DescriptionEditor.refresh("Full")'
        for sourcePlug, destinationPlug in self.__getModifierConnections():
            # Get the source node name
            sourceNode = sourcePlug[:sourcePlug.find(r'.')]

            # Connection Change (source)
            self.scriptJobs.append(cmds.scriptJob(con=[sourcePlug, refreshCmd]))

            # Mute Attribute Change
            try:
                self.scriptJobs.append(cmds.scriptJob(ac=[sourceNode + r'.mute', refreshCmd]))
            except:
                pass

            # Message Connection Change
            try:
                self.scriptJobs.append(cmds.scriptJob(con=[sourceNode + r'.message', refreshCmd]))
            except:
                pass

            # Node Name Change (Spline Description will take care of itself)
            self.scriptJobs.append(cmds.scriptJob(nnc=[sourceNode, refreshCmd]))
        
    def __refreshTreeUI(self):
        ''' Update the Modifiers View with the latest info from Maya DG '''

        # Drop all existing tree view items
        self.treeUI.clear()
        
        # Get the MDagPath of the current spline description
        dagPath = getCurrentSplineDescriptionDagPath()
        if not dagPath.isValid():
            xglog.XGDebug(maya.stringTable[u'y_xgenm_ui_tabs_xgIgSplineModifierTab.kNoActiveDescription'])
            return
        
        # Starting with the source of xgmSplineDescription.inSplineData plug
        plug = om.MFnDagNode(dagPath).findPlug(r'inSplineData').source()
        if plug.isNull():
            xglog.XGDebug(maya.stringTable[u'y_xgenm_ui_tabs_xgIgSplineModifierTab.kNoModifiersFound'])
            return
        
        # Recursively iterate the DG graph for a modifier chain
        while not plug.isNull() and isSplineModifierNode(plug.node()):
            self.__addTreeViewItem(plug.node())
            plug = findUpstreamSplinePlug(plug).source()
            
        # Mark the active sculpt modifier
        plug = om.MFnDagNode(dagPath).findPlug(r'activeSculpt').source()
        if not plug.isNull():
            matchItems = self.treeUI.findItems(om.MFnDependencyNode(plug.node()).name(),
                QtCore.Qt.MatchFlag.MatchExactly, self.TREE_COLUMN_NAME)
            if len(matchItems) > 0:
                matchItems[0].setIcon(self.TREE_COLUMN_ACTIVE, self.TREE_ICON_ACTIVE_GREEN)
                
    def __updateTreeUIPalette(self, current):
        ''' Update the palette of the Modifiers View '''

        palette = QPalette()

        # Update the highlight text color to the current color...
        # Qt uses a highlight text color instead of the foreground color
        if current:
            brush = current.foreground(self.TREE_COLUMN_NAME)
            if brush and brush.style() != QtCore.Qt.NoBrush:
                palette.setColor(QPalette.HighlightedText, brush.color())

        self.treeUI.setPalette(palette)
            
    def __addTreeViewItem(self, node):
        ''' Add a modifier to the Modifier View '''
        
        # Create a new tree view item for the modifier
        item = QTreeWidgetItem(self.treeUI)
        self.__updateTreeViewItem(node, item)
        
    def __updateTreeViewItem(self, node, item):
        ''' Update a modifier in the Modifier View '''
        dgNode = om.MFnDependencyNode(node)
        
        # Only allow to rename the node when it's in the master scene
        if not dgNode.isFromReferencedFile():
            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        else:
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
            
        # Not droppable
        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsDropEnabled)
        
        # Role to remember the modifier dg node name
        item.setData(0, self.TREE_ROLE_NAME, dgNode.name())
        
        # Lock
        #item.setIcon(self.TREE_COLUMN_LOCK, self.TREE_ICON_LOCK)
        
        # Refresh
        #item.setIcon(self.TREE_COLUMN_REFRESH, self.TREE_ICON_REFRESH)
        
        # Enable
        mute = dgNode.findPlug(r'mute').asBool()
        enableWidget = CheckBoxItemWidget(self.treeUI)
        if not mute:
            enableWidget.setCheckState(QtCore.Qt.Checked)
        else:
            enableWidget.setCheckState(QtCore.Qt.Unchecked)
        self.treeUI.setItemWidget(item, self.TREE_COLUMN_ENABLE, enableWidget)
        
        # Icon & Name
        icon = CreateIcon(getSplineModifierIcon(dgNode.typeName()))
        item.setIcon(self.TREE_COLUMN_NAME, icon)
        item.setText(self.TREE_COLUMN_NAME, dgNode.name())
        if not mute:
            item.setData(self.TREE_COLUMN_NAME, QtCore.Qt.ForegroundRole, None)
        else:
            item.setForeground(self.TREE_COLUMN_NAME, self.TREE_BRUSH_DISABLED)
        
        # Expired
        #item.setIcon(self.TREE_COLUMN_EXPIRED, self.TREE_ICON_EXPIRED)
        
    def __getCurrentModifier(self):
        ''' Return the dg node name of the current modifier '''
        
        # Get the current tree view item
        item = self.treeUI.currentItem()
        
        # No current item ?
        if not item:
            return r''
        
        return item.text(self.TREE_COLUMN_NAME)
        
    def __getModifierConnections(self):
        ''' Return an array of connections from description to base node '''
        connections = []
        
        # Get the MDagPath of the current spline description
        dagPath = getCurrentSplineDescriptionDagPath()
        if not dagPath.isValid():
            return connections
        
        # Starting with the xgmSplineDescription.outSplineData plug
        plug = om.MFnDagNode(dagPath).findPlug(r'outSplineData')
        if plug.isNull():
            return connections
        
        # Recursively iterate the DG graph for the node chain
        while not plug.isNull():
            # Go upstream
            destinationPlug = findUpstreamSplinePlug(plug)
            sourcePlug = destinationPlug.source()
            plug = sourcePlug
            # Add the connection (src,dst)
            if not destinationPlug.isNull() and not sourcePlug.isNull():
                pair = (sourcePlug.name(), destinationPlug.name())
                connections.append(pair)
            
        return connections
            
    def __internalDisconnectModifier(self, modifier):
        ''' Disconnect a modifier from the modifier chain '''
        
        # Get the modifier connections
        connections = self.__getModifierConnections()
        
        # Find the output connection of the modifier
        index = next((i for i in range(0, len(connections))
            if connections[i][0].startswith(modifier + r'.')), -1)
        
        # No such modifier ?
        if index < 0:
            raise RuntimeError(r'Internal error : %s not found in %s'
                % (modifier, str(connections)))
        
        # output = modifier.out -> other.in
        # This plug usually exists because we find the modifier by tracing
        # from the description node
        output = connections[index]
        
        # Find the input connection of the modifier
        input = None
        if index + 1 < len(connections):
            if connections[index + 1][1].startswith(modifier + r'.'):
                input = connections[index + 1]
        
        # Disconnect the modifier from the chain
        cmds.disconnectAttr(output[0], output[1])
        cmds.disconnectAttr(input[0], input[1])
        cmds.connectAttr(input[0], output[1])
        return (input[1], output[0])
        
    def __internalInsertModifier(self, inOut, modifier):
        ''' Insert a modifier to the modifier chain '''
        
        # Get the modifier connections
        connections = self.__getModifierConnections()
        
        # Find the input connection to insert before
        index = next((i for i in range(0, len(connections))
            if connections[i][1].startswith(modifier + r'.')), -1)
        
        # modifier to insert before does not exist ?
        if index < 0:
            raise RuntimeError(r'Internal error : %s not found in %s'
                % (modifier, str(connections)))
            
        # This is the insertion point
        insertion = connections[index]
            
        # Insert inOut to the modifier chain
        cmds.disconnectAttr(insertion[0], insertion[1])
        cmds.connectAttr(insertion[0], inOut[0])
        cmds.connectAttr(inOut[1], insertion[1])
        
    def __internalActivateSculptModifier(self, modifier):
        ''' Activate a sculpt modifier '''
            
        # Get the current description
        description = cmds.ls(xgg.DescriptionEditor.currentDescription(),
                                dag=True, type=r'xgmSplineDescription')
        
        # Already activated ?
        prev = cmds.listConnections(description[0] + r'.activeSculpt',
                destination=False, source=True, type=r'xgmModifierSculpt')
        if prev and len(prev) > 0 and prev[0] == modifier:
            return 

        # Connect sculpt.message to description.activeSculpt
        cmds.connectAttr(modifier + r'.message',
            description[0] + r'.activeSculpt',
            force=True)
        cmds.setToolTo(cmds.currentCtx())

    def __isModifierShared(self, modifier):
        ''' Return True if the specified modifier is shared among descriptions '''

        # Get the modifier connections
        connections = self.__getModifierConnections()

        # Find the output connection of the modifier
        index = next((i for i in range(0, len(connections))
            if connections[i][0].startswith(modifier + r'.')), -1)
        
        # No such modifier ?
        if index < 0:
            raise RuntimeError(r'Internal error : %s not found in %s'
                % (modifier, str(connections)))

        # output = modifier.out -> other.in
        # This plug usually exists because we find the modifier by tracing
        # from the description node
        output = connections[index]
        
        # Get the output MPlug from the plug name
        plug = om.MPlug()
        try:
            sl = om.MSelectionList()
            sl.add(output[0])
            sl.getPlug(0, plug)
        except:
            pass
        
        # Get the destinations of the connection
        plugList = om.MPlugArray()
        plug.destinations(plugList)

        # Shared Modifier Case #1 : Fan-out
        if plugList.length() > 1:
            return True
        
        # Shared Modifier Case #2 : Multi
        if plug.isElement():
            parentPlug = plug.array()
            if parentPlug.numConnectedElements() > 1:
                return True
        
        return False
    
    def __getNextSculptModifier(self, modifier):
        ''' Return the name of the next sculpt modifier '''

        # Get the modifier connections
        connections = self.__getModifierConnections()

        # Find the output connection of the modifier
        index = next((i for i in range(0, len(connections))
            if connections[i][0].startswith(modifier + r'.')), -1)
        
        # No such modifier ?
        if index < 0:
            raise RuntimeError(r'Internal error : %s not found in %s'
                % (modifier, str(connections)))
            
        for i in list(range(index + 1, len(connections))) + list(range(0, index)):
            plug = connections[i][0]
            node = plug[:plug.find(r'.')]
            if cmds.objectType(node, isAType=r'xgmModifierSculpt'):
                return node
        return r''
    
    def __isActiveSculptModifier(self, modifier):
        ''' Return True if the specified modifier is an active sculpt modifier '''
        
        # Get the current description
        description = cmds.ls(xgg.DescriptionEditor.currentDescription(),
                                dag=True, type=r'xgmSplineDescription')
        
        # Already activated ?
        prev = cmds.listConnections(description[0] + r'.activeSculpt',
                destination=False, source=True, type=r'xgmModifierSculpt')
        if prev and len(prev) > 0 and prev[0] == modifier:
            return True
        return False

    def __moveModifier(self, direction):
        ''' Move the modifier up or down '''
        
        # Get the current tree view item
        item = self.treeUI.currentItem()
        
        # No current item ?
        if not item:
            return
        
        # Get the modifier dg node name to move
        modifier  = item.text(self.TREE_COLUMN_NAME)
        insertion = r''
            
        # Move Up / Down
        if direction > 0:
            # Insert after the above item
            insertAfterItem = self.treeUI.itemAbove(item)
            
            # Already the topmost modifier ?
            if not insertAfterItem:
                return
            
            # Move a modifier topmost means inserting it before
            # the description node
            insertBeforeItem = self.treeUI.itemAbove(insertAfterItem)
            
            # Get the modifier dg node name to insert before
            if insertBeforeItem:
                insertion = insertBeforeItem.text(self.TREE_COLUMN_NAME)
            else:
                dagPath = getCurrentSplineDescriptionDagPath()
                if not dagPath.isValid():
                    return
                dagPath.extendToShape()
                insertion = om.MFnDagNode(dagPath).name()
            
        elif direction < 0:
            # Insert before the below item
            insertBeforeItem = self.treeUI.itemBelow(item)
            
            # Already the downmost modifier ?
            if not insertBeforeItem:
                return
            
            # Get the modifier dg node name to insert before
            insertion = insertBeforeItem.text(self.TREE_COLUMN_NAME)
            
        # Perform dg modification
        with MayaCmdsTransaction():
            inOut = self.__internalDisconnectModifier(modifier)
            self.__internalInsertModifier(inOut, insertion)
            
        # Refresh UI
        self.refresh()
        
    def __addModifier(self):
        ''' Add a modifier to the end of the modifier chain '''
        
        # Show an Add Modifier Dialog
        pos = QCursor.pos()
        pos += QPoint(-600, 10)
        dialog = IgSplineAddModifierUI(pos.x(), pos.y())
        
        if dialog.exec_() != QDialog.Accepted:
            return
        
        # Insert the new modifier before the description node
        dagPath = getCurrentSplineDescriptionDagPath()
        if not dagPath.isValid():
            return
        dagPath.extendToShape()
        insertion = om.MFnDagNode(dagPath).name()
        
        # Create new modifier nodes and insert them
        with MayaCmdsTransaction() as context:
            # createNode command will change the current selection..
            context.saveSelectionList()

            # Create modifier nodes
            for nodeType in dialog.getNodeTypes():
                # Guess a better node name
                nodeName = nodeType
                if nodeType.startswith(r'xgmModifier'):
                    nodeName = nodeType[11:]
                elif nodeType.startswith(r'xgm'):
                    nodeName = nodeType[3:]
                if len(nodeName) > 0:
                    nodeName = nodeName[0].lower() + nodeName[1:]
                else:
                    nodeName = nodeType

                # Create the modifier dg node
                modifier = cmds.createNode(nodeType, n=nodeName)
                
                # Find the input and output plug
                inPlug  = modifier + r'.inSplineData'
                outPlug = modifier + r'.outSplineData' 
                if cmds.attributeQuery(r'inSplineData', n=modifier, m=True):
                    inPlug = inPlug + r'[0]'
                if cmds.attributeQuery(r'outSplineData', n=modifier, m=True):
                    outPlug = outPlug + r'[0]'
                inOut = (inPlug, outPlug)

                # Insert to the last of the modifier chain
                self.__internalInsertModifier(inOut, insertion)

                # Activate the new modifier if it's a sculpt
                if cmds.objectType(modifier, isAType=r'xgmModifierSculpt'):
                    self.__internalActivateSculptModifier(modifier)
            
                # Add a dummy QTreeWidgetItem so it's the selection
                self.isUpdating = True
                newItem = QTreeWidgetItem(self.treeUI)
                newItem.setData(0, self.TREE_ROLE_NAME, modifier)
                newItem.setText(self.TREE_COLUMN_NAME, modifier)
                self.treeUI.setCurrentItem(newItem)
                self.isUpdating = False
        
        self.refresh()

    def __deleteModifier(self):
        ''' Delete the current modifier '''
        
        # Get the current tree view item
        item = self.treeUI.currentItem()
        
        # No current item ?
        if not item:
            return
        
        # Get the modifier dg node name to move
        modifier = item.text(self.TREE_COLUMN_NAME)
        
        # The dg node is already deleted ?
        if not cmds.objExists(modifier):
            cmds.warning(maya.stringTable[u'y_xgenm_ui_tabs_xgIgSplineModifierTab.kModifierToDeleteNotExist'] % modifier)
            return
        
        # Confirm the deletion of a shared modifier. The user can choose
        # to disconnect it instead of deleting it.
        operation = r'cancel'
        if self.__isModifierShared(modifier):
            # Show a Delete Shared Modifier Dialog
            pos = QCursor.pos()
            pos += QPoint(-600, 10)
            dialog = IgSplineDeleteSharedModifierUI(modifier, pos.x(), pos.y())
            if dialog.exec_() == QDialog.Accepted:
                operation = dialog.getOperation()
        else:
            # The modifier is not shared. just delete it.
            operation = r'delete'
            
        # The user choose to cancel the deletion
        if operation == r'cancel':
            return
        
        # User is not allowed to delete a dg node in the following conditions
        isReferenced = cmds.referenceQuery(modifier, isNodeReferenced=True)
        isLocked     = cmds.lockNode(modifier, q=True, lock=True)[0]
        isActive     = self.__isActiveSculptModifier(modifier)
        
        # Referenced node is not allowed to delete. Changing to disconnect
        if isReferenced:
            operation = r'disconnect'
            cmds.warning(maya.stringTable[u'y_xgenm_ui_tabs_xgIgSplineModifierTab.kCantDeleteReferencedNode'] % modifier)
            
        # Activate another sculpt modifier if an active sculpt modifier is deleted
        nextActive = r''
        if isActive:
            nextActive = self.__getNextSculptModifier(modifier)
            
        # Select the next modifier so we don't lose selection
        itemBelow = self.treeUI.itemBelow(item)
        if itemBelow:
            self.treeUI.setCurrentItem(itemBelow)
        else:
            itemAbove = self.treeUI.itemAbove(item)
            if itemAbove:
                self.treeUI.setCurrentItem(itemAbove)
        
        # Perform dg modification
        with MayaCmdsTransaction():
            if operation == r'delete':
                # Unlock the node before deletion
                if isLocked:
                    cmds.lockNode(modifier, lock=False)
                # Delete the node
                cmds.delete(modifier)
            elif operation == r'disconnect':
                # Disconnect the modifier node but leave it in the scene
                self.__internalDisconnectModifier(modifier)

            if len(nextActive) > 0:
                self.__internalActivateSculptModifier(nextActive)
            
        # Refresh UI
        self.refresh()

    def __duplicateModifier(self):
        ''' Duplicate the current modifier '''
        
        # Get the current tree view item
        item = self.treeUI.currentItem()
        
        # No current item ?
        if not item:
            return
        
        # Get the modifier dg node name to move
        modifier = item.text(self.TREE_COLUMN_NAME)
        
        # The dg node is already deleted ?
        if not cmds.objExists(modifier):
            cmds.warning(maya.stringTable[u'y_xgenm_ui_tabs_xgIgSplineModifierTab.kModifierToDuplicateNotExist'] % modifier)
            return
        
        # Get the modifier connections
        connections = self.__getModifierConnections()
        
        # Find the output connection of the modifier
        index = next((i for i in range(0, len(connections))
            if connections[i][0].startswith(modifier + r'.')), -1)
        
        # No such modifier ?
        if index < 0:
            raise RuntimeError(r'Internal error : %s not found in %s'
                % (modifier, str(connections)))
            
        # output = modifier.out -> other.in
        # This plug usually exists because we find the modifier by tracing
        # from the description node
        output = connections[index]
        insertion = output[1][:output[1].find(r'.')]
        
        # Perform dg modification
        with MayaCmdsTransaction():
            # Duplicate the dg node
            replicant = cmds.duplicate(modifier)[0]

            # Find the input and output plug
            inPlug  = replicant + r'.inSplineData'
            outPlug = replicant + r'.outSplineData' 
            if cmds.attributeQuery(r'inSplineData', n=replicant, m=True):
                inPlug = inPlug + r'[0]'
            if cmds.attributeQuery(r'outSplineData', n=replicant, m=True):
                outPlug = outPlug + r'[0]'
            inOut = (inPlug, outPlug)

            # Rewire connections
            self.__internalInsertModifier(inOut, insertion)
            
            # Activate the new modifier if it's a sculpt
            if cmds.objectType(replicant, isAType=r'xgmModifierSculpt'):
                self.__internalActivateSculptModifier(replicant)
            
            # Add a dummy QTreeWidgetItem so it's the selection
            self.isUpdating = True
            replicantItem = QTreeWidgetItem(self.treeUI)
            replicantItem.setData(0, self.TREE_ROLE_NAME, replicant)
            replicantItem.setText(self.TREE_COLUMN_NAME, replicant)
            self.treeUI.setCurrentItem(replicantItem)
            self.isUpdating = False
            
        # Refresh UI
        self.refresh()
        
    def __activateSculptModifier(self, node):
        ''' Activate a sculpt modifier in the current description '''
        
        # Already activated ?
        if self.__isActiveSculptModifier(node):
            return
        
        # Connect sculpt.message to description.activeSculpt
        with MayaCmdsTransaction():
            self.__internalActivateSculptModifier(node)

        # Refresh UI
        QtCore.QTimer.singleShot(0, lambda: self.refresh())
        
    def __toggleModifier(self, modifier):
        ''' Toggle on/off the modifier '''
        
        # Check if the modifier has mute attribute
        try:
            type = cmds.attributeQuery(r'mute', n=modifier, at=True)
            if type != r'bool':
                return
        except:
            return
        
        # Get the old mute attribute
        mute = cmds.getAttr(modifier + r'.mute')

        # Toggle the mute attribute
        with MayaCmdsTransaction():
            cmds.setAttr(modifier + r'.mute', not mute)

        # Refresh UI
        QtCore.QTimer.singleShot(0, lambda: self.refresh())
        
    def __renameModifierOnChange(self, item):
        ''' Rename a modifier to the new name '''

        # Refresh UI even on failure
        QtCore.QTimer.singleShot(0, lambda: self.refresh())
        
        # Get the old name of the modifier
        modifier = str(item.data(0, self.TREE_ROLE_NAME))
        
        # Get the new name of the modifier
        newName  = item.text(self.TREE_COLUMN_NAME)

        # Rename the modifier dg node
        with MayaCmdsTransaction():
            cmds.rename(modifier, newName)
            
        # Update the name role
        item.setData(0, self.TREE_ROLE_NAME, newName)
        
    def __reorderModifiers(self, item):
        ''' Reorder a modifier according to the current UI state '''
        
        # Refresh UI even on failure
        QtCore.QTimer.singleShot(0, lambda: self.refresh())
        
        # Get the dg node name of the modifier
        modifier  = item.text(self.TREE_COLUMN_NAME)
        
        # Find the item above the inserted item as insertion point
        insertBeforeItem = self.treeUI.itemAbove(item)
        
        # Get the modifier dg node name to insert before
        insertion = None
        if insertBeforeItem:
            insertion = insertBeforeItem.text(self.TREE_COLUMN_NAME)
        else:
            dagPath = getCurrentSplineDescriptionDagPath()
            if not dagPath.isValid():
                return
            dagPath.extendToShape()
            insertion = om.MFnDagNode(dagPath).name()
        
        # Perform  dg modification
        with MayaCmdsTransaction():
            inOut = self.__internalDisconnectModifier(modifier)
            self.__internalInsertModifier(inOut, insertion)
            
    def __showContextMenu(self, pos):
        ''' Show a context menu at the global pos '''

        # Create the context menu
        ctxMenu = QMenu()
        
        ctxMenu.addAction(maya.stringTable[u'y_xgenm_ui_tabs_xgIgSplineModifierTab.kContextMenuNewModifier'],
            self.__addModifier)
        ctxMenu.addAction(maya.stringTable[u'y_xgenm_ui_tabs_xgIgSplineModifierTab.kContextMenuDeleteSelected'],
            self.__deleteModifier)
        ctxMenu.addAction(maya.stringTable[u'y_xgenm_ui_tabs_xgIgSplineModifierTab.kContextMenuDuplicateSelected'],
            self.__duplicateModifier)
        
        # Popup the menu
        ctxMenu.exec_(pos)
    
    def __onCurrentItemChanged(self, current, previous):
        ''' Invoked when the current modifier is changed '''
        
        # Ignore if updating
        if self.isUpdating or not current:
            return
        
        # Update the highlight text color
        self.__updateTreeUIPalette(current)

        # Get the modifier dg node name
        modifier = current.text(self.TREE_COLUMN_NAME)
        
        # Update the Modifier Attributes
        self.modifierSelectionChanged.emit(modifier)
        
    def __onItemClicked(self, item, column):
        ''' Invoked when a modifier is clicked '''

        # Ignore if updating
        if self.isUpdating:
            return

        # Get the modifier dg node name
        modifier = item.text(self.TREE_COLUMN_NAME)

        # Which column ?
        if column == self.TREE_COLUMN_ENABLE:
            # Turning on/off a modifier ?
            self.__toggleModifier(modifier)

        elif column == self.TREE_COLUMN_ACTIVE:
            if cmds.objectType(modifier) == r'xgmModifierSculpt':
                # Activate a sculpt modifier node
                self.__activateSculptModifier(modifier)

    def __onItemDoubleClicked(self, item, column):
        ''' Invoked when a modifier is double clicked '''
        
        # Ignore if updating
        if self.isUpdating:
            return

        # Double clicking the name column should bring up a line edit control
        if column == self.TREE_COLUMN_NAME:
            # Edit the name column. We don't use setEditTriggers() because it
            # allows to edit all columns of the QTreeWidget
            self.treeUI.editItem(item, column)
    
    def __onItemPressed(self, item, column):
        ''' Invoked when a modifier is pressed '''
        
        # Get the modifier dg node name
        modifier = item.text(self.TREE_COLUMN_NAME)

        # Activate the sculpt modifier when its name or active column is pressed
        if column in [self.TREE_COLUMN_NAME, self.TREE_COLUMN_ACTIVE]:
            if cmds.objectType(modifier, isAType=r'xgmModifierSculpt'):
                # Activate a sculpt modifier node
                self.__activateSculptModifier(modifier)

    def __onItemChanged(self, item, column):
        ''' Invoked when a modifier column is changed '''

        # Ignore if updating
        if self.isUpdating:
            return

        # Changing a name column should rename the modifier
        if column == self.TREE_COLUMN_NAME:
            self.__renameModifierOnChange(item)
            
    def __onCustomContextMenuRequested(self, pos):
        ''' Invoked when a custom context menu is requested '''
        
        self.__showContextMenu(self.treeUI.viewport().mapToGlobal(pos))
        
    def __onRowsInserted(self, parent, start, end):
        ''' Invoked during Drag & Drop '''
        
        # Ignore if updating
        if self.isUpdating:
            return

        # QTreeWidget does not emit rowsMoved signal so we have to use rowsInserted
        #
        
        # Get the modifier to move around
        item = self.treeUI.topLevelItem(start)
        
        # Not likely to happen
        if not item:
            QtCore.QTimer.singleShot(0, lambda: self.refresh())
            return
        
        # Leave the selection to the item
        self.treeUI.setCurrentItem(item)
        
        # Reorder the modifier
        self.__reorderModifiers(item)
        
 
'''
    Modifier Attribute for Interactive Groom Splines
'''
class IgSplineModifierAttrUI(QWidget):
    
    # Interactive Groom Tools shelf
    igToolUI    = None

    # Attribute Editor Wrapper widget
    psWidget    = None
    psName      = r'xgenModifierAttributeWindow'
    
    def __init__(self):
        ''' Constructor '''
        QWidget.__init__(self)
        
        # Create shelf buttons
        self.__createIgToolUI()
        
        # Create the wrapper widget for Maya's Attribute Editor
        self.psWidget = AttrEdUI(self.psName)
        
        # Main layout of the Modifier Attributes UI
        layout = QVBoxLayout()
        QLayoutItem.setAlignment(layout, QtCore.Qt.AlignTop)
        layout.setSpacing(DpiScale(0))
        layout.setContentsMargins(DpiScale(0), DpiScale(3), DpiScale(0), DpiScale(3))
        layout.addWidget(self.igToolUI)
        layout.addWidget(self.psWidget)
        self.setLayout(layout)
        
    def __createIgToolUI(self):
        ''' Create the shelf buttons for Interactive Groom Tools '''
        
        buttonDescs = [
            # Density
            (   r'Density',
                r'xgCreateDescription.png',
                maya.stringTable[u'y_xgenm_ui_tabs_xgIgSplineModifierTab.kDensityBrush'],
                lambda: self.setBrush(r'XgmSetDensityBrushTool'),
                lambda: self.setBrush(r'XgmSetDensityBrushToolOption')),
            # Length
            (   r'Length',
                r'iGroom_length.png',
                maya.stringTable[u'y_xgenm_ui_tabs_xgIgSplineModifierTab.kLengthBrush'],
                lambda: self.setBrush(r'XgmSetLengthBrushTool'),
                lambda: self.setBrush(r'XgmSetLengthBrushToolOption')),
            # Cut
            (   r'Cut',
                r'fx_cut.png',
                maya.stringTable[u'y_xgenm_ui_tabs_xgIgSplineModifierTab.kCutBrush'],
                lambda: self.setBrush(r'XgmSetCutBrushTool'),
                lambda: self.setBrush(r'XgmSetCutBrushToolOption')),
            # Width
            (   r'Width',
                r'iGroom_width.png',
                maya.stringTable[u'y_xgenm_ui_tabs_xgIgSplineModifierTab.kWidthBrush'],
                lambda: self.setBrush(r'XgmSetWidthBrushTool'),
                lambda: self.setBrush(r'XgmSetWidthBrushToolOption')),
            # Twist Direction
            (   r'Twist',
                r'iGroom_twist.png',
                maya.stringTable[u'y_xgenm_ui_tabs_xgIgSplineModifierTab.kDirectionrush'],
                lambda: self.setBrush(r'XgmSetDirectionBrushTool'),
                lambda: self.setBrush(r'XgmSetDirectionBrushToolOption')),
            # Comb
            (   r'Comb',
                r'iGroom_orient.png',
                maya.stringTable[u'y_xgenm_ui_tabs_xgIgSplineModifierTab.kCombBrush'],
                lambda: self.setBrush(r'XgmSetCombBrushTool'),
                lambda: self.setBrush(r'XgmSetCombBrushToolOption')),
            # Grab
            (   r'Grab',
                r'iGroom_pose.png',
                maya.stringTable[u'y_xgenm_ui_tabs_xgIgSplineModifierTab.kGrabBrush'],
                lambda: self.setBrush(r'XgmSetGrabBrushTool'),
                lambda: self.setBrush(r'XgmSetGrabBrushToolOption')),
            # Smooth
            (   r'Smooth',
                r'iGroom_smooth.png',
                maya.stringTable[u'y_xgenm_ui_tabs_xgIgSplineModifierTab.kSmoothBrush'],
                lambda: self.setBrush(r'XgmSetSmoothBrushTool'),
                lambda: self.setBrush(r'XgmSetSmoothBrushToolOption')),
            # Noise
            (   r'Noise',
                r'iGroom_noise.png',
                maya.stringTable[u'y_xgenm_ui_tabs_xgIgSplineModifierTab.kNoiseBrush'],
                lambda: self.setBrush(r'XgmSetNoiseBrushTool'),
                lambda: self.setBrush(r'XgmSetNoiseBrushToolOption')),

            # Clump
            (   r'Clump',
                r'iGroom_attract.png',
                maya.stringTable[u'y_xgenm_ui_tabs_xgIgSplineModifierTab.kClumpBrush'],
                lambda: self.setBrush(r'XgmSetClumpBrushTool'),
                lambda: self.setBrush(r'XgmSetClumpBrushToolOption')),
            # Part
            (   r'Part',
                r'iGroom_part.png',
                maya.stringTable[u'y_xgenm_ui_tabs_xgIgSplineModifierTab.kPartBrush'],
                lambda: self.setBrush(r'XgmSetPartBrushTool'),
                lambda: self.setBrush(r'XgmSetPartBrushToolOption')),

            # Freeze
            (   r'Freeze',
                r'iGroom_mask.png',
                maya.stringTable[u'y_xgenm_ui_tabs_xgIgSplineModifierTab.kFreezeBrush'],
                lambda: self.setBrush(r'XgmSetFreezeBrushTool'),
                lambda: self.setBrush(r'XgmSetFreezeBrushToolOption')),

            # Select
            (   r'Select',
                r'xgPrimSelection.png',
                maya.stringTable[u'y_xgenm_ui_tabs_xgIgSplineModifierTab.kSelectBrush'],
                lambda: self.setBrush(r'XgmSetSelectBrushTool'),
                lambda: self.setBrush(r'XgmSetselectBrushToolOption')),

            # Region
            # TODO
        ]
        
        # Create the widget to hold buttons
        shelfUI = ToolBarUI(QSize(32, 32), 2)
        
        # Add buttons
        for toolName, icon, text, callable, doubleClick in buttonDescs:
            button = shelfUI.addButton(icon, text, callable)
            button.setAccessibleName(toolName)
            button.setText(text)
            button.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
            button.setMinimumSize(ToolButtonSizeHint(button, IgGroomBrushButtonSize, bottomText=text))
            button.setStyleSheet(ToolButtonFlatStyle)
            button.doubleClicked.connect(doubleClick)
            
        # Frame Layout for the Interactive Groom Tools buttons
        self.igToolUI = ExpandUI(maya.stringTable[u'y_xgenm_ui_tabs_xgIgSplineModifierTab.kInteractiveGroomTools'], True)
        self.igToolUI.addWidget(shelfUI)
        
    def setNode(self, node):
        ''' Set the current node to be shown in Attribute Editor '''
        
        # Get the node type
        nodeType = cmds.objectType(node) if cmds.objExists(node) else r''
        
        # Set shelf visibility
        self.igToolUI.setVisible(nodeType == r'xgmModifierSculpt')
        
        # Set the current dg node name and update UI
        self.psWidget.setNode(node)
        self.psWidget.refresh()
        
    def setBrush(self, command):
        ''' Set the Maya brush by executing the specified command '''
        
        # Execute the default runtime command to activate the brush
        mel.eval(command)
        
    def refresh(self):
        ''' Update the UI from the description '''
        
        # Refresh the embeded Maya Attribute Editor
        self.psWidget.refresh()
        

# ===========================================================================
# Copyright 2021 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
