# Copyright (C) 1997-2013 Autodesk, Inc., and/or its licensors.
# All rights reserved.
#
# The coded instructions, statements, computer programs, and/or related
# material (collectively the "Data") in these files contain unpublished
# information proprietary to Autodesk, Inc. ("Autodesk") and/or its licensors,
# which is protected by U.S. and Canadian federal copyright law and by
# international treaties.
#
# The Data is provided for use exclusively by You. You have the right to use,
# modify, and incorporate this Data into other products for purposes authorized 
# by the Autodesk software license agreement, without fee.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND. AUTODESK
# DOES NOT MAKE AND HEREBY DISCLAIMS ANY EXPRESS OR IMPLIED WARRANTIES
# INCLUDING, BUT NOT LIMITED TO, THE WARRANTIES OF NON-INFRINGEMENT,
# MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE, OR ARISING FROM A COURSE 
# OF DEALING, USAGE, OR TRADE PRACTICE. IN NO EVENT WILL AUTODESK AND/OR ITS
# LICENSORS BE LIABLE FOR ANY LOST REVENUES, DATA, OR PROFITS, OR SPECIAL,
# DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES, EVEN IF AUTODESK AND/OR ITS
# LICENSORS HAS BEEN ADVISED OF THE POSSIBILITY OR PROBABILITY OF SUCH DAMAGES.
import maya
maya.utils.loadStringResourcesForModule(__name__)


##
# @file xgUtil.py
# @brief Contains utility functions for use in the ui module.
#
# <b>CONFIDENTIAL INFORMATION: This software is the confidential and
# proprietary information of Walt Disney Animation Studios ("WDAS").
# This software may not be used, disclosed, reproduced or distributed
# for any purpose without prior written authorization and license
# from WDAS. Reproduction of any section of this software must include
# this legend and all copyright notices.
# Copyright Disney Enterprises, Inc. All rights reserved.</b>
#
# @author Thomas V Thompson II
#
# @version Created 04/08/09
#

from builtins import object
import os
import re
import sys
import traceback
from contextlib import contextmanager
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *

import xgenm as xg
import xgenm.xgGlobal as xgg
import maya.mel as mel
import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaUI as omui

# For exposed getBackingScaleFactor
from xgenm.ui.XgExprEditor import XgExprEditor

def DpiScale(i):
    ''' Scale an integer or a float by the current dpi settings '''
    return omui.MQtUtil.dpiScale(i)

def DpiScalesz(size):
    ''' Scale a QSize by the current dpi settings '''
    scaledSize = QSize(size)
    scaledSize.scale(omui.MQtUtil.dpiScale(size.width()),
                     omui.MQtUtil.dpiScale(size.height()),
                     QtCore.Qt.KeepAspectRatio)
    return scaledSize

def makeLabel(label):
    """Adds spaces to a camel case string.

    >>> _makeLabel('HTMLServicesByTom')
    'HTML Services By Tom'
    """
    if label is None:
        return None

    # Check to see if this is a custom attribute
    if label[:7] == "custom_":
        return label[7:].replace("_"," ",1)

    if label[:8] == "archive_":
        return label[8:].replace("_"," ",1)

    pattern = re.compile('([A-Z][A-Z][a-z])|([a-z][A-Z])')
    result = pattern.sub(lambda m: m.group()[:1] + " " + m.group()[1:], label)
    return result[:1].capitalize() + result[1:]


def labelWidth():
    """Sets the label widgets width given the current font metrics.
    """
    if xgg.LabelWidth > 0:
        return xgg.LabelWidth
    label = QLabel("")
    currentFont = label.font()
    fontMetrics = QFontMetrics(currentFont)
    brect = fontMetrics.boundingRect("XGen Generates Primitives")
    xgg.LabelWidth = brect.width()
    return xgg.LabelWidth

# QToolButton size hint
def ToolButtonSizeHint(button, inSize, bottomText=r'', rightText=r'', withMenu=False):
    ''' Return the size hint of a QToolButton '''
    w = DpiScale(inSize.width())
    h = DpiScale(inSize.height())

    # FontMetrics
    fm    = button.fontMetrics()

    # Include text under the icon
    if len(bottomText) > 0:
        textSize = fm.size(Qt.TextShowMnemonic, bottomText)
        textSize.setWidth(textSize.width() + fm.width(r' ') * 2)
        w = max(w, textSize.width())
        h = h + DpiScale(4) + textSize.height()

    # Include text on the right
    if len(rightText) > 0:
        textSize = fm.size(Qt.TextShowMnemonic, rightText)
        textSize.setWidth(textSize.width() + fm.width(r' ') * 2)
        w = w + DpiScale(4) + textSize.width()
        h = max(h, textSize.height())

    # Include popup menu
    if withMenu:
        w = w + QApplication.style().pixelMetric(QStyle.PM_MenuButtonIndicator)

    return QSize(w, h)

