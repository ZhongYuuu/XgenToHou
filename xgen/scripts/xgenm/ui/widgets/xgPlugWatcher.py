from builtins import object
from builtins import range
import weakref

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma


'''
    Watch and manipulate a Maya plug of a dg node.
    
    We use a weak reference to the listener object so that there are no
    circular strong references. GC is not determinstic... Be careful.
'''
class PlugWatcher(object):
    
    # MPlug and MObjectHandle of the interest
    plug = om.MPlug()
    node = om.MObjectHandle()
    attr = om.MObjectHandle()

    # Helper to call MFnAnimCurve.find()
    uintRef = None
    
    # Maya callbacks
    mayaAttributeChangedCallback = None
    mayaTimeChangeCallback = None
    mayaKeyframeEditedCallback = None
    
    # Weak references to python callbacks
    weakRefs = dict()
    
    def __init__(self):
        ''' Constructor '''
        self.resetPlug()
    
    def __del__(self):
        ''' Clean up callbacks '''
        self.resetPlug()
        
    def __repr__(self):
        ''' Return the string representation '''
        return r'PlugWatcher at %s' % self.plug.name()
    
    def resetPlug(self):
        ''' Reset this watcher to initial state '''
        
        # Reset the plug and node
        self.plug = om.MPlug()
        self.node = om.MObjectHandle()
        self.attr = om.MObjectHandle()

        # Allocate helper
        self.uintRef = om.MScriptUtil()
        self.uintRef.createFromInt(0)

        # Reset the Maya callbacks
        if self.mayaAttributeChangedCallback is not None:
            om.MMessage.removeCallback(self.mayaAttributeChangedCallback)
        self.mayaAttributeChangedCallback = None
        
        if self.mayaTimeChangeCallback is not None:
            om.MMessage.removeCallback(self.mayaTimeChangeCallback)
        self.mayaTimeChangeCallback = None
        
        if self.mayaKeyframeEditedCallback is not None:
            om.MMessage.removeCallback(self.mayaKeyframeEditedCallback)
        self.mayaKeyframeEditedCallback = None
            
        # Reset python callbacks
        self.weakRefs = dict()

    def connectPlug(self, plugName):
        ''' Connect to a Maya plug by name '''
        
        # Find the plug by matching plug name
        try:
            sl = om.MSelectionList()
            sl.add(plugName)
            sl.getPlug(0, self.plug)
        except:
            self.plug = om.MPlug()

        # Plug not found ?
        if self.plug.isNull():
            self.resetPlug()
            return
            
        # Reset callbacks if we connect to a different node
        if self.node != self.plug.node():
            plug = om.MPlug(self.plug)
            self.resetPlug()
            self.plug = plug
            self.node = om.MObjectHandle(self.plug.node())
            self.attr = om.MObjectHandle(self.plug.attribute())
        
        if self.attr != self.plug.attribute():
            self.attr = om.MObjectHandle(self.plug.attribute())
        
    def watchAttributeSet(self, callable):
        ''' Invoke callback when plug changes '''

        # Ensure Maya callback
        self.__ensureAttributeChangedCallback()

        # Replace the python callback
        self.weakRefs[r'kAttributeSet'] = (
            weakref.ref(callable.__self__), callable.__name__, self.attr)
        
    def watchAttributeLock(self, callable):
        ''' Invoke callback when plug is locked / unlocked '''

        # Ensure Maya callback
        self.__ensureAttributeChangedCallback()

        # Replace the python callback
        self.weakRefs[r'kAttributeLocked']   = (
            weakref.ref(callable.__self__), callable.__name__, self.attr)
        self.weakRefs[r'kAttributeUnlocked'] = (
            weakref.ref(callable.__self__), callable.__name__, self.attr)
        
    def watchAttributeConnection(self, callable):
        ''' Invoke callback when plug is connected / disconnected '''

        # Ensure Maya callback
        self.__ensureAttributeChangedCallback()

        # Replace the python callback
        self.weakRefs[r'kConnectionMade']   = (
            weakref.ref(callable.__self__), callable.__name__, self.attr)
        self.weakRefs[r'kConnectionBroken'] = (
            weakref.ref(callable.__self__), callable.__name__, self.attr)
        
    def watchTimeChange(self, callable):
        ''' Invoke callback when time changes '''
        
        # Ensure Maya callbacks
        self.__ensureTimeChangeCallback()
        
        # Replace the python callback
        self.weakRefs[r'kTimeChange'] = (
            weakref.ref(callable.__self__), callable.__name__)
        
    def watchKeyframeEdited(self, callable):
        ''' Invoke callback when keyframe is edited '''

        # Ensure Maya callbacks
        self.__ensureKeyframeEditedCallback()

        # Replace the python callback
        self.weakRefs[r'kKeyframeEdited'] = (
            weakref.ref(callable.__self__), callable.__name__)

    def isValidPlug(self):
        ''' Return True if the plug is valid '''
        return self.node.isValid() and self.attr.isValid() and not self.plug.isNull()
    
    def isPlugLocked(self):
        ''' Return True if the plug is locked '''
        return self.plug.isLocked() if self.isValidPlug() else False
    
    def lockPlug(self):
        ''' Lock the plug '''
        if self.isValidPlug():
            cmds.setAttr(self.plug.name(), l=True)
            
    def unlockPlug(self):
        ''' Unlock the plug '''
        if self.isValidPlug():
            cmds.setAttr(self.plug.name(), l=False)
            
    def isPlugConnected(self, asDst=True, asSrc=False):
        ''' Return True if the plug is connected '''
        if self.isValidPlug():
            return (asDst and self.plug.isDestination()) or (asSrc and self.plug.isSource())
        return False
    
    def plugSourceName(self):
        ''' Return the source plug name of the connection '''
        return self.plug.source().name() if self.isPlugConnected() else r''
    
    def plugOpenSourceAE(self):
        ''' Open the attribute editor for the source plug '''
        srcPlugName = self.plugSourceName()
        if len(srcPlugName) > 0:
            srcNodeName = srcPlugName.split(r'.')[0]
            mel.eval(r'evalDeferred("showEditor %s");' % srcNodeName)
    
    def breakPlugConnection(self, asDst=True, asSrc=False):
        ''' Disconnect connected plugs '''
        if self.isValidPlug():
            if asDst:
                srcPlug = self.plug.source()
                if not srcPlug.isNull():
                    cmds.disconnectAttr(srcPlug.name(), self.plug.name())
            if asSrc:
                dstPlugs = om.MPlugArray()
                if self.plug.destinations(dstPlugs):
                    for i in range(0, dstPlugs.length()):
                        cmds.disconnectAttr(self.plug.name(), dstPlugs[i].name())
    
    def isPlugHasExpression(self):
        ''' Return True if the plug has an expression '''
        if self.isValidPlug():
            srcPlug = self.plug.source()
            return not srcPlug.isNull() and srcPlug.node().hasFn(om.MFn.kExpression)
        return False
    
    def plugSetExpression(self):
        ''' Open Expression Editor for the plug '''
        if self.isValidPlug():
            plugNameList = self.plug.name().split(r'.')
            plugNode     = plugNameList[0]
            plugAttr     = r'.'.join(plugNameList[1:])
            mel.eval(r'expressionEditor EE "%s" "%s";' % (plugNode, plugAttr))
            
    def plugDeleteExpression(self):
        ''' Delete the expression for the plug '''
        if self.isValidPlug():
            srcPlug = self.plug.source()
            if not srcPlug.isNull() and srcPlug.node().hasFn(om.MFn.kExpression):
                exprNode = om.MFnDependencyNode(srcPlug.node())
                mel.eval(r'delete "%s"' % exprNode.name())
            
    def isPlugKeyed(self):
        ''' Return True if the plug is driven by a curve '''
        if self.isValidPlug():
            srcPlug = self.plug.source()
            return not srcPlug.isNull() and srcPlug.node().hasFn(om.MFn.kAnimCurve)
        return False
    
    def isPlugDrivenKeyed(self):
        ''' Return True if the plug is keyed and the key is driven '''
        if self.isValidPlug():
            srcPlug = self.plug.source()
            if not srcPlug.isNull() and srcPlug.node().hasFn(om.MFn.kAnimCurve):
                inputPlug = om.MFnDependencyNode(srcPlug.node()).findPlug(r'input', False)
                return not inputPlug.isNull() and inputPlug.isDestination()
        return False
    
    def plugSetDrivenKey(self):
        ''' Set driven keyframe on the plug '''
        if self.isValidPlug():
            plugNameList = self.plug.name().split(r'.')
            plugNode     = plugNameList[0]
            plugAttr     = r'.'.join(plugNameList[1:])
            mel.eval(r'setDrivenKeyWindow "%s" {"%s"};' % (plugNode, plugAttr))
    
    def isPlugOnKey(self):
        ''' Return (True, KeyValue) if the plug is on the key for the current time '''
        if self.isValidPlug():
            srcPlug = self.plug.source()
            if not srcPlug.isNull() and srcPlug.node().hasFn(om.MFn.kAnimCurve):
                curve    = oma.MFnAnimCurve(srcPlug.node())
                time     = oma.MAnimControl.currentTime()
                uintPtr  = self.uintRef.asUintPtr()
                if curve.find(time, uintPtr):
                    return (True, curve.value(om.MScriptUtil.getUintArrayItem(uintPtr, 0)))
                return (False, None)
        return (False, None)
    
    def plugSetKey(self):
        ''' Set keyframe on the plug '''
        if self.isValidPlug():
            cmds.setKeyframe(self.plug.name())
    
    def plugCreateTexture(self):
        ''' Create texture node and connect to the plug '''
        if self.isValidPlug():
            mel.eval(r'defaultNavigation -force true -createNew -destination "%s";' % self.plug.name())
            
    def isPlugIgnoreWhenRendering(self):
        ''' Return True if the connection is ignored when rendering '''
        if self.isValidPlug():
            return not cmds.shadingConnection(self.plug.name(), q=True, cs=True)
        return False
    
    def plugToggleIgnoreWhenRendering(self):
        ''' Toggle the ignore when rendering state '''
        if self.isValidPlug():
            ignoreWhenRendering = self.isPlugIgnoreWhenRendering()
            onOff = r'on' if ignoreWhenRendering else r'off'
            mel.eval(r'shadingConnection -e -cs %s { "%s" };' % (onOff, self.plug.name()))
            
    def plugAsFloat(self):
        ''' Return the plug value as float '''
        return self.plug.asFloat() if self.isValidPlug() else 0.0
    
    def plugSetFloat(self, value):
        ''' Set the plug value as float '''
        if self.isValidPlug():
            cmds.setAttr(self.plug.name(), value)
            
    def __ensureAttributeChangedCallback(self):
        ''' Register Maya Attribute Changed callback '''

        # No valid plug ?
        if not self.isValidPlug():
            return

        # Already registered ?
        if self.mayaAttributeChangedCallback is not None:
            return

        # Register Maya attribute changed callback
        self.mayaAttributeChangedCallback = om.MNodeMessage.addAttributeChangedCallback(
            self.plug.node(), PlugWatcher.onAttributeChanged, self.weakRefs)

    def __ensureTimeChangeCallback(self):
        ''' Register Maya Time Change callback '''

        # Already registered ?
        if self.mayaTimeChangeCallback is not None:
            return
        
        # Register Maya time change callback
        self.mayaTimeChangeCallback = om.MDGMessage.addTimeChangeCallback(
            PlugWatcher.onTimeChange, self.weakRefs)

    def __ensureKeyframeEditedCallback(self):
        ''' Register Maya keyframe edited callback '''

        # Already registered ?
        if self.mayaKeyframeEditedCallback is not None:
            return
        
        # Register Maya keyframe edited callback
        self.mayaKeyframeEditedCallback = oma.MAnimMessage.addAnimKeyframeEditedCallback(
            PlugWatcher.onKeyframeEdited, self.weakRefs)
        
    @staticmethod
    def __invokeAttributeChanged(msg, plug, weakRefs, type, key):
        ''' Helper to invoke the python callback of the specified type '''
        
        # Not interested in the attribute change type?
        if (msg & type) == 0:
            return
        
        # No python callback ?
        if key not in weakRefs:
            return
        
        # Unpack the python callback
        weakInst, imName, attr = weakRefs[key] 
        
        # Not interested in the attribute ?
        if attr != plug.attribute():
            return

        # Invoke the callback (Instance Method only!)
        instance = weakInst()
        if instance:
            getattr(instance, imName)(plug)
        
    @staticmethod
    def onAttributeChanged(msg, plug, otherPlug, weakRefs):
        ''' Invoked when a plug changed '''
        
        # Attribute Set ?
        PlugWatcher.__invokeAttributeChanged(msg, plug, weakRefs,
            om.MNodeMessage.kAttributeSet, r'kAttributeSet')
        
        # Attribute Locked ?
        PlugWatcher.__invokeAttributeChanged(msg, plug, weakRefs,
            om.MNodeMessage.kAttributeLocked, r'kAttributeLocked')
        
        # Attribute Unlocked ?
        PlugWatcher.__invokeAttributeChanged(msg, plug, weakRefs,
            om.MNodeMessage.kAttributeUnlocked, r'kAttributeUnlocked')

        # Connection Made
        PlugWatcher.__invokeAttributeChanged(msg, plug, weakRefs,
            om.MNodeMessage.kConnectionMade, r'kConnectionMade')

        # Connection Broken
        PlugWatcher.__invokeAttributeChanged(msg, plug, weakRefs,
            om.MNodeMessage.kConnectionBroken, r'kConnectionBroken')
        
    @staticmethod
    def onTimeChange(time, weakRefs):
        ''' Invoked when time changes '''
        
        # No python callback ?
        if r'kTimeChange' not in weakRefs:
            return
        
        # Unpack the python callback
        weakInst, imName = weakRefs[r'kTimeChange'] 
        
        # Invoke the callback (Instance Method only!)
        instance = weakInst()
        if instance:
            getattr(instance, imName)(time)
            
    @staticmethod
    def onKeyframeEdited(objects, weakRefs):
        ''' Invoked when keyframe is edited '''
        
        # No python callback ?
        if r'kKeyframeEdited' not in weakRefs:
            return
        
        # Unpack the python callback
        weakInst, imName = weakRefs[r'kKeyframeEdited'] 
        
        # Invoke the callback (Instance Method only!)
        instance = weakInst()
        if instance:
            getattr(instance, imName)(objects)
        
# ===========================================================================
# Copyright 2021 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
