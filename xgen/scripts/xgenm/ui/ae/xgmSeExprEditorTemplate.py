from __future__ import division
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from shiboken2 import wrapInstance
import maya.cmds as cmds
import maya.OpenMayaUI as omui
import xgenm.xgGlobal as xgg
import maya.OpenMaya as om

from xgenm.ui.XgExprEditor import XgExprEditor
import sys

long_type = int if sys.version_info[0] >= 3 else long

# This script is executed in batch mode!
_mayaMainWindowPtr = None
_mayaMainWindow    = None
if om.MGlobal.mayaState() == om.MGlobal.kInteractive:
    _mayaMainWindowPtr = omui.MQtUtil.mainWindow()
    _mayaMainWindow    = wrapInstance(long_type(_mayaMainWindowPtr), QWidget)

xgmSeExprEditor = None
attr = ""

def resetEditor():
    ''' Clear XgExprEditor members '''

    global xgmSeExprEditor
    global attr

    xgmSeExprEditor.setParent(None)
    xgmSeExprEditor.deleteLater()
    xgmSeExprEditor = None
    attr = ""

def onXgmSeExprEditorFinished(result):
    ''' Callback when the XgExprEditor is closed '''
    
    global xgmSeExprEditor
    global attr

    # If the user accepts the expression..
    if result == QDialog.Accepted:

        # Get the expression string and set to the attribute
        val = xgmSeExprEditor.attributeValue()
        cmds.setAttr( attr, val, typ=r"string" )

    # Clear the editor dialog object
    resetEditor()

def onXgmSeExprEditorApplyExpr():
    ''' Callback when the XgExprEditor's apply button is clicked '''

    global xgmSeExprEditor
    global attr

    # Get the expression string and set to the attribute
    val = xgmSeExprEditor.attributeValue()
    cmds.setAttr(attr, val, typ=r"string" )

def onRequestColorPicker(position, mini, result):
    ''' Callback when the XgExprEditor requests a color picker '''

    if xgg.Maya:
        # Open color picker dialog
        rgbF = [result.red()/255.0, result.green()/255.0, result.blue()/255.0]
        if mini:
            cmds.colorEditor(rgbValue=rgbF, mini=True, pos=[position.x()-424/2,position.y()-178/2])
        else:
            cmds.colorEditor(rgbValue=rgbF, pos=[position.x(),position.y()])

        # Check the result
        if cmds.colorEditor(query=True, result=True):
            # Success
            rgbF = cmds.colorEditor(query=True, rgb=True)
            result.setRgb(int(rgbF[0] * 255.0), int(rgbF[1] * 255.0), int(rgbF[2] * 255.0), 255)
        else:
            # No color was chosen, return an invalid color
            result.setNamedColor("")

def XgmSeExprShowEditor(nodeAttr):
    ''' Open an XgExprEditor dialog for this expression '''

    global xgmSeExprEditor
    global attr

    # Return if there is already an open dialog
    if xgmSeExprEditor is not None:
        return

    attr = nodeAttr
    value = cmds.getAttr(attr)

    # Create XgExprEditor dialog object
    xgmSeExprEditor = XgExprEditor(attr, value, "", "", _mayaMainWindow)

    # Set editor dialog attributes
    xgmSeExprEditor.setModal(False)
    xgmSeExprEditor.setAttribute(Qt.WA_DeleteOnClose)
    xgmSeExprEditor.setWindowFlags(Qt.Tool | xgmSeExprEditor.windowFlags())

    # Hook on the editor dialog signals
    xgmSeExprEditor.finished.connect(onXgmSeExprEditorFinished)
    xgmSeExprEditor.applyExpr.connect(onXgmSeExprEditorApplyExpr)
    xgmSeExprEditor.requestColorPicker.connect(onRequestColorPicker)

    # Show the modeless editor dialog and set focus
    xgmSeExprEditor.show()
    xgmSeExprEditor.activateWindow()
    xgmSeExprEditor.setFocus()
# ===========================================================================
# Copyright 2021 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
