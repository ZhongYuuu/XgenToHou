from builtins import object
import weakref

import maya.OpenMaya as om


'''
    Invoke callbacks whenever there is a change in Maya dg.

    We use a weak reference to the listener object so that there are no
    circular strong references. GC is not determinstic... Be careful.
'''
class IgSplineEditorDgWatcher(object):

    # Python callbacks
    listeners       = None

    # Maya callbacks
    cbNodeAdded         = None
    cbNodeRemoved       = None
    cbNodeNameChanged   = None
    cbDagChanged        = None
    cbAttributeChanged  = None
    cbSelectionChanged  = None
    cbNodePlugDirtied   = None

    def __init__(self):
        ''' Constructor '''
        self.reset()

    def __del__(self):
        ''' Destructor '''
        self.reset()

    def reset(self):
        ''' Reset all callbacks '''
        self.listeners = dict()

        if self.cbNodeAdded is not None:
            om.MMessage.removeCallback(self.cbNodeAdded)
        self.cbNodeAdded = None

        if self.cbNodeRemoved is not None:
            om.MMessage.removeCallback(self.cbNodeRemoved)
        self.cbNodeRemoved = None

        if self.cbNodeNameChanged is not None:
            om.MMessage.removeCallback(self.cbNodeNameChanged)
        self.cbNodeNameChanged = None

        if self.cbDagChanged is not None:
            om.MMessage.removeCallback(self.cbDagChanged)
        self.cbDagChanged = None

        if self.cbAttributeChanged is not None:
            om.MMessage.removeCallback(self.cbAttributeChanged)
        self.cbAttributeChanged = None

        if self.cbSelectionChanged is not None:
            om.MMessage.removeCallback(self.cbSelectionChanged)
        self.cbSelectionChanged = None

        if self.cbNodePlugDirtied is not None:
            om.MMessage.removeCallback(self.cbNodePlugDirtied)
        self.cbNodePlugDirtied = None

    def watchNodeAdded(self, nodeType, callable):
        ''' Register a dg node added callback '''

        # Ensure Maya node added callback
        if self.cbNodeAdded is None:
            self.cbNodeAdded = om.MDGMessage.addNodeAddedCallback(
                IgSplineEditorDgWatcher.onMayaNodeAdded, nodeType, self.listeners)

        # Add python node added callback
        self.listeners[r'kNodeAdded'] = (
            weakref.proxy(callable.__self__), callable.__name__)

    def watchNodeRemoved(self, nodeType, callable):
        ''' Register a dg node removed callback '''

        # Ensure Maya node removed callback
        if self.cbNodeRemoved is None:
            self.cbNodeRemoved = om.MDGMessage.addNodeRemovedCallback(
                IgSplineEditorDgWatcher.onMayaNodeRemoved, nodeType, self.listeners)

        # Add python node removed callback
        self.listeners[r'kNodeRemoved'] = (
            weakref.proxy(callable.__self__), callable.__name__)

    def watchNodeNameChanged(self, node, callable):
        ''' Register a dg node name changed callback '''
        
        # Ensure Maya node name changed callback
        if self.cbNodeNameChanged is None:
            self.cbNodeNameChanged = om.MNodeMessage.addNameChangedCallback(
                node, IgSplineEditorDgWatcher.onMayaNodeNameChanged, self.listeners)

        # Add python node name changed callback
        self.listeners[r'kNodeNameChanged'] = (
            weakref.proxy(callable.__self__), callable.__name__)

    def watchDagChanged(self, callable):
        ''' Register a dag changed callback '''

        # Ensure Maya dag changed callback
        if self.cbDagChanged is None:
            self.cbDagChanged = om.MDagMessage.addAllDagChangesCallback(
                IgSplineEditorDgWatcher.onMayaDagChanged, self.listeners)

        # Add python dag changed callback
        self.listeners[r'kDagChanged'] = (
            weakref.proxy(callable.__self__), callable.__name__)

    def watchConnectionMade(self, node, callable):
        ''' Register a connection made callback '''

        # Ensure Maya attribute changed callback
        if self.cbAttributeChanged is None:
            self.cbAttributeChanged = om.MNodeMessage.addAttributeChangedCallback(
                node, IgSplineEditorDgWatcher.onMayaAttributeChanged, self.listeners)

        # Add python connection made callback
        self.listeners[r'kConnectionMade'] = (
            weakref.proxy(callable.__self__), callable.__name__, None)

    def watchConnectionBroken(self, node, callable):
        ''' Register a connection broken callback '''

        # Ensure Maya attribute changed callback
        if self.cbAttributeChanged is None:
            self.cbAttributeChanged = om.MNodeMessage.addAttributeChangedCallback(
                node, IgSplineEditorDgWatcher.onMayaAttributeChanged, self.listeners)

        # Add python connection broken callback
        self.listeners[r'kConnectionBroken'] = (
            weakref.proxy(callable.__self__), callable.__name__, None)

    def watchAttributeSet(self, node, attribute, callable):
        ''' Register an attribute set callback '''

        # Ensure Maya attribute changed callback
        if self.cbAttributeChanged is None:
            self.cbAttributeChanged = om.MNodeMessage.addAttributeChangedCallback(
                node, IgSplineEditorDgWatcher.onMayaAttributeChanged, self.listeners)

        # Add python attribute set callback
        self.listeners[r'kAttributeSet'] = (
            weakref.proxy(callable.__self__), callable.__name__, attribute)

    def watchAttributeArrayAdded(self, node, attribute, callable):
        ''' Register an array element added callback '''

        # Ensure Maya attribute changed callback
        if self.cbAttributeChanged is None:
            self.cbAttributeChanged = om.MNodeMessage.addAttributeChangedCallback(
                node, IgSplineEditorDgWatcher.onMayaAttributeChanged, self.listeners)

        # Add python attribute array added callback
        self.listeners[r'kAttributeArrayAdded'] = (
            weakref.proxy(callable.__self__), callable.__name__, attribute)

    def watchAttributeArrayRemoved(self, node, attribute, callable):
        ''' Register an array element removed callback '''

        # Ensure Maya attribute changed callback
        if self.cbAttributeChanged is None:
            self.cbAttributeChanged = om.MNodeMessage.addAttributeChangedCallback(
                node, IgSplineEditorDgWatcher.onMayaAttributeChanged, self.listeners)

        # Add python attribute array removed callback
        self.listeners[r'kAttributeArrayRemoved'] = (
            weakref.proxy(callable.__self__), callable.__name__, attribute)

    def watchSelectionChanged(self, callable):
        ''' Register a selection changed callback '''

        # Ensure Maya selection changed callback
        if self.cbSelectionChanged is None:
            self.cbSelectionChanged = om.MModelMessage.addCallback(
                om.MModelMessage.kActiveListModified,
                IgSplineEditorDgWatcher.onMayaSelectionChanged, self.listeners)

        # Add python selection changed callback
        self.listeners[r'kSelectionChanged'] = (
            weakref.proxy(callable.__self__), callable.__name__)

    def watchNodePlugDirtied(self, node, callable):
        ''' Register a node plug dirty callback '''

        # Ensure Maya node plug dirty callback
        if self.cbNodePlugDirtied is None:
            self.cbNodePlugDirtied = om.MNodeMessage.addNodeDirtyPlugCallback(
                node, IgSplineEditorDgWatcher.onMayaNodePlugDirtied, self.listeners)

        # Add python node plug dirty callback
        self.listeners[r'kNodePlugDirty'] = (
            weakref.proxy(callable.__self__), callable.__name__)

    @staticmethod
    def onMayaNodeAdded(node, listeners):
        ''' Maya callback when a dg node is added '''
        proxy, method = listeners.get(r'kNodeAdded', (None, None))
        if proxy and method:
            getattr(proxy, method)(node)

    @staticmethod
    def onMayaNodeRemoved(node, listeners):
        ''' Maya callback when a dg node is removed '''
        proxy, method = listeners.get(r'kNodeRemoved', (None, None))
        if proxy and method:
            getattr(proxy, method)(node)

    @staticmethod
    def onMayaNodeNameChanged(node, prevName, listeners):
        ''' Maya callback when a dg node name changes '''
        proxy, method = listeners.get(r'kNodeNameChanged', (None, None))
        if proxy and method:
            getattr(proxy, method)(node, prevName)

    @staticmethod
    def onMayaDagChanged(msgType, child, parent, listeners):
        ''' Maya callback when dag changes '''
        proxy, method = listeners.get(r'kDagChanged', (None, None))
        if proxy and method:
            getattr(proxy, method)(msgType, child, parent)

    @staticmethod
    def __invokeAttributeChanged(msg, plug, listeners, type, key):
        ''' Helper to invoke the python callback of the specified type '''
        
        # Not interested in the attribute change type?
        if (msg & type) == 0:
            return

        # Unpack the python callback
        proxy, method, attribute = listeners.get(key, (None, None, None))
        
        # Lost reference?
        if not proxy or not method:
            return
        
        # Not interested in the attribute ?
        if attribute is not None and plug.attribute() != attribute:
            isInterested = False

            # Go up to check if the compound/multi parent is interested 
            parentPlug = plug
            while not parentPlug.isNull():
                if parentPlug.attribute() == attribute:
                    isInterested = True
                    break
                if parentPlug.isChild():
                    parentPlug = parentPlug.parent()
                elif parentPlug.isElement():
                    parentPlug = parentPlug.array()
                else:
                    break

            # Still not a plug of interest
            if not isInterested:
                return

        # Invoke the callback (Instance Method only!)
        getattr(proxy, method)(plug)

    @staticmethod
    def onMayaAttributeChanged(msg, plug, otherPlug, listeners):
        ''' Maya callback when an attribute changes '''

        # Connection Made ?
        IgSplineEditorDgWatcher.__invokeAttributeChanged(msg, plug, listeners,
            om.MNodeMessage.kConnectionMade, r'kConnectionMade')

        # Connection Broken ?
        IgSplineEditorDgWatcher.__invokeAttributeChanged(msg, plug, listeners,
            om.MNodeMessage.kConnectionBroken, r'kConnectionBroken')

        # Attribute Set ?
        IgSplineEditorDgWatcher.__invokeAttributeChanged(msg, plug, listeners,
            om.MNodeMessage.kAttributeSet, r'kAttributeSet')

        # Attribute Array Added ?
        IgSplineEditorDgWatcher.__invokeAttributeChanged(msg, plug, listeners,
            om.MNodeMessage.kAttributeArrayAdded, r'kAttributeArrayAdded')

        # Attribute Array Removed ?
        IgSplineEditorDgWatcher.__invokeAttributeChanged(msg, plug, listeners,
            om.MNodeMessage.kAttributeArrayRemoved, r'kAttributeArrayRemoved')

    @staticmethod
    def onMayaSelectionChanged(listeners):
        ''' Maya callback when the current selection list changes '''
        proxy, method = listeners.get(r'kSelectionChanged', (None, None))
        if proxy and method:
            getattr(proxy, method)()

    @staticmethod
    def onMayaNodePlugDirtied(node, plug, listeners):
        ''' Maya callback when a plug is dirtied '''
        proxy, method = listeners.get(r'kNodePlugDirty', (None, None))
        if proxy and method:
            getattr(proxy, method)(node, plug)


