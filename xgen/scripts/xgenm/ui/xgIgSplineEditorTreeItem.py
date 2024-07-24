import maya
maya.utils.loadStringResourcesForModule(__name__)

from builtins import object
from builtins import range
import weakref

pysideVersion = r'-1'
import PySide2, PySide2.QtCore, PySide2.QtGui, PySide2.QtWidgets
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
pysideVersion = PySide2.__version__

from xgenm.ui.util.xgIgSplineUtil import *
from xgenm.ui.util.xgUtil import *
from xgenm.ui.widgets import *
from xgenm.ui.xgIgSplineEditorDgWatcher import *

'''
    Column definition of all items
'''
class IgSplineEditorTreeColumn(object):

    # Column enum
    NAME    = 0
    ENABLE  = 1
    WEIGHT  = 2
    EDIT    = 3
    KEY     = 4
    COUNT   = 5

    # Column height
    HEIGHT  = 26
    INDENT  = 20


'''
    MIME data for dragging
'''
class IgSplineEditorMimeData(object):

    # Drag & Drop constants
    MIME_TYPE_DAG       = r'application/xgenigsplineeditor-dag'
    MIME_TYPE_MODIFIER  = r'application/xgenigsplineeditor-modifier'
    MIME_TYPE_SCULPT    = r'application/xgenigsplineeditor-sculpt'

    MIME_TYPES = [MIME_TYPE_DAG, MIME_TYPE_MODIFIER, MIME_TYPE_SCULPT]


'''
    StyleSheet for items
'''
class IgSplineEditorTreeStyle(object):

    # StyleSheet for Edit button
    EditButtonStyleCommon = (r'''
        QPushButton::pressed
        {
            color: #EEEEEE;
            background-color: #1D1D1D;
            border: 1px solid #191919;
        }
        QPushButton::disabled
        {
            color: #808080;
            background-color: #4B4B4B;
            border: 1px solid #4D4D4D;
        }
    ''')

    EditButtonStyleInactive = (r'''
        QPushButton
        {
            background-color: #5D5D5D;
            border: 1px solid #626262;
        }
        QPushButton::hover
        {
            background-color: #707070;
            border: 1px solid #757575;
        }
    ''' + EditButtonStyleCommon)

    EditButtonStyleActive = (r'''
        QPushButton
        {
            background-color: #DF2020;
            border: 1px solid #E42525;
        }
        QPushButton::hover
        {
            background-color: #DF3333;
            border: 1px solid #E43838;
        }
    ''' + EditButtonStyleCommon)


'''
    Base class for all column types in Interactive Groom Editor.
'''
class IgSplineEditorTreeItem(object):

    # Reference to the QTreeView
    view = None

    def __init__(self, view):
        ''' Constructor '''
        self.view = view

    def flags(self, column):
        ''' Return the item flags for the given index '''
        
        # Default flags for all columns
        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        
        # Name column is draggable
        if column == IgSplineEditorTreeColumn.NAME:
            flags = flags | Qt.ItemIsDragEnabled

        return flags

    def data(self, column, role):
        ''' Return the data stored under the given role '''

        # Common roles for all items
        if role == Qt.SizeHintRole:
            # Uniform row height. Width is determined by header view.
            return QSize(DpiScale(1), DpiScale(IgSplineEditorTreeColumn.HEIGHT))

        return None

    def setData(self, column, value, role):
        ''' Set the role data for the item at index to value '''
        return False

    def getView(self):
        ''' Get the QTreeView reference '''
        return self.view

    def getModel(self):
        ''' Get the QAbstractItemModel reference '''
        return self.view.model()

    def getIndex(self, column = 0):
        ''' Get the QModelIndex of the item '''
        return self.view.model().itemToIndex(self, column)

    def getChildCount(self):
        ''' Return the number of children in the tree '''
        return 0

    def getChild(self, i):
        ''' Return the i-th child of this item in the tree '''
        return None

    def getParent(self):
        ''' Return the parent of this item in the tree '''
        return None

    def getChildIndex(self, item):
        ''' Return the index of the child item '''
        for i in range(0, self.getChildCount()):
            if self.getChild(i) == item:
                return i
        raise Exception(r'%s is not a child of %s' % (str(item), str(self)))

    def emitDataChanged(self):
        ''' Emit a dataChanged signal '''
        self.getModel().emit(
            QtCore.SIGNAL(r'dataChanged(QModelIndex,QModelIndex)'), 
            self.getIndex(0),
            self.getIndex(IgSplineEditorTreeColumn.COUNT - 1))


'''
    Base class for items with enable states
'''
class IgSplineEditorEnableInterface(object):

    # Enable state flags
    isEnabled           = True
    isOwnerEnabled      = True
    isOverridden        = False

    # Icons
    onIcon              = None
    offIcon             = None
    offIndirectIcon     = None

    # Colors
    offColor            = None

    def __init__(self, view):
        ''' Constructor '''

        # Load icons
        self.onIcon             = CreateIcon(r':/radio-white.svg')
        self.offIcon            = CreateIcon(r':/radio-black.svg')
        self.offIndirectIcon    = CreateIcon(r':/radio-gray.svg')

        # Load colors
        self.offColor           = view.palette().color(QPalette.Disabled, QPalette.Text)

    def getEnabledIcon(self):
        ''' Get the icon for the current enable state '''
        if self.isEnabled:
            return self.onIcon if self.isOwnerEnabled and not self.isOverridden else self.offIndirectIcon
        else:
            return self.offIcon

    def getEnabledTextColor(self):
        ''' Get the text color for the current enable state. None is QVariant(). '''
        return None if self.isEnabled and self.isOwnerEnabled and not self.isOverridden else self.offColor

    def setOverridden(self, isOverridden):
        anyChanges = False
        if self.isOverridden != isOverridden:
            self.isOverridden = isOverridden
            anyChanges = True
        return anyChanges

'''
    Base class for all dg nodes
'''
class IgSplineEditorDgItem(IgSplineEditorTreeItem):

    # Handle to a Maya dg node. This can be none or shared by items.
    handle = None

    def __init__(self, view, handle):
        ''' Constructor '''
        IgSplineEditorTreeItem.__init__(self, view)

        # Associate to the specified Maya dg node
        self.handle = handle

    #
    # Maya dg management
    #

    def getHandle(self):
        ''' Return the python wrapper to the Maya dg node '''
        return self.handle if self.handle is not None else IgSplineEditorDgNode()

    def getNodeName(self):
        ''' Return the Maya dg node name '''
        return self.getHandle().name()

    def setNodeName(self, newName):
        ''' Set the name of the Maya dg node '''
        self.getModel().renameDgNode(self.getNodeName(), newName)


