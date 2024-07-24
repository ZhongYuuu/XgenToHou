import maya
maya.utils.loadStringResourcesForModule(__name__)

from builtins import next
from builtins import range
import weakref

pysideVersion = r'-1'
import PySide2, PySide2.QtCore, PySide2.QtGui, PySide2.QtWidgets
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
pysideVersion = PySide2.__version__

import maya.cmds as cmds
import maya.OpenMaya as om

import xgenm as xg
import xgenm.xgLog as xglog
from xgenm.ui.util.xgIgSplineUtil import *
from xgenm.ui.util.xgUtil import *
from xgenm.ui.xgIgSplineEditorDgWatcher import *
from xgenm.ui.xgIgSplineEditorTreeItem import *


'''
    QAbstractItemModel for XGen Interactive Groom Spline Editor
'''
class IgSplineEditorTreeModel(QAbstractItemModel):

    # Default names
    DEFAULT_LAYER_NAME  = maya.stringTable[u'y_xgenm_ui_xgIgSplineEditorTreeModel.kDefaultLayerName']
    DEFAULT_GROUP_NAME  = maya.stringTable[u'y_xgenm_ui_xgIgSplineEditorTreeModel.kDefaultGroupName']
    DEFAULT_MERGE_NAME  = maya.stringTable[u'y_xgenm_ui_xgIgSplineEditorTreeModel.kDefaultMergeName']

    # Header Data
    HEADER_DATA         = None

    # Brushes
    BRUSH_DISABLED      = QBrush(QColor(102,102,102))

    # Descriptions are ignored when connected to these plugs
    IGNORED_PLUGS       = [r'inGuideData', r'inWireData']

    # Maya dg notifications
    dgWatcher           = None

    # Owner QTreeView
    view                = None

    # Root (world) item
    worldItem           = None

    # Description items (for fast lookup)
    descriptionItems    = list()

    # A set of dag nodes of interest
    dagNodesOfInterest  = set()

    # Flags
    isUpdatingSelection = False

    # Delayed refresh flags in case that we don't queue too many refreshes
    refreshDagInQueue         = False
    refreshDescriptionInQueue = set()
    refreshSelectionInQueue   = False

    def __init__(self, parent=None):
        ''' Constructor '''
        QAbstractItemModel.__init__(self, parent)

    def columnCount(self, parent):
        ''' Return the number of columns '''
        return IgSplineEditorTreeColumn.COUNT

    def rowCount(self, parent):
        ''' Return the number of the rows '''

        # Not meaningful for other columns
        if parent.column() > 0:
            return 0

        # Get the parent item from the parent index
        parentItem = self.__getItemFromIndex(parent)

        # Return the number of children of the parent item
        return parentItem.getChildCount()

    def index(self, row, column, parent):
        ''' Return the index of the item '''

        # Check if we have a valid index at (row, column, parent)
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        # Get the parent item from the parent index
        parentItem = self.__getItemFromIndex(parent)

        # Get the row-th child item of the parent item
        item = parentItem.getChild(row)
        if item is not None:
            return self.createIndex(row, column, item)
        return QModelIndex()

    def parent(self, index):
        ''' Return the parent of the item '''

        # World item doesn't have a parent
        if not index.isValid():
            return QModelIndex()

        # Get the row by looking into the parent item
        item       = self.__getItemFromIndex(index)
        parentItem = item.getParent()

        # Return the index of the parent item
        if parentItem and parentItem != self.worldItem:
            parentParentItem = parentItem.getParent()
            parentRow        = parentParentItem.getChildIndex(parentItem)
            return self.createIndex(parentRow, 0, parentItem)
        return QModelIndex()

    def headerData(self, section, orientation, role):
        ''' Return the data stored under the given role in the header '''
        if orientation != Qt.Horizontal:
            return None

        # One-time loading the header data
        if self.HEADER_DATA is None:
            self.HEADER_DATA = {
                IgSplineEditorTreeColumn.ENABLE: {
                    Qt.SizeHintRole: QSize(DpiScale(20), DpiScale(20))
                    },
                IgSplineEditorTreeColumn.NAME: {
                    Qt.DisplayRole: maya.stringTable[u'y_xgenm_ui_xgIgSplineEditorTreeModel.kColumnName'],
                    Qt.TextAlignmentRole: Qt.AlignCenter
                    },
                IgSplineEditorTreeColumn.WEIGHT: {
                    Qt.DisplayRole: maya.stringTable[u'y_xgenm_ui_xgIgSplineEditorTreeModel.kColumnWeight'],
                    Qt.TextAlignmentRole: Qt.AlignCenter
                    },
                IgSplineEditorTreeColumn.EDIT: {
                    Qt.DisplayRole: maya.stringTable[u'y_xgenm_ui_xgIgSplineEditorTreeModel.kColumnEdit'],
                    Qt.TextAlignmentRole: Qt.AlignCenter
                    },
                IgSplineEditorTreeColumn.KEY: {
                    Qt.DisplayRole: maya.stringTable[u'y_xgenm_ui_xgIgSplineEditorTreeModel.kColumnKey'],
                    Qt.TextAlignmentRole: Qt.AlignCenter
                    }
                }

        # Get the data for the specific column
        columnData = self.HEADER_DATA.get(section, None)

        # Return the data for the specific role
        return columnData.get(role, None) if columnData is not None else None

    def flags(self, index):
        ''' Return the item flags for the given index '''
        return self.__getItemFromIndex(index).flags(index.column())

    def data(self, index, role):
        ''' Return the data stored under the given role '''
        return self.__getItemFromIndex(index).data(index.column(), role)

    def setData(self, index, value, role):
        ''' Set the role data for the item at index to value '''
        return self.__getItemFromIndex(index).setData(index.column(), value, role)

    def supportedDropActions(self):
        ''' Return the drop actions supported by this model '''
        return Qt.MoveAction

    def mimeTypes(self):
        ''' Return the list of allowed MIME types '''
        return IgSplineEditorMimeData.MIME_TYPES

    def mimeData(self, indexes):
        ''' Return an object that contains serialized items of data '''

        # MIME data for the items being dragged
        mimeData    = QMimeData()
        encodedData = QByteArray()
        stream      = QDataStream(encodedData, QIODevice.WriteOnly)

        # Turn the indexes into items
        items = []
        for index in indexes:
            if index.isValid():
                items.append(self.__getItemFromIndex(index))

        # Return empty data if there are no items to drag
        if len(items) == 0:
            return mimeData

        # Determine the type of this drag action. We allow to drag dag,
        # modifier, sculpt groups and sculpt layers.
        # We also record the owner description and modifier if any.
        dragMimeType    = r''
        dragDescription = r''
        dragModifier    = r''

        if isinstance(items[0], IgSplineEditorDagItem):
            # A dag move operation
            dragMimeType    = IgSplineEditorMimeData.MIME_TYPE_DAG
        elif isinstance(items[0], IgSplineEditorModifierItem):
            # A modifier move operation
            dragMimeType    = IgSplineEditorMimeData.MIME_TYPE_MODIFIER
            dragDescription = items[0].getDescription().getNodeName()
        elif isinstance(items[0], IgSplineEditorAbstractSculptItem):
            # A sculpt group or layer move operation
            dragMimeType    = IgSplineEditorMimeData.MIME_TYPE_SCULPT
            dragDescription = items[0].getModifierParent().getDescription().getNodeName()
            dragModifier    = items[0].getModifierParent().getNodeName()
        else:
            return mimeData

        # Write the description and modifier owner if any
        stream.writeQString(dragDescription)
        stream.writeQString(dragModifier)

        # Serialize items. We don't completely serialize items but just encode
        # enough information to indentify the items.
        dragData = []
        for item in items:
            # We write a tag to identify the data type and a list of strings
            # following the tag.
            if (dragMimeType == IgSplineEditorMimeData.MIME_TYPE_DAG
                    and isinstance(item, IgSplineEditorDagItem)):

                # Item(dag): name of the dag node
                dragData.append(item.getNodeName())

            elif (dragMimeType == IgSplineEditorMimeData.MIME_TYPE_MODIFIER
                    and isinstance(item, IgSplineEditorModifierItem)):

                # Item(modifier): name of the modifier node
                if item.getDescription().getNodeName() == dragDescription:
                    dragData.append(item.getNodeName())

            elif (dragMimeType == IgSplineEditorMimeData.MIME_TYPE_SCULPT
                    and isinstance(item, IgSplineEditorAbstractSculptItem)):

                # Item(sculpt): plug of the sculpt layer or group
                if (item.getModifierParent().getDescription().getNodeName() == dragDescription
                        and item.getModifierParent().getNodeName() == dragModifier):
                    dragData.append(item.getPlug().name())

        # Write the drag data
        stream.writeQStringList(dragData)

        # Return the serialized MIME data
        mimeData.setData(dragMimeType, encodedData)
        return mimeData

    def dropMimeData(self, data, action, row, column, parent):
        ''' Handles the data supplied by a drag and drop operation '''

        # Ignored ?
        if action == Qt.IgnoreAction:
            return True

        # Check for the supported mime types
        dragMimeType = None
        for mimeType in IgSplineEditorMimeData.MIME_TYPES:
            if data.hasFormat(mimeType):
                dragMimeType = mimeType
                break

        # The drag operation is not supported
        if not dragMimeType:
            return False

        # Get the drag data of the recognized mime type
        encodedData = data.data(dragMimeType)
        stream      = QDataStream(encodedData, QIODevice.ReadOnly)

        if stream.atEnd():
            return False

        # Read the encoded data
        dragDescription = stream.readQString()
        dragModifier    = stream.readQString()
        dragData        = stream.readQStringList()

        # Only allow to drop to name column
        if parent.isValid() and parent.column() != IgSplineEditorTreeColumn.NAME:
            # Forbid to drop onto a non-name column
            return False
        elif column >= 0 and column != IgSplineEditorTreeColumn.NAME:
            # Forbid to insert between two non-name columns
            return False

        # Get the parent item being dropped on
        parentItem = self.__getItemFromIndex(parent)

        # Drop onto differnt items
        if dragMimeType == IgSplineEditorMimeData.MIME_TYPE_DAG:
            return self.__dropDags(parentItem, row, dragData)
        elif dragMimeType == IgSplineEditorMimeData.MIME_TYPE_MODIFIER:
            # Perform a modifier drop operation
            return self.__dropModifiers(parentItem, row, dragDescription, dragData)
        elif dragMimeType == IgSplineEditorMimeData.MIME_TYPE_SCULPT:
            return self.__dropSculpts(parentItem, row, dragModifier, dragData)

        # Not handled !
        return False

    def itemToIndex(self, item, column = 0):
        ''' Get the QModelIndex of the item. createIndex() is protected.. '''

        # Get the parent of the item
        parent = item.getParent()

        # No parent (world item?)
        if parent is None:
            return QModelIndex()

        # Get the row of the item in its parent. We don't expect a large
        # number of rows so a linear search is used..
        row = parent.getChildIndex(item)

        # Create a valid model index..
        return self.createIndex(row, column, item)

    def __getItemFromIndex(self, index):
        ''' Get the item from the model index '''
        return index.internalPointer() if index.isValid() else self.worldItem

    def setView(self, view):
        ''' Set the reference to the owner QTreeView '''
        self.view                       = weakref.proxy(view)
        self.worldItem                  = IgSplineEditorWorldItem(self.view)
        self.descriptionItems           = list()
        self.dagNodesOfInterest         = set()
        self.refreshDagInQueue          = False
        self.refreshDescriptionInQueue  = set()

    def getDefaultSculptGroupName(self, logicalIndex):
        ''' Return the default sculpt group name '''
        return self.DEFAULT_GROUP_NAME % (logicalIndex + 1)

    def getDefaultSculptLayerName(self, logicalIndex):
        ''' Return the default sculpt layer name '''
        return self.DEFAULT_LAYER_NAME % (logicalIndex + 1)

    def getDefaultMergeLayerName(self, logicalIndex):
        ''' Return the default merge layer name '''
        return self.DEFAULT_MERGE_NAME % (logicalIndex + 1)

    def delayedRefreshDag(self, notUsed0=None):
        ''' Schedule a self.__refreshDagItems() in the next idle event '''
        if not self.refreshDagInQueue:
            self.refreshDagInQueue = True
            QTimer.singleShot(0, lambda: self.__refreshDagItems())

    def delayedRefreshDescription(self, node):
        ''' Schedule a self.__refreshDescriptionItem() in the next idle event '''
        handle = IgSplineEditorDgNode(node)
        if handle not in self.refreshDescriptionInQueue:
            self.refreshDescriptionInQueue.add(handle)
            QTimer.singleShot(0, lambda: self.__refreshDescriptionItem(handle))

    def delayedRefreshSelection(self):
        ''' Schedule a self.__refreshSelection() in the next idle event '''
        if not self.refreshSelectionInQueue:
            self.refreshSelectionInQueue = True
            QTimer.singleShot(0, lambda: self.__refreshSelection())

    def refresh(self):
        ''' Refresh the model based on the current Maya dg graph '''

        # Register dg notification callbacks
        if self.dgWatcher is None:
            self.dgWatcher = IgSplineEditorDgWatcher()
            self.dgWatcher.watchNodeAdded(r'xgmSplineDescription', self.delayedRefreshDag)
            self.dgWatcher.watchNodeRemoved(r'xgmSplineDescription', self.delayedRefreshDag)
            self.dgWatcher.watchDagChanged(self.onMayaDagChanged)
            self.dgWatcher.watchSelectionChanged(self.onMayaSelectionChanged)

        # Refresh dag hierarchy
        self.__refreshDagItems()

    def __refreshDagItems(self):
        ''' Refresh the model based on Dag hierarchy '''
        sl = om.MSelectionList()
        self.refreshDagInQueue         = False
        self.refreshDescriptionInQueue = set()

        # If the current description goes away for some reason (e.g. deleted),
        # we choose a new description as the current description.
        if not xgg.IgSplineEditor.currentDescription():
            descriptions = cmds.xgmSplineQuery(listSplineDescriptions=True, shape=True)
            if descriptions:
                xgg.IgSplineEditor.setCurrentDescription(descriptions[0])

        # Get the spline description nodes in O(1). Iterating the whole dag
        # hierarchy is not allowed.
        descriptionNames = cmds.xgmSplineQuery(listSplineDescriptions=True, shape=True)

        # Get the dag paths of the descriptions. Note that we don't support
        # instances. We only use the first path where possible.
        descriptionDagPaths = []
        ignoredDagPaths     = []
        for name in descriptionNames:
            # Get the MDagPath of the spline description. MSelectionList
            # should not throw exception. Otherwise, we need to check the
            # xgmSplineQuery command.
            dagPath = om.MDagPath()
            sl.add(name)
            sl.getDagPath(0, dagPath)
            sl.clear()

            # We use a hard-coded blacklist to filter out descriptions that
            # are connected to the specified plugs.
            dagNode = om.MFnDagNode(dagPath)
            outPlug = dagNode.findPlug(r'outSplineData')
            destinations = om.MPlugArray()
            if outPlug.destinations(destinations):
                # Check the destination plugs of the output of the spline description
                isIgnored = False
                for i in range(0, destinations.length()):
                    # WARNING: MPlugArray() doesn't support python foreach.
                    name = destinations[i].partialName(False, False, False, False, False, True)
                    if name in self.IGNORED_PLUGS:
                        # Found the plug in our blacklist
                        isIgnored = True
                        break
                # Ignore the description...
                if isIgnored:
                    ignoredDagPaths.append(dagPath)
                    continue

            # Survive. We are going to display the description.
            descriptionDagPaths.append(dagPath)

        # Build dag items from spline description shapes (bottom to top)
        for dagPath in descriptionDagPaths:
            # Update the spline description item
            item = self.__updateDescriptionItem(dagPath)

        # We have created all new dag items. Now remove orphan dag items
        # and reorder the dag items.
        self.__removeIgnoredDagItems(self.worldItem, ignoredDagPaths)
        self.__removeOrphanDagItems(self.worldItem)
        self.__reorderDagItems(self.worldItem)

        # Cache the set of dag nodes
        self.dagNodesOfInterest = set()
        self.worldItem.collectDagNodes(self.dagNodesOfInterest)

    def __updateWorldItem(self):
        ''' Update the world item. Note that we update from shape to world. '''
        return self.worldItem

    def __updateTransformItem(self, dagPath):
        ''' Update a transform item according to the given dag path '''

        # Get the parent dag path of the transform node
        parentPath = om.MDagPath(dagPath)
        parentPath.pop()

        # Update the parent transform item or world item
        parentItem = None
        if parentPath.length() == 0:
            parentItem = self.__updateWorldItem()
        else:
            parentItem = self.__updateTransformItem(parentPath)

        # Get the existing transform item
        handle  = IgSplineEditorDgNode(dagPath.node())
        dagItem = parentItem.getDagChildByHandle(handle)
        if dagItem is None:
            # Slow path to look up the whole hierarchy
            dagItem = self.worldItem.findDagChild(handle)

        # Build a brand new transform item if there is none
        if dagItem is None:
            dagItem = IgSplineEditorTransformItem(self.view, handle)

        # Move the transform item to its new parent
        parentItem.addDagChild(dagItem)

        # Update the transform item since the visibility is affected by its
        # parent and grandparents.
        dagItem.update()

        # Return the transform item
        return dagItem

    def __updateDescriptionItem(self, dagPath):
        ''' Update a description item according to the given dag path '''

        # Get the parent dag path of the description shape node
        parentPath = om.MDagPath(dagPath)
        parentPath.pop()

        # Update the parent transform item
        parentItem = self.__updateTransformItem(parentPath)

        # Get the existing spline description shape item
        handle   = IgSplineEditorDgNode(dagPath.node())
        dagShape = self.worldItem.findDagChild(handle)

        # Whether to update the description shape ?
        isRefreshDescription = False

        # Build a spline description shape item if there is none
        if dagShape is None:
            dagShape = IgSplineEditorDescriptionItem(self.view, handle)
            self.__descriptionItemCreated(dagShape)
            isRefreshDescription = True

        # Make the description shape of the transform parent
        if parentItem.getDagShape() != dagShape:
            parentItem.setDagShape(dagShape)

        # Refresh the modifier chains if needed
        if isRefreshDescription:
            self.__internalRefreshDescriptionItem(handle, dagShape)

        # Return the spline description shape item
        return dagShape

    def __removeIgnoredDagItems(self, dagItem, ignoredDagPaths, deduplication=None):
        ''' Remove filtered (ignored) description items '''

        # Nothing to do ?
        if len(ignoredDagPaths) == 0:
            return

        # Build a set of handles to make lookup faster. We don't support
        # instances so deduplication is a set of object handles.
        if deduplication is None:
            deduplication = set()
            for dagPath in ignoredDagPaths:
                deduplication.add(IgSplineEditorDgNode(dagPath.transform()))

        # Recursively remove items in ignoredDagPaths in the hierarchy
        for i in range(dagItem.getDagChildCount() - 1, -1, -1):
            childDagItem = dagItem.getDagChildByIndex(i)
            if childDagItem.getHandle() in deduplication:
                dagItem.removeDagChild(childDagItem)
            else:
                self.__removeIgnoredDagItems(childDagItem, ignoredDagPaths, deduplication)

    def __removeOrphanDagItems(self, dagItem):
        ''' Remove orphan (no shapes) child items '''
        isValid = False

        # Recursively remove child transform items
        for i in range(dagItem.getDagChildCount() - 1, -1, -1):
            childDagItem = dagItem.getDagChildByIndex(i)
            isChildValid = self.__removeOrphanDagItems(childDagItem)
            if not isChildValid:
                dagItem.removeDagChild(childDagItem)
            isValid = isValid or isChildValid

        # Check if we have any valid shape nodes
        if dagItem.getDagShape() is not None:
            isValid = isValid or dagItem.getDagShape().getHandle().isValid()

        # Does the sub-hierarchy contains a valid shape ?
        return isValid

    def __reorderDagItems(self, dagItem, dagIt = None):
        ''' Reorder the child items by the current Maya order '''

        # No need to reorder when there is no or one child ..
        if dagItem.getDagChildCount() <= 1:
            for i in range(0, dagItem.getDagChildCount()):
                self.__reorderDagItems(dagItem.getDagChildByIndex(i), dagIt)
            return

        # We only reorder transform items for simplicity ...
        if dagIt is None or dagItem == self.worldItem:
            dagIt = om.MItDag(om.MItDag.kBreadthFirst, om.MFn.kTransform)

        # Reset the iterator to the current transform item
        if dagItem != self.worldItem:
            dagIt.reset(dagItem.getHandle().node(),
                        om.MItDag.kBreadthFirst, om.MFn.kTransform)

        # Skip the root item
        next(dagIt)

        # Iterate the children dag nodes and reorder items
        pos = 0
        while not dagIt.isDone() and dagIt.depth() <= 1:
            # Examine the order of the current node
            currentItem = dagIt.currentItem()

            # Find the node index in the dag item
            childIndex = -1
            for i in range(pos, dagItem.getDagChildCount()):
                if dagItem.getDagChildByIndex(i).getHandle().node() == currentItem:
                    childIndex = i
                    break

            # Reorder the child item
            if childIndex >= 0:
                if childIndex != pos:
                    dagItem.moveDagChild(childIndex, pos)
                pos += 1

            # Goto the next child
            next(dagIt)

        # Recursive into children
        for i in range(0, dagItem.getDagChildCount()):
            self.__reorderDagItems(dagItem.getDagChildByIndex(i), dagIt)

    def onMayaDagChanged(self, msgType, child, parent):
        ''' Invoked when Maya dag changes '''

        # Is child interested ?
        if child.isValid() and IgSplineEditorDgNode(child.node()) in self.dagNodesOfInterest:
            self.delayedRefreshDag()

        # Is parent interested ?
        if parent.isValid() and IgSplineEditorDgNode(parent.node()) in self.dagNodesOfInterest:
            self.delayedRefreshDag()

        # Reject if both child and parent are not interested
        return

    def __refreshDescriptionItem(self, handle):
        ''' Refresh the modifier list of the description items '''
        self.refreshDescriptionInQueue.discard(handle)

        # A deleted description ?
        if not handle.isValid():
            return

        # Find the description items representing the handle
        itemList = []
        for itemRef in self.descriptionItems:
            item = itemRef()
            if item and item.getHandle() == handle:
                itemList.append(item)

        # Not found ? call self.__refreshDagItems() first ..
        if not itemList:
            return

        # Refresh all items
        for item in itemList:
            self.__internalRefreshDescriptionItem(handle, item)

    def __internalRefreshDescriptionItem(self, handle, item):
        ''' Refresh the modifier list of the description item '''

        # Starting with the source of xgmSplineDescription.inSplineData plug
        plug = om.MFnDagNode(handle.node()).findPlug(r'inSplineData').source()
        pos  = -1

        if not plug.isNull():
            # Recursively iterate the DG graph for a modifier chain
            while not plug.isNull() and isSplineModifierNode(plug.node()):
                # Update the specific modifier item
                pos += 1
                self.__updateModifierItem(item, IgSplineEditorDgNode(plug.node()), pos)

                # Goto the next modifier
                plug = findUpstreamSplinePlug(plug).source()

        # Include spline base node
        if not plug.isNull() and isSplineBaseNode(plug.node()):
            pos += 1
            self.__updateModifierItem(item, IgSplineEditorDgNode(plug.node()), pos)

        # Remove orphan modifiers
        item.removeModifiers(pos + 1, item.getModifierCount())


        # Updates the overridden status of the description
        item.updateOverridden()

    def __updateModifierItem(self, descriptionItem, handle, pos):
        ''' Update a modifier node in the description item '''

        # Find the existing modifier item
        item = descriptionItem.getModifierByHandle(handle)

        # Update based on modifier types
        if isSplineModifierSculptNode(handle.node()):
            # Build a sculpt modifier item
            if item is None:
                item = IgSplineEditorSculptModifierItem(self.view, handle)
            descriptionItem.addModifier(item, pos)

            # Update the scupt modifier
            self.__updateSculptModifierItem(handle, item)

        elif isSplineBaseNode(handle.node()):
            # Build a spline base node item
            if item is None:
                item = IgSplineEditorBaseNodeItem(self.view, handle)
            descriptionItem.addModifier(item, pos)

        elif isSplineModifierGuideNode(handle.node()):
            # Build a guide modifier node item
            if item is None:
                item = IgSplineEditorLinkModifierItem(self.view, handle)
            descriptionItem.addModifier(item, pos)

            # Update the guide modifier
            self.__updateLinkModifierItem(handle, item, r'inGuideData')

        elif isSplineModifierLinearWireNode(handle.node()):
            # Build a linear wire modifier node item
            if item is None:
                item = IgSplineEditorLinkModifierItem(self.view, handle)
            descriptionItem.addModifier(item, pos)

            # Update the linear wire modifier
            self.__updateLinkModifierItem(handle, item, r'inWireData')

        elif isOverrideModifierNode(handle.node()):
            # Build a linear wire modifier node item
            if item is None:
                item = IgSplineEditorOverrideModifierItem(self.view, handle)
            descriptionItem.addModifier(item, pos)

        else:
            # Build a common modifier item
            if item is None:
                item = IgSplineEditorModifierItem(self.view, handle)
            descriptionItem.addModifier(item, pos)

    def __updateLinkModifierItem(self, handle, item, linkPlug):
        ''' Update a link modifier item '''

        # Find the plug of the link
        dgNode = om.MFnDependencyNode(handle.node())
        plug   = dgNode.findPlug(linkPlug)

        # No link found ...
        if not plug.isDestination():
            item.setLink(None)
            return

        # Found a link. Check the source of the link.
        plug = plug.source()

        # We only support description link
        if isSplineDescriptionNode(plug.node()):
            # Find the transform node
            dagPath = om.MDagPath.getAPathTo(plug.node())

            # Nothing to do ?
            handle = IgSplineEditorDgNode(dagPath.transform())
            if item.getLink() and item.getLink().getHandle() == handle and item.getLink().getDagShape():
                return

            # New link or Link changed ?
            linkItem = IgSplineEditorDescriptionLinkItem(self.view, handle)
            item.setLink(linkItem)

            # Get the handle to the description shape
            shapeHandle = IgSplineEditorDgNode(dagPath.node())
            dagShape    = linkItem.findDagChild(shapeHandle)

            # Whether to update the description shape ?
            isRefreshDescription = False

            # Build a spline description shape item if there is none
            if dagShape is None:
                dagShape = IgSplineEditorDescriptionItem(self.view, shapeHandle)
                self.__descriptionItemCreated(dagShape)
                isRefreshDescription = True

            # Make the description shape of the transform parent
            if linkItem.getDagShape() != dagShape:
                linkItem.setDagShape(dagShape)

            # Refresh the modifier chains if needed
            if isRefreshDescription:
                self.__internalRefreshDescriptionItem(shapeHandle, dagShape)
        else:
            item.setLink(None)

    def __updateSculptModifierItem(self, handle, item):
        ''' Update a sculpt modifier item '''
        dgNode = om.MFnDependencyNode(handle.node())

        # This is the list of multi-child plugs for sculpt groups
        groupPlugs = []

        # Collect a list of sculpt group plugs
        plug = dgNode.findPlug(r'tweakGroups')
        for i in range(0, plug.numElements()):
            groupPlugs.append(plug.elementByPhysicalIndex(i))

        # This is the list of multi-child plugs for sculpt layers
        layerPlugs = []

        # Collect a list of sculpt layer plugs
        plug = dgNode.findPlug(r'tweaks')
        for i in range(0, plug.numElements()):
            layerPlugs.append(plug.elementByPhysicalIndex(i))

        # Build from top to bottom
        self.__updateSculptModifierItemOneLevel(dgNode, item.getRootGroup(), groupPlugs, layerPlugs)

    def __updateSculptModifierItemOneLevel(self, dgNode, parentItem, groupPlugs, layerPlugs):
        ''' Update a level of sculpt layers and sculpt groups '''
        
        # Logical index of the parent group
        ownerId = parentItem.getLogicalIndex()

        # Make a list of tuples: (uiOrder, plug, isGroup)
        levelPlugs = []

        # Attributes of interest
        attrLayerOwnerId = dgNode.attribute(r'ownerId')
        attrLayerUIOrder = dgNode.attribute(r'uiOrder')
        attrGroupOwnerId = dgNode.attribute(r'tweakGroupOwnerId')
        attrGroupUIOrder = dgNode.attribute(r'tweakGroupUIOrder')

        # Inspect Sculpt Groups
        for i in range(0, len(groupPlugs)):
            plug = groupPlugs[i]
            if plug and plug.child(attrGroupOwnerId).asInt() == ownerId:
                levelPlugs.append((plug.child(attrGroupUIOrder).asInt(),
                                   plug,
                                   True))
                groupPlugs[i] = None

        # Inspect Sculpt Layers
        for i in range(0, len(layerPlugs)):
            plug = layerPlugs[i]
            if plug and plug.child(attrLayerOwnerId).asInt() == ownerId:
                levelPlugs.append((plug.child(attrLayerUIOrder).asInt(),
                                   plug,
                                   False))
                layerPlugs[i] = None

        # Sort by uiOrder
        levelPlugs.sort(key=lambda x: x[0])

        # Update one level of Sculpt Groups and/or Sculpt Layers
        pos = -1
        for uiOrder, plug, isGroup in levelPlugs:
            # Update the specific Sculpt Group or Sculpt Layer
            pos += 1
            if isGroup:
                self.__updateSculptGroupItem(parentItem, plug, pos)
            else:
                self.__updateSculptLayerItem(parentItem, plug, pos)

        # Recursively update the next level
        for i in range(0, pos + 1):
            item = parentItem.getSculptChildByIndex(i)
            if item.isGroup():
                self.__updateSculptModifierItemOneLevel(dgNode, item, groupPlugs, layerPlugs)

        # Remove Orphan modifiers
        parentItem.removeSculptChildren(pos + 1, parentItem.getSculptChildCount())

    def __updateSculptGroupItem(self, parentItem, plug, pos):
        ''' Update a Sculpt Group item in the parent Sculpt Group '''

        # Logical index of the Sculpt Group plug
        logicalIndex = plug.logicalIndex()

        # Find the existing Sculpt Group item
        item = parentItem.getRootGroup().findSculptChildByLogicalIndex(logicalIndex, True)

        # Build a Sculpt Group item
        if item is None:
            item = IgSplineEditorSculptGroupItem(self.view,
                parentItem.getHandle(), parentItem.getModifierParent(), plug)
        parentItem.addSculptChild(item, pos)

    def __updateSculptLayerItem(self, parentItem, plug, pos):
        ''' Update a Sculpt Layer item in the parent Sculpt Group '''

        # Logical index of the Sculpt Layer plug
        logicalIndex = plug.logicalIndex()

        # Find the existing Sculpt Layer item
        item = parentItem.getRootGroup().findSculptChildByLogicalIndex(logicalIndex, False)

        # Whether the item is newly created ?
        isNewItem = False

        # Build a Sculpt Layer item
        if item is None:
            item = IgSplineEditorSculptLayerItem(self.view,
                parentItem.getHandle(), parentItem.getModifierParent(), plug)
            isNewItem = True
        parentItem.addSculptChild(item, pos)

        # Decorate the item if it's newly created
        if isNewItem:
            # Assign the weight control to the item
            weightIndex  = item.getIndex(IgSplineEditorTreeColumn.WEIGHT)
            weightWidget = item.getWeightWidget()
            self.view.setIndexWidget(weightIndex, weightWidget)

            # Assign the edit indicator control to the item
            editIndex  = item.getIndex(IgSplineEditorTreeColumn.EDIT)
            editWidget = item.getEditWidget()
            editWidget.setProperty(r'xgenItem', weakref.proxy(item))
            editWidget.clicked.connect(self.onEditClicked)
            self.view.setIndexWidget(editIndex, editWidget)

    def onMayaSelectionChanged(self):
        ''' Invoked when the active selection list changes '''
        if self.isUpdatingSelection:
            return
        self.delayedRefreshSelection()

    def __refreshSelection(self):
        ''' Refresh the model based on Dag hierarchy '''
        self.refreshSelectionInQueue = False

        # Build a lookup table : node -> item
        lookup = dict()
        self.__buildNodeItemLookupTable(self.worldItem, lookup)

        # Prepare the future model selection
        itemSl = QItemSelection()

        # Get the current Maya selection
        mayaSl = om.MSelectionList()
        om.MGlobal.getActiveSelectionList(mayaSl)

        # Iterate the active selection list and find corresponding items
        mayaIt = om.MItSelectionList(mayaSl)
        while not mayaIt.isDone():
            itemType = mayaIt.itemType()
            if itemType == om.MItSelectionList.kDagSelectionItem:
                # Get the dag path of the selected transform object
                dagPath = om.MDagPath()
                mayaIt.getDagPath(dagPath)
                handle = IgSplineEditorDgNode(dagPath.transform())

                # Add the item to the selection(we don't support instancing..)
                itemList = lookup.get(handle, None)
                if itemList:
                    for item in itemList:
                        index = item.getIndex()
                        itemSl.select(index, index)
            elif itemType == om.MItSelectionList.kDNselectionItem:
                # Get the node of the selected object
                node = om.MObject()
                mayaIt.getDependNode(node)
                handle = IgSplineEditorDgNode(node)

                # Add the item to the selection
                itemList = lookup.get(handle, None)
                if itemList:
                    for item in itemList:
                        index = item.getIndex()
                        itemSl.select(index, index)
            next(mayaIt)

        # Update the tree view selection
        self.isUpdatingSelection = True
        self.view.selectionModel().select(itemSl,
            QItemSelectionModel.Clear | QItemSelectionModel.Select | QItemSelectionModel.Current | QItemSelectionModel.Rows)
        self.isUpdatingSelection = False

    def __buildNodeItemLookupTable(self, item, lookup):
        ''' Build a hashtable for node -> item lookup recursively '''

        # Add lookup entry (handle -> item) to the lookup table
        handle = item.getHandle()
        if handle.isValid():
            if handle in lookup:
                lookup[handle].append(item)
            else:
                lookup[handle] = [item]

        # Recursively add tree children to the lookup table
        for i in range(0, item.getChildCount()):
            childItem = item.getChild(i)

            # We are only interested in dag and dg history items
            if (isinstance(childItem, IgSplineEditorDagItem)
                    or isinstance(childItem, IgSplineEditorHistoryItem)):
                self.__buildNodeItemLookupTable(childItem, lookup)

    def __findAncestorDescriptionItems(self, items=None):
        ''' Find the description item that is the ancestor of the given item '''
        descriptionItems = []
        deduplication    = set()

        # We use the current selection if items are not specified.
        if items is None:
            items = []
            for index in self.view.selectedIndexes():
                if index.column() == 0:
                    items.append(self.__getItemFromIndex(index))

        # Find the ancestor description items of the given items
        for item in items:
            # Iterate from bottom to top in the tree view
            while item is not None:
                # Find a transform with description shape item
                if isinstance(item, IgSplineEditorDagItem):
                    shapeItem = item.getDagShape()
                    if isinstance(shapeItem, IgSplineEditorDescriptionItem):
                        # Found a description shape item
                        if shapeItem not in deduplication:
                            descriptionItems.append(shapeItem)
                            deduplication.add(shapeItem)
                        break
                item = item.getParent()

        return descriptionItems

    def __findAncestorDescriptionHandles(self, items=None):
        ''' Find the description item that is the ancestor of the given item '''
        descriptionHandles = []
        deduplication      = set()

        # Get a list of description objects
        for item in self.__findAncestorDescriptionItems(items):
            handle = item.getHandle()
            if (handle is not None
                    and handle.isValid()
                    and handle not in deduplication):
                descriptionHandles.append(handle)
                deduplication.add(handle)
        return descriptionHandles

    def __findAncestorSculptGroupItems(self, items=None):
        ''' Find the sculpt group item that is the ancestor of the given item '''
        sculptGroupItems = []
        deduplication    = set()

        # We use the current selection if items are not specified.
        if items is None:
            items = []
            for index in self.view.selectedIndexes():
                if index.column() == 0:
                    items.append(self.__getItemFromIndex(index))

        # Find the ancestor sculpt group item of the given items
        for item in items:
            # Iterate from bottom to top in the sculpt modifier
            while isinstance(item, IgSplineEditorAbstractSculptItem):
                if item.isGroup():
                    # Found a sculpt group item
                    if item not in deduplication:
                        sculptGroupItems.append(item)
                        deduplication.add(item)
                    break
                item = item.getSculptParent()

            # Use the root group if a sculpt modifier is selected
            if isinstance(item, IgSplineEditorSculptModifierItem):
                rootGroup = item.getRootGroup()
                if rootGroup not in deduplication:
                    sculptGroupItems.append(rootGroup)
                    deduplication.add(rootGroup)

        return sculptGroupItems

    def __getModifierConnections(self, description):
        ''' Return an array of connections from description to base node '''
        connections = []

        # Get the description shape node
        node = om.MObject()
        try:
            sl = om.MSelectionList()
            sl.add(description)
            sl.getDependNode(0, node)
        except:
            return connections

        if node.isNull():
            return connections
        
        # Starting with the xgmSplineDescription.outSplineData plug
        plug = om.MFnDependencyNode(node).findPlug(r'outSplineData')
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
                pair = (getUniquePlugName(sourcePlug), getUniquePlugName(destinationPlug))
                connections.append(pair)
            
        return connections
            
    def __internalDisconnectModifier(self, description, modifier):
        ''' Disconnect a modifier from the modifier chain '''
        
        # Get the modifier connections
        connections = self.__getModifierConnections(description)
        
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
        
    def __internalInsertModifier(self, description, inOut, modifier):
        ''' Insert a modifier to the modifier chain '''
        
        # Get the modifier connections
        connections = self.__getModifierConnections(description)
        
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
        
    def __internalActivateSculptModifier(self, description, modifier):
        ''' Activate a sculpt modifier in the given description '''
            
        # Already activated ?
        prev = cmds.listConnections(description + r'.activeSculpt',
                destination=False, source=True, type=r'xgmModifierSculpt')
        if prev and len(prev) > 0 and prev[0] == modifier:
            return 

        # Connect sculpt.message to description.activeSculpt
        cmds.connectAttr(modifier + r'.message',
            description + r'.activeSculpt',
            force=True)
        cmds.setToolTo(cmds.currentCtx())

    def __internalReassignSculptModifier(self, description):
        ''' Assign a new active sculpt modifier if there is none '''

        # Get the current active sculpt modifier
        activeSculpts = cmds.listConnections(description + r'.activeSculpt', d=False, s=True)

        # Proceed if there is no active sculpt modifier
        if not activeSculpts:
            # Choose a new sculpt modifier
            historyNodes = cmds.listHistory(description, pdo=True)
            if historyNodes:
                sculptNodes = cmds.ls(historyNodes, type=r'xgmModifierSculpt')
                if sculptNodes:
                    self.__internalActivateSculptModifier(description, sculptNodes[0])

    def __isModifierShared(self, description, modifier):
        ''' Return True if the specified modifier is shared among descriptions '''

        # Get the modifier connections
        connections = self.__getModifierConnections(description)

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

    def __getNextMultiIndex(self, handle, attribute):
        ''' Get the next available multi index '''
        indices = cmds.getAttr(r'%s.%s' % (handle.name(), attribute), multiIndices=True)
        return indices[-1] + 1 if indices else 0

    def __getNextSculptModifierUIOrder(self, modifier):
        ''' Get the next UI Order '''

        # Compute a maximum uiOrder value
        uiOrder = 0

        # Inspect tweaks array
        indices = cmds.getAttr(r'%s.tweaks' % modifier, multiIndices=True)
        if indices:
            for logicalIndex in indices:
                plug = r'%s.tweaks[%d].uiOrder' % (modifier, logicalIndex)
                uiOrder = max(uiOrder, cmds.getAttr(plug))
        # Inspect tweakGroups array
        indices = cmds.getAttr(r'%s.tweakGroups' % modifier, multiIndices=True)
        if indices:
            for logicalIndex in indices:
                plug = r'%s.tweakGroups[%d].tweakGroupUIOrder' % (modifier, logicalIndex)
                uiOrder = max(uiOrder, cmds.getAttr(plug))

        return uiOrder + 1

    def __setKeyframeOnPlug(self, plug, mode=0):
        ''' Set keyframe on weight plug '''

        with MayaCmdsTransaction(r'SetKeyframe'):
            if mode == 0 or mode == 1 or mode == 2:
                if mode == 1:
                    cmds.setAttr(plug, 0.0)
                elif mode == 2:
                    cmds.setAttr(plug, 1.0)
                cmds.setKeyframe(plug)
            elif mode == 3:
                time = cmds.currentTime(q=True)
                cmds.cutKey(plug, clear=True, time=(time, time))

    def __dropDags(self, parentItem, row, srcDags):
        ''' Drop a list of dag nodes to the parent item '''

        # Reject if the item being dropped on is not a transform or world item
        if not (isinstance(parentItem, IgSplineEditorTransformItem) or
                isinstance(parentItem, IgSplineEditorWorldItem)):
            return

        # Get the full path name conveniently
        getFullPath = lambda item: om.MDagPath.getAPathTo(item.getHandle().node()).fullPathName()

        # Get the parent full path. '|' is the world (root)
        parentPath = getFullPath(parentItem) if parentItem != self.worldItem else r'|'

        # Drop to -1 row means appending
        if row < 0:
            row = parentItem.getChildCount()

        # Find a transform dag node to insert *below*
        insertBelow    = None
        insertBelowRow = row - 1
        while insertBelowRow >= 0:
            item = parentItem.getChild(insertBelowRow)
            if isinstance(item, IgSplineEditorTransformItem):
                insertBelow = getFullPath(item)
                break
            insertBelowRow = insertBelowRow - 1

        # Find a transform dag node to insert *above*. Because
        # the tree view doesn't list every transform node ...
        insertAbove    = None
        insertAboveRow = row
        while insertAboveRow < parentItem.getChildCount():
            item = parentItem.getChild(insertAboveRow)
            if isinstance(item, IgSplineEditorTransformItem):
                insertAbove = getFullPath(item)
                break
            insertAboveRow = insertAboveRow + 1

        # Perform dag modification
        with MayaCmdsTransaction(r'Reparent'):
            for dagNode in srcDags:
                # Get the current parent of the dag node. We don't support
                # instances so the following parent command will remove extra
                # parents.
                oldParentPath = cmds.listRelatives(dagNode, parent=True, fullPath=True)

                # World is the parent ?
                oldParentPath = oldParentPath[0] if oldParentPath else r'|'

                # Reparent the dag node
                if oldParentPath != parentPath:
                    if parentPath != r'|':
                        dagNode = cmds.parent(dagNode, parentPath)[0]
                    else:
                        dagNode = cmds.parent(dagNode, world=True)[0]

                # Get the full path of the dag node in its parent
                dagNode = cmds.ls(dagNode, long=True)[0]

                # Get the ordering of the children in the parent
                childrenPaths = []
                if parentPath != r'|':
                    childrenPaths = cmds.listRelatives(parentPath, children=True, fullPath=True)
                else:
                    childrenPaths = cmds.ls(assemblies=True, long=True)

                # Get the positions (slow ?)
                insertBelowIdx = childrenPaths.index(insertBelow) if insertBelow in childrenPaths else -1
                insertAboveIdx = childrenPaths.index(insertAbove) if insertAbove in childrenPaths else -1
                dagNodeIdx     = childrenPaths.index(dagNode)     if dagNode     in childrenPaths else -1

                # Offset to move the dag node in its sibilings
                offset = None

                # Move below ?
                if dagNodeIdx >= 0 and insertBelowIdx >= 0:
                    # The steps to move dag node below the target
                    offsetBelow = 0
                    if dagNodeIdx > insertBelowIdx:
                        offsetBelow = insertBelowIdx - dagNodeIdx + 1
                    else:
                        offsetBelow = insertBelowIdx - dagNodeIdx
                    # Use a minimum offset
                    if offset is None or abs(offsetBelow) < abs(offset):
                        offset = offsetBelow

                # Move above ?
                if dagNodeIdx >= 0 and insertAboveIdx >= 0:
                    # The steps to move dag node above the target
                    offsetAbove = 0
                    if dagNodeIdx < insertAboveIdx:
                        offsetAbove = insertAboveIdx - dagNodeIdx - 1
                    else:
                        offsetAbove = insertAboveIdx - dagNodeIdx
                    # Use a minimum offset
                    if offset is None or abs(offsetAbove) < abs(offset):
                        offset = offsetAbove

                # Move it
                if offset is not None:
                    cmds.reorder(dagNode, relative=offset)

        return True

    def __dropModifiers(self, parentItem, row, srcDescription, srcModifiers):
        ''' Drop a list of modifiers to the parent item '''

        # Get the spline description shape item from the parent item
        shapeItem = parentItem

        if isinstance(parentItem, IgSplineEditorDagItem):
            shapeItem = parentItem.getDagShape()

        # Reject if the shape is not a spline description shape
        if not isinstance(shapeItem, IgSplineEditorDescriptionItem):
            return False

        # Reject if drop to a different spline description
        if srcDescription != shapeItem.getNodeName():
            return False

        # Find a modifier item to insert *before*
        insertion = None
        row = row - 1
        while row >= 0:
            item = parentItem.getChild(row)
            if isinstance(item, IgSplineEditorModifierItem):
                insertion = item.getNodeName()
                break
            row = row - 1

        # Insert before description if not found
        if row < 0:
            insertion = srcDescription

        # Perform dg modification
        with MayaCmdsTransaction(r'DropModifier'):
            for modifier in srcModifiers:
                # Skip if the modifier is already at the insertion point
                if modifier == insertion:
                    continue

                # Disconnect the modifier from the history and reconnect it
                # back just before the insertion point.
                inOut = self.__internalDisconnectModifier(srcDescription, modifier)
                self.__internalInsertModifier(srcDescription, inOut, insertion)

                # Chain the next modifier
                insertion = modifier

        return True

    def __dropSculpts(self, parentItem, row, srcSculptModifier, srcSculpts):
        ''' Drop a list of sculpt groups or sculpt layers to the parent item '''

        # Behavior is different depending on the item being dropped on
        if isinstance(parentItem, IgSplineEditorSculptLayerItem):
            return self.__dropSculptsOntoLayer(parentItem, row, srcSculptModifier, srcSculpts)
        else:
            return self.__dropSculptsOntoGroup(parentItem, row, srcSculptModifier, srcSculpts)

    def __dropSculptsOntoGroup(self, parentItem, row, srcSculptModifier, srcSculpts):
        ''' Drop a list of sculpt groups or sculpt layers to a sculpt group '''

        # Get the sculpt gropu item from the parent item
        parentGroupItem = parentItem

        # Dropping to a sculpt modifier is equivalent to drop to its root group
        if isinstance(parentItem, IgSplineEditorSculptModifierItem):
            parentGroupItem = parentItem.getRootGroup()

        # Reject if the parent is not a sculpt group
        if not isinstance(parentGroupItem, IgSplineEditorSculptGroupItem):
            return False

        # Reject if drop to a different sculpt modifier
        if srcSculptModifier != parentGroupItem.getModifierParent().getNodeName():
            return False

        # Build a set for faster lookup
        srcSculptsSet = set(srcSculpts)

        # Reorder the items below the insertion
        reorderItems = []
        if row >= 0:
            for i in range(row, parentGroupItem.getSculptChildCount()):
                itemBelow = parentGroupItem.getSculptChildByIndex(i)
                if itemBelow.getPlug().name() not in srcSculptsSet:
                    reorderItems.append(itemBelow)

        # Get the logical index of the new parent group
        parentLogicalIndex = parentGroupItem.getLogicalIndex()

        # Perform dg modification
        with MayaCmdsTransaction(r'DropSculpt'):
            for plug in srcSculpts:
                # Is the plug a sculpt group or a sculpt layer ?
                isGroup = r'.tweakGroups' in plug

                # Get the attribute names
                ownerId = r'.tweakGroupOwnerId' if isGroup else r'.ownerId'
                uiOrder = r'.tweakGroupUIOrder' if isGroup else r'.uiOrder'

                # Reparent the sculpt group or sculpt layer to the new parent
                cmds.setAttr(plug + ownerId, parentLogicalIndex)

                # Order the sculpt group or the sculpt layer being moved
                newOrder = self.__getNextSculptModifierUIOrder(srcSculptModifier)
                cmds.setAttr(plug + uiOrder, newOrder)

            for item in reorderItems:
                # Get the attribute names
                uiOrder = r'.tweakGroupUIOrder' if item.isGroup() else r'.uiOrder'

                # Order the sculpt groups and the scupt layers below the insertion
                newOrder = self.__getNextSculptModifierUIOrder(srcSculptModifier)
                cmds.setAttr(item.getPlug().name() + uiOrder, newOrder)

            # Compact uiOrder to avoid integer overflow
            self.__internalCompactOrdering(srcSculptModifier)

        return True

    def __dropSculptsOntoLayer(self, parentItem, row, srcSculptModifier, srcSculpts):
        ''' Drop a list of sculpt groups or sculpt layers to a sculpt layer '''

        # Reject is the parent is not a sculpt layer
        if not isinstance(parentItem, IgSplineEditorSculptLayerItem):
            return False

        # Reject if drop to a different sculpt modifier
        if srcSculptModifier != parentItem.getModifierParent().getNodeName():
            return False

        # Get the ownerId and uiOrder of the sculpt layer. The new sculpt group
        # will be created in place of the layer.
        parentOwnerId = parentItem.getChildPlug(r'ownerId').asInt()
        parentUIOrder = parentItem.getChildPlug(r'uiOrder').asInt()

        # Perform dg modification
        with MayaCmdsTransaction(r'DropSculptNewGroup'):
            # Get the handle to the sculpt modifier
            handle = parentItem.getModifierParent().getHandle()

            # Find the next available logical index for the new group
            groupLogicalIndex = self.__getNextMultiIndex(handle, r'tweakGroups')

            # Create a new group in place of the layer
            plug = r'%s.tweakGroups[%d]' % (handle.name(), groupLogicalIndex)
            cmds.setAttr(plug + r'.tweakGroupOwnerId', parentOwnerId)
            cmds.setAttr(plug + r'.tweakGroupUIName', r'', type=r'string')
            cmds.setAttr(plug + r'.tweakGroupUIOrder', parentUIOrder)

            # Add the layer being dropped on to the group
            plug     = parentItem.getPlug().name()
            newOrder = self.__getNextSculptModifierUIOrder(srcSculptModifier)
            cmds.setAttr(plug + r'.ownerId', groupLogicalIndex)
            cmds.setAttr(plug + r'.uiOrder', newOrder)

            # Add the sculpt groups and sculpt layers being dragged to the group
            for plug in srcSculpts:
                # Is the plug a sculpt group or a sculpt layer ?
                isGroup = r'.tweakGroups' in plug

                # Get the attribute names
                ownerId = r'.tweakGroupOwnerId' if isGroup else r'.ownerId'
                uiOrder = r'.tweakGroupUIOrder' if isGroup else r'.uiOrder'

                # Reparent the sculpt group or sculpt layer to the new group
                cmds.setAttr(plug + ownerId, groupLogicalIndex)

                # Order the sculpt group or the sculpt layer being moved
                newOrder = self.__getNextSculptModifierUIOrder(srcSculptModifier)
                cmds.setAttr(plug + uiOrder, newOrder)

            # Compact uiOrder to avoid integer overflow
            self.__internalCompactOrdering(srcSculptModifier)

        return True

    def __internalCompactOrdering(self, modifier):
        ''' Compact the uiOrder to avoid integer overflow '''

        # We are going to build a uiOrder -> plug list. In case that there
        # may be two or more layers using the same uiOrder. 
        ordering = []

        # Inspect tweaks array
        indices = cmds.getAttr(r'%s.tweaks' % modifier, multiIndices=True)
        if indices:
            for logicalIndex in indices:
                plug = r'%s.tweaks[%d].uiOrder' % (modifier, logicalIndex)
                ordering.append((cmds.getAttr(plug), plug))

        # Inspect tweakGroups array
        indices = cmds.getAttr(r'%s.tweakGroups' % modifier, multiIndices=True)
        if indices:
            for logicalIndex in indices:
                plug = r'%s.tweakGroups[%d].tweakGroupUIOrder' % (modifier, logicalIndex)
                ordering.append((cmds.getAttr(plug), plug))

        # Sort by uiOrder
        ordering.sort(key=lambda x: x[0])

        # Reset uiOrder to a continuous sequence
        for i in range(0, len(ordering)):
            uiOrder, plug = ordering[i]
            if uiOrder != i:
                cmds.setAttr(plug, i)

    def renameDgNode(self, oldName, newName):
        ''' Rename a Maya dg node from oldName to newName '''
        with MayaCmdsTransaction(r'RenameNode'):
            cmds.rename(oldName, newName)

    def renameSculptGroup(self, dgNodeName, logicalIndex, newName):
        ''' Rename a Sculpt Group to a new name '''
        plug = r'%s.tweakGroups[%d].tweakGroupUIName' % (dgNodeName, logicalIndex)
        with MayaCmdsTransaction(r'RenameSculptGroup'):
            cmds.setAttr(plug, newName, type=r'string')

    def renameSculptLayer(self, dgNodeName, logicalIndex, newName):
        ''' Rename a Sculpt Layer to a new name '''
        plug = r'%s.tweaks[%d].uiName' % (dgNodeName, logicalIndex)
        with MayaCmdsTransaction(r'RenameSculptLayer'):
            cmds.setAttr(plug, newName, type=r'string')

    def addModifier(self, nodeType):
        ''' Add a modifier to the description construction history '''

        # Get a list of description handles to add modifier
        descriptionHandles = self.__findAncestorDescriptionHandles()

        # No description is selected ?
        if len(descriptionHandles) == 0:
            xglog.XGTip(maya.stringTable[u'y_xgenm_ui_xgIgSplineEditorTreeModel.kAddModifierNoSelectionTip'])
            return

        with MayaCmdsTransaction(r'AddModifier') as context:
            # createNode command will change the current selection..
            context.saveSelectionList()

            # Insert the specified modifier to the specific description
            for handle in descriptionHandles:
                # Get the name of the description dg node
                description = handle.name()
            
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
                self.__internalInsertModifier(description, inOut, description)

                # Activate the new modifier if it's a sculpt
                if cmds.objectType(modifier, isAType=r'xgmModifierSculpt'):
                    self.__internalActivateSculptModifier(description, modifier)

                # Connect a time if it's a cache
                if cmds.objectType(modifier, isAType=r'xgmSplineCache'):
                    cmds.connectAttr(r'time1.outTime', modifier + r'.time', f=True)

                # Connect outMeshData to the curve to spline's inMeshData
                if (cmds.objectType(modifier, isAType=r'xgmCurveToSpline')
                        or cmds.objectType(modifier, isAType=r'xgmModifierClump')):
                    for outPlug, inPlug in self.__getModifierConnections(description):
                        node = outPlug[:outPlug.index(r'.')]
                        if cmds.objectType(node, isAType=r'xgmSplineBase'):
                            cmds.connectAttr(node + r'.outMeshData', modifier + r'.inMeshData')
                            break

    def __findAncestorSculptGroupItem(self, item):
        # Iterate from bottom to top in the sculpt modifier
        if item.isGroup():
            item = item.getSculptParent()
            if item.isGroup():
                return item
            else:
                return None
        while isinstance(item, IgSplineEditorAbstractSculptItem):
            if item.isGroup():
                return item
            item = item.getSculptParent()

        return None

    def addLayer(self):
        ''' Add a Sculpt Layer to the sculpt modifier node '''

        # Get a list of sculpt group items to add sculpt layers
        groupItems = self.__findAncestorSculptGroupItems()

        # No sculpt group is selected ?
        if len(groupItems) == 0:
            xglog.XGTip(maya.stringTable[u'y_xgenm_ui_xgIgSplineEditorTreeModel.kAddLayerNoSelectionTip'])
            return

        # Add a sculpt layer to the selected groups
        with MayaCmdsTransaction(r'AddLayer'):
            for groupItem in groupItems:

                # Get the handle to the sculpt modifier node
                handle = groupItem.getModifierParent().getHandle()

                # Find the next available logical index to add
                logicalIndex = self.__getNextMultiIndex(handle, r'tweaks')

                # We will create a new Sculpt Layer in the group. The logical
                # index of the root group is -1. i.e. No owner.
                ownerId = groupItem.getLogicalIndex()

                # Add the last
                uiOrder = self.__getNextSculptModifierUIOrder(handle.name())

                # Create the array element by accessing it
                plug = r'%s.tweaks[%d]' % (handle.name(), logicalIndex)
                cmds.setAttr(plug + r'.ownerId', ownerId)
                cmds.setAttr(plug + r'.uiName', r'', type=r'string')
                cmds.setAttr(plug + r'.uiOrder', uiOrder)

                # Initialize newly created layer
                cmds.xgmSculptLayerInit(plug)

    def duplicateOneLayer(self, item):
        groupItem = self.__findAncestorSculptGroupItem(item)
        if groupItem == None:
            return None

        # Get the handle to the sculpt modifier node
        handle = groupItem.getModifierParent().getHandle()

        # Find the next available logical index to add
        logicalIndex = self.__getNextMultiIndex(handle, r'tweaks')

        # We will create a new Sculpt Layer in the group. The logical
        # index of the root group is -1. i.e. No owner.
        ownerId = groupItem.getLogicalIndex()

        # Add the last
        uiOrder = self.__getNextSculptModifierUIOrder(handle.name())

        # Create the array element by accessing it
        plug = r'%s.tweaks[%d]' % (handle.name(), logicalIndex)
        cmds.setAttr(plug + r'.ownerId', ownerId)
        cmds.setAttr(plug + r'.uiName', r'', type=r'string')
        cmds.setAttr(plug + r'.uiOrder', uiOrder)

        # source 
        logicalIndexSource = item.getLogicalIndex()
        handleSource = item.getModifierParent().getHandle()
        sourcePlug = r'%s.tweaks[%d]' % (handleSource.name(), logicalIndexSource)

        strength = cmds.getAttr(sourcePlug + r'.strength')
        strengthPlug = om.MFnDependencyNode(handle.node()).findPlug(r'strength', False)
        strengthPlug.selectAncestorLogicalIndex(logicalIndex, handle.attribute(r'tweaks'));
        strengthPlug.setFloat(strength)

        # Initialize newly created layer
        cmds.xgmSculptLayerMerge(plug, sourcePlug)
        return (plug, logicalIndex)

    def addOneGroup(self, item):
        groupItem = self.__findAncestorSculptGroupItem(item)
        if groupItem == None:
            return None

        # Get the handle to the sculpt modifier node
        handle = groupItem.getModifierParent().getHandle()

        # Find the next available logical index to add
        logicalIndex = self.__getNextMultiIndex(handle, r'tweakGroups')

        # We will create a new Sculpt Layer in the group. The logical
        # index of the root group is -1. i.e. No owner.
        ownerId = groupItem.getLogicalIndex()

        # Add the last
        uiOrder = self.__getNextSculptModifierUIOrder(handle.name())

        # Create the array element by accessing it
        plug = r'%s.tweakGroups[%d]' % (handle.name(), logicalIndex)
        cmds.setAttr(plug + r'.tweakGroupOwnerId', ownerId)
        cmds.setAttr(plug + r'.tweakGroupUIName', r'', type=r'string')
        cmds.setAttr(plug + r'.tweakGroupUIOrder', uiOrder)

        return (plug, logicalIndex, handle)

    def duplicateGroup(self, group):
        if not group.isGroup():
            return None
        
        newGroupPlug, logicalIndex, handle = self.addOneGroup(group)

        for i in range(0, group.getSculptChildCount()):
            item = group.getSculptChildByIndex(i)
            if item.isGroup():
                childGroupPlug, childGroupLogicalIndex = self.duplicateGroup(item)
                plug = r'%s.%s[%d].%s' % (
                        handle.name(),
                        r'tweakGroups',
                        childGroupLogicalIndex,
                        r'tweakGroupOwnerId')
                cmds.setAttr(plug, logicalIndex)
            else:
                childItem, childLogicalIndex = self.duplicateOneLayer(item)
                plug = r'%s.%s[%d].%s' % (
                        handle.name(),
                        r'tweaks',
                        childLogicalIndex,
                        r'ownerId')
                cmds.setAttr(plug, logicalIndex)

        return (newGroupPlug, logicalIndex)

    def duplicateLayerAndGroup(self):
        # We use the current selection if items are not specified.
        items = []
        for index in self.view.selectedIndexes():
            if index.column() == 0:
                item = self.__getItemFromIndex(index)
                if isinstance(item, IgSplineEditorAbstractSculptItem):
                    items.append(item)

        # No sculpt group is selected ?
        if len(items) == 0:
            xglog.XGTip(maya.stringTable[u'y_xgenm_ui_xgIgSplineEditorTreeModel.kDeleteLayerNoSelectionTip2'])
            return

        # Add a sculpt layer to the selected groups
        with MayaCmdsTransaction(r'DuplicateLayerAndGroup'):
            for item in items:
                if item.isGroup():
                    self.duplicateGroup(item)
                else:
                    self.duplicateOneLayer(item)

    def isGroupEnable(self, item):
        logicalIndexSource = item.getLogicalIndex()
        if logicalIndexSource == -1:
            return True
        handleSource = item.getModifierParent().getHandle()
        aGroupPlug = r'%s.tweakGroups[%d]' % (handleSource.name(), logicalIndexSource)
        bEnable = cmds.getAttr(aGroupPlug + r'.tweakGroupEnable')
        return bEnable

    def findGroupLeafLayers(self, group, leafLayers, bVisibleGroupOnly):
        if not self.isGroupEnable(group) and not bVisibleGroupOnly:
            return leafLayers

        for i in range(0, group.getSculptChildCount()):
            item = group.getSculptChildByIndex(i)
            if item.isGroup():
                bEnable = True
                if bVisibleGroupOnly:
                    bEnable = self.isGroupEnable(item)
                if bEnable:
                    leafLayers = self.findGroupLeafLayers(item, leafLayers, bVisibleGroupOnly)
            else:
                if not item in leafLayers:
                    leafLayers.append(item)
        return leafLayers

    def findParents(self, item):
        parents = []
        while isinstance(item, IgSplineEditorAbstractSculptItem):
            item = item.getSculptParent()
            parents.insert(0, item)
        return parents

    def findShareGroups(self, items):
        shareGroups = None
        for item in items:
            parents = self.findParents(item)
            if shareGroups == None:
                shareGroups = parents
            else:
                shareGroupsCandidate = shareGroups
                shareGroups = []
                for index in range(0, len(shareGroupsCandidate)):
                    if index < len(parents) and shareGroupsCandidate[index] == parents[index]:
                        shareGroups.append(shareGroupsCandidate[index])
        return shareGroups

    def isLayerEnable(self, item):
        logicalIndexSource = item.getLogicalIndex()
        handleSource = item.getModifierParent().getHandle()
        sourcePlug = r'%s.tweaks[%d]' % (handleSource.name(), logicalIndexSource)
        enable = cmds.getAttr(sourcePlug + r'.enable')
        return enable

    def isLayerFullEnable(self, item):
        if not self.isLayerEnable(item):
            return False

        parents = self.findParents(item)
        for parentItem in parents:
            if parentItem and isinstance(parentItem, IgSplineEditorAbstractSculptItem) and parentItem.isGroup():
                if not self.isGroupEnable(parentItem):
                    return False
        return True

    def isFullVisibleGroup(self, group):
        if not group.isGroup() or not self.isGroupEnable(group):
            return False
        for i in range(0, group.getSculptChildCount()):
            item = group.getSculptChildByIndex(i)
            if item.isGroup():
                if not self.isFullVisibleGroup(item):
                    return False
            else:
                if not self.isLayerEnable(item):
                    return False
        return True

    def getAllBrotherItems(self, item):
        allBrotherItems = []
        group = item.getSculptParent()
        for i in range(0, group.getSculptChildCount()):
            item = group.getSculptChildByIndex(i)
            allBrotherItems.append(item)
        return allBrotherItems

    def mergeLayers(self, bVisibleOnly):
        # We use the current selection if items are not specified.
        sculptItems = []
        for index in self.view.selectedIndexes():
            if index.column() == 0:
                item = self.__getItemFromIndex(index)
                if isinstance(item, IgSplineEditorAbstractSculptItem):
                    sculptItems.append(item)

        if len(sculptItems) == 0:
            xglog.XGTip(maya.stringTable[u'y_xgenm_ui_xgIgSplineEditorTreeModel.kMergeLayerNoSelectionTip'])
            return

        # Add a sculpt layer to the selected groups
        with MayaCmdsTransaction(r'MergeLayers'):
            while len(sculptItems) > 0:
                # We are not able to group sculpt items across different
                # modifiers. Create one group for each modifier in a batch.
                items    = []
                batchModifierItem   = sculptItems[0].getModifierParent()
                for i in range(len(sculptItems) - 1, -1, -1):
                    if sculptItems[i].getModifierParent() == batchModifierItem:
                        items.append(sculptItems[i])
                        del sculptItems[i]

                # select one layer means select all brother layer
                if len(items) == 1 and not items[0].isGroup():
                    items = self.getAllBrotherItems(items[0])

                # leaf layers
                layers = []
                deleteLayers = []
                for item in items:
                    if item.isGroup():
                        layers = self.findGroupLeafLayers(item, layers, True)
                    else:
                        if not item in layers:
                            layers.append(item)
                
                bHasVisibleLayer = False
                for item in layers:
                    if self.isLayerFullEnable(item) :
                        bHasVisibleLayer = True

                if not bHasVisibleLayer or len(layers) < 1 or (len(items) == 1 and not items[0].isGroup()):
                    xglog.XGTip(maya.stringTable[u'y_xgenm_ui_xgIgSplineEditorTreeModel.kMergeLayerMoreSelectionTip'])
                    continue

                # new layer
                plugs =[]
                shareGroups = self.findShareGroups(items)
                if len(shareGroups) < 1:
                    continue
                groupItem = shareGroups[len(shareGroups) - 1]

                # Get the handle to the sculpt modifier node
                handle = groupItem.getModifierParent().getHandle()

                # Find the next available logical index to add
                logicalIndex = self.__getNextMultiIndex(handle, r'tweaks')

                # We will create a new Sculpt Layer in the group. The logical
                # index of the root group is -1. i.e. No owner.
                ownerId = groupItem.getLogicalIndex()

                # Add the last
                uiOrder = self.__getNextSculptModifierUIOrder(handle.name())

                # Create the array element by accessing it
                plug = r'%s.tweaks[%d]' % (handle.name(), logicalIndex)
                cmds.setAttr(plug + r'.ownerId', ownerId)
                name = groupItem.getModel().getDefaultMergeLayerName(logicalIndex)
                cmds.setAttr(plug + r'.uiName', name, type=r'string')
                cmds.setAttr(plug + r'.uiOrder', uiOrder)
                plugs.append(plug)


                # source layers
                for item in layers:
                    logicalIndexSource = item.getLogicalIndex()
                    handleSource = item.getModifierParent().getHandle()
                    sourcePlug = r'%s.tweaks[%d]' % (handleSource.name(), logicalIndexSource)
                    if self.isLayerFullEnable(item) :
                        plugs.append(sourcePlug)
                        deleteLayers.append(item)

                # Initialize newly created layer
                cmds.xgmSculptLayerMerge(plugs)

                # detete target layer and group
                if bVisibleOnly:
                    for item in items:
                        if self.isFullVisibleGroup(item):
                            deleteLayers.append(item)
                    self.deleteSculptItems(deleteLayers)
                else:
                    self.deleteSculptItems(items)

                
    def addGroup(self):
        ''' Group selected dag nodes or Add a Sculpt Group '''

        # We can only group transforms, sculpt groups and sculpt layers
        transformItems  = []
        sculptItems     = []

        for index in self.view.selectedIndexes():
            # Get the item for the selected row
            if index.column() != 0:
                continue
            item = self.__getItemFromIndex(index)
            
            # Transform selection
            if isinstance(item, IgSplineEditorTransformItem):
                transformItems.append(item)
                continue

            # Sculpt Group or Sculpt Layer item
            if isinstance(item, IgSplineEditorAbstractSculptItem):
                sculptItems.append(item)
                continue

        # No valid selection ?
        if len(transformItems) == 0 and len(sculptItems) == 0:
            xglog.XGTip(maya.stringTable[u'y_xgenm_ui_xgIgSplineEditorTreeModel.kAddGroupNoSelectionTip'])
            return

        with MayaCmdsTransaction(r'AddGroup') as context:

            # Group transform nodes
            if len(transformItems) > 0:
                # group command will change the current selection..
                context.saveSelectionList()

                # Get the names of the transform nodes. We don't support
                # instances so group command may fail on instances..
                transforms = []
                for item in transformItems:
                    transforms.append(item.getHandle().name())

                # Group the selected transform nodes
                cmds.group(transforms)

            # Group sculpt items
            while len(sculptItems) > 0:
                # We are not able to group sculpt items across different
                # modifiers. Create one group for each modifier in a batch.
                batchSculptItems    = []
                batchModifierItem   = sculptItems[0].getModifierParent()

                for i in range(len(sculptItems) - 1, -1, -1):
                    if sculptItems[i].getModifierParent() == batchModifierItem:
                        batchSculptItems.append(sculptItems[i])
                        del sculptItems[i]

                # Get the handle to the sculpt modifier node
                handle = batchModifierItem.getHandle()

                # Find the next available logical index to add
                logicalIndex = self.__getNextMultiIndex(handle, r'tweakGroups')

                # We will create a new Sculpt Group in the same group of the first
                # selected Sculpt Group or Sculpt Layer. The logical index of the
                # root group is -1. i.e. No owner.
                ownerId = batchSculptItems[0].getSculptParent().getLogicalIndex()

                # Add the last
                uiOrder = self.__getNextSculptModifierUIOrder(handle.name())

                # Create the array element by accessing it
                plug = r'%s.tweakGroups[%d]' % (handle.name(), logicalIndex)
                cmds.setAttr(plug + r'.tweakGroupOwnerId', ownerId)
                cmds.setAttr(plug + r'.tweakGroupUIName', r'', type=r'string')
                cmds.setAttr(plug + r'.tweakGroupUIOrder', uiOrder)

                # Set the new group as the owner of the selected items
                for item in batchSculptItems:
                    plug = r'%s.%s[%d].%s' % (
                        handle.name(),
                        r'tweakGroups' if item.isGroup() else r'tweaks',
                        item.getLogicalIndex(),
                        r'tweakGroupOwnerId' if item.isGroup() else r'ownerId')
                    cmds.setAttr(plug, logicalIndex)

    def duplicateItem(self):
        ''' Duplicate the selected items '''

        # Get the current selected items
        modifierItems = []

        for index in self.view.selectedIndexes():
            # Get the item for the selected row
            if index.column() != 0:
                continue
            item = self.__getItemFromIndex(index)

            # Modifier ?
            if isinstance(item, IgSplineEditorModifierItem):
                modifierItems.append(item)
                continue

        # Nothing is selected ?
        if len(modifierItems) == 0:
            xglog.XGTip(maya.stringTable[u'y_xgenm_ui_xgIgSplineEditorTreeModel.kDuplicateNoSelectionTip'])
            return

        with MayaCmdsTransaction(r'Duplicate'):
            for item in modifierItems:
                # Get the modifier dg node name to duplicate
                modifier = item.getNodeName()

                # Get the owner description node name
                description = item.getDescription().getNodeName()

                # Ensure the modifier exists
                if not cmds.objExists(modifier):
                    cmds.warning(maya.stringTable[u'y_xgenm_ui_xgIgSplineEditorTreeModel.kModifierToDuplicateNotExist'] % modifier)
                    continue

                # Ensure the description exists
                if not cmds.objExists(description):
                    cmds.warning(maya.stringTable[u'y_xgenm_ui_xgIgSplineEditorTreeModel.kDescriptionToDuplicateNotExist'] % description)
                    continue

                # Get the modifier connections
                connections = self.__getModifierConnections(description)

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
                self.__internalInsertModifier(description, inOut, insertion)
                
                # Activate the new modifier if it's a sculpt
                if cmds.objectType(replicant, isAType=r'xgmModifierSculpt'):
                    self.__internalActivateSculptModifier(description, replicant)

                # Connect a time if it's a cache
                if cmds.objectType(replicant, isAType=r'xgmSplineCache'):
                    cmds.connectAttr(r'time1.outTime', replicant + r'.time', f=True)

                # Connect outMeshData to the curve to spline's inMeshData
                if (cmds.objectType(replicant, isAType=r'xgmCurveToSpline')
                        or cmds.objectType(replicant, isAType=r'xgmModifierClump')):
                    for outPlug, inPlug in self.__getModifierConnections(description):
                        node = outPlug[:outPlug.index(r'.')]
                        if cmds.objectType(node, isAType=r'xgmSplineBase'):
                            cmds.connectAttr(node + r'.outMeshData', replicant + r'.inMeshData')
                            break

            # Multiple Maya commands will change the selection. We refresh the
            # selection again after all commands are executed.
            QTimer.singleShot(0, lambda: self.__refreshSelection())

    def moveItem(self, direction):
        ''' Move the selected items '''

        # Get the current selected items
        transformItems  = {}
        modifierItems   = {}
        sculptItems     = {}

        for index in self.view.selectedIndexes():
            # Get the item for the selected row
            if index.column() != 0:
                continue
            item = self.__getItemFromIndex(index)

            # We group items with the same parent because we can't move
            # items out of its parent.
            parentIndex = index.parent()

            # Transform ?
            if isinstance(item, IgSplineEditorTransformItem):
                if parentIndex in transformItems:
                    transformItems[parentIndex].append(item)
                else:
                    transformItems[parentIndex] = [item]
                continue

            # Modifier ?
            if isinstance(item, IgSplineEditorModifierItem):
                if parentIndex in modifierItems:
                    modifierItems[parentIndex].append(item)
                else:
                    modifierItems[parentIndex] = [item]
                continue

            # Sculpt Layer or Sculpt Group ?
            if isinstance(item, IgSplineEditorAbstractSculptItem):
                if parentIndex in sculptItems:
                    sculptItems[parentIndex].append(item)
                else:
                    sculptItems[parentIndex] = [item]
                continue

        # Nothing is selected ?
        if (len(transformItems) == 0
                and len(modifierItems) == 0
                and len(sculptItems) == 0):
            xglog.XGTip(maya.stringTable[u'y_xgenm_ui_xgIgSplineEditorTreeModel.kMoveNoSelectionTip'])
            return

        # Sort the children with the same parent. For example, we move
        # the last item first when moving items down.
        for items in [transformItems, sculptItems]:
            for parentIndex, children in list(items.items()):
                if direction > 0:
                    children.sort(key=lambda x: x.getIndex().row())
                else:
                    children.sort(key=lambda x: -x.getIndex().row())
        # We use insertBefore so always the reverse direction
        for parentIndex, children in list(modifierItems.items()):
            children.sort(key=lambda x: -x.getIndex().row())

        with MayaCmdsTransaction(r'UberMove'):
            # Move sculpt groups and layers
            for parentIndex, children in list(sculptItems.items()):
                # Get the parent item from the index
                parentItem = self.__getItemFromIndex(parentIndex)

                # Move children one by one
                for item in children:
                    # Get the modifier dg node name
                    index    = item.getIndex()
                    modifier = item.getModifierParent().getNodeName()

                    # We are going to swap the UI order of two items
                    plugA = item.getChildPlug(r'tweakGroupUIOrder' if item.isGroup() else r'uiOrder').name()
                    plugB = None

                    if direction > 0:
                        # Get the item above the item being moved
                        indexAbove = index
                        while indexAbove.isValid() and self.__getItemFromIndex(indexAbove) in children:
                            indexAbove = indexAbove.sibling(indexAbove.row() - 1, indexAbove.column())
                        if not indexAbove.isValid():
                            continue
                        itemAbove = self.__getItemFromIndex(indexAbove)

                        # Swap the UI order with the item above
                        plugB = itemAbove.getChildPlug(r'tweakGroupUIOrder' if itemAbove.isGroup() else r'uiOrder').name()
                    else:
                        # Get the item below the item being moved
                        indexBelow = index
                        while indexBelow.isValid() and self.__getItemFromIndex(indexBelow) in children:
                            indexBelow = indexBelow.sibling(indexBelow.row() + 1, indexBelow.column())
                        if not indexBelow.isValid():
                            continue
                        itemBelow = self.__getItemFromIndex(indexBelow)

                        # Swap the UI order with the item below
                        plugB = itemBelow.getChildPlug(r'tweakGroupUIOrder' if itemBelow.isGroup() else r'uiOrder').name()

                    # Move it
                    uiOrderA = cmds.getAttr(plugA)
                    uiOrderB = cmds.getAttr(plugB)
                    cmds.setAttr(plugA, uiOrderB)
                    cmds.setAttr(plugB, uiOrderA)

            # Move modifier nodes
            for parentIndex, children in list(modifierItems.items()):
                # Get the parent item from the index
                parentItem = self.__getItemFromIndex(parentIndex)

                # Move children one by one
                for item in children:
                    # Get the modifier dg node name
                    index    = item.getIndex()
                    modifier = item.getNodeName()

                    # Get the description node name
                    description = item.getDescription().getNodeName()

                    # The insertion point of the modifier
                    insertion = None

                    if direction > 0:
                        # Get the item above the item being moved
                        indexAbove = index
                        while indexAbove.isValid() and self.__getItemFromIndex(indexAbove) in children:
                            indexAbove = indexAbove.sibling(indexAbove.row() - 1, indexAbove.column())
                        if not indexAbove.isValid():
                            continue

                        # Move a modifier topmost means inserting it before
                        # the description node
                        insertBeforeIndex = indexAbove.sibling(indexAbove.row() - 1, indexAbove.column())
                        while insertBeforeIndex.isValid() and self.__getItemFromIndex(insertBeforeIndex) in children:
                            insertBeforeIndex = insertBeforeIndex.sibling(insertBeforeIndex.row() - 1, insertBeforeIndex.column())
                        if insertBeforeIndex.isValid():
                            insertion = self.__getItemFromIndex(insertBeforeIndex).getNodeName()
                        else:
                            insertion = description

                    else:
                        # Get the item below the item being moved
                        indexBelow = index
                        while indexBelow.isValid() and self.__getItemFromIndex(indexBelow) in children:
                            indexBelow = indexBelow.sibling(indexBelow.row() + 1, indexBelow.column())
                        if not indexBelow.isValid():
                            continue
                        if isinstance(self.__getItemFromIndex(indexBelow), IgSplineEditorBaseNodeItem):
                            continue
                        insertion = self.__getItemFromIndex(indexBelow).getNodeName()

                    # Move it
                    inOut = self.__internalDisconnectModifier(description, modifier)
                    self.__internalInsertModifier(description, inOut, insertion)

            # Move transform nodes
            for parentIndex, children in list(transformItems.items()):
                # Get the parent item from the index
                parentItem = self.__getItemFromIndex(parentIndex)

                # Move children one by one
                for item in children:
                    # Get the full dag path
                    index      = item.getIndex()
                    dagPath    = cmds.ls(item.getNodeName(), long=True)[0]
                    parentPath = cmds.ls(parentItem.getNodeName(), long=True)[0] if parentItem != self.worldItem else r'|'

                    # Get the ordering of the children in the parent
                    childrenPaths = []
                    if parentPath != r'|':
                        childrenPaths = cmds.listRelatives(parentPath, children=True, fullPath=True)
                    else:
                        childrenPaths = cmds.ls(assemblies=True, long=True)

                    # Get the position of the node being moved
                    dagNodeIdx = childrenPaths.index(dagPath)

                    # Offset to move the dag node in its siblings
                    offset = None

                    if direction > 0:
                        # Get the item above the item being moved
                        indexAbove = index
                        while indexAbove.isValid() and self.__getItemFromIndex(indexAbove) in children:
                            indexAbove = indexAbove.sibling(indexAbove.row() - 1, indexAbove.column())
                        if not indexAbove.isValid():
                            continue
                        itemAbove = self.__getItemFromIndex(indexAbove)

                        # Get the position of the item above
                        insertAbove = cmds.ls(itemAbove.getNodeName(), long=True)[0]
                        insertAboveIdx = childrenPaths.index(insertAbove)

                        # The steps to move dag node above the target
                        if dagNodeIdx < insertAboveIdx:
                            offset = insertAboveIdx - dagNodeIdx - 1
                        else:
                            offset = insertAboveIdx - dagNodeIdx
                    else:
                        # Get the item below the item being moved
                        indexBelow = index
                        while indexBelow.isValid() and self.__getItemFromIndex(indexBelow) in children:
                            indexBelow = indexBelow.sibling(indexBelow.row() + 1, indexBelow.column())
                        if not indexBelow.isValid():
                            continue
                        itemBelow = self.__getItemFromIndex(indexBelow)

                        # Get the position of the item below
                        insertBelow = cmds.ls(itemBelow.getNodeName(), long=True)[0]
                        insertBelowIdx = childrenPaths.index(insertBelow)

                        # The steps to move dag node below the target
                        if dagNodeIdx > insertBelowIdx:
                            offset = insertBelowIdx - dagNodeIdx + 1
                        else:
                            offset = insertBelowIdx - dagNodeIdx

                    # Move it
                    if offset is not None:
                        cmds.reorder(dagPath, relative=offset)

    def deleteSculptItems(self, sculptItems):
        # Delete Sculpt Layers or/and Sculpt Groups. Recursively delete
        # child layers and groups.
        deletedGroupItems = set()
        while len(sculptItems) > 0:
            # Pop one item to delete
            item = sculptItems.pop()

            # Also delete the children of a sculpt group
            if item.isGroup() and item not in deletedGroupItems:
                # Ensure the children of the group is deleted first
                sculptItems.append(item)
                deletedGroupItems.add(item)
                for i in range(0, item.getSculptChildCount()):
                    sculptItems.append(item.getSculptChildByIndex(i))
                continue

            # Get the handle of the modifier node
            handle = item.getModifierParent().getHandle()

            # Skip the already deleted modifier node
            if not handle.isValid():
                continue

            # Get the logical index of the item
            logicalIndex = item.getLogicalIndex()

            # Update the active tweak if it's out-of-bound
            if not item.isGroup():
                # Get the current layer logical indices
                plug = handle.name() + r'.tweaks'
                indices = cmds.getAttr(plug, multiIndices=True)

                # Pretend we have deleted the logical index
                if logicalIndex in indices:
                    indices.remove(logicalIndex)

                # Get the current active tweak
                plug = handle.name() + r'.activeTweak'
                activeTweak = cmds.getAttr(plug) - 1

                # The active tweak is out-of-bound, set it to the last layer.
                if activeTweak >= len(indices):
                    cmds.setAttr(plug, len(indices) if indices else 1)

            # item should be a layer or an empty group
            if item.isGroup():
                plug = r'%s.tweakGroups[%d]' % (handle.name(), logicalIndex)
                cmds.removeMultiInstance(plug, b=True)
            else:
                # Stop watching plug changes any more.
                item.retire()
                plug = r'%s.tweaks[%d]' % (handle.name(), logicalIndex)
                cmds.removeMultiInstance(plug, b=True)

    def deleteItem(self):
        ''' Delete the selected items '''

        # Get the current selected items
        transformItems  = []
        modifierItems   = []
        sculptItems     = []

        for index in self.view.selectedIndexes():
            # Get the item for the selected row
            if index.column() != 0:
                continue
            item = self.__getItemFromIndex(index)

            # Transform ?
            if isinstance(item, IgSplineEditorTransformItem):
                transformItems.append(item)
                continue

            # Modifier ?
            if isinstance(item, IgSplineEditorModifierItem):
                modifierItems.append(item)
                continue

            # Sculpt Layer or Sculpt Group ?
            if isinstance(item, IgSplineEditorAbstractSculptItem):
                sculptItems.append(item)
                continue

        # Nothing is selected ?
        if (len(transformItems) == 0
                and len(modifierItems) == 0
                and len(sculptItems) == 0):
            xglog.XGTip(maya.stringTable[u'y_xgenm_ui_xgIgSplineEditorTreeModel.kDeleteNoSelectionTip'])
            return

        with MayaCmdsTransaction(r'UberDelete'):
            
            # Delete transform and modifiers. Maya's delete command should
            # recursively delete child transform nodes. Modifiers should
            # implement MPxNode::passThroughToOne() so that the input/output
            # connections are fixed when the modifier is deleted automatically.
            nodesToDelete = []
            for item in transformItems + modifierItems:
                nodesToDelete.append(item.getHandle().name())
            if len(nodesToDelete) > 0:
                cmds.delete(nodesToDelete)

            # If the current description is deleted in the above operation, we
            # choose the next description as the new current description.
            if not xgg.IgSplineEditor.currentDescription():
                descriptions = cmds.xgmSplineQuery(listSplineDescriptions=True, shape=True)
                if descriptions and descriptions[0]:
                    cmds.xgmSplineSetCurrentDescription(descriptions[0])

            # If the current sculpt modifier item is deleted, we choose another
            # sculpt modifier as the new active sculpt.
            for item in modifierItems:
                if isinstance(item, IgSplineEditorSculptModifierItem):
                    handle = item.getDescription().getHandle()
                    if handle.isValid():
                        self.__internalReassignSculptModifier(handle.name())

            # Delete Sculpt Layers or/and Sculpt Groups. Recursively delete
            # child layers and groups.
            deletedGroupItems = set()
            while len(sculptItems) > 0:
                # Pop one item to delete
                item = sculptItems.pop()

                # Also delete the children of a sculpt group
                if item.isGroup() and item not in deletedGroupItems:
                    # Ensure the children of the group is deleted first
                    sculptItems.append(item)
                    deletedGroupItems.add(item)
                    for i in range(0, item.getSculptChildCount()):
                        sculptItems.append(item.getSculptChildByIndex(i))
                    continue

                # Get the handle of the modifier node
                handle = item.getModifierParent().getHandle()

                # Skip the already deleted modifier node
                if not handle.isValid():
                    continue

                # Get the logical index of the item
                logicalIndex = item.getLogicalIndex()

                # Update the active tweak if it's out-of-bound
                if not item.isGroup():
                    # Get the current layer logical indices
                    plug = handle.name() + r'.tweaks'
                    indices = cmds.getAttr(plug, multiIndices=True)

                    # Pretend we have deleted the logical index
                    if logicalIndex in indices:
                        indices.remove(logicalIndex)

                    # Get the current active tweak
                    plug = handle.name() + r'.activeTweak'
                    activeTweak = cmds.getAttr(plug) - 1

                    # The active tweak is out-of-bound, set it to the last layer.
                    if activeTweak >= len(indices):
                        cmds.setAttr(plug, len(indices) if indices else 1)

                # item should be a layer or an empty group
                if item.isGroup():
                    plug = r'%s.tweakGroups[%d]' % (handle.name(), logicalIndex)
                    cmds.removeMultiInstance(plug, b=True)
                else:
                    # Stop watching plug changes any more.
                    item.retire()
                    plug = r'%s.tweaks[%d]' % (handle.name(), logicalIndex)
                    cmds.removeMultiInstance(plug, b=True)

    def makeCurrent(self, item):
        ''' Make the Sculpt Layer item to be the current '''

        # Not a Sculpt Layer item ?
        if not isinstance(item, IgSplineEditorSculptLayerItem):
            return
        
        # Get the description handle
        descriptionHandle = item.getModifierParent().getDescription().getHandle()

        # Get the sculpt modifier handle
        sculptModifierHandle = item.getModifierParent().getHandle()

        # Get the logical index of the sculpt layer
        logicalIndex = item.getLogicalIndex()

        # Get the full path to the description shape. We don't support
        # instances so just get the first path.
        description = om.MDagPath.getAPathTo(descriptionHandle.node()).fullPathName()

        with MayaCmdsTransaction(r'SetCurrentSculptLayer'):
            # Set the current spline description (undoable)
            cmds.xgmSplineSetCurrentDescription(description)

            # Set the current sculpt modifier
            self.__internalActivateSculptModifier(
                descriptionHandle.name(),
                sculptModifierHandle.name())

            # Get the current layer indices
            indices = cmds.getAttr(
                r'%s.tweaks' % sculptModifierHandle.name(), multiIndices=True)

            # Set the current sculpt layer
            for i in range(0, len(indices)):
                if indices[i] == logicalIndex:
                    # Get the physical index...
                    cmds.setAttr(r'%s.activeTweak' % sculptModifierHandle.name(), i + 1)
                    break

    def onClicked(self, index):
        ''' Slot when a mouse button is clicked in a cell '''

        # Get the item from the index
        item = self.__getItemFromIndex(index)

        # Get the column being clicked
        column = index.column()

        if isinstance(item, IgSplineEditorTransformItem):
            # Transform
            if column == IgSplineEditorTreeColumn.ENABLE:
                # Transform / Visibility column is clicked
                plug = r'%s.visibility' % item.getHandle().name()
                vis  = cmds.getAttr(plug)
                with MayaCmdsTransaction(r'ToggleVisibility'):
                    cmds.setAttr(plug, not vis)

        elif isinstance(item, IgSplineEditorModifierItem):
            # Modifier
            if column == IgSplineEditorTreeColumn.ENABLE:
                # Skip hidden mute (not implemented)
                if cmds.attributeQuery(r'mute', node=item.getNodeName(), hidden=True):
                    return
                # Modifier / Enable column is clicked
                plug = r'%s.mute' % item.getHandle().name()
                mute = cmds.getAttr(plug)
                with MayaCmdsTransaction(r'ToggleModifierMute'):
                    cmds.setAttr(plug, not mute)

        elif isinstance(item, IgSplineEditorAbstractSculptItem):
            # Sculpt Group or Sculpt Layer
            if column == IgSplineEditorTreeColumn.ENABLE:
                # Sculpt Group or Sculpt Layer / Enable column is clicked
                plug = r'%s.%s[%d].%s' % (
                    item.getHandle().name(),
                    r'tweakGroups' if item.isGroup() else r'tweaks',
                    item.getLogicalIndex(),
                    r'tweakGroupEnable' if item.isGroup() else r'enable')
                isEnabled = cmds.getAttr(plug)
                with MayaCmdsTransaction(r'ToggleVisibility'):
                    cmds.setAttr(plug, not isEnabled)

            elif column == IgSplineEditorTreeColumn.KEY:
                if isinstance(item, IgSplineEditorSculptLayerItem):
                    # Key layer weights
                    self.__setKeyframeOnPlug(item.getChildPlug(r'strength').name())

    def onCustomContextMenuRequested(self, pos):
        ''' Slot when a custom context menu is requested '''

        # Get the index under the mouse cursor
        index   = self.view.indexAt(pos)
        column  = index.column()
        item    = self.__getItemFromIndex(index)

        if isinstance(item, IgSplineEditorAbstractSculptItem):
            # Sculpt Group or Sculpt Layer
            if column == IgSplineEditorTreeColumn.KEY:
                if isinstance(item, IgSplineEditorSculptLayerItem):
                    # Key column of Sculpt Layer
                    plug = item.getChildPlug(r'strength').name()

                    # Check if the plug is on keyframe
                    plugWatcher = PlugWatcher()
                    plugWatcher.connectPlug(plug)
                    isOnKeyframe, keyValue = plugWatcher.isPlugOnKey()

                    popupMenu = QMenu()
                    popupMenu.addAction(
                        maya.stringTable[u'y_xgenm_ui_xgIgSplineEditorTreeModel.kSetKeyframeKeyAtCurrent'],
                        lambda plug=plug: self.__setKeyframeOnPlug(plug, 0))
                    popupMenu.addAction(
                        maya.stringTable[u'y_xgenm_ui_xgIgSplineEditorTreeModel.kSetKeyframeKeyAt0'],
                        lambda plug=plug: self.__setKeyframeOnPlug(plug, 1))
                    popupMenu.addAction(
                        maya.stringTable[u'y_xgenm_ui_xgIgSplineEditorTreeModel.kSetKeyframeKeyAt1'],
                        lambda plug=plug: self.__setKeyframeOnPlug(plug, 2))
                    popupMenu.addSeparator()
                    removeKeyItem = popupMenu.addAction(
                        maya.stringTable[u'y_xgenm_ui_xgIgSplineEditorTreeModel.kSetKeyframeRemoveKey'],
                        lambda plug=plug: self.__setKeyframeOnPlug(plug, 3))
                    removeKeyItem.setEnabled(isOnKeyframe)
                    popupMenu.exec_(self.view.viewport().mapToGlobal(pos))
                    return

        # Context Menus for various item types
        if column == IgSplineEditorTreeColumn.NAME:
            # Build a popup menu for the item under the cursor
            popupMenu = QMenu()

            # Add Modifier menu. Only presence in Descriptions
            if isinstance(item, IgSplineEditorDagItem):
                if isinstance(item.getDagShape(), IgSplineEditorDescriptionItem):
                    # A sub-menu contains a list of available modifiers to add
                    subMenu = popupMenu.addMenu(maya.stringTable[u'y_xgenm_ui_xgIgSplineEditorTreeModel.kContextMenuAddModifier'])
                    for nodeType in getSplineModifierTypes():
                        subMenu.addAction(
                            CreateIcon(getSplineModifierIcon(nodeType)),
                            getSplineNodeNiceName(nodeType),
                            lambda nodeType=nodeType: self.addModifier(nodeType))
                    popupMenu.addSeparator()

            # Group menu. Modifiers doesn't support groups.
            if not isinstance(item, IgSplineEditorHistoryItem):
                popupMenu.addAction(
                    maya.stringTable[u'y_xgenm_ui_xgIgSplineEditorTreeModel.kContextMenuGroup'],
                    lambda: self.addGroup())

            # Rename menu.
            popupMenu.addAction(
                maya.stringTable[u'y_xgenm_ui_xgIgSplineEditorTreeModel.kContextMenuRename'],
                lambda index=index: self.delayedEdit(index))
            
            # Duplicte menu. We currently only support duplicating modifiers.
            if isinstance(item, IgSplineEditorModifierItem):
                popupMenu.addAction(
                    maya.stringTable[u'y_xgenm_ui_xgIgSplineEditorTreeModel.kContextMenuDuplicate'],
                    lambda: self.duplicateItem())
            
            if isinstance(item, IgSplineEditorAbstractSculptItem):
                popupMenu.addAction(
                    maya.stringTable[u'y_xgenm_ui_xgIgSplineEditorTreeModel.kContextMenuLayerDuplicate'],
                    lambda: self.duplicateLayerAndGroup())

            # Delete menu. Base node is not deleteable.
            if not isinstance(item, IgSplineEditorBaseNodeItem):
                popupMenu.addAction(
                    maya.stringTable[u'y_xgenm_ui_xgIgSplineEditorTreeModel.kContextMenuDelete'],
                    lambda: self.deleteItem())
            
            popupMenu.addSeparator()
            
            # Merge menu
            if isinstance(item, IgSplineEditorAbstractSculptItem):
                popupMenu.addAction(
                    maya.stringTable[u'y_xgenm_ui_xgIgSplineEditorTreeModel.kContextMenuMerge'],
                    lambda: self.mergeLayers(False))
            
            # Merge menu
            if isinstance(item, IgSplineEditorAbstractSculptItem):
                popupMenu.addAction(
                    maya.stringTable[u'y_xgenm_ui_xgIgSplineEditorTreeModel.kContextMenuMergeVisible'],
                    lambda: self.mergeLayers(True))

            # Show the menu
            popupMenu.exec_(self.view.viewport().mapToGlobal(pos))
            return

    def delayedEdit(self, index):
        ''' Slot when the Rename menu item is clicked '''
        QTimer.singleShot(0, lambda: self.view.edit(index))

    def onEditClicked(self):
        ''' Slot when the Edit button is clicked '''
        
        # Get the item from sender. All Edit buttons are connected to this slot.
        item = self.sender().property(r'xgenItem')

        # Set the Sculpt Layer item as the current
        self.makeCurrent(item)

        # Reset tool
        cmds.setToolTo(cmds.currentCtx())

    def onSelectionChanged(self, selected, deselected):
        ''' Slot when the selection changes '''
        
        # Ignored when we are updating selection from Maya
        if self.isUpdatingSelection:
            return

        # Hack to determine if we are going to merge selections with Maya.
        # When Shift or Ctrl is pressed, we merge the selection instead of 
        # reset the whole selection list.
        isMerge = (QGuiApplication.keyboardModifiers() == Qt.ShiftModifier or
                   QGuiApplication.keyboardModifiers() == Qt.ControlModifier)

        if isMerge:
            self.__mergeMayaSelection(selected, deselected)
        else:
            self.__replaceMayaSelection()

        # Reset tools after we changed Maya selection
        currentCtx = cmds.currentCtx()
        if currentCtx and currentCtx.startswith(r'xgm'):
            cmds.setToolTo(currentCtx)

    def __mergeMayaSelection(self, selected, deselected):
        ''' Merge the selection changes to Maya selection '''

        # Future maya selection changes
        slToAdd = []
        slToDel = []

        # Merge items to select
        for index in selected.indexes():
            # Get the item to select
            item = self.__getItemFromIndex(index)

            # Select the dag/dg node
            if (isinstance(item, IgSplineEditorDagItem)
                    or isinstance(item, IgSplineEditorHistoryItem)):
                if item.getHandle().isValid():
                    slToAdd.append(item.getHandle().name())

        # Merge items to deselect
        for index in deselected.indexes():
            # Get the item to deselect
            item = self.__getItemFromIndex(index)

            # Deselect the dag/dg node
            if (isinstance(item, IgSplineEditorDagItem)
                    or isinstance(item, IgSplineEditorHistoryItem)):
                if item.getHandle().isValid():
                    slToDel.append(item.getHandle().name())

        # Perform the selection
        self.isUpdatingSelection = True
        if len(slToAdd) > 0:
            cmds.select(slToAdd, add=True, noExpand=True)
        if len(slToDel) > 0:
            cmds.select(slToDel, deselect=True, noExpand=True)
        self.isUpdatingSelection = False

    def __replaceMayaSelection(self):
        ''' Replace the Maya selection with the current model selection '''

        # Future maya selection
        sl = []

        # Convert the current model selection to maya selection
        selectedRows = self.view.selectionModel().selectedRows()
        for index in selectedRows:
            # Get the item of the selected row
            item = self.__getItemFromIndex(index)

            # Update dag/dg selection
            if (isinstance(item, IgSplineEditorDagItem)
                    or isinstance(item, IgSplineEditorHistoryItem)):
                if item.getHandle().isValid():
                    sl.append(item.getHandle().name())

        # Perform the selection
        self.isUpdatingSelection = True
        if len(sl) > 0:
            cmds.select(sl, r=True, noExpand=True)
        self.isUpdatingSelection = False

    def __descriptionItemCreated(self, item):
        ''' Cache the description item for faster lookup '''
        self.descriptionItems.append(weakref.ref(item, self.__descriptionItemDestroyed))

    def __descriptionItemDestroyed(self, item):
        ''' Clean up the weak proxy when the item dies '''
        self.descriptionItems.remove(item)












# ===========================================================================
# Copyright 2021 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