'''
    Python wrapper for MObjectHandle
'''
class IgSplineEditorDgNode(object):

    # Maya dg node
    handle = om.MObjectHandle()

    def __init__(self, node = om.MObject()):
        ''' Constructor '''
        self.handle = om.MObjectHandle(node)

    def __hash__(self):
        ''' Return the hash code of the dg node pointer '''
        return self.handle.hashCode()

    def __eq__(self, other):
        ''' Return True if this == other '''
        return self.handle == other.handle

    def __repr__(self):
        ''' Return the string representation '''
        if self.handle.isAlive():
            if self.handle.isValid():
                return self.name()
            else:
                return r'%s (deleted)' % self.name()
        return r'Invalid'

    def node(self):
        ''' Return the object of the dg node '''
        return self.handle.object()

    def attribute(self, name):
        ''' Return the attribute MObject '''
        if self.handle.isValid():
            return om.MFnDependencyNode(self.handle.object()).attribute(name)
        return om.MObject()

    def name(self):
        ''' Return the unique name of the dg node '''
        if self.handle.isValid():
            # Get the MObject of the dg/dag node
            node = self.handle.object()
            if node.hasFn(om.MFn.kDagNode):
                # Return the unique name of the dag node
                return om.MFnDagNode(node).partialPathName()
            else:
                # Return the name of the dg node
                return om.MFnDependencyNode(node).name()
        return r''

    def isValid(self):
        ''' Return True if the dg node exists in scene '''
        return self.handle.isValid()




# ===========================================================================
# Copyright 2021 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