'''
    Base class for all dag nodes
'''
class IgSplineEditorDagItem(IgSplineEditorDgItem):

    # Children of the dag node
    dagChildren = None

    # Shape of the dag node (We don't show shapes)
    dagShape    = None

    # Parent of the dag node
    dagParent   = None

    def __init__(self, view, handle):
        ''' Constructor '''
        IgSplineEditorDgItem.__init__(self, view, handle)

        # Children are represented as item list. Note that this does not
        # scale well when there are huge number of child items. If this is
        # the case, we need to consider to use a dict.
        # Also, we don't want to show shapes so shapes are not children.
        self.dagChildren = []
        self.dagShape    = None

        # Parent is a weak ref proxy to the parent item
        self.dagParent = None

    #
    # IgSplineEditorTreeItem interface implementation
    #
    def flags(self, column):
        ''' Return the item flags for the given index '''

        # Inherit flags from parent class
        flags = IgSplineEditorDgItem.flags(self, column)

        # Determine if the item is droppable
        if column < 0 or column == IgSplineEditorTreeColumn.NAME:
            if self.view.mimeType == IgSplineEditorMimeData.MIME_TYPE_DAG:
                # Items("dag") can be dropped onto dag items
                flags = flags | Qt.ItemIsDropEnabled

        # Delegate to shape for more flags
        if self.getDagShape() is not None:
            flags = flags | self.getDagShape().flags(column)

        return flags

    def getChildCount(self):
        ''' Return the number of children in the tree '''

        # Regular dag children
        childCount = self.getDagChildCount()

        # Shape children delegation
        if self.dagShape is not None:
            childCount += self.dagShape.getChildCount()

        return childCount

    def getChild(self, i):
        ''' Return the i-th child of this item in the tree '''

        # Find in regular dag children
        dagChildCount = self.getDagChildCount()
        if i < dagChildCount:
            return self.getDagChildByIndex(i)
        elif self.dagShape:
            # Find in shape children
            shapeChildCount = self.dagShape.getChildCount()
            if i < dagChildCount + shapeChildCount:
                return self.dagShape.getChild(i - dagChildCount)
        return None

    def getParent(self):
        ''' Return the parent of this item in the tree '''
        return self.getDagParent()

    #
    # Maya dag management
    #

    def getDagChildCount(self):
        ''' Return the dag children of this dag node '''
        return len(self.dagChildren)

    def getDagChildByHandle(self, handle):
        ''' Return the child item by looking up Maya dg node '''
        for item in self.dagChildren:
            if item.getHandle() == handle:
                return item
        return None

    def getDagChildByIndex(self, i):
        ''' Return the i-th child item by array index '''
        return self.dagChildren[i] if i < len(self.dagChildren) else None

    def addDagChild(self, dagItem):
        ''' Append a dag item to the children of this dag item '''

        # Get the current parent item of the dag item
        dagParent = dagItem.getDagParent()

        # Is the dag item already a child of this dag item ?
        if dagParent == self:
            return

        # Add or Reparent ?
        if dagParent is None:
            # Begin a row insert operation
            rowFirst = len(self.dagChildren)
            rowLast  = rowFirst
            self.getModel().beginInsertRows(self.getIndex(), rowFirst, rowLast)

            # Append the new item to the child list
            dagItem.setDagParent(self)
            self.dagChildren.append(dagItem)

            # End a row insert operation
            self.getModel().endInsertRows()
        else:
            # Begin a row move operation
            srcIndex = dagParent.getIndex()
            srcFirst = dagItem.getIndex().row()
            srcLast  = srcFirst
            dstIndex = self.getIndex()
            dstChild = len(self.dagChildren)
            self.getModel().beginMoveRows(srcIndex, srcFirst, srcLast, dstIndex, dstChild)

            # Move the item to the child list
            dagParent.dagChildren.remove(dagItem)
            dagItem.setDagParent(self)
            self.dagChildren.append(dagItem)

            # End a row move operation
            self.getModel().endMoveRows()

    def removeDagChild(self, dagItem):
        ''' Remove a dag item from the children '''

        # Get the current parent item of the dag item
        dagParent = dagItem.getDagParent()

        # Not parent ?
        if dagParent != self:
            return

        # Begin a row remove operation
        rowFirst = self.dagChildren.index(dagItem)
        rowLast  = rowFirst
        self.getModel().beginRemoveRows(self.getIndex(), rowFirst, rowLast)

        # Remove the dag item
        self.dagChildren.remove(dagItem)
        dagItem.dagParent = None

        # End a row remove operation
        self.getModel().endRemoveRows()

    def moveDagChild(self, fromIndex, toIndex):
        ''' Move the child item between child items '''

        # No changes ?
        if fromIndex == toIndex:
            return

        # Begin a row move operation
        srcIndex = self.getIndex()
        srcFirst = fromIndex
        srcLast  = fromIndex
        dstIndex = self.getIndex()
        dstChild = toIndex
        self.getModel().beginMoveRows(srcIndex, srcFirst, srcLast, dstIndex, dstChild)

        # Move the child dag item
        childDagItem = self.dagChildren[fromIndex]
        self.dagChildren.remove(childDagItem)
        self.dagChildren.insert(toIndex, childDagItem)

        # End a row move operation
        self.getModel().endMoveRows()

    def getDagShape(self):
        ''' Get the shape '''
        return self.dagShape

    def setDagShape(self, dagShape):
        ''' Set the shape '''

        # Remove the existing shape
        if self.dagShape:
            if self.dagShape.getChildCount() > 0:
                rowFirst = len(self.dagChildren)
                rowLast  = rowFirst + self.dagShape.getChildCount() - 1
                self.getModel().beginRemoveRows(self.getIndex(), rowFirst, rowLast)
                self.dagShape = None
                self.getModel().endRemoveRows()
            else:
                self.dagShape = None

        # Set the new shape
        if dagShape:
            if dagShape.getParent():
                dagShape.getParent().setDagShape(None)

            if dagShape.getChildCount() > 0:
                rowFirst = len(self.dagChildren)
                rowLast  = rowFirst + dagShape.getChildCount() - 1
                self.getModel().beginInsertRows(self.getIndex(), rowFirst, rowLast)
                dagShape.setDagParent(self)
                self.dagShape = dagShape
                self.getModel().endInsertRows()
            else:
                dagShape.setDagParent(self)
                self.dagShape = dagShape

    def getDagParent(self):
        ''' Return the parent item of this dag item '''
        return self.dagParent() if self.dagParent else None

    def setDagParent(self, dagItem):
        ''' Set the given dag item as the parent of this dag item '''
        self.dagParent = weakref.ref(dagItem)

    def findDagChild(self, handle):
        ''' Find the dag item in the hierarchy '''

        # We don't expect a large amound of dag items here. If this is the
        # case, we need to build a lookup cache in the world item.

        # Is this item ?
        if self.getHandle() == handle:
            return self

        # Recursive info descendents
        for dagItem in self.dagChildren:
            found = dagItem.findDagChild(handle)
            if found is not None:
                return found
        if self.dagShape:
            found = self.dagShape.findDagChild(handle)
            if found is not None:
                return found
        return None

    def collectDagNodes(self, nodeSet):
        ''' Collect a set of dag node in the hierarchy '''

        # Add the dag node to the set
        if self.getHandle().isValid():
            nodeSet.add(self.getHandle())

        # Recursive info descendents
        for dagItem in self.dagChildren:
            dagItem.collectDagNodes(nodeSet)
        if self.dagShape:
            self.dagShape.collectDagNodes(nodeSet)


'''
    Visitor for dag hierarchy
'''
class IgSplineEditorDagVisitor(object):

    def visitWorld(self, item):
        ''' Visit a world item '''
        pass

    def visitTransform(self, item):
        ''' Visit a transform item '''
        pass

    def visitDescription(self, item):
        ''' Visit a spline description shape item '''
        pass

'''
    Visitor to iterate the dag hierarchy
'''
class IgSplineEditorDagTraverser(IgSplineEditorDagVisitor):

    def visitWorld(self, item):
        ''' Visit a world item '''
        self.__traverseDagChildren(item)

    def visitTransform(self, item):
        ''' Visit a transform item '''
        self.__traverseDagChildren(item)
        self.__traverseDagShape(item)

    def visitDescription(self, item):
        ''' Visit a spline description shape item '''
        pass

    def __traverseDagChildren(self, item):
        ''' Traverse the children of the dag item '''
        for i in range(0, item.getDagChildCount()):
            item.getDagChildByIndex(i).accept(self)

    def __traverseDagShape(self, item):
        ''' Traverse the shape of the dag item '''
        shapeItem = item.getDagShape()
        if shapeItem:
            shapeItem.accept(self)


'''
    Root item for top level transform nodes
'''
class IgSplineEditorWorldItem(IgSplineEditorDagItem):

    def __init__(self, view):
        ''' Constructor '''
        IgSplineEditorDagItem.__init__(self, view, None)

    def accept(self, visitor):
        ''' Visit the world item '''
        visitor.visitWorld(self)