# Create and optionally scale icons
def CreateIcon(path, autoScale=True):
    ''' Create a QIcon with matching resolution '''

    # Only load icons in GUI mode
    if om.MGlobal.mayaState() != om.MGlobal.kInteractive:
        return QIcon()

    # NULL icon
    if len(path) == 0:
        return QIcon()

    # We are looking for icons in xgen/icons directory
    if not path.startswith(r':/') and not os.path.isabs(path):
        path = xg.iconDir() + path

    # SVG doesn't need scaling
    if path.endswith(r'.svg'):
        return QIcon(path)

    # We will load icon file into the QPixmap
    pm = QPixmap()

    # Look for a best resolution
    if autoScale:
        # Default to the standard size icon
        matchingPath = path

        # Get the current scale factor
        scaleFactor = 1.0
        if sys.platform == r'darwin':
            scaleFactor = XgExprEditor.getBackingScaleFactor()
        else:
            scaleFactor = omui.MQtUtil.dpiScale(1.0)

        # Find the best resolution for the current scale factor
        if scaleFactor != 1.0:
            # Modify the path to include the resolution
            resolution = int(scaleFactor * 100.0)
            if resolution != 100:
                root, ext = os.path.splitext(path)
                matchingPath = r'%s_%d%s' % (root, resolution, ext)

        # Try to load the icon in the best resolution
        pm.load(matchingPath)

        # Set device pixel ratio to 2 for 200% images
        if sys.platform == r'darwin':
            if not pm.isNull() and matchingPath.rfind(r'_200') >= 0:
                pm.setDevicePixelRatio(2)

    # Fallback to scaled low resolution icon on failure
    if pm.isNull():
        # Load the standard size icon
        pm.load(path)

        # Scale the icon to the resolution
        if autoScale and not pm.isNull():
            scaledWidth  = omui.MQtUtil.dpiScale(pm.size().width())
            scaledHeight = omui.MQtUtil.dpiScale(pm.size().height())
            pm = pm.scaled(scaledWidth, scaledHeight, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

    # Create the final icon
    return QIcon(pm) if not pm.isNull() else QIcon()

def destroyWidget(wid):
    """Destroy a widget as completely and quickly as possible.
    """
    if not wid:
        return
    wid.hide()
    wid.setParent(None)
    wid.deleteLater()

def createScrollArea( widget ):
          scrollArea = QScrollArea()
          scrollArea.setWidget(widget)
          scrollArea.setWidgetResizable(True)
          scrollArea.setFrameStyle(QFrame.NoFrame)
          scrollArea.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))
          return scrollArea

def currentPalette():
    """Get the current palette. This requires the description editor
    to exist but not necessarily be open.
    """
    if xgg.DescriptionEditor is None:
        return ""
    return xgg.DescriptionEditor.currentPalette()


def currentDescription():
    """Get the current description. This requires the description editor
    to exist but not necessarily be open.
    """
    if xgg.DescriptionEditor is None:
        return ""
    return xgg.DescriptionEditor.currentDescription()


def information(parent, title, message=None, details=None, informative_text=None):
    """Show information with the provided title and message."""
    if message is None:
        message = title
    mbox = QMessageBox(parent)
    mbox.setStandardButtons(QMessageBox.Close)
    mbox.setDefaultButton(QMessageBox.Close)
    mbox.setWindowTitle(title)
    mbox.setWindowModality(Qt.WindowModal)
    mbox.setTextFormat(Qt.PlainText)
    mbox.setText(message)
    if informative_text:
        mbox.setInformativeText(informative_text)
    if details:
        mbox.setDetailedText(details)
    pixmap = mbox.style().standardPixmap(QStyle.SP_MessageBoxInformation)
    mbox.setIconPixmap(pixmap)
    mbox.exec_()

def executeDeferred( script ):
    try:
        import maya.utils as utils
        utils.executeDeferred( script )
    except ImportError:
        # just evaluate the script if maya is not loaded
        try:
            eval( script )
        except:
            import sys
            print(sys.exc_info()[1])
            raise
    except:
        import sys
        print(sys.exc_info()[1])
        raise

def parseFilePath( path ):
    """parse a file path to obtain a custom attribute - the name of the final folder of the path
    expects "/" as filepath delimiter, regardless of os."""
    splitList = path.split("/")
    if len(splitList) == 0:
        return ""
    newattr = splitList[-1]
    # allow for file paths ending relative, such as ${DESC}/Region/
    if newattr == "":
        return splitList[-2]
    else:
        return newattr