'''
    Represent a transform node
'''
class IgSplineEditorTransformItem(IgSplineEditorDagItem,IgSplineEditorEnableInterface):

    # Maya dg notifications
    dgWatcher   = None

    # Name of the dag node
    dagNodeName = None

    # Icon
    dagIcon     = None

    def __init__(self, view, handle):
        ''' Constructor '''
        IgSplineEditorDagItem.__init__(self, view, handle)
        IgSplineEditorEnableInterface.__init__(self, view)

        # Observe the dag node name. We don't show shapes so the
        # name of the shape node is not significant.
        self.update(notify=False)

        # Icon of the transform node
        self.dagIcon = CreateIcon(r':/folder-open')

        # Register dg notification callbacks
        self.dgWatcher = IgSplineEditorDgWatcher()
        self.dgWatcher.watchNodeNameChanged(handle.node(), self.onMayaNodeNameChanged)
        self.dgWatcher.watchNodePlugDirtied(
            handle.node(),
            self.onMayaNodePlugDirtied)

    def accept(self, visitor):
        ''' Visit the transform item '''
        visitor.visitTransform(self)

    def flags(self, column):
        ''' Return the item flags for the given index '''

        # Flags for a dag node row
        if column == IgSplineEditorTreeColumn.NAME:
            # Name column : dag node name is editable
            return IgSplineEditorDagItem.flags(self, column) | Qt.ItemIsEditable

        # The flag is not handled ..
        return IgSplineEditorDagItem.flags(self, column)

    def data(self, column, role):
        ''' Return the data stored under the given role '''

        # Roles for a dag node row
        if column == IgSplineEditorTreeColumn.NAME:
            # Name column : dag node icon and name
            if role == Qt.DisplayRole or role == Qt.EditRole:
                return self.dagNodeName
            elif role == Qt.ForegroundRole:
                return self.getEnabledTextColor()
            elif role == Qt.DecorationRole:
                shape = self.getDagShape()
                return self.dagIcon if shape is None else shape.data(column, role)
        elif column == IgSplineEditorTreeColumn.ENABLE:
            # Enable column : visibility
            if role == Qt.DecorationRole:
                return self.getEnabledIcon()

        # The role is not handled ..
        return IgSplineEditorDagItem.data(self, column, role)

    def setData(self, column, value, role):
        ''' Set the role data for the item at index to value '''

        # Alter the data for a dag node row
        if column == IgSplineEditorTreeColumn.NAME:
            # Name column : change the dag node name
            if role == Qt.EditRole:
                self.setNodeName(value)
                return True

        # The role is not handled ..
        return IgSplineEditorDagItem.setData(self, column, value, role)

    def update(self, notify=True):
        ''' Update the cached node name of the dag node '''

        # Not in model ?
        if notify and self.getParent() is None:
            return

        # Not a valid node (deleted) ?
        if not self.getHandle().isValid():
            return

        # Any changes to the cached data ?
        anyChanges = False

        # Get the MDagPath and MFnDagNode
        dagPath = om.MDagPath.getAPathTo(self.getHandle().node())
        dagNode = om.MFnDagNode(dagPath)

        # Name
        dagNodeName = self.getNodeName()
        if self.dagNodeName != dagNodeName:
            self.dagNodeName = dagNodeName
            anyChanges = True

        # Visibility of this node
        isEnabled = (dagNode.findPlug(r'visibility').asBool() and
                     dagNode.findPlug(r'lodVisibility').asBool())
        if self.isEnabled != isEnabled:
            self.isEnabled = isEnabled
            anyChanges = True

        # Visibility of parent node
        parentDagPath = om.MDagPath(dagPath)
        parentDagPath.pop()
        isOwnerEnabled = parentDagPath.isVisible()
        if self.isOwnerEnabled != isOwnerEnabled:
            self.isOwnerEnabled = isOwnerEnabled
            anyChanges = True

        # Notify the view about the data changes
        if anyChanges and notify:
            self.emitDataChanged()

    def setOverridden(self, isOverridden):
        ''' Update the overridden status of the item '''
        anyChanges = IgSplineEditorEnableInterface.setOverridden(self, isOverridden)
        if anyChanges:
            # Also update descendent nodes
            class UpdateOverridden(IgSplineEditorDagTraverser):
                def visitDescription(self, item):
                    IgSplineEditorDagTraverser.visitDescription(self, item)
                    item.setOverridden(isOverridden)
            self.accept(UpdateOverridden())
            self.emitDataChanged()
        return anyChanges

    def onMayaNodeNameChanged(self, node, prevName):
        ''' Invoked when the dag node name has been changed '''
        QTimer.singleShot(0, self.update)

    def onMayaNodePlugDirtied(self, node, plug):
        ''' Invoked when a plug is dirtied '''

        # Get the attribute being dirtied
        attribute = plug.attribute()

        # Get the handle of the transform node
        handle = self.getHandle()

        # Update when visibility and lodVisibility are changed
        if (attribute == handle.attribute(r'visibility')
                or attribute == handle.attribute(r'lodVisibility')):
            # Update this node
            QTimer.singleShot(0, self.update)

            # Also update descendent nodes
            class UpdateDescendent(IgSplineEditorDagTraverser):
                def visitTransform(self, item):
                    IgSplineEditorDagTraverser.visitTransform(self, item)
                    QTimer.singleShot(0, item.update)
            self.accept(UpdateDescendent())


'''
    Represent a spline description shape node
'''
class IgSplineEditorDescriptionItem(IgSplineEditorDagItem):

    # Modifiers in the construction history
    modifiers       = None

    # Icon
    descriptionIcon = None

    # Maya dg notifications
    dgWatcher       = None

    # Indicates if the description item is overridden
    isOverridden    = False

    def __init__(self, view, handle):
        ''' Constructor '''
        IgSplineEditorDagItem.__init__(self, view, handle)

        # We keep track of a list of modifiers in the spline description
        # shape's construction history. The modifiers might be shared but
        # we create separate modifier items for a shared modifier node.
        self.modifiers = []

        # Icon of the spline description shape
        self.descriptionIcon = CreateIcon(r'out_xgmDescription.png')

        # Register dg notification callbacks
        self.dgWatcher = IgSplineEditorDgWatcher()
        self.dgWatcher.watchConnectionMade(handle.node(), self.onMayaConnectionChanged)
        self.dgWatcher.watchConnectionBroken(handle.node(), self.onMayaConnectionChanged)

    def accept(self, visitor):
        ''' Visit the spline description item '''
        visitor.visitDescription(self)

    #
    # IgSplineEditorTreeItem interface implementation
    #
    def flags(self, column):
        ''' Return the item flags for the given index '''

        # Inherit flags from parent class
        flags = IgSplineEditorDagItem.flags(self, column)

        # Determine if the item is droppable
        if column < 0 or column == IgSplineEditorTreeColumn.NAME:
            if self.view.mimeType == IgSplineEditorMimeData.MIME_TYPE_MODIFIER:
                # Items("modifier") can be dropped onto description items
                flags = flags | Qt.ItemIsDropEnabled

        return flags

    def data(self, column, role):
        ''' Return the data stored under the given role '''

        # Roles for a spline description shape row
        if column == IgSplineEditorTreeColumn.NAME:
            if role == Qt.DecorationRole:
                return self.descriptionIcon

        # The role is not handled ..
        return IgSplineEditorDagItem.data(self, column, role)

    def getChildCount(self):
        ''' Return the number of children in the tree '''
        return self.getModifierCount()

    def getChild(self, i):
        ''' Return the i-th child of this item in the tree '''
        return self.getModifierByIndex(i)

    def getParentIndex(self, column = 0):
        ''' Get the QModelIndex of the parent item '''
        return self.view.model().itemToIndex(self.getDagParent(), column)

    def getParentChildCount(self):
        ''' Get the number of dag children of the parent item '''
        return self.getDagParent().getDagChildCount()

    #
    # Modifiers management
    #
    def getModifierCount(self):
        ''' Return the number of modifier items '''
        return len(self.modifiers)

    def getModifierByHandle(self, handle):
        ''' Get the modifier item by dg node handle '''
        for item in self.modifiers:
            if item.getHandle() == handle:
                return item
        return None

    def getModifierByIndex(self, i):
        ''' Get the i-th modifier item '''
        return self.modifiers[i] if i < len(self.modifiers) else None

    def addModifier(self, item, pos = -1):
        ''' Add the modifier item to the description '''

        # Check the insertion position
        if pos < 0 or pos > len(self.modifiers):
            pos = len(self.modifiers)

        # Get the current description item of the modifier item
        descriptionItem = item.getDescription()

        # Nothing to do ?
        if descriptionItem == self and self.getModifierByIndex(pos) == item:
            return

        # Add or Move ?
        if descriptionItem is None:
            # Begin a row insert operation
            row = self.getParentChildCount() + pos
            self.getModel().beginInsertRows(self.getParentIndex(), row, row)

            # Insert the modifier
            item.setDescription(self)
            self.modifiers.insert(pos, item)

            # End a row insert operation
            self.getModel().endInsertRows()
        else:
            # Begin a row move operation
            srcIndex = descriptionItem.getParentIndex()
            srcRow   = item.getIndex().row()
            dstIndex = self.getParentIndex()
            dstRow   = self.getParentChildCount() + pos
            self.getModel().beginMoveRows(srcIndex, srcRow, srcRow, dstIndex, dstRow)

            # Move the modifier
            if descriptionItem == self:
                i = self.modifiers.index(item)
                if pos > i:
                    pos -= 1
                descriptionItem.modifiers.remove(item)
                self.modifiers.insert(pos, item)
            else:
                descriptionItem.modifiers.remove(item)
                item.setDescription(self)
                self.modifiers.insert(pos, item)

            # End a row move operation
            self.getModel().endMoveRows()

    def removeModifiers(self, fromIndex, toIndex):
        ''' Remove the modifiers in range(from, to) '''

        # Bad range ?
        if fromIndex >= toIndex or toIndex > len(self.modifiers):
            return

        # Begin a row remove operation
        rowFirst = self.getParentChildCount() + fromIndex
        rowLast  = self.getParentChildCount() + toIndex - 1
        self.getModel().beginRemoveRows(self.getParentIndex(), rowFirst, rowLast)

        # Remove the modifier
        for i in range(fromIndex, toIndex):
            self.modifiers[i].description = None
        del self.modifiers[fromIndex:toIndex]

        # End a row remove operation
        self.getModel().endRemoveRows()

    def setOverridden(self, isOverridden):
        ''' Update the overridden status of the item '''
        if self.isOverridden != isOverridden:
            self.isOverridden = isOverridden
            self.getModel().delayedRefreshDescription(
                self.getHandle().node())

    def updateOverridden(self):
        ''' Refresh the overridden status for each modifier '''
        isOverridden = self.isOverridden

        for item in self.modifiers:
            item.setOverridden(isOverridden)
            if isOverrideModifierNode(item.getHandle().node()) and not item.isOverridden:
                mute = om.MFnDependencyNode(item.getHandle().node()).findPlug(r'mute').asBool()
                isOverridden = not mute

    def onMayaConnectionChanged(self, plug):
        ''' Invoked when the connection has been changed '''
        self.getModel().delayedRefreshDescription(
            self.getHandle().node())


'''
    Represent a dg node in the contruction history of a spline description
'''
class IgSplineEditorHistoryItem(IgSplineEditorDgItem):

    # Parent spline description item
    description = None

    # Maya dg notifications
    dgWatcher   = None

    # Name of the dg node
    dgNodeName  = None

    def __init__(self, view, handle):
        ''' Constructor '''
        IgSplineEditorDgItem.__init__(self, view, handle)

        # The downstream description shape item
        self.description = None

        # Observe the dg node name. We don't show shapes so the
        # name of the shape node is not significant.
        self.updateNodeName(notify=False)

        # Register dg notification callbacks
        self.dgWatcher = IgSplineEditorDgWatcher()
        self.dgWatcher.watchNodeNameChanged(handle.node(), self.onMayaNodeNameChanged)
        self.dgWatcher.watchConnectionMade(handle.node(), self.onMayaConnectionChanged)
        self.dgWatcher.watchConnectionBroken(handle.node(), self.onMayaConnectionChanged)

    #
    # IgSplineEditorTreeItem interface implementation
    #
    def flags(self, column):
        ''' Return the item flags for the given index '''

        # Flags for a history node row
        if column == IgSplineEditorTreeColumn.NAME:
            # Name column : dg node name is editable
            return IgSplineEditorDgItem.flags(self, column) | Qt.ItemIsEditable

        # The flag is not handled ..
        return IgSplineEditorDgItem.flags(self, column)

    def data(self, column, role):
        ''' Return the data stored under the given role '''

        # Roles for a history node row
        if column == IgSplineEditorTreeColumn.NAME:
            # Name column : dg node name
            if role == Qt.DisplayRole or role == Qt.EditRole:
                return self.dgNodeName

        # The role is not handled ..
        return IgSplineEditorDgItem.data(self, column, role)

    def setData(self, column, value, role):
        ''' Set the role data for the item at index to value '''

        # Alter the data for a history node row
        if column == IgSplineEditorTreeColumn.NAME:
            # Name column : change the dg node name
            if role == Qt.EditRole:
                self.setNodeName(value)
                return True

        # The role is not handled ..
        return IgSplineEditorDgItem.setData(self, column, value, role)

    def getParent(self):
        ''' Parent is the transform since we don't show shape.. '''
        description = self.getDescription()
        return description.getDagParent() if description else None

    #
    # History node management
    #
    def getDescription(self):
        ''' Return the parent description item '''
        return self.description() if self.description else None

    def setDescription(self, description):
        ''' Set the description parent '''
        self.description = weakref.ref(description)

    def updateNodeName(self, notify=True):
        ''' Update the cached node name of the dg node '''

        # Not in model ?
        if notify and self.getDescription() is None:
            return

        # Get the current node name
        dgNodeName = self.getNodeName()

        # No changes ?
        if self.dgNodeName == dgNodeName:
            return

        # Update the cached name
        self.dgNodeName = dgNodeName
        if notify:
            self.emitDataChanged()

    def onMayaNodeNameChanged(self, node, prevName):
        ''' Invoked when the dg node name has been changed '''
        QTimer.singleShot(0, self.updateNodeName)

    def onMayaConnectionChanged(self, plug):
        ''' Invoked when the connection has been changed '''
        self.getModel().delayedRefreshDescription(
            self.getDescription().getHandle().node())


'''
    Represent a spline base node
'''
class IgSplineEditorBaseNodeItem(IgSplineEditorHistoryItem, IgSplineEditorEnableInterface):

    # Icon of the dg node
    dgNodeIcon  = None

    def __init__(self, view, handle):
        ''' Constructor '''
        IgSplineEditorHistoryItem.__init__(self, view, handle)
        IgSplineEditorEnableInterface.__init__(self, view)

        # Icon of the spline base node
        self.dgNodeIcon = CreateIcon(r'out_xgmSubdPatch.png')

    def data(self, column, role):
        ''' Return the data stored under the given role '''

        # Roles for a spline base node row
        if column == IgSplineEditorTreeColumn.NAME:
            # Name column : dg node icon
            if role == Qt.DecorationRole:
                return self.dgNodeIcon
            elif role == Qt.ForegroundRole:
                return self.getEnabledTextColor()

        # The role is not handled ..
        return IgSplineEditorHistoryItem.data(self, column, role)

    def setOverridden(self, isOverridden):
        ''' Update the overridden status of the item '''
        anyChanges = IgSplineEditorEnableInterface.setOverridden(self, isOverridden)
        if anyChanges:
            self.emitDataChanged()
        return anyChanges