def saveScene():
    """ Save scene if the scene has not been saved or modified after last save. """
    sceneName = ""
    try:
        sceneName = cmds.file( query=True, sceneName=True )
        saveSceneStr = maya.stringTable[ u'y_xgenm_ui_util_xgUtil.kSaveScene' ]
        if len( sceneName ) > 0:
            modified = cmds.file( query=True, modified=True )
            if modified:
                # modified after last save, prompt to save the scene
                msgBox = QMessageBox(QMessageBox.NoIcon, saveSceneStr, maya.stringTable[ u'y_xgenm_ui_util_xgUtil.kSaveModifiedScene' ], QMessageBox.Save | QMessageBox.Cancel) #, Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
                ret = msgBox.exec_()
                if ret == QMessageBox.Save:
                    cmds.file( save=True )
                else:
                    sceneName = ""
        else:
            # not saved
            msgBox = QMessageBox(QMessageBox.NoIcon, saveSceneStr, maya.stringTable[ u'y_xgenm_ui_util_xgUtil.kSaveSceneToContinue' ], QMessageBox.Save | QMessageBox.Cancel) #, Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
            ret = msgBox.exec_()
            if ret == QMessageBox.Save:
                mel.eval("SaveScene")
            
            sceneName = cmds.file( query=True, sceneName=True )
    except RuntimeError:
        pass
    
    return sceneName

def uiPalettes(igSplines=False):
    """ Filters out the collections generated by MR rendering. Returns those can be used in UI display """
    pals = xg.palettes()
    ret = []
    for pal in pals:
        if not pal.startswith("XG_RENDER_"):
            ret.append( pal )
    # Interactive groom splines are regular Maya nodes and they are not
    # managed by xgapi.
    if igSplines and xgg.Maya:
        nodes = cmds.xgmSplineQuery(listSplineDescriptions=True)
        if len(nodes) > 0:
            ret.append(xgg.igSplinePalette)
    return ret

def uiDescriptionsAll(igSplines=False):
    # Regular xgen descriptions
    ret = list(xg.descriptions())
    # Interactive groom splines are regular Maya nodes and they are not
    # managed by xgapi.
    if igSplines and xgg.Maya:
        for node in cmds.xgmSplineQuery(listSplineDescriptions=True):
            ret.append(str(node))
    return ret

def uiDescriptions(palette):
    ret = []
    if palette == xgg.igSplinePalette:
        # Interactive groom spline descriptions
        if xgg.Maya:
            for node in cmds.xgmSplineQuery(listSplineDescriptions=True):
                ret.append(str(node))
    else:
        # Regular xgen descriptions
        ret = list(xg.descriptions(palette))
    return ret

@contextmanager
def MayaCmdsTransaction(chunkName=None):
    ''' All commands executed will success or fail as a whole (atomic) '''
    
    # Client can have an instance of the context to interact
    # with the transaction.
    class TransactionContext(object):

        def __init__(self):
            self.selection = None
            
        def saveSelectionList(self):
            self.selection = cmds.ls(sl=True)
            
        def loadSelectionList(self):
            if self.selection:
                cmds.select(self.selection, r=True, ne=True)
        
    
    context     = TransactionContext()
    undoEnabled = cmds.undoInfo(q=True, state=True)
    stackTrace  = None
    
    # Tempoary enable undo if not enabled before
    if not undoEnabled:
        cmds.undoInfo(state=True)
    
    # Open an undo chunk for the following commands
    if chunkName:
        cmds.undoInfo(openChunk=True, chunkName=chunkName)
    else:
        cmds.undoInfo(openChunk=True)
    
    # Caller to execute maya.cmds.* within the context
    try:
        # Make sure there is at least one undoable command
        cmds.xgmNop()
        
        # Execute body
        yield context

        # Load the selection if selection was saved
        context.loadSelectionList()
    except:
        # Error happend ...
        stackTrace = traceback.format_exc()
    finally:
        # Commands executed so far are grouped in one chunk
        cmds.undoInfo(closeChunk=True)
        
        # If any error happend, rollback successful commands
        if stackTrace:
            cmds.undo()
            print(stackTrace)
        
        # Restore undo state
        if not undoEnabled:
            cmds.undoInfo(state=False)

@contextmanager
def MayaWaitCursor():
    ''' Display a wait cursor during the body execution '''
    
    try:
        # Enable wait cursor. Maya's waitCursor command maintains a
        # counter internally so we don't manage here.
        cmds.waitCursor(state=True)

        # Execute body
        yield
    except:
        # Passthrough exceptions
        raise
    finally:
        # Disable wait cursor.
        cmds.waitCursor(state=False)

        