'''
    Represent a spline modifier dg node
'''
class IgSplineEditorModifierItem(IgSplineEditorHistoryItem,IgSplineEditorEnableInterface):

    # Icon of the dg node
    dgNodeIcon  = None

    # Maya dg notifications
    modWatcher  = None

    def __init__(self, view, handle):
        ''' Constructor '''
        IgSplineEditorHistoryItem.__init__(self, view, handle)
        IgSplineEditorEnableInterface.__init__(self, view)

        # Icon of the modifier node
        dgNode = om.MFnDependencyNode(handle.node())
        self.dgNodeIcon = CreateIcon(getSplineModifierIcon(dgNode.typeName()))

        # Whether the spline modifier is muted
        self.isEnabled = not dgNode.findPlug(r'mute').asBool()

        # Observe attribute changes
        self.modWatcher = IgSplineEditorDgWatcher()
        self.modWatcher.watchAttributeSet(
            handle.node(),
            handle.attribute(r'mute'),
            self.onMayaAttributeSet)

    #
    # IgSplineEditorTreeItem interface implementation
    #
    def data(self, column, role):
        ''' Return the data stored under the given role '''

        # Roles for a spline modifier node row
        if column == IgSplineEditorTreeColumn.NAME:
            # Name column : dg node icon
            if role == Qt.DecorationRole:
                return self.dgNodeIcon
            elif role == Qt.ForegroundRole:
                return self.getEnabledTextColor()
        elif column == IgSplineEditorTreeColumn.ENABLE:
            # Enable column : mute icon
            if role == Qt.DecorationRole:
                return self.getEnabledIcon()

        # The role is not handled ..
        return IgSplineEditorHistoryItem.data(self, column, role)

    #
    # Modifier node management
    #
    def update(self, notify=True):
        ''' Update the cached data '''

        # Not in model ?
        if notify and self.getDescription() is None:
            return

        # Reject if the dg node no longer exists ..
        if not self.getHandle().isValid():
            return
        dgNode = om.MFnDependencyNode(self.getHandle().node())

        # Any changes to the cached data ?
        anyChanges = False

        # Mute
        isEnabled = not dgNode.findPlug(r'mute').asBool()
        if self.isEnabled != isEnabled:
            self.isEnabled = isEnabled
            anyChanges = True

        # Notify the view about the data changes
        if anyChanges and notify:
            self.emitDataChanged()

    def setOverridden(self, isOverridden):
        ''' Update the overridden status of the item '''
        anyChanges = IgSplineEditorEnableInterface.setOverridden(self, isOverridden)
        if anyChanges:
            self.emitDataChanged()
        return anyChanges

    def onMayaAttributeSet(self, plug):
        ''' Invoked when the "mute" attribute changes '''
        QTimer.singleShot(0, self.update)

'''
    Represent a modifier linked to another item
'''
class IgSplineEditorLinkModifierItem(IgSplineEditorModifierItem):

    # The link to another item
    linkTarget      = None

    def __init__(self, view, handle):
        ''' Constructor '''
        IgSplineEditorModifierItem.__init__(self, view, handle)

    #
    # IgSplineEditorTreeItem interface implementation
    #
    def getChildCount(self):
        ''' Return the number of children in the tree '''
        return 1 if self.linkTarget else 0

    def getChild(self, i):
        ''' Return the i-th child of this item in the tree '''
        return self.linkTarget if i == 0 else None

    #
    # Maya dg connection link management
    #
    def getLink(self):
        ''' Get the link target '''
        return self.linkTarget

    def setLink(self, item):
        ''' Set the link target to the specified item '''

        # Remove the previous link target
        if self.linkTarget:
            self.getModel().beginRemoveRows(self.getIndex(), 0, 0)
            self.linkTarget.setLinkParent(None)
            self.linkTarget = None
            self.getModel().endRemoveRows()

        # Add the new link target
        if item:
            self.getModel().beginInsertRows(self.getIndex(), 0, 0)
            self.linkTarget = item
            self.linkTarget.setLinkParent(self)
            self.getModel().endInsertRows()

    def setOverridden(self, isOverridden):
        ''' Update the overridden status of the item '''
        anyChanges = IgSplineEditorModifierItem.setOverridden(self, isOverridden)
        if anyChanges and self.linkTarget is not None:
            self.linkTarget.setOverridden(isOverridden)
        return anyChanges

    def onMayaConnectionChanged(self, plug):
        ''' Invoked when the connection has been changed '''
        IgSplineEditorModifierItem.onMayaConnectionChanged(self, plug)
        self.getModel().delayedRefreshDag()


'''
    Represent a link to a spline description
'''
class IgSplineEditorDescriptionLinkItem(IgSplineEditorTransformItem):

    # The parent with the link
    linkParent = None

    def __init__(self, view, handle):
        ''' Constructor '''
        IgSplineEditorTransformItem.__init__(self, view, handle)

    #
    # IgSplineEditorTreeItem interface implementation
    #
    def flags(self, column):
        ''' Return the item flags for the given index '''

        # Default flags as a transform dag node
        flags = IgSplineEditorTransformItem.flags(self, column)

        # Transform node of the link description is not draggable
        flags = flags & ~Qt.ItemIsDragEnabled

        # It's not allowed to reparent dag nodes to the transform node
        if self.view.mimeType == IgSplineEditorMimeData.MIME_TYPE_DAG:
            flags = flags & ~Qt.ItemIsDropEnabled

        return flags

    def getParent(self):
        ''' Return the parent of this item in the tree '''
        return self.linkParent()

    #
    # Maya dg connection link management
    #
    def setLinkParent(self, parent):
        ''' Set the parent (modifier?) of the link '''
        self.linkParent = weakref.ref(parent) if parent else None


'''
    Represent a sculpt modifier dg node
'''
class IgSplineEditorSculptModifierItem(IgSplineEditorModifierItem):

    # The root sculpt group
    rootGroup   = None

    def __init__(self, view, handle):
        ''' Constructor '''
        IgSplineEditorModifierItem.__init__(self, view, handle)
        
        # The root of all sculpt layers and groups
        self.rootGroup = IgSplineEditorSculptGroupItem(view, handle, self, None)

        # Register dg notification callbacks
        self.dgWatcher.watchAttributeArrayAdded(
            handle.node(),
            None, # Watch both tweaks and tweakGroups
            self.onMayaAttributeArrayChanged)
        self.dgWatcher.watchAttributeArrayRemoved(
            handle.node(),
            None, # Watch both tweaks and tweakGroups
            self.onMayaAttributeArrayChanged)

    #
    # IgSplineEditorTreeItem interface implementation
    #
    def flags(self, column):
        ''' Return the item flags for the given index '''

        # Inherit flags from parent class
        flags = IgSplineEditorModifierItem.flags(self, column)

        # Determine if the item is droppable
        if column < 0 or column == IgSplineEditorTreeColumn.NAME:
            if self.view.mimeType == IgSplineEditorMimeData.MIME_TYPE_SCULPT:
                # Items("sculpt") can be dropped onto sculpt modifier items
                flags = flags | Qt.ItemIsDropEnabled

        return flags

    def getChildCount(self):
        ''' Return the number of children in the tree '''
        return self.rootGroup.getSculptChildCount()

    def getChild(self, i):
        ''' Return the i-th child of this item in the tree '''
        return self.rootGroup.getSculptChildByIndex(i)

    #
    # Root Sculpt Group delegation
    #
    def getRootGroup(self):
        ''' Get the root group of the sculpt modifier item '''
        return self.rootGroup

    def setOverridden(self, isOverridden):
        ''' Update the overridden status of the item '''
        anyChanges = IgSplineEditorModifierItem.setOverridden(self, isOverridden)
        if anyChanges and self.rootGroup is not None:
            self.rootGroup.setOverridden(isOverridden)
        return anyChanges

    #
    # Sculpt Group / Layer management
    #
    def onMayaAttributeArrayChanged(self, plug):
        ''' Invoked when the number of elements of an array attribute changed '''
        self.getModel().delayedRefreshDescription(
            self.getDescription().getHandle().node())


'''
    Represent a cache modifier dg node
'''
class IgSplineEditorOverrideModifierItem(IgSplineEditorModifierItem):

    def __init__(self, view, handle):
        ''' Constructor '''
        IgSplineEditorModifierItem.__init__(self, view, handle)

    def update(self, notify=True):
        ''' Update the cached data '''

        # Not in model ?
        descriptionItem = self.getDescription()
        if notify and descriptionItem is None:
            return

        # Reject if the dg node no longer exists ..
        if not self.getHandle().isValid():
            return
        dgNode = om.MFnDependencyNode(self.getHandle().node())

        # Mute
        anyChanges = False
        isEnabled = not dgNode.findPlug(r'mute').asBool()
        if self.isEnabled != isEnabled:
            self.isEnabled = isEnabled
            if not self.isOverridden:
                self.getModel().delayedRefreshDescription(
                    descriptionItem.getHandle().node())
            anyChanges = True

        # Notify the view about the data changes
        if anyChanges and notify:
            self.emitDataChanged()

    def onMayaAttributeSet(self, plug):
        IgSplineEditorModifierItem.onMayaAttributeSet(self, plug)

        # Reset tools after we changed Maya selection
        currentCtx = cmds.currentCtx()
        if currentCtx and currentCtx.startswith(r'xgm'):
            cmds.setToolTo(currentCtx)

'''
    Represent a sculpt group or a sculpt layer in the sculpt modifier node
'''
class IgSplineEditorAbstractSculptItem(IgSplineEditorDgItem):

    # Parent sculpt modifier
    modifierParent  = None

    # Parent sculpt group
    sculptParent    = None

    # MPlug
    plug            = None

    # Logical index of the array plug
    logicalIndex    = -1

    def __init__(self, view, handle, modifier, plug):
        ''' Constructor '''
        IgSplineEditorDgItem.__init__(self, view, handle)

        # All sculpt groups or sculpt layers belong to one modifier item
        self.setModifierParent(modifier)

        # MPlug for the sculpt group or sculpt layer. It's the array element
        # plug of the "tweaks" or "tweakGroups" plug. Root group doesn't have
        # a valid plug.
        self.plug         = om.MPlug(plug) if plug else om.MPlug()
        self.logicalIndex = plug.logicalIndex() if plug else -1

    #
    # IgSplineEditorTreeItem interface implementation
    #
    def flags(self, column):
        ''' Return the item flags for the given index '''

        # Inherit flags from parent class
        flags = IgSplineEditorDgItem.flags(self, column)

        # Determine if the item is droppable
        if column < 0 or column == IgSplineEditorTreeColumn.NAME:
            if self.view.mimeType == IgSplineEditorMimeData.MIME_TYPE_SCULPT:
                # Items("sculpt") can be dropped onto sculpt groups or layers
                flags = flags | Qt.ItemIsDropEnabled

        return flags

    def getParent(self):
        ''' Return the parent of this item in the tree '''
        sculptParent = self.getSculptParent()
        return sculptParent if not sculptParent.isRoot() else self.getModifierParent()

    #
    # Common Sculpt Layer / Sculpt Group management
    #
    def setModifierParent(self, modifier):
        ''' Set the modifier parent '''
        self.modifierParent = weakref.ref(modifier) if modifier is not None else None

    def getModifierParent(self):
        ''' Get the modifier parent '''
        return self.modifierParent() if self.modifierParent is not None else None

    def setSculptParent(self, sculpt):
        ''' Set the sculpt parent '''
        self.sculptParent = weakref.ref(sculpt) if sculpt is not None else None

    def getSculptParent(self):
        ''' Get the sculpt parent '''
        return self.sculptParent() if self.sculptParent is not None else None

    def isRoot(self):
        ''' Return True if the item is a root sculpt group '''
        return self.sculptParent is None

    def isGroup(self):
        ''' Return True if the item can have children '''
        return False

    def getRootGroup(self):
        ''' Return the root group '''
        return self.getModifierParent().getRootGroup()

    def getPlug(self):
        ''' Return the MPlug object '''
        return self.plug

    def getChildPlug(self, attribute):
        ''' Return the child plug MPlug object '''
        return self.plug.child(self.getHandle().attribute(attribute))

    def getLogicalIndex(self):
        ''' Return the logical index of the plug '''
        return self.logicalIndex

    def retire(self):
        ''' Mark the item is going to be deleted and stop watching plug changes '''
        pass


'''
    Represent a sculpt group in the sculpt modifier node
'''
class IgSplineEditorSculptGroupItem(IgSplineEditorAbstractSculptItem,IgSplineEditorEnableInterface):

    # Sculpt layers or sculpt group children
    sculptChildren  = None

    # Maya dg notifications
    dgWatcher       = None

    # Name of the Sculpt Group
    uiName          = r''
    uiNameDefault   = r''

    # Icon of the Sculpt Group
    uiIcon          = None

    def __init__(self, view, handle, modifier, plug):
        ''' Constructor '''
        IgSplineEditorAbstractSculptItem.__init__(self, view, handle, modifier, plug)
        IgSplineEditorEnableInterface.__init__(self, view)

        # A sculpt group contains a list of sculpt layers or sculpt groups
        self.sculptChildren = []

        # Default Name if no UI name
        self.uiNameDefault = self.getModel().getDefaultSculptGroupName(self.getLogicalIndex())

        # Update initial Sculpt Group data
        self.update(notify=False)

        # Icon of the Sculpt Group
        self.uiIcon = CreateIcon(r':/fileOpen.png')

        # Register dg notification callbacks
        self.dgWatcher = IgSplineEditorDgWatcher()
        self.dgWatcher.watchAttributeSet(
            handle.node(),
            None,
            self.onMayaAttributeSet)

    #
    # IgSplineEditorTreeItem interface implementation
    #
    def flags(self, column):
        ''' Return the item flags for the given index '''

        # Flags for a Sculpt Group row
        if column == IgSplineEditorTreeColumn.NAME:
            # Name column : Sculpt Group name is editable
            return IgSplineEditorAbstractSculptItem.flags(self, column) | Qt.ItemIsEditable

        # The flag is not handled ..
        return IgSplineEditorAbstractSculptItem.flags(self, column)

    def data(self, column, role):
        ''' Return the data stored under the given role '''

        # Roles for a Sculpt Group row
        if column == IgSplineEditorTreeColumn.NAME:
            # Name column : UI name and icon
            if role == Qt.DisplayRole or role == Qt.EditRole:
                return self.uiName if len(self.uiName) > 0 else self.uiNameDefault
            elif role == Qt.ForegroundRole:
                return self.getEnabledTextColor()
            elif role == Qt.DecorationRole:
                return self.uiIcon
        elif column == IgSplineEditorTreeColumn.ENABLE:
            # Enable column : enable state
            if role == Qt.DecorationRole:
                return self.getEnabledIcon()

        # The role is not handled ..
        return IgSplineEditorAbstractSculptItem.data(self, column, role)

    def setData(self, column, value, role):
        ''' Set the role data for the item at index to value '''

        # Alter the data for a Sculpt Group row
        if column == IgSplineEditorTreeColumn.NAME:
            # Name column : change the Sculpt Group name
            if role == Qt.EditRole:
                self.getModel().renameSculptGroup(
                    self.getNodeName(), self.getLogicalIndex(), value)
                return True

        # The role is not handled ..
        return IgSplineEditorAbstractSculptItem.setData(self, column, value, role)

    def getChildCount(self):
        ''' Return the number of children in the tree '''
        return self.getSculptChildCount()

    def getChild(self, i):
        ''' Return the i-th child of this item in the tree '''
        return self.getSculptChildByIndex(i)

    def getParent(self):
        ''' Return the parent of this item in the tree '''
        if self.isRoot():
            # Root group = Sculpt Modifier
            return self.getModifierParent().getParent()
        return IgSplineEditorAbstractSculptItem.getParent(self)

    def getIndex(self, column = 0):
        ''' Get the QModelIndex of the item '''
        if self.isRoot():
            # Root group = Sculpt Modifier
            return self.getModifierParent().getIndex(column)
        return IgSplineEditorAbstractSculptItem.getIndex(self, column)

    #
    # Sculpt Group management
    #
    def getSculptChildCount(self):
        ''' Return the number of sculpt layers or sculpt groups '''
        return len(self.sculptChildren)

    def getSculptChildByIndex(self, i):
        ''' Return the i-th sculpt layer or sculpt group '''
        return self.sculptChildren[i] if i < len(self.sculptChildren) else None

    def addSculptChild(self, item, pos = -1):
        ''' Add a sculpt layer or sculpt group to this group '''

        # Check the insertion position
        if pos < 0 or pos > len(self.sculptChildren):
            pos = len(self.sculptChildren)

        # Get the sculpt parent (Sculpt Group, may be root group)
        sculptParent = item.getSculptParent()

        # Nothing to do ?
        if sculptParent == self and self.getSculptChildByIndex(pos) == item:
            return

        # Add or Move ?
        if sculptParent is None:
            # Begin a row insert operation
            self.getModel().beginInsertRows(self.getIndex(), pos, pos)

            # Insert the sculpt layer or sculpt group
            item.setSculptParent(self)
            self.sculptChildren.insert(pos, item)

            # End a row insert operation
            self.getModel().endInsertRows()
        else:
            # Begin a row move operation
            srcIndex = sculptParent.getIndex()
            srcRow   = item.getIndex().row()
            dstIndex = self.getIndex()
            self.getModel().beginMoveRows(srcIndex, srcRow, srcRow, dstIndex, pos)

            # Move the sculpt layer or sculpt group
            if sculptParent == self:
                i = self.sculptChildren.index(item)
                if pos > i:
                    pos -= 1
                sculptParent.sculptChildren.remove(item)
                self.sculptChildren.insert(pos, item)
            else:
                sculptParent.sculptChildren.remove(item)
                item.setSculptParent(self)
                self.sculptChildren.insert(pos, item)

            # End a row move operation
            self.getModel().endMoveRows()

    def removeSculptChildren(self, fromIndex, toIndex):
        ''' Remove the modifiers in range(from, to) '''

        # Bad range ?
        if fromIndex >= toIndex or toIndex > len(self.sculptChildren):
            return

        # Begin a row remove operation
        self.getModel().beginRemoveRows(self.getIndex(), fromIndex, toIndex - 1)

        # Remove the sculpt children
        for i in range(fromIndex, toIndex):
            self.sculptChildren[i].setSculptParent(None)
            self.sculptChildren[i].retire()
        del self.sculptChildren[fromIndex:toIndex]

        # End a row remove operation
        self.getModel().endRemoveRows()

    def isGroup(self):
        ''' Return True if the item can have children '''
        return True

    def findSculptChildByLogicalIndex(self, logicalIndex, isGroup):
        ''' Find the specified sculpt group or sculpt layer in descendents '''

        # Match this ?
        if isGroup and self.logicalIndex == logicalIndex:
            return self

        # Find in descendents
        for item in self.sculptChildren:
            if item.isGroup():
                found = item.findSculptChildByLogicalIndex(logicalIndex, isGroup)
                if found is not None:
                    return found
            else:
                if not isGroup and item.logicalIndex == logicalIndex:
                    return item
        return None

    def update(self, notify=True):
        ''' Update the cached data '''

        # Not in model ?
        if notify and self.getSculptParent() is None:
            return

        # Reject if the dg node no longer exists ..
        if not self.getHandle().isValid() or self.getPlug().isNull():
            return

        # Reject if the logicalIndex no longer exists ..
        indices = om.MIntArray()
        self.getPlug().array().getExistingArrayAttributeIndices(indices)
        if self.getLogicalIndex() not in indices:
            return

        # Any changes to the cached data ?
        anyChanges = False

        # UI name
        uiName = self.getChildPlug(r'tweakGroupUIName').asString()
        if self.uiName != uiName:
            self.uiName = uiName
            anyChanges = True

        # Enable
        isEnabled = self.getChildPlug(r'tweakGroupEnable').asBool()
        if self.isEnabled != isEnabled:
            self.isEnabled = isEnabled
            anyChanges = True

        isOwnerEnabled = isSculptGroupOwnerEnabled(
            self.getHandle().node(),
            self.getChildPlug(r'tweakGroupOwnerId').asInt())
        if self.isOwnerEnabled != isOwnerEnabled:
            self.isOwnerEnabled = isOwnerEnabled
            anyChanges = True

        # Notify the view about the data changes
        if anyChanges and notify:
            self.emitDataChanged()

    def setOverridden(self, isOverridden):
        ''' Update the overridden status of the item '''
        anyChanges = IgSplineEditorEnableInterface.setOverridden(self, isOverridden)
        if anyChanges:
            for item in self.sculptChildren:
                item.setOverridden(isOverridden)
            self.emitDataChanged()
        return anyChanges

    def onMayaAttributeSet(self, plug):
        ''' Invoked when the "tweakGroups" attribute changes '''

        # Get the attribute being set
        attribute = plug.attribute()

        # Get the handle of the sculpt node
        handle = self.getHandle()

        # These attributes affect all rows
        if (attribute == handle.attribute(r'mute')
                or attribute == handle.attribute(r'tweakGroupEnable')
                or attribute == handle.attribute(r'tweakGroupOwnerId')):
            QTimer.singleShot(0, self.update)

        # Reject when the plug is not a child of tweakGroups
        if not plug.isChild() or plug.parent().attribute() != handle.attribute(r'tweakGroups'):
            return

        # Reject when the logical index mismatch
        if plug.parent().isElement() and plug.parent().logicalIndex() != self.logicalIndex:
                return

        # Refresh the whole description if the attribute affects the
        # tree view hierarchy.
        if (attribute == handle.attribute(r'tweakGroupOwnerId')
                or attribute == handle.attribute(r'tweakGroupUIOrder')):
            self.getModel().delayedRefreshDescription(
                self.getModifierParent().getDescription().getHandle().node())

        # Update the cached data if the attribute affects the row only
        if attribute == handle.attribute(r'tweakGroupUIName'):
            QTimer.singleShot(0, self.update)


'''
    Represent a sculpt layer in the sculpt modifier node
'''
class IgSplineEditorSculptLayerItem(IgSplineEditorAbstractSculptItem,IgSplineEditorEnableInterface):

    # Maya dg notifications
    dgWatcher       = None
    plugWatcher     = None

    # Name of the Sculpt Layer
    uiName          = r''
    uiNameDefault   = r''

    # Icon of the Sculpt Layer
    uiIcon          = None

    # Weight control
    weightWidget    = None

    # Edit indicator control
    editWidget      = None

    # On Keyframe ?
    isOnKeyframe    = False
    onKeyframeIcon  = None
    offKeyframeIcon = None

    def __init__(self, view, handle, modifier, plug):
        ''' Constructor '''
        IgSplineEditorAbstractSculptItem.__init__(self, view, handle, modifier, plug)
        IgSplineEditorEnableInterface.__init__(self, view)

        # Default Name if no UI name
        self.uiNameDefault = self.getModel().getDefaultSculptLayerName(self.getLogicalIndex())

        # Update initial Sculpt Layer data
        self.update(notify=False)

        # Icon of the Sculpt Layer
        self.uiIcon          = CreateIcon(r':/out_displayLayer.png')
        self.onKeyframeIcon  = CreateIcon(r':/radio-red.svg')
        self.offKeyframeIcon = CreateIcon(r':/radio-black.svg')

        # Register dg notification callbacks
        self.dgWatcher = IgSplineEditorDgWatcher()
        self.dgWatcher.watchAttributeSet(
            handle.node(),
            None,
            self.onMayaAttributeSet)
        self.dgWatcher.watchConnectionMade(
            handle.node(), self.onMayaConnectionChanged)
        self.dgWatcher.watchConnectionBroken(
            handle.node(), self.onMayaConnectionChanged)
        self.dgWatcher.watchAttributeArrayAdded(
            handle.node(),
            handle.attribute(r'tweaks'),
            self.onMayaAttributeArrayChanged)
        self.dgWatcher.watchAttributeArrayRemoved(
            handle.node(),
            handle.attribute(r'tweaks'),
            self.onMayaAttributeArrayChanged)

        # Keep track of keyframes
        self.plugWatcher = PlugWatcher()
        self.plugWatcher.connectPlug(self.getChildPlug(r'strength').name())
        self.plugWatcher.watchTimeChange(self.onMayaTimeChanged)
        self.plugWatcher.watchKeyframeEdited(self.onMayaKeyframeEdited)
        self.updateKeyframe(notify=False)

        # Get notified when the current description changes
        xgg.IgSplineEditor.currentDescriptionChanged.connect(self.onCurrentDescriptionChanged)

    #
    # IgSplineEditorTreeItem interface implementation
    #
    def flags(self, column):
        ''' Return the item flags for the given index '''

        # Flags for a Sculpt Layer row
        if column == IgSplineEditorTreeColumn.NAME:
            # Name column : Sculpt Layer name is editable
            return IgSplineEditorAbstractSculptItem.flags(self, column) | Qt.ItemIsEditable

        # The flag is not handled ..
        return IgSplineEditorAbstractSculptItem.flags(self, column)

    def data(self, column, role):
        ''' Return the data stored under the given role '''

        # Roles for a Sculpt Layer row
        if column == IgSplineEditorTreeColumn.NAME:
            # Name column : UI name and icon
            if role == Qt.DisplayRole or role == Qt.EditRole:
                return self.uiName if len(self.uiName) > 0 else self.uiNameDefault
            elif role == Qt.ForegroundRole:
                return self.getEnabledTextColor()
            elif role == Qt.DecorationRole:
                return self.uiIcon
        elif column == IgSplineEditorTreeColumn.ENABLE:
            # Enable column : enable state
            if role == Qt.DecorationRole:
                return self.getEnabledIcon()
        elif column == IgSplineEditorTreeColumn.KEY:
            # Key column : on keyframe ?
            if role == Qt.DecorationRole:
                return self.onKeyframeIcon if self.isOnKeyframe and not self.isOverridden else self.offKeyframeIcon

        # The role is not handled ..
        return IgSplineEditorAbstractSculptItem.data(self, column, role)

    def setData(self, column, value, role):
        ''' Set the role data for the item at index to value '''

        # Alter the data for a Sculpt Layer row
        if column == IgSplineEditorTreeColumn.NAME:
            # Name column : change the Sculpt Layer name
            if role == Qt.EditRole:
                self.getModel().renameSculptLayer(
                    self.getNodeName(), self.getLogicalIndex(), value)
                return True

        # The role is not handled ..
        return IgSplineEditorAbstractSculptItem.setData(self, column, value, role)

    #
    # Sculpt Layer management
    #
    def update(self, notify=True):
        ''' Update the cached data '''

        # Not in model ?
        if notify and self.getSculptParent() is None:
            return

        # Reject if the dg node no longer exists ..
        if not self.getHandle().isValid() or self.getPlug().isNull():
            return

        # Reject if the logicalIndex no longer exists ..
        indices = om.MIntArray()
        self.getPlug().array().getExistingArrayAttributeIndices(indices)
        if self.getLogicalIndex() not in indices:
            return

        # Any changes to the cached data ?
        anyChanges = False

        # UI name
        uiName = self.getChildPlug(r'uiName').asString()
        if self.uiName != uiName:
            self.uiName = uiName
            anyChanges = True

        # Enable
        isEnabled = self.getChildPlug(r'enable').asBool()
        if self.isEnabled != isEnabled:
            self.isEnabled = isEnabled
            anyChanges = True

        isOwnerEnabled = isSculptGroupOwnerEnabled(
            self.getHandle().node(),
            self.getChildPlug(r'ownerId').asInt())
        if self.isOwnerEnabled != isOwnerEnabled:
            self.isOwnerEnabled = isOwnerEnabled
            anyChanges = True

        # Weight
        if self.weightWidget is None:
            self.weightWidget = AttrFloatFieldSliderUI()
            self.weightWidget.setFieldMinMax(-9999999.9, 9999999.9)
            self.weightWidget.setSliderColor(groove=QColor(0, 0, 0))
            self.weightWidget.setSliderSoftMinMax(0.0, 1.0)
            self.weightWidget.field.setMinimumHeight(DpiScale(12))
            self.weightWidget.connectPlug(r'%s.strength' % self.getPlug().name())
        self.weightWidget.setEnabled(isEnabled and isOwnerEnabled and not self.isOverridden)

        # Edit
        if self.editWidget is None:
            self.editWidget = QPushButton()
            self.editWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.editWidget.setText(maya.stringTable[u'y_xgenm_ui_xgIgSplineEditorTreeItem.kEdit'])
        self.editWidget.setEnabled(isEnabled and isOwnerEnabled and not self.isOverridden)

        isActiveLayer = isActiveSculptLayer(
            self.getModifierParent().getDescription().getHandle().node(),
            self.getHandle().node(),
            self.getLogicalIndex())
        self.editWidget.setStyleSheet(
            IgSplineEditorTreeStyle.EditButtonStyleActive if isActiveLayer else
            IgSplineEditorTreeStyle.EditButtonStyleInactive)

        # Notify the view about the data changes
        if anyChanges and notify:
            self.emitDataChanged()

    def updateKeyframe(self, notify=True):
        ''' Update is the current time is on keyframe '''

        # Not in model ?
        if notify and self.getSculptParent() is None:
            return

        # Time change callback happens on playback so we separate this from
        # the heavy update() method.
        isOnKeyframe, keyValue = self.plugWatcher.isPlugOnKey()
        if self.isOnKeyframe != isOnKeyframe:
            self.isOnKeyframe = isOnKeyframe
            if notify:
                self.emitDataChanged()

    def getWeightWidget(self):
        ''' Get the widget for weight attribute '''
        return self.weightWidget

    def getEditWidget(self):
        ''' Get the widget for edit indicator '''
        return self.editWidget

    def setOverridden(self, isOverridden):
        ''' Update the overridden status of the item '''
        anyChanges = IgSplineEditorEnableInterface.setOverridden(self, isOverridden)
        if anyChanges:
            self.weightWidget.setEnabled(self.isEnabled and self.isOwnerEnabled and not self.isOverridden)
            self.editWidget.setEnabled(self.isEnabled and self.isOwnerEnabled and not self.isOverridden)
            self.emitDataChanged()
        return anyChanges

    def onMayaAttributeSet(self, plug):
        ''' Invoked when the "tweaks" attribute changes '''

        # Get the attribute being set
        attribute = plug.attribute()

        # Get the handle of the sculpt node
        handle = self.getHandle()

        # These attributes affect all rows
        if (attribute == handle.attribute(r'mute')
                or attribute == handle.attribute(r'tweakGroupEnable')
                or attribute == handle.attribute(r'tweakGroupOwnerId')
                or attribute == handle.attribute(r'ownerId')
                or attribute == handle.attribute(r'activeTweak')):
            QTimer.singleShot(0, self.update)

        # Reject when the plug is not a child of tweaks
        if not plug.isChild() or plug.parent().attribute() != handle.attribute(r'tweaks'):
            return

        # Reject when the logical index mismatch
        if plug.parent().isElement() and plug.parent().logicalIndex() != self.logicalIndex:
                return

        # Refresh the whole description if the attribute affects the
        # tree view hierarchy.
        if (attribute == handle.attribute(r'ownerId')
                or attribute == handle.attribute(r'uiOrder')):
            self.getModel().delayedRefreshDescription(
                self.getModifierParent().getDescription().getHandle().node())

        # Update the cached data if the attribute affects the row only
        if (attribute == handle.attribute(r'enable')
                or attribute == handle.attribute(r'uiName')):
            QTimer.singleShot(0, self.update)

    def onMayaConnectionChanged(self, plug):
        ''' Invoked when the connection has been changed '''
        QTimer.singleShot(0, self.update)

    def onMayaAttributeArrayChanged(self, plug):
        ''' Invoked when the number of elements of an array attribute changed '''
        QTimer.singleShot(0, self.update)

    def onMayaTimeChanged(self, time):
        ''' Invoked when Maya time changes '''
        QTimer.singleShot(0, self.updateKeyframe)

    def onMayaKeyframeEdited(self, plug):
        ''' Invoked when Maya keyframe is edited '''
        QTimer.singleShot(0, self.updateKeyframe)

    def onCurrentDescriptionChanged(self):
        ''' Invoked when the current description changed '''
        QTimer.singleShot(0, self.update)

    def retire(self):
        ''' Mark the item is going to be deleted and stop watching plug changes '''
        self.plugWatcher = PlugWatcher()
        self.weightWidget.disconnectPlug()


# ===========================================================================
# Copyright 2021 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
