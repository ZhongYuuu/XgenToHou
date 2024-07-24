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


#
# @file xgDescriptionEditor.py
# @brief Contains the XGen Description Editor base UI.
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
# @version Created 03/02/09
#


from builtins import object
from builtins import range
import os
import sys
import inspect
import traceback
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from shiboken2 import wrapInstance

import xgenm as xg
import xgenm.xgGlobal as xgg
import xgenm.xgUtil as xgu
import xgenm.xgLog as xglog
if xgg.Maya:
    import maya.mel as mel
    import maya.cmds as cmds
    import maya.OpenMaya as om
    import maya.OpenMayaUI as mui
    from xgenm.xmaya.xgmArchiveExport import xgmArchiveExport
    from xgenm.xmaya.xgmArchiveExportBatchUI import xgmArchiveExportBatchUI

from xgenm.ui.widgets import *
from xgenm.ui.tabs import *
from xgenm.ui.fxmodules import *
from xgenm.ui.xgConsts import *
from xgenm.ui.XgMessageUI import XgMessageUI
from xgenm.ui.util.xgUtil import *
from xgenm.ui.util.xgProgressBar import setProgressInfo
from xgenm.ui.util.xgProgressBar import isProgressVisible
from xgenm.ui.util.xgComboBox import _ComboBoxUI
from xgenm.ui.dialogs.xgImportFile import importFile
from xgenm.ui.dialogs.xgExportFile import exportFile
from xgenm.ui.dialogs.xgImportPreset import importPreset
from xgenm.ui.dialogs.xgExportPreset import exportPreset
from xgenm.ui.dialogs.igExport import igExportFile
from xgenm.ui.dialogs.igImport import igImportFile
from xgenm.ui.dialogs.xgCreateDescription import createDescription
from xgenm.ui.dialogs.xgCopyMoveDescription import copyDescription
from xgenm.ui.dialogs.xgCopyMoveDescription import moveDescription
from xgenm.ui.dialogs.xgStrayPercentage import strayPercentage
from xgenm.ui.dialogs.xgExportToP3D import exportToP3D
from xgenm.ui.dialogs.xgExportCaf import exportCaf
from xgenm.ui.dialogs.xgMapBindings import mapBindings
from xgenm import XgExternalAPI as xgapi
import xgenm.xmaya.xgmExternalAPI as xgmExternalAPI
from contextlib import contextmanager
import sys
from maya.internal.common.qt.doubleValidator import MayaQclocaleDoubleValidator


long_type = int if sys.version_info[0] >= 3 else long

###########################################################################

def _isUI(name, cls, xgenmodules):
    """
    Return true if the name is an XGen UI class that corresponds to one of the
    XGen modules.
    """
    if not inspect.isclass(cls): return False
    if not name.endswith("TabUI"): return False
    xgenname = name[:-5] # strip off TabUI
    if not xgenname in xgenmodules: return False
    return True

###########################################################################

def _importUI(basepath):
    """
    Import custom UI for the custom FX modules.

    We read through basepath/plugins/*.py and return a dictionary of all the UI
    classes we found.

    We generate a warning if the directory has the same UI class twice, and we
    use the most recent one (in alphabetical order).

    This gets invoked with the GlobalRepo, LocalRepo, and UserRepo as basepath.
    """
    classes = dict()

    # Look up ~/xgen/plugins if it exists.
    uipath = os.path.join(basepath, "plugins")
    if not os.path.isdir(uipath): return classes

    # Add ~/xgen/plugins to the python path if it isn't yet there.
    # Remove it in the finally block.
    sys.path.insert(0, uipath)
    try:
        # List ~/xgen/plugins and import all the python files.
        # Sort so that duplicate class names at least get a consistent result.
        files = sorted([ x for x in os.listdir(uipath) if x.endswith(".py") ])

        xgenmodules = set(xgapi.availableModules())

        for filename in files:
            # Strip off the '.py' and import.
            pyname = filename[:-3]

            # equivalent to "import pyname", but catch errors and go on to the
            # next file.
            try:
                pymodule = __import__(pyname)
                print(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kLoadedPathPython'  ] % (uipath, pyname))
            except Exception as e:
                print(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kFailedToLoadPathPython'  ] % (uipath, pyname, e))
                traceback.print_exc()
                continue

            for name in dir(pymodule):
                cls = getattr(pymodule, name)
                if not _isUI(name, cls, xgenmodules): continue
                if name in classes:
                    print(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kWarningDefinedTwiceInDirectory'  ] % (name, uipath))
                classes[name] = cls

    finally:
        sys.path.pop(0)

    return classes
# end _importUI

class PaletteExpressionUI(ExpressionUI):
    """
    Specialized widget for palette expressions which provides a remove expression button.
    """
    def __init__(self,attr):
        # if its a color expr, allow color to be painted                                                                                                                           
        isColor = True if attr.find("custom_color") != -1 else False
        ExpressionUI.__init__(self,attr, maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kGlobalExpression'  ] % attr, "Palette","",isColor)
        
    def BuildHorizontalLayout(self):
        removeButton = QToolButton()
        removeButton.setIcon(CreateIcon("xgDelete.png"))
        removeButton.setFixedSize(DpiScale(24),DpiScale(24))
        removeButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kRemoveAnn'  ])
        self.connect(removeButton, QtCore.SIGNAL("clicked()"), self.remPalExpr)

        layout = QHBoxLayout()
        QLayoutItem.setAlignment(layout, Qt.AlignLeft)
        layout.addWidget(self.label)
        layout.addWidget(self.optionButton)
        layout.addWidget(removeButton)
        layout.setSpacing(DpiScale(3))
        layout.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
        return layout

    def remPalExpr(self):
        if self.attr=="":
            return
        de = xgg.DescriptionEditor

        key = de.currentPalette() + " " + self.attr
        if key in de.palExprExpandState:
            del de.palExprExpandState[key]

        xg.remCustomAttr(self.attr,de.currentPalette())
        de.refreshPalExprs()

class PaletteExpressionExpandUI(ExpandUI):
    def __init__(self, palette, text, expanded=True):
        ExpandUI.__init__(self, text, expanded)
        self.palette = palette

###########################################################################
ExportStartFrame = "1.0"
ExportEndFrame = "2.0"
Anim = False

class ExportUI(QDialog):
    """Function to export geometry for XGen using a dialog.

    This provides a simple dialog to accept the file name and a check
    box for optionally animated results. The user can use a browser to
    search for the file.
    """
    def __init__(self):
        QDialog.__init__(self)
        self.setWindowTitle(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kXgenExport'  ])
        self.setSizeGripEnabled(True)
        self.setMinimumWidth(DpiScale(550))
        layout = QVBoxLayout()
        self.anim = CheckBoxUI(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kAnimatedXGenExport'  ],
                               maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kSetToTrueIfTheGeometryIsAnimated'  ])
        self.anim.setValue(Anim)
        self.connect(self.anim.boxValue[0],
                     QtCore.SIGNAL("clicked(bool)"),
                     lambda x: self.animUpdate())
        layout.addWidget(self.anim)

        label = QLabel(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kFrameRange'  ])
        label.setFixedWidth(int(labelWidth()))
        label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        label.setIndent(DpiScale(10))
        self.startFrame = QLineEdit()
        self.startFrame.setValidator(MayaQclocaleDoubleValidator(-100000.0,100000.0,6,self.startFrame))
        self.startFrame.setText(ExportStartFrame)
        self.startFrame.setFixedWidth(DpiScale(70))
        self.startFrame.setToolTip(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kFirstFrameAnn' ])
        self.endFrame = QLineEdit()
        self.endFrame.setValidator(MayaQclocaleDoubleValidator(-100000.0,100000.0,6,self.endFrame))
        self.endFrame.setText(ExportEndFrame)
        self.endFrame.setFixedWidth(DpiScale(70))
        self.endFrame.setToolTip(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kLastFrameAnn' ])
        
        row = QWidget()
        boxlayout = QHBoxLayout()
        QLayoutItem.setAlignment(boxlayout, Qt.AlignLeft)
        boxlayout.addWidget(label)
        boxlayout.addWidget(self.startFrame)
        boxlayout.addSpacing(DpiScale(5))
        boxlayout.addWidget(self.endFrame)
        row.setLayout(boxlayout)
        layout.addWidget(row)        

        row = QWidget()
        hbox = QHBoxLayout()
        QLayoutItem.setAlignment(hbox, Qt.AlignRight)
        hbox.setSpacing(DpiScale(3))
        hbox.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
        self.exportButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kExportFileButton'  ])
        self.exportButton.setFixedWidth(DpiScale(100))
        self.exportButton.setAutoRepeat(False)
        self.exportButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kExportFileAnn'])
        self.connect(self.exportButton, QtCore.SIGNAL("clicked()"),
                     self.accept)
        hbox.addWidget(self.exportButton)
        self.cancelButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kCancelButton'  ])
        self.cancelButton.setFixedWidth(DpiScale(100))
        self.cancelButton.setAutoRepeat(False)
        self.cancelButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kCancelExportAnn' ])
        self.connect(self.cancelButton, QtCore.SIGNAL("clicked()"),
                     self.reject)
        hbox.addWidget(self.cancelButton)
        row.setLayout(hbox)
        layout.addWidget(row)
        self.setLayout(layout)
        self.animUpdate()

    def animUpdate(self):
        value = self.anim.value()
        if value:
            self.startFrame.setEnabled(True)
            self.endFrame.setEnabled(True)
        else:
            self.startFrame.setEnabled(False)
            self.endFrame.setEnabled(False)
            
    def getAnim(self):
        return self.anim.value()

    def getStartFrame(self):
        return str(self.startFrame.text())

    def getEndFrame(self):
        return str(self.endFrame.text())


class DescriptionEditorUI(QWidget):
    xgCurrentDescriptionChanged = QtCore.Signal( str, str )
    xgDescriptionEditorEnableUI = QtCore.Signal( int )

    # Enum for Preview/Clear Modes
    class PreviewMode(object):
        Description = 0
        Collection = 1
        All = 2

    class Previewer(object):
        """ Handler for managing calls to preview. The previewer collects and executes 
            calls on idle with lowest priority to make sure preview is always the last 
            process to run. The previewer collects calls in a set to make sure duplicates 
            are not run. 
        """
        def __init__(self):
            self._stack = set()
            self._tracking = True
            self._idle = True

        def add( self, item ):      
            if cmds.about(batch=True):
                # no need to record preview calls in batch
                return

            if not self._idle:
                # immediate eval if not idle
                mel.eval(item) 
                return

            if not self._tracking:
                return

            if not len(self._stack):
                import maya.cmds
                script = 'xgg.DescriptionEditor.previewer.execute()'
                maya.cmds.evalDeferred( script, lowestPriority=True)
            self._stack.add(item)

        def execute(self ):
            # Delay the preview calls if there is some work in progress.
            # This method can be called from progress dialog's idle event.
            if isProgressVisible():
                import maya.cmds
                script = 'xgg.DescriptionEditor.previewer.execute()'
                maya.cmds.evalDeferred( script, lowestPriority=True)
                return

            import maya.mel as mel
            for item in self._stack:                
                mel.eval(item) 
            self._stack.clear()

        @property
        def tracking(self):
            return self._tracking

        @tracking.setter
        def tracking(self,val):
            self._tracking = val

        @property
        def idle(self):
            return self._idle

        @idle.setter
        def idle(self,val):
            self._idle = val

    def __init__(self,parent = None,fl = Qt.Widget ):
        QWidget.__init__(self, parent, fl)
        self.arcExport=None
        self.arcBatchExport=None

        if xgg.Maya and cmds.about(batch=True):
            print('=============================================')
            xglog.XGError( maya.stringTable[u'y_xgenm_ui_xgDescriptionEditor.kCreatingDEUIInBatch' ] )
            print(xgu.callStack())
            print('=============================================')

        # Global holder of the editor. Dont reference values through
        # this inside of other constructors since we aren't ready until
        # we finish the full setup. We do this here though to allow
        # widgets to connect.
        xgg.DescriptionEditor = self
        self.setWindowTitle(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kXgenDescriptionEditor'  ])
        self.setWindowIcon(CreateIcon("xgDEditor.png"))
        self.setGeometry(0,0,DpiScale(360),DpiScale(750))

        self.optionVars = {}
        # message level options
        self.optionVars['debug'] = 'xgenDebugMsgLevelVar'
        self.optionVars['warning'] = 'xgenWarningMsgLevelVar'
        self.optionVars['stats'] = 'xgenStatsMsgLevelVar'

        # undo support
        self._undoRequired = True 
        self._tempUndoRequired = None

        # Preview and Clear Options
        self.previewSel = False
        self.previewMode = self.PreviewMode.Description
        self.clearSel = False
        self.clearCache = False
        self.clearMode = self.PreviewMode.Description
        self.autoCreateMR = True
        xgg.PlayblastWarning = True
        self._previewer = None

        # build welcome screen and main ui
        # which one will be shown will depend on EnableUI()
        self.welcomeUI = QWidget()
        self.welcomeUI.setVisible(False)
        self.welcomeUI.setLayout(self.buildWelcomeUI())
        
        self.mainUI = QWidget()
        self.mainUI.setVisible(False)
        self.mainUI.setLayout(self.buildMainUI())
        
        layout = QVBoxLayout()
        layout.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))
        self.setLayout(layout)
        layout.addWidget(self.welcomeUI)
        layout.addWidget(self.mainUI)

        xg.registerCallback( "PostPaletteDelete", "xgenm.ui.xgDescriptionEditor.postPaletteDeleteCB" )

    def __del__(self):
        xg.deregisterCallback( "PostPaletteDelete", "xgenm.ui.xgDescriptionEditor.postPaletteDeleteCB" )
        QWidget.__del__(self)

    @property
    def previewer(self):
        if self._previewer:
            return self._previewer
        self._previewer = DescriptionEditorUI.Previewer()
        return self._previewer

    @contextmanager
    def setAttrGuard( self ):
        """ Context manager to make sure attributes are not set through the undo command """
        try:
            # save undo initial value
            if self._tempUndoRequired == None:
                self._tempUndoRequired = self._undoRequired

            # prevent setAttrCmd to be called
            self._undoRequired = False
            yield

        except Exception:
            import traceback
            print(traceback.print_exc())

        finally:
            # restore undo value
            if self._tempUndoRequired:
                self._undoRequired = self._tempUndoRequired
            self._tempUndoRequired = None
            
    @contextmanager
    def currentPaletteGuard(self):
        ''' Get the name of the current palette and restore it later '''

        # Get the current palette selection. The current selection will be
        # restored after body execution.
        palette = self.currentPalette()
        
        # Execute the body and restore
        try:
            yield
        finally:
            # Restore the previous palette selection
            index = self.palettes.findText(palette)
            self.palettes.setCurrentIndex(index if index >= 0 else 0)
            
    @contextmanager
    def currentDescriptionGuard(self):
        ''' Get the name of the current description and restore it later '''

        # Get the current description selection. The current selection will be
        # restored after body execution.
        description = self.currentDescription()

        description = xg.stripNameSpace(description)
        
        # Execute the body and restore
        try:
            yield
        finally:
            # Restore the previous description selection      
            index = self.descs.findText(description)
            self.descs.setCurrentIndex(index if index >= 0 else 0)
            
    def saveGlobals(self):
        '''Saving the per Scene flags of the UI inside a single script node'''
        if not xg.descriptions():
            return

        try:
            cmds.delete( "xgenGlobals")
        except:
            pass

        select = cmds.ls( sl=True )
        try:
            #These are created on file import (ex.: file -f -i "scenes/impSaveimpSave.ma;")
            cmds.select( "*_xgenGlobals*")
            selectXgenGlobals = cmds.ls( sl=True )
            for item in selectXgenGlobals:
                if cmds.nodeType(item, api=True) == "kScript":
                    cmds.delete( item )
        except:
            pass            
        if select == []:
            cmds.select( cl=True )
        else:
            cmds.select( select, r=True, ne=True )

        kOnDemand = 0
        kIgnoreReferenceEdits=1
        cmds.scriptNode( name="xgenGlobals", st=0, sourceType="Python", scriptType=kOnDemand, ignoreReferenceEdits=kIgnoreReferenceEdits, \
            afterScript="import maya.cmds as cmds\nif cmds.about(batch=True):\n\txgg.Playblast=False\nelse:\n\txgui.createDescriptionEditor(False).setGlobals( previewSel=%d, previewMode=%d, clearSel=%d, clearMode=%d, playblast=%d, clearCache=%d, autoCreateMR=%d )"%(self.previewSel,self.previewMode,self.clearSel,self.clearMode,xgg.Playblast, self.clearCache, self.autoCreateMR ) )


        # Update the geometry shaders before saving
        try:
            if mel.eval('exists "xgmr"'):
                cmds.xgmr( ugs=True, description="", palette="" )
        except:
            pass

    def setGlobals(self, previewSel=False, previewMode=0, clearSel=False, clearMode=0, playblast=False, clearCache=False, autoCreateMR=True ):
        '''setGlobals is a method called by the script node. Please keep the arguments with the same names and always add '''
        self.previewSel = previewSel
        self.previewMode = previewMode
        self.clearSel = clearSel
        self.clearCache = clearCache
        self.clearMode = clearMode
        xgg.Playblast = playblast
        xgg.PlayblastWarning = True
        self.autoCreateMR = autoCreateMR
        self.updatePreviewControls()
        self.updateClearControls()
        self.updateMentalrayControls()

    
    def loadGlobals(self):
        '''Set default Globals and  try to execute the xgenGlobals script. This is run on scene load and new scene.'''
        # Preview and Clear Options
        self.previewSel = False
        self.previewMode = self.PreviewMode.Description
        self.clearSel = False
        self.clearCache = False
        self.clearMode = self.PreviewMode.Description
        self.autoCreateMR = True
        xgg.PlayblastWarning = True
        xgg.Playblast = True

        try:
            cmds.scriptNode( "xgenGlobals", executeAfter=True )
        except:
            pass

    def buildMainUI(self):

        # Create the main layout with a splitter in it
        mainUILayout = QVBoxLayout()
        QLayoutItem.setAlignment(mainUILayout, Qt.AlignTop)
        mainUILayout.setSpacing(DpiScale(0))
        mainUILayout.setContentsMargins(DpiScale(3),DpiScale(3),DpiScale(3),DpiScale(3))

        # Top Menu Bar
        mainUILayout.addWidget(self.createMenuBar())

        self.splitter = QSplitter()
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setOpaqueResize(False)
        mainUILayout.addWidget(self.splitter)
       
        # middle section, top is a compound layout for showing the big preview button + 2 lines on the right
        # bottom is the tab bar.
        middleWidget = QWidget()
        middleUILayout = QVBoxLayout(middleWidget)
        QLayoutItem.setAlignment(middleUILayout, QtCore.Qt.AlignTop)
        middleUILayout.setSpacing(DpiScale(0))
        middleUILayout.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))
        self.splitter.addWidget(middleWidget)

        bottomWidget = QWidget()
        bottomUILayout = QVBoxLayout(bottomWidget)
        QLayoutItem.setAlignment(bottomUILayout, QtCore.Qt.AlignTop)
        bottomUILayout.setSpacing(DpiScale(0))
        bottomUILayout.setContentsMargins(DpiScale(3),DpiScale(3),DpiScale(3),DpiScale(3))
        self.splitter.addWidget(bottomWidget)        
        self.splitter.setCollapsible(0,False)
        self.splitter.setCollapsible(1,False)
        
        # middleH is a compound layout
        # with big preview button on the left side
        # and 2 horizontal lines on the right.
        # First line is current Palette/Description  
        # Second is the tool bar.
        middleHWidget = QWidget()
        middleHUILayout = QHBoxLayout(middleHWidget)
        QLayoutItem.setAlignment(middleHUILayout, QtCore.Qt.AlignTop)
        middleHUILayout.setSpacing(DpiScale(0))
        middleHUILayout.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))
        middleUILayout.addWidget(middleHWidget)
        middleUILayout.addSpacing(DpiScale(2))
        
        (middleRVWidget1,middleRVWidget2) = self.createEmptyFrame()
        middleRVUILayout = QVBoxLayout(middleRVWidget2)
        QLayoutItem.setAlignment(middleRVUILayout, QtCore.Qt.AlignTop)
        middleRVUILayout.setSpacing(DpiScale(2))
        middleRVUILayout.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))
        middleHUILayout.addWidget(middleRVWidget1)
        
        self.createTopBar(middleRVUILayout)
        if ( xgg.Maya ):
            self.createShelfBar(middleRVUILayout)
        
        self.createTabBar(middleUILayout)

        self.messageUI = XgMessageUI()
        self.messageUI.setMinimumHeight(DpiScale(35))
        logExpand = ExpandUI(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kMainLog'  ],False)

        logExpand.addWidget(self.messageUI)        
        bottomUILayout.addWidget(logExpand)

        self.splitter.setStretchFactor(0,100)
        self.splitter.setStretchFactor(1,0)
        self.splitter.setSizes([DpiScale(100),DpiScale(0)])

        return mainUILayout 

    def buildWelcomeUI(self):

        def addIconButtonLine( layout, icon, title):
            layout.addSpacing(DpiScale(20))
            row = QWidget()
            hbox = QHBoxLayout()
            hbox.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))
            QLayoutItem.setAlignment(hbox, QtCore.Qt.AlignRight)
            row.setLayout(hbox)
            layout.addWidget(row)

            thumbWidget = QLabel()
            pixmap = QPixmap()
            if icon!="":
                pixmap = CreateIcon(icon).pixmap(DpiScale(24),DpiScale(24))
            thumbWidget.setPixmap( pixmap )
            hbox.addWidget(thumbWidget)
            

            execButton = QPushButton(title)
            execButton.setFixedWidth(DpiScale(200))
            execButton.setAutoRepeat(False)
            hbox.addWidget(execButton)

            return execButton

        welcomeUILayout = QVBoxLayout()
        QLayoutItem.setAlignment(welcomeUILayout, QtCore.Qt.AlignTop)
        welcomeUILayout.setSpacing(DpiScale(0))
        welcomeUILayout.setContentsMargins(DpiScale(15),DpiScale(15),DpiScale(15),DpiScale(15))
   
        splashIconWidget = QLabel()
        splashIconWidget.setPixmap(CreateIcon('xgSplash_Scaled.png').pixmap(DpiScale(400),DpiScale(100)))

        frame = QFrame()
        frame.setFrameShadow(QFrame.Plain)
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFixedSize(DpiScale(400),DpiScale(100))
        frame.setLayout(QVBoxLayout())
        frame.layout().setSpacing(DpiScale(0))
        frame.layout().setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))
        frame.layout().addWidget(splashIconWidget)

        welcomeUILayout.addWidget(frame)

        welcomeUILayout.addSpacing(DpiScale(10))
        label = QLabel(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kGettingStartedWithXgen'  ] % ("<b>","</b>"))
        #label.setStyleSheet('font-size: 15pt;')
        welcomeUILayout.addWidget(label)

        welcomeUILayout.addSpacing(DpiScale(10))
        label = QLabel(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kUseXgenToCreateArbitraryPrimitivesOnASurface'  ])
        #label.setStyleSheet('font-size: 11pt;')
        welcomeUILayout.addWidget(label)
        welcomeUILayout.addSpacing(DpiScale(5))
        label = QLabel(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kHairFurFeathersScalesRocksAndMore'  ])
        #label.setStyleSheet('font-size: 11pt;')
        welcomeUILayout.addWidget(label)

        welcomeUILayout.addSpacing(DpiScale(15))
        label = QLabel(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.ktoStart'  ] % ("<b>","</b>"))
        #label.setStyleSheet('font-size: 11pt;')
        welcomeUILayout.addWidget(label)

        welcomeUILayout.addSpacing(DpiScale(5))
        label = QLabel(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kSelectTheGeometryOrFacesToCreatePrimitiveOn'  ])
        #label.setStyleSheet('font-size: 11pt;')
        label.setWordWrap( True ) 
        welcomeUILayout.addWidget(label)

        welcomeUILayout.addSpacing(DpiScale(5))
        label = QLabel(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kCreateANewXgenDescription'  ])
        #label.setStyleSheet('font-size: 11pt;')
        label.setWordWrap( True ) 
        welcomeUILayout.addWidget(label)
        self.connect(addIconButtonLine(welcomeUILayout, "xgCreateDescription.png", maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kCreateNewDescription'  ] ), QtCore.SIGNAL("clicked()"), self.createDescription)
        self.connect(addIconButtonLine(welcomeUILayout, "xgImportDescription.png", maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kImportDescription'  ] ), QtCore.SIGNAL("clicked()"), DescriptionEditorUI.importFileCB )
        self.connect(addIconButtonLine(welcomeUILayout, "xgLibrary.png", maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kWelcomeUIImportPreset'  ] ), QtCore.SIGNAL("clicked()"), self.openLibraryWindow )

        # palettes
        self.palettes = _ComboBoxUI()
        self.connect(self.palettes, 
                    QtCore.SIGNAL("activated(const QString&)"), 
                    lambda x: self.refresh('Palette') )

        self.palettes.setMinimumWidth(DpiScale(50))

        return welcomeUILayout

    def detachMe(self):
        ''' Remove the widget from its parent's children list '''
        self.setParent(None)

    @staticmethod
    def importFileCB():
        importFile('description')

    def keyPressEvent(self,event):
        QWidget.keyPressEvent(self,event)
        # This prevents the focus from going back to the Maya panel under the description editor
        # The behavior is the same as the attribute editor.
        focusWidget = QApplication.focusWidget()
        if self.isAncestorOf(focusWidget):
            if focusWidget.inherits(r'QLineEdit') or focusWidget.inherits(r'QTextEdit') or focusWidget.inherits(r'QPlainTextEdit'):
                event.accept()

    def createMenuBar(self):
        menubar = QMenuBar(self)
        menubar.setNativeMenuBar(False)  #For the mac standalone xgen editor
        
        self.fileMenu = menubar.addMenu(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kFileMenuName'  ])
        if ( xgg.Maya ):
            self.fileMenu.aboutToShow.connect( self.onFileMenuShow )
            self.fileMenu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kImportMenuBar'  ],importFile)
            self.fileMenu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kImportPresetMenuBar'  ],importPreset)
            self.importGrooming = self.fileMenu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kImportGroomingMenuBar'  ],igImportFile)
            self.fileMenu.addSeparator()
            self.fileMenu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kExportMenuBar'  ],exportFile)
            self.fileMenu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kExportPresetMenuBar'  ],exportPreset)        
            self.exportGrooming = self.fileMenu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kExportGroomingMenuBar'  ],igExportFile)
            self.fileMenu.addSeparator()
        self.fileMenu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kExportPatchesForBatchRender'  ], self.exportPatches)
        self.fileMenu.addSeparator()    
        if ( xgg.Maya ):
            self.fileMenu.addAction(maya.stringTable[u'y_xgenm_ui_xgDescriptionEditor.kExportSelectionAsArchives' ], lambda: mel.eval('XgExportArchive();') )
            self.fileMenu.addAction(maya.stringTable[u'y_xgenm_ui_xgDescriptionEditor.kBatchConvertScenesToArchives'], lambda: mel.eval('XgBatchExportArchive();') )
        else:
            self.fileMenu.addAction(maya.stringTable[u'y_xgenm_ui_xgDescriptionEditor.kExportSelectionAsArchives2'], self.exportArchives)
            self.fileMenu.addAction(maya.stringTable[u'y_xgenm_ui_xgDescriptionEditor.kBatchConvertScenesToArchives2'], self.batchExportArchives)
            
        self.palMenu = menubar.addMenu(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kCollectionMenuName'  ])
        self.palMenu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kEditFilePathPalMenu'  ], 
                   self.editPath)
        if ( xgg.Maya ):
            self.palMenu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kFixPatchNamesPalMenu'  ], 
                               lambda: xg.fixPatchNames(self.currentPalette()))
        self.palMenu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kDeleteCollectionPalMenu'  ], 
                   self.deletePalette)

        self.descMenu = menubar.addMenu(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kDescriptionFileMenu'  ])
        self.descMenu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kCreateDescriptionDescMenu'  ], self.createDescription)
        if ( xgg.Maya ):
            self.descMenu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kDuplicateDescriptionDescMenu'  ], copyDescription)
            self.descMenu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kMoveDescriptionToCollectionDescMenu'  ], moveDescription)
            self.descMenu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kSelectDescriptionDescMenu'  ], 
                                    lambda: cmds.select( self.currentDescription(), replace=True )  )
            self.descMenu.addSeparator()
            self.bindMenu1 = QMenu(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kBindPatches'  ])
            self.addBindActions( self.bindMenu1, None ) 
            self.descMenu.addMenu(self.bindMenu1)
            self.descMenu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kHideShowPatchesBasedOnGeometryVisibilityDescMenu'  ],
                 lambda: mel.eval("xgmSyncPatchVisibility"))

        self.descMenu.addSeparator()
        self.descMenu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kSetStrayPercentageDescMenu'  ],strayPercentage)
        self.descMenu.addSeparator()
        self.descMenu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kDeleteDescriptionDescMenu'  ],self.deleteDescription)

        if ( xgg.Maya ):
            self.guidesMenu = menubar.addMenu(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kGuidesFileMenu'  ])

            self.guidesMenu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kBakeGuideVerticesGuidesMenu'  ], 
                lambda: mel.eval("xgmBakeGuideVertices"))
            self.displayGuideRange = self.guidesMenu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kDisplayGuideRangeOfInfluenceGuidesMenu'  ], 
                 self.toggleVisualizer)
            self.displayGuideRange.setCheckable(True)

            self.mrMenu = QMenu(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kMentalrayFileMenu'  ])
            self.mrMenu.setVisible( False )
            self.mrMenu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kSetupMentalrayGeometryShadersMentalrayMenu'  ], 
                 lambda: mel.eval("xgmr -setupGeometryShader -description \"%s\" -palette \"%s\"" % (self.currentDescription(), self.currentPalette() )))
            self.mrAutoGeo = self.mrMenu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kAutoSetupMentalrayGeometryShadersMentalrayMenu'  ], 
                 self.onAutoCreateMR )
            self.mrAutoGeo.setCheckable( True )
            self.updateMentalrayControls()
            self.mrMenu.addSeparator()
            self.mrMenu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kApplyHairShaderMentalrayMenu'  ], 
                 lambda: mel.eval("xgmr -applyShader \"hair\" -description \"%s\" -palette \"%s\"" % (self.currentDescription(), self.currentPalette )))

        self.logMenu = menubar.addMenu(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kLogFileMenu'  ])
        self.logMenu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kClearLogMenu'  ],
                               lambda: self.messageUI.clearLog())

        self.logMenu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kSaveLog'  ], lambda: self.messageUI.saveLog())
        val = self.getMessageLevel("warning")
        self.logWarnMenu = QMenu(maya.stringTable[u'y_xgenm_ui_xgDescriptionEditor.kWarningLevelLogWarnMenu' ] % str(val))
        self.logWarnMenu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.k0LogWarnMenu'  ],
                                   lambda: self.setMessageLevel("warning",0))
        self.logWarnMenu.addAction("1",
                                   lambda: self.setMessageLevel("warning",1))
        self.logWarnMenu.addAction("2",
                                   lambda: self.setMessageLevel("warning",2))
        self.logWarnMenu.addAction("3",
                                   lambda: self.setMessageLevel("warning",3))
        self.logWarnMenu.addAction("4",
                                   lambda: self.setMessageLevel("warning",4))
        self.logWarnMenu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.k5LogWarnMenu'  ],
                                   lambda: self.setMessageLevel("warning",5))
        self.logMenu.addMenu(self.logWarnMenu)
        val = self.getMessageLevel("stats")
        self.logStatsMenu = QMenu(maya.stringTable[u'y_xgenm_ui_xgDescriptionEditor.kStatisticsLevelLogStatsMenu' ] % str(val))
        self.logStatsMenu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.k0LogStatsMenu'  ],
                                   lambda: self.setMessageLevel("stats",0))
        self.logStatsMenu.addAction("1",
                                   lambda: self.setMessageLevel("stats",1))
        self.logStatsMenu.addAction("2",
                                   lambda: self.setMessageLevel("stats",2))
        self.logStatsMenu.addAction("3",
                                   lambda: self.setMessageLevel("stats",3))
        self.logStatsMenu.addAction("4",
                                   lambda: self.setMessageLevel("stats",4))
        self.logStatsMenu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.k5LogStatsMenu'  ],
                                   lambda: self.setMessageLevel("stats",5))
        self.logMenu.addMenu(self.logStatsMenu)
        val = self.getMessageLevel("debug")
        self.logDebugMenu = QMenu(maya.stringTable[u'y_xgenm_ui_xgDescriptionEditor.kDebugLevelLogDebugMenu'] % str(val))
        self.logDebugMenu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.k0LogDebugMenu'  ],
                                   lambda: self.setMessageLevel("debug",0))
        self.logDebugMenu.addAction("1",
                                   lambda: self.setMessageLevel("debug",1))
        self.logDebugMenu.addAction("2",
                                   lambda: self.setMessageLevel("debug",2))
        self.logDebugMenu.addAction("3",
                                   lambda: self.setMessageLevel("debug",3))
        self.logDebugMenu.addAction("4",
                                   lambda: self.setMessageLevel("debug",4))
        self.logDebugMenu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.k5LogDebugMenu'  ],
                                   lambda: self.setMessageLevel("debug",5))
        self.logMenu.addMenu(self.logDebugMenu)
        
        self.helpMenu = menubar.addMenu(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kHelpFileMenu'  ])
        self.helpMenu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kHelpOnXgenHelpMenu'  ], self._showHelp)
        
        return menubar

    def onFileMenuShow( self ):
        igDesc = xg.igDescription( self.currentDescription() )
        self.importGrooming.setEnabled( len(igDesc) )
        self.exportGrooming.setEnabled( len(igDesc) )

    def createDoubleFrame(self):
        frame1 = QFrame()
        frame1.setFrameShadow(QFrame.Sunken)
        frame1.setFrameShape(QFrame.Panel) 
        layout = QHBoxLayout()
        layout.setSpacing(DpiScale(0))
        layout.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))
        frame2 = QFrame()
        frame2.setFrameShadow(QFrame.Raised)
        frame2.setFrameShape(QFrame.Panel) 
        layout.addWidget( frame2 )
        frame1.setLayout( layout )
        return (frame1,frame2)

    def createSunkenFrame(self):
        frame1 = QFrame()
        frame1.setFrameShadow(QFrame.Sunken)
        frame1.setFrameShape(QFrame.Panel) 
        return (frame1,frame1)

    def createEmptyFrame(self):
        frame1 = QWidget()
        return (frame1,frame1)

    def createTopBar(self,theLayout):
        # Create the row for selecting the current palette/description
        (frame1,frame2) = self.createEmptyFrame()
        currentHbox = QHBoxLayout()
        currentHbox.setSpacing(DpiScale(4))
        currentHbox.setContentsMargins(DpiScale(4),DpiScale(4),DpiScale(4),DpiScale(4))

        # palettes
        label = QLabel( maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kCollection'  ] )
        label.setAlignment( QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter )
        currentHbox.addWidget(label)
        self.palettes = _ComboBoxUI()
        self.connect(self.palettes, 
                    QtCore.SIGNAL("activated(const QString&)"), 
                    self.onSelectPalette )
        self.palettes.setMinimumWidth(DpiScale(50))
        currentHbox.addWidget(self.palettes)
        currentHbox.setStretchFactor(self.palettes,50)

        # descriptions
        label = QLabel( maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kDescription'  ] )
        label.setAlignment( QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter )
        currentHbox.addWidget(label)
        self.descs = _ComboBoxUI()
        self.connect(self.descs, 
                    QtCore.SIGNAL("activated(const QString&)"), 
                    self.onSelectDescription )

        self.descs.setMinimumWidth(DpiScale(50))
        currentHbox.addWidget(self.descs)
        currentHbox.setStretchFactor(self.descs,50)

        # Assign the layout and pack widgets
        frame2.setLayout(currentHbox)
        theLayout.addWidget(frame1)

    def onSelectDescription( self, descr ):
        oldV = xgg.PlayblastWarning
        self.refresh('Description')
        self.setPreviewWarning( oldV )
       
        # tell others about the new selected description
        self.xgCurrentDescriptionChanged.emit( self.currentPalette(), self.currentDescription() )
        
    def onSelectPalette( self, palette ):
        oldV = xgg.PlayblastWarning
        self.refresh('Palette')
        self.setPreviewWarning( oldV )

        # tell others about the new selected palette
        self.xgCurrentDescriptionChanged.emit( palette, self.currentDescription() )

    def buildMenus(self):
        self.gmenu.clear()
        self.lmenu.clear()
        self.umenu.clear()
        self.allExprMenus = []
        self.buildMenu(self.gmenu,xg.globalRepo()+"descriptions/")
        self.buildMenu(self.lmenu,xg.localRepo()+"descriptions/")
        self.buildMenu(self.umenu,xg.userRepo()+"descriptions/")

    def buildMenu(self,topmenu,startDir):
        # first verify that the directory exists
        try:
            buf = os.stat(startDir)
        except:
            action = topmenu.addAction("<None>")
            action.setDisabled(True)
            return None
        subdirlist = [startDir]
        depths = [0]
        menus = []
        while subdirlist:
            dir = subdirlist.pop()
            depth = depths.pop()
            try:
                files = os.listdir(dir)
                files.sort()
                menu = None
                if depth:
                    menu = QMenu(os.path.basename(dir))
                    menus[depth-1].addMenu(menu)
                else:
                    menu = topmenu
                self.allExprMenus.append(menu)
                if len(menus)>depth:
                    menus[depth] = menu
                else:
                    menus.append(menu)
                for item in files:
                    long_ = os.path.join(dir, item)
                    if os.path.isfile(long_):
                        parts = os.path.splitext(item)
                        if parts[1] == ".xdsc":
                            menu.addAction(parts[0],
                                           lambda x=long_: self.repoMan(x))
                    else:
                        subdirlist.insert(0, long_)
                        depths.insert(0, depth+1)
            except:
                pass
        if topmenu.isEmpty():
            action = topmenu.addAction("<None>")
            action.setDisabled(True)

    def createPalExprs(self,theLayout):
        # UI for adding/deleting expressions
        label = QLabel(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kName'  ])
        label.setFixedWidth(int(labelWidth()))
        label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        label.setIndent(DpiScale(10))
        label.setToolTip(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kNameAnn'  ])
        self.pexprName = QLineEdit()
        self.pexprName.setFixedWidth(DpiScale(100))
        self.pexprName.setToolTip(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kExprNameAnn'  ])
        rx = QRegExp("[A-Za-z]+[A-Za-z0-9_]*")
        self.pexprName.setValidator(QRegExpValidator(rx,self))
        self.pexprType = _ComboBoxUI()
        self.pexprType.addItem('float')
        self.pexprType.addItem('color')
        self.pexprType.addItem('vector')
        self.pexprType.addItem('point')
        self.pexprType.addItem('normal')
        self.pexprType.setFixedWidth(DpiScale(62))
        self.pexprType.setToolTip(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kExprTypeAnn'  ])
        self.pexprAddButton = QToolButton()
        self.pexprAddButton.setIcon(CreateIcon("xgAddExpr.png"))
        self.pexprAddButton.setFixedSize(DpiScale(24),DpiScale(24))
        self.pexprAddButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kCollectionExprAnn'  ])
        self.connect(self.pexprAddButton, QtCore.SIGNAL("clicked()"), self.addPalExpr)

        # expression names UI
        palExprNameW = QWidget()
        layout = QHBoxLayout()
        QLayoutItem.setAlignment(layout, QtCore.Qt.AlignLeft)        
        layout.addSpacing(DpiScale(0))
        layout.addWidget(label)
        layout.addWidget(self.pexprName)
        layout.addSpacing(DpiScale(10))
        layout.addWidget(self.pexprType)
        layout.addSpacing(DpiScale(15))
        layout.addWidget(self.pexprAddButton)
        layout.setSpacing(DpiScale(3))
        layout.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
        palExprNameW.setLayout(layout)

        # expressions layout
        self.palTabW = QWidget()
        self.palTabLayout = QVBoxLayout()
        self.palTabLayout.setSpacing(DpiScale(0))
        self.palTabLayout.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))
        self.palTabW.setLayout(self.palTabLayout)

        # Empty layout for palette expressions
        palExprW = QWidget()
        self.palExprLayout = QVBoxLayout()
        QLayoutItem.setAlignment(self.palExprLayout, QtCore.Qt.AlignTop)
        self.palExprLayout.setSpacing(DpiScale(0))
        self.palExprLayout.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))
        palExprW.setLayout(self.palExprLayout)

        self.palTabLayout.layout().addSpacing(DpiScale(5))
        self.palTabLayout.addWidget(palExprNameW)
        self.palTabLayout.addItem(QSpacerItem(DpiScale(100),DpiScale(10)))
        self.palTabLayout.addWidget(palExprW)
        theLayout.addWidget(self.palTabW)

        self.palExprExpandState = {}
    
    def addAttrExprsLayout(self, attr, expand=False):
        exprUI = PaletteExpressionUI(attr)
        exprUI.refresh()

        pal = self.currentPalette()
        key = pal + " " + attr
        self.palExprExpandState[key] = expand

        frameLayout = PaletteExpressionExpandUI(pal, makeLabel(attr), expand)
        frameLayout.addWidget(exprUI)
        self.palExprLayout.addWidget(frameLayout)

    def refreshPalExprs(self):
        while True:
            item = self.palExprLayout.takeAt(0)
            if not item:
                break
            else:
                itemWidget = item.widget()
                (type, attrName) = itemWidget.header.text.split()
                key = itemWidget.palette + " " + "custom_" + type + "_" + attrName
                self.palExprExpandState[key] = itemWidget.expanded
                itemWidget.cleanScriptJob()
                self.palExprLayout.removeWidget(itemWidget)
                destroyWidget(itemWidget)
        de = xgg.DescriptionEditor
        params = xg.customAttrs(de.currentPalette())
        for param in params:
            key = de.currentPalette() + " " + param
            expanded = False
            if key in self.palExprExpandState:
                expanded = self.palExprExpandState[key]
            self.addAttrExprsLayout(param, expanded)

    def addPalExpr(self):
        if self.pexprName.text()=="":
            return
        attr = "custom_"+str(self.pexprType.currentText())+"_"+str(self.pexprName.text())
        de = xgg.DescriptionEditor
        xg.addCustomAttr(attr,de.currentPalette())
        self.pexprName.setText("")
        self.addAttrExprsLayout(attr, True)
            
    def onRefreshPreviewAuto(self):
        self.setPlayblast( not( xgg.Playblast ) )
        self.updatePreviewControls()

    def onRefreshPreviewMode(self,act):
        self.previewMode = act.data()
        self.updatePreviewControls()

    def onRefreshPreviewSel(self):
        self.previewSel = not( self.previewSel )
        self.updatePreviewControls()

    def setPreviewWarning( self, v ):
        xgg.PlayblastWarning=v
        self.updatePreviewIcon()

    def updatePreviewIcon(self):
        if xgg.Maya:
            icon = self.iconPreview
            if xgg.Playblast:
                icon = self.iconPreviewRefresh
            elif xgg.PlayblastWarning:
                icon = self.iconPreviewWarning
            self.previewButton.setIcon(icon)

    def updatePreviewControls(self):
        self.previewAutoAction.setChecked( xgg.Playblast )
        self.previewGroup.actions()[self.previewMode].setChecked( True )
        self.previewSelAction.setChecked( self.previewSel )
        
        self.updatePreviewIcon()

    def onClearPreviewMode(self,act):
        self.clearMode = act.data()
        self.updateClearControls()

    def onClearPreviewSel(self):
        self.clearSel = not( self.clearSel )
        self.updateClearControls()

    def onClearPreviewCache(self):
        self.clearCache = not( self.clearCache )
        self.updateClearControls()

    def updateClearControls(self):
        self.clearGroup.actions()[self.clearMode].setChecked( True )
        self.clearSelAction.setChecked( self.clearSel )
        self.clearCacheAction.setChecked( self.clearCache )
    
    def onAutoCreateMR(self):
        self.autoCreateMR = not( self.autoCreateMR )
        self.updateMentalrayControls()

    def updateMentalrayControls(self):
        self.mrAutoGeo.setChecked( self.autoCreateMR )

    def getPreviewText(self):
        return self.getSelModeText( self.previewSel, self.previewMode )

    def getClearText(self):
        return self.getSelModeText( self.clearSel, self.clearMode, self.clearCache )

    def getSelModeText( self, sel, mode, cache=False ):
        t =""
        if sel:
            t +=  maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kSelected'  ] + ": "
        if mode==self.PreviewMode.All:
            t+= maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kAll'  ]
        elif mode==self.PreviewMode.Collection:
            t+= maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kCurrentCollection'  ]
        elif mode==self.PreviewMode.Description:
            t+= maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kCurrentDescription'  ]
        if cache:
            t+= maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kClearArchiveCache'  ]

        return t

    def cullSelectedPrimitives(self):
        mel.eval('xgmSelectedPrims -c "'+self.currentDescription()+'"')

    def appendFacesAction(self):
        self.modifyBinding("Append")
        
    def replaceFacesAction(self):
        self.modifyBinding("Replace")
        
    def removeFacesAction(self):
        self.modifyBinding("Remove")
        
    def mapFacesAction(self):
        self.modifyBinding("Map")
        
    def addBindActions( self, menu, bar ):
        button = None
        if bar:
            button = bar.addButton("xgBindFaces.png",
                                   maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kModifyCurrentDescriptionsFaceBindings'  ],
                                   self.appendFacesAction )
            button.setPopupMode(QToolButton.MenuButtonPopup)
            button.setMinimumSize(ToolButtonSizeHint(button, ShelfToolButtonSize, withMenu=True))
        else:
            menu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kAddFacesBindMenu'  ], self.appendFacesAction )

        menu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kReplaceFacesBindMenu'  ], self.replaceFacesAction )
        menu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kRemoveFacesBindMenu'  ], self.removeFacesAction )
        menu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kMapFacesBindMenu'  ], self.mapFacesAction )
        menu.addSeparator()
        menu.addAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kSelectFacesBindMenu'  ], self.selectBinding )

        if button:
            button.myMenu = menu # Keep a reference to the QMenu
            button.setMenu(menu)

    def update(self):
        """ refresh the editor and tell others about the update """
        self.refresh("Full")
        self.xgCurrentDescriptionChanged.emit( self.currentPalette(), self.currentDescription() )

    def createShelfBar(self,theLayout):
        
        #currentRow = QWidget()
        (frame1,frame2) = self.createSunkenFrame()
        currentHbox = QHBoxLayout()
        currentHbox.setSpacing(DpiScale(0))
        currentHbox.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))
        
        # Create the toolbar of shelf buttons
        bar = ToolBarUI(QSize(32,32),2)
        
        self.iconPreview = CreateIcon("xgPreview.png")
        self.iconPreviewRefresh = CreateIcon("xgPreviewRefresh.png")
        self.iconPreviewWarning = CreateIcon("xgPreviewWarning.png")

        # Add Preview button
        button = bar.addButton( "xgPreview.png", maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kPreview'  ], self.previewCIP )
        button.setAutoRaise(True)
        button.setPopupMode(QToolButton.MenuButtonPopup)
        button.setToolTip( maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kUpdateTheXGenPreview'  ] )
        button.setMinimumSize(ToolButtonSizeHint(button, ShelfToolButtonSize, withMenu=True))

        menu = QMenu()

        self.previewAutoAction = menu.addAction( maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kUpdatePreviewAutomatically'  ], self.onRefreshPreviewAuto )
        menu.addSeparator()
        self.previewGroup = QActionGroup(menu)
        act = QAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kPreviewCurrentDescriptionOnly'  ], self.previewGroup )
        act.setData(self.PreviewMode.Description)
        act.setCheckable(True)
        act = QAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kPreviewAllDescriptionsinCollection'  ], self.previewGroup )
        act.setData(self.PreviewMode.Collection)
        act.setCheckable(True)
        act = QAction(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kPreviewAllCollections'  ], self.previewGroup )
        act.setData(self.PreviewMode.All)
        act.setCheckable(True)
        self.previewGroup.triggered.connect( self.onRefreshPreviewMode )
        menu.addActions( self.previewGroup.actions() )
        menu.addSeparator()
        self.previewSelAction = menu.addAction( maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kPreviewSelectedObjectsOnly'  ], self.onRefreshPreviewSel )

        self.previewAutoAction.setCheckable(True)
        self.previewSelAction.setCheckable(True)

        button.myMenu = menu # Keep a reference to the QMenu
        button.setMenu(menu)
        self.previewButton = button
        self.previewMenu = menu
        self.updatePreviewControls()
        

        # Add Clear button
        button = bar.addButton( "xgPreviewClear.png", maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kClearPreview'  ], self.clearPreview )
        button.setAutoRaise(True)
        button.setPopupMode(QToolButton.MenuButtonPopup)
        button.setToolTip( maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kClearTheXGenPreview'  ] )
        button.setMinimumSize(ToolButtonSizeHint(button, ShelfToolButtonSize, withMenu=True))

        menu = QMenu()
        self.clearGroup = QActionGroup(menu)
        act = QAction( maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kClearCurrentDescriptionOnly'  ], self.clearGroup )
        act.setData(self.PreviewMode.Description)
        act.setCheckable(True)
        act = QAction( maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kClearAllDescriptionsInCollection'  ], self.clearGroup )
        act.setData(self.PreviewMode.Collection)
        act.setCheckable(True)
        act = QAction( maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kClearAllCollections'  ], self.clearGroup )
        act.setData(self.PreviewMode.All)
        act.setCheckable(True)
        self.clearGroup.triggered.connect( self.onClearPreviewMode )
        menu.addActions( self.clearGroup.actions() )
        menu.addSeparator()
        self.clearSelAction = menu.addAction( maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kClearSelectedObjectsOnly'  ], self.onClearPreviewSel )        
        self.clearSelAction.setCheckable(True)
        self.clearCacheAction = menu.addAction( maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kClearCachedArchives'  ], self.onClearPreviewCache )        
        self.clearCacheAction.setCheckable(True)

        button.myMenu = menu # Keep a reference to the QMenu
        button.setMenu(menu)
        self.clearButton = button
        self.clearMenu = menu
        self.updateClearControls()

        # Create description
        button = bar.addButton("xgCreateDescription.png",
                               maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kCreateANewDescription'  ],
                               self.createDescription )
        button.setMinimumSize(ToolButtonSizeHint(button, ShelfToolButtonSize))

        # Bind faces
        self.bindMenu = QMenu()
        self.addBindActions( self.bindMenu, bar ) 

        # Add/move guide
        button = bar.addButton("xgGuideContext.png",
                               maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kAddOrMoveGuidesForTheCurrentDescription'  ],
                               lambda: mel.eval("XgGuideTool"))
        button.setMinimumSize(ToolButtonSizeHint(button, ShelfToolButtonSize))

        # Toggle guide visibility
        button = bar.addButton("xgToggleGuide.png",
                               maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kToggleVisibilityOfCurrentDescriptionsGuides'  ],
                               lambda: xg.toggleGuideDisplay(self.currentDescription()))
        button.setMinimumSize(ToolButtonSizeHint(button, ShelfToolButtonSize))

        # Toggle guide reference
        button = bar.addButton("xgToggleGuideReference.png",
                               maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kToggleAbilityToSelectCurrentDescriptionsGuides'  ],
                               lambda: xg.toggleGuideReference(self.currentDescription()))
        button.setMinimumSize(ToolButtonSizeHint(button, ShelfToolButtonSize))

        # Flip guides across model
        button = bar.addButton("xgFlipGuides.png",
                               maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kFlipSelectedGuidesAcrossXAxis'  ],
                               lambda: mel.eval("xgmFlipGuides(\"" + self.currentDescription() + "\")"))
        button.setMinimumSize(ToolButtonSizeHint(button, ShelfToolButtonSize))

        # Sync patch to geometry visibility
        #bar.addButton("xgSyncPatchVisibility.png",
        #              _L10N( kMatchXgenPatchVisibilityToGeometryVisibility, "Match XGen patch visibility to geometry visibility." ),
        #              lambda: mel.eval("xgmSyncPatchVisibility"))

        # Toggle selection of xgen and geometry
        button = bar.addButton("xgSelectionToggle.png",
                               maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kToggleBetweenXgenPatchesAndGeometry'  ],
                               lambda: xg.selectionToggle(self.currentDescription()))
        button.setMinimumSize(ToolButtonSizeHint(button, ShelfToolButtonSize))

        # Isolate select of primitives
        button = bar.addButton("xgPrimSelection.png",
                               maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kCreatePrimitiveSelectionBox'  ],
                               self.primSelectionContext )
        button.setMinimumSize(ToolButtonSizeHint(button, ShelfToolButtonSize))

        # Cull primitives
        button = bar.addButton("xgCullPrimContextSelect.png",
                               maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kCullPrimitivesWithinSelectionBox'  ],
                               self.cullSelectedPrimitives )
        button.setMinimumSize(ToolButtonSizeHint(button, ShelfToolButtonSize))

        # Add the toolbar to main layout
        currentHbox.addWidget(bar)
        currentHbox.addStretch()
        
        frame2.setLayout(currentHbox)
        theLayout.addWidget(frame1)
        
    def createTabBar(self,theLayout):
        """
        Create the tab bar.
        This includes importing the custom UI modules.
        """

        # Create the symbol table for the UI.
        # We take:
        # - all the UI classes from the global namespace
        # - all the UI classes from globalRepo
        # - all the UI classes from localRepo
        # - all the UI classes from userRepo.
        # Each stage can override the previous stages, so the user can override
        # everything.
        self.uiclasses = dict()
        xgenmodules = set(xgapi.availableModules())
        for name in globals():
            cls = globals()[name]
            if _isUI(name, cls, xgenmodules):
                self.uiclasses[name] = cls
        for (name, cls) in list(_importUI(xgapi.globalRepo()).items()):
            self.uiclasses[name] = cls
        for (name, cls) in list(_importUI(xgapi.localRepo()).items()):
            self.uiclasses[name] = cls
        for (name, cls) in list(_importUI(xgapi.userRepo()).items()):
            self.uiclasses[name] = cls

        
        def addTab(tabset, typename, clsname, BlankWidget):
            # It's critical we get the right number of widgets, so if we fail,
            # print an error and put in a blank widget.  Two ways of 
            # failing: either no UI defined, or the UI has an error.
            tabclassname = typename + clsname + 'TabUI'
            if tabclassname not in self.uiclasses:
                print(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kNoUiDefinedFor'  ] % (typename, clsname))
                tabset.addWidget(BlankWidget(typename))
                return
            try:
                TabClass = self.uiclasses[tabclassname]
                widget = TabClass()
                tabset.addWidget(widget)
            except Exception as e:
                print(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kErrorBuildingUiFor'  ] % (typename, clsname))
                traceback.print_exc()
                tabset.addWidget(BlankWidget(typename))

        # Create the tabs
        self.tabs = QTabWidget()
        self.tabs.setMovable( True )
        
        tabsOpt = QStyleOptionTabWidgetFrame()
        tabsOpt.lineWidth = 0
        self.tabs.initStyleOption(tabsOpt)

        # Grooming tab is only available with Maya
        self.brushTab = None
        if xgg.Maya:
            self.brushTab = BrushTabUI(self)
        
        # Primitive tab
        self.primitiveTab = StackUI(margin=0)
        self.primitiveTab.setParent(self.tabs)
        self.primitiveTab.setVisible(False)
        for type in xgg.PrimitiveTypes():
            addTab(self.primitiveTab, type, "Primitive", PrimitiveTabBlankUI)
        # FX Module tab
        self.fxStackTab = FXStackTabUI()
        # Generator tab
        self.generatorTab = StackUI()
        for type in xgg.GeneratorTypes():
            addTab(self.generatorTab, type, "Generator", GeneratorTabBlankUI)
        # Renderer tab
        self.rendererTab = StackUI()
        for type in xgg.RendererTypes():
            addTab(self.rendererTab, type, "Renderer", RendererTabBlankUI)
        # LOD tab
        self.lodTab = LodTabUI()

        # Previewer tab
        self.previewerTab = StackUI(margin=0)
        for type in xgg.PreviewerTypes:
            widget = eval(type+'PreviewerTabUI()')
            self.previewerTab.addWidget(widget)

        # tool manager tab
        self.utilitiesTab = UtilitiesTabUI()

        # palette expressions tab
        self.palExprsTab = StackUI()
        self.createPalExprs(self.palExprsTab)

        # Add the tabs, We reorder them to be like the user workflow
        self.tabs.addTab(createScrollArea(self.generatorTab) ,maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kPrimitives'  ])
        self.tabs.addTab(createScrollArea(self.createPreviewAndRenderTab()),maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kPreviewRender'  ])
        self.tabs.addTab(createScrollArea(self.fxStackTab),maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kModifiers'  ])
        if xgg.Maya:
            self.tabs.addTab(createScrollArea(self.brushTab),maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kGrooming'  ])
        self.tabs.addTab(createScrollArea(self.utilitiesTab),maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kUtilities'  ])
        self.tabs.addTab(createScrollArea(self.palExprsTab),maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kExpressions'  ])
        
        # Create the tabsets. Only one of the QTabWidget is visible at a time.
        self.tabsets = StackUI()
        self.tabsets.addWidget(self.tabs)
        self.tabsets.setCurrent(0)

        theLayout.addWidget(self.tabsets)

    def activateTab( self, whichOne ):
        """ 
            Makes a tab the current widget given a name.
            note: As tab widgets are now localized, you can't just pass the Ascii name. 
            Instead you must use the localize string table to refer the tab you want to activate.
        """
        count = self.tabs.count()
        for i in range(count):
            text = self.tabs.tabText(i)
            if text == whichOne:
                self.tabs.setCurrentIndex(i)
                return

    def createPreviewAndRenderTab(self):
        newTab = QWidget()
        layout = QVBoxLayout()
        QLayoutItem.setAlignment(layout, QtCore.Qt.AlignTop)
        layout.setSpacing(DpiScale(0))
        layout.setContentsMargins(DpiScale(3),DpiScale(3),DpiScale(3),DpiScale(3))
        newTab.setLayout(layout)
        
        expand = ExpandUI(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kPreviewSettings'  ])
        expand.addWidget(self.previewerTab)
        layout.addWidget(expand)

        expand = ExpandUI(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kRenderSettings'  ])
        expand.addWidget(self.rendererTab)
        layout.addWidget(expand)

        expand = ExpandUI(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kLODSettings'  ])
        expand.addWidget(self.lodTab)
        layout.addWidget(expand)
        
        return newTab

    def setPlayblast(self, v):
        xgg.Playblast=v
        if ( xgg.Maya and ((xgg.Playblast and not cmds.objExists('xgmRefreshPreview')) or (not xgg.Playblast and not cmds.objExists('xgmPreviewWarning'))) ):
            # this will avoid logging xgmAddExpressions on the undo stack when it's not necessary
            mel.eval("xgmAddExpressions")

    def createDescription(self):
        if ( xgg.Maya ):
             mel.eval('XgCreateDescription();')
        else:
            createDescription()

    def openLibraryWindow(self):
        if ( xgg.Maya ):
             mel.eval("XGenLibraryWindow")

    def playblast(self):
        if xgg.Playblast:
            if (QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier) :
                pass # Holding shift. Ignore preview request.
            else:
                self.preview(False,False)
        else:
            self.setPreviewWarning(True)
        
    def previewCIP(self):
        if xgg.maya:
            mel.eval("XgPreview")
        else:
            self.preview()

    def clearPreview(self):
        self.preview(True)

    def preview(self,clean=False,progress=True,idle=True):
        if not xgg.Maya:
            return

        with self.setAttrGuard():
            # move focus to parent to make sure that any outstanding widget values are set
            # before refreshing.
            self.setFocus()
        
        text = ""
        sel = False
        mode = 0
        cache=False

        cmd = 'xgmPreview '
        if clean:
            cmd += '-clean '
            text = self.getClearText()
            sel = self.clearSel
            mode = self.clearMode
            cache = self.clearCache
            self.setPreviewWarning(True)
        else:
            self.setPreviewWarning(False)
            text = self.getPreviewText()
            sel = self.previewSel
            mode = self.previewMode
            if progress:
                setProgressInfo(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kPreviewProgressBar'  ] % text)
                cmd += '-pb '

        if sel:
            cmd += '-s '
        if cache:
            cmd += '-cache '
        cmd += '{'
        first = True
        if mode==self.PreviewMode.All:
            # get all of the descriptions in scene to preview
            # or add as option to xgmPreview
            palettes = uiPalettes()
            for pal in palettes:
                descs = xg.descriptions(pal)
                for desc in descs:
                    if not first:
                        cmd += ','
                    cmd += '"'+desc+'"'
                    first = False
        elif mode==self.PreviewMode.Collection:
            # get all of the descriptions in current palette to preview
            # or add as option to xgmPreview
            descs = xg.descriptions(self.currentPalette())
            for desc in descs:
                if not first:
                    cmd += ','
                cmd += '"'+desc+'"'
                first = False
        elif mode==self.PreviewMode.Description:
            cmd += '"'+self.currentDescription()+'"'
        cmd += '}'

        # register command for idle execution
        if idle:
            self.previewer.add( cmd )
        else:
            mel.eval(cmd)

    def currentPalette(self):
        return str(self.palettes.currentText())

    def setCurrentPalette(self, palette):
        index = self.palettes.findText(palette)
        if index < 0:
            return

        self.palettes.setCurrentIndex(index)
        self.refresh("Palette")

        # tell others about the new description
        self.xgCurrentDescriptionChanged.emit( palette, self.currentDescription() )
    
    def currentDescription(self):
        ns = xg.objNameSpace(self.currentPalette())
        return str(ns+self.descs.currentText())

    def setCurrentDescription(self,description):
        targetPalette     = ''
        targetDescription = ''      

        targetPalette     = xg.palette(description)
        targetDescription = xg.stripNameSpace(description)
            
        if targetPalette == '':
            return
        
        if targetPalette != self.currentPalette():
            self.setCurrentPalette(targetPalette)
            
        index = self.descs.findText(targetDescription)
        if index < 0:
            return

        self.descs.setCurrentIndex(index)
        self.refresh("Description")

        # tell others about the new description
        self.xgCurrentDescriptionChanged.emit(targetPalette, targetDescription)

    def activePrimitive(self):
        return xg.getActive(self.currentPalette(),
                self.currentDescription(),"Primitive")
    
    def activeGenerator(self):
        return xg.getActive(self.currentPalette(),
                self.currentDescription(),"Generator")
    
    def activeRenderer(self):
        return xg.getActive(self.currentPalette(),
                self.currentDescription(),"Renderer")
    
    def activePreviewer(self):
        return xg.getActive(self.currentPalette(),
                self.currentDescription(),"Previewer")
    
    def setActive(self,objectType,newActive,previewer=False,clean=True):
        """Set the active object type both in XGen and the editor."""
        
        oldPlayblast = xgg.Playblast
        if previewer == False:
            xgg.Playblast = False
        
        if previewer:
            current = xg.getActive(self.currentPalette(),
                                   self.currentDescription(),"Previewer")
        else:
            current = xg.getActive(self.currentPalette(),
                                   self.currentDescription(),objectType)
        if current != newActive+objectType:
            xg.setActive(self.currentPalette(),self.currentDescription(),
                         newActive+objectType,previewer)
        if objectType == "Primitive":
            index = xgg.PrimitiveTypes().index(newActive)
            self.primitiveTab.setCurrent(index)
            widget = self.primitiveTab.widget()
            widget.setActiveByTypeName(newActive)
            widget.refresh()
            self.fxStackTab.rebuildFXStackUI()
            if xgg.Maya and clean:
                mel.eval('xgmPreview -clean {"'+self.currentDescription()+'"}')
        elif objectType == "Generator":
            index = xgg.GeneratorTypes().index(newActive)
            self.generatorTab.setCurrent(index)
            widget = self.generatorTab.widget()
            widget.setActiveByTypeName(newActive)
            widget.refresh()
        elif objectType == "Renderer":
            if previewer:
                index = xgg.PreviewerIndex[newActive]
                self.previewerTab.setCurrent(index)
                widget = self.previewerTab.widget()
                #widget.setActiveByTypeName(newActive)
                widget.refresh()
            else:
                index = xgg.RendererTypes().index(newActive)
                self.rendererTab.setCurrent(index)
                widget = self.rendererTab.widget()
                widget.setActiveByTypeName(newActive)
                widget.refresh()

        xgg.Playblast = oldPlayblast
        self.playblast()

    def getFXModules(self):
        """Returns the list of modules for the current description"""
        return xg.fxModules( self.currentPalette(), self.currentDescription() )

    def getFXModulesReversed(self):
        """Returns a list of the modules in reverse order, with the last module executed as the first"""
        return self.getFXModules()[::-1] 

    def setAttr(self,object,attr,value, undoRequired=False):
        """Set an attribute via the editor."""
        desc=""
        obj=""
        if object!="Palette":
            desc = self.currentDescription()
            if object!="Description":
                obj = object
        
        try:            
            if xgg.Maya and undoRequired:
                with xg.undoable(attr):
                    cmds.xgmSetAttr( a=attr, v=value, p=self.currentPalette(), d=desc, o=obj )
            else:
                xg.setAttr( attr, value, self.currentPalette(), desc, obj )
        except:
            import traceback
            traceback.print_exc()            
    
    def getAttr(self,object,attr):
        """Get an attribute via the editor."""
        desc=""
        obj=""
        if object!="Palette":
            desc = self.currentDescription()
            if object!="Description":
                obj = object
        return xg.getAttr(attr,self.currentPalette(),desc,obj)

    def setAttrCmd( self, object, attr, value ):
        """ Set attribute value through an undoable command. Returns True if the value was changed"""         
        current = self.getAttr( object, attr )
        changeValue = current != value
        if changeValue:
            # don't set the attribute if value is different than the current value
            self.setAttr( object, attr, value, self._undoRequired )
        return changeValue
    
    def enableUI(self,state):
        """Enable/disable the whole UI."""
        self.primitiveTab.setVisible(state)
        self.fxStackTab.setVisible(state)
        self.generatorTab.setVisible(state)
        self.rendererTab.setVisible(state)
        self.lodTab.setVisible(state)
        self.previewerTab.setVisible(state)
        self.utilitiesTab.setVisible(state)
        self.palExprsTab.setVisible(state)
        if xgg.Maya:
            self.brushTab.setVisible(state)

        self.welcomeUI.setVisible(not state)
        self.mainUI.setVisible(state)

        self.xgDescriptionEditorEnableUI.emit( state )
        
    def scheduleRefresh(self):
        ''' Schedule an idle refresh '''
        
        # Refresh command to execute in the idle event
        refreshCmd = 'if xgg.DescriptionEditor:\n\txgg.DescriptionEditor.refresh("Full")'
        if refreshCmd not in cmds.evalDeferred(list=True):
            cmds.evalDeferred(refreshCmd)
        
    def refresh(self,type):
        """Refresh the contents of the description editor.
        This method supports a full refresh, a palette change, or a
        description change. The mini modification is always made.
        """

        with self.setAttrGuard():            
            self.showWelcome = False

            if type == 'Full':
                # A full refresh will rebuild the palette list
                self.__refreshPalettes()
                self.__refreshPalette()
                self.__refreshDescription()
            elif type == 'Palette':
                # A palette refresh will rebuild the description list
                self.__refreshPalette()
                self.__refreshDescription()
            elif type == 'Description':
                # A description refresh will update tabs
                self.__refreshDescription()
            else:
                xg.XGWarning(3,
                    maya.stringTable[u'y_xgenm_ui_xgDescriptionEditor.kInvalidRefreshType'])

            if xgg.Maya:
                xg.invokeCallbacks("CurrentDescriptionSet",
                                   [self.currentDescription()])            

            self.enableUI(not self.showWelcome)
                
    def __refreshPalettes(self):
        ''' Rebuild the palette list combobox '''

        # Get a list of palettes to be shown
        palettes = uiPalettes()
        palettes.sort()
        
        # No palettes ?
        if len(palettes) == 0:
            self.palettes.clear()
            self.descs.clear()
            self.showWelcome = True
            return
        
        # Retain the current palette selection after rebuild
        with self.currentPaletteGuard():
            # Reset the palette list combobox
            self.palettes.clear()

            # Populate the palette list combobox
            for palette in palettes:
                self.palettes.addItem(palette)
    
    def __refreshPalette(self):
        # No palettes ?
        if self.palettes.count() == 0:
            return

        # No descriptions ?
        if len(list(xg.descriptions())) == 0:
            self.descs.clear()
            self.showWelcome = True
            return
        
        # Get the current palette selection
        palette = self.currentPalette()
        
        self.tabsets.setCurrent(0)
        self.refreshPalExprs()

        # Get the list of descriptions from the current palette
        descriptions = list(xg.descriptions(palette))
        descriptions.sort()
        
        # No descriptions in the current palette ?
        if len(descriptions) == 0:
            self.descs.clear()
            return
        
        # Retain the current description selection after rebuild
        with self.currentDescriptionGuard():
            descriptions[:] = [xg.stripNameSpace(x) for x in descriptions]

            # Reset the description list combobox
            self.descs.clear()
            
            # Populate the description list combobox
            for description in descriptions:
                self.descs.addItem(description)
                
    def __refreshDescription(self):
        # No palettes or descriptions ?
        if self.palettes.count() == 0 or self.descs.count() == 0:
            return
        
        # Get the current palette and description selection
        palette     = self.currentPalette()
        description = self.currentDescription()

        if len(xg.stripNameSpace(description)) == 0:
            return
        
        # Update the tabs for the current description
        value = self.activePrimitive()
        self.setActive('Primitive',value[:len(value)-9],clean=False)
        value = self.activeGenerator()
        self.setActive('Generator',value[:len(value)-9])
        value = self.activeRenderer()
        self.setActive('Renderer',value[:len(value)-8])
        value = self.activePreviewer()
        self.setActive('Renderer',value[:len(value)-8],True)

        self.lodTab.refresh()
        self.generatorTab.widget().refresh()

        self.xgCurrentDescriptionChanged.emit(palette, description)

    def editPath(self):
        value = xg.getAttr("xgDataPath",self.currentPalette())
        (res,ok) = QInputDialog.getText(self,maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kEditFilePath2'  ],
                    maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kEditXGenPathDescription'  ],
                    QLineEdit.Normal,value)
        if ok:
             self.setAttrCmd(self.currentPalette(),"xgDataPath",str(res))          
    
    def modifyBinding(self,mode):
        if xgg.Maya:
            cpal = self.currentPalette()
            cdesc = self.currentDescription()
            if not cpal:
                return
            if not cdesc:
                return

            with xg.undoable('Face:'+mode):
                if mode=="Map":
                    mapBindings(cpal,cdesc)
                else:
                    xg.modifyFaceBinding(cpal,cdesc,mode)
                if self.autoCreateMR and mel.eval('exists "xgmr"'):
                    # update the bound patches
                    cmds.xgmr( ugs=True, description=cdesc, palette=cpal )
            self.playblast()
       
    def repoMan(self,value):
        # if the value is "save" then we raise a browser in user repo
        if str(value)=="save":
            startDir  = xg.userRepo() + "descriptions/"
            try:
                buf = os.stat(startDir)
            except:
                # if the directory isn't there the browser will send us to
                # some unexpected location
                os.makedirs(startDir)
            result = fileBrowserDlg(self,startDir,"*.xdsc","out")
            if len(result):
                if not result.endswith(".xdsc"):
                    result += ".xdsc"
                xg.exportDescription(self.currentPalette(),
                                     self.currentDescription(),result)
                self.buildMenus()
        else:
            try:
                filename = str(value)
                buf = os.stat(filename)
                name = xg.importDescription(self.currentPalette(),filename)
                self.refresh("Full")
                self.setCurrentDescription(name)
            except:
                xglog.XGError(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kTheGivenDescriptionDoesntExist'  ] % filename)
                self.buildMenus()
                return

    def selectBinding(self):
        if xgg.Maya:
            cpal = self.currentPalette()
            cdesc = self.currentDescription()
            geoms = xg.boundGeometry(cpal,cdesc)
            faceStr = []
            with xg.undoable('Face:Select'):
                cmds.select(None)
                for geom in geoms:
                    faces = xg.boundFaces(cpal,cdesc,geom,True)
                    for face in faces:
                        faceStr.append(geom+".f["+str(face)+"]")
                cmds.select(faceStr,replace=True)
                    
    def primSelectionContext(self,type="Selection"):
        if xgg.Maya:
            cmd = "xgmPrimSelectionContext -q -ex xgenPrim"+type+"Instance"
            if not mel.eval(cmd):
                cmd = "xgmPrimSelectionContext "
                if type=="Isolate":
                    cmd += "-is "
                cmd += "xgenPrim"+type+"Instance"
                mel.eval(cmd)
            cmds.setToolTo("xgenPrim"+type+"Instance")

    def guideSculptContext(self,options=False):
        if xgg.Maya:
            cmd = "xgmGuideSculptContext -q -ex xgmGuideSculptTool"
            if not mel.eval(cmd):
                cmd = "xgmGuideSculptContext xgmGuideSculptTool"
                mel.eval(cmd)
            cmds.setToolTo("xgmGuideSculptTool")

            if options:
                cmds.toolPropertyWindow()

    def batchExportArchives(self):
        if self.arcBatchExport==None:
            self.arcBatchExport = xgmArchiveExportBatchUI( True )
        self.arcBatchExport.exec_()

    def exportArchives(self):
        if self.arcExport==None:
            self.arcExport = xgmArchiveExportBatchUI( False )
        self.arcExport.exec_()

    def exportPatches(self):
        strCurrentScene = cmds.file( q=True, sn=True )
        strSceneName = ""
        if strCurrentScene:
            strScenePath = os.path.dirname( strCurrentScene )
            strSceneFile = os.path.basename( strCurrentScene )
            strSceneName = os.path.splitext( strSceneFile )[0];
        else:
            xglog.XGError(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kYouMustSaveTheSceneFirst'  ])
            return 

        dialog = ExportUI()
        dialog.setWindowTitle(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kExportPatchesForBatchRenderDialog'  ])
        result = dialog.exec_()
        if result == QDialog.Accepted:
            global Anim, ExportStartFrame, ExportEndFrame
            ExportStartFrame = dialog.getStartFrame()
            ExportEndFrame = dialog.getEndFrame()

            cmdAlembicBase = 'AbcExport -j "' 
            Anim = dialog.getAnim()
            if Anim:
                cmdAlembicBase = cmdAlembicBase + '-frameRange '+str(ExportStartFrame)+' '+str(ExportEndFrame)
            cmdAlembicBase = cmdAlembicBase + ' -uvWrite -attrPrefix xgen -worldSpace'
            palette = cmds.ls( exactType="xgmPalette" )
            for p in range( len(palette) ):
                filename = strScenePath+ "/" + strSceneName + "__" + xgmExternalAPI.encodeNameSpace(str(palette[p])) + ".abc"
                descShapes = cmds.listRelatives( palette[p], type="xgmDescription", ad=True )
                cmdAlembic = cmdAlembicBase
                for d in range( len(descShapes) ):
                    descriptions = cmds.listRelatives( descShapes[d], parent=True )
                    if len(descriptions):
                        patches = xg.descriptionPatches(descriptions[0])
                        for patch in patches:
                            cmd = 'xgmPatchInfo -p "'+patch+'" -g';
                            geom = mel.eval(cmd)
                            geomFullName = cmds.ls( geom, l=True )
                            cmdAlembic += " -root " + geomFullName[0]
                
                cmdAlembic = cmdAlembic + ' -stripNamespaces -file \''+ filename+ '\'";';
                print(cmdAlembic)
                mel.eval(cmdAlembic)

    def toggleVisualizer(self):
        visual = cmds.ls(type="xgmConnectivity")
        if visual:
            for v in visual:
                p = cmds.listRelatives(v,parent=True)
                cmds.delete(p)

        if self.displayGuideRange.isChecked():
            selection = cmds.ls(sl=True)
            parent = cmds.listRelatives(self.currentPalette(),parent=True)
            if parent:
                xform = cmds.createNode("transform",name="xgmConnectivity#",
                                        parent=parent[0])
            else:
                xform = cmds.createNode("transform",name="xgmConnectivity#")
            node = cmds.createNode("xgmConnectivity",name=xform+"Shape",
                                   parent=xform)
            cmds.select(selection,r=True)

    def onPaletteDelete(self, pal):
        for key in list(self.palExprExpandState.keys()):
            if key.startswith(pal + " "):
                del self.palExprExpandState[key]

    def deletePalette(self):
        xg.deletePalette(self.currentPalette())
        self.refresh("Full")
        self.xgCurrentDescriptionChanged.emit( self.currentPalette(), self.currentDescription() )
        
    def deleteDescription(self):
        xg.deleteDescription(self.currentPalette(),self.currentDescription())
        self.refresh("Full")
        self.xgCurrentDescriptionChanged.emit( self.currentPalette(), self.currentDescription() )

    def getMessageLevel( self, type ):
        """ return message value from option vars or default value if doesn't exist """
        try:
            if xgg.Maya:
                val = xg.getOptionVar( self.optionVars[type] )
            else:
                val = None
        except:
            traceback.print_exc()
            return None

        if val == None:
            val = xg.getMessageLevel(type)
        return val
        
    def setMessageLevel(self,type,level):
        """set message level and save in option var """
        if type=="debug":
            self.logDebugMenu.setTitle(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kDebugLevelMenuChange'  ] % str(level))
            xg.setMessageLevel(type,level)
        elif type=="warning":
            self.logWarnMenu.setTitle(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kWarningLevelMenuChange'  ] % str(level))
            xg.setMessageLevel(type,level)
        elif type=="stats":
            self.logStatsMenu.setTitle(maya.stringTable[ u'y_xgenm_ui_xgDescriptionEditor.kStatisticsLevelMenuChange'  ] % str(level))
            xg.setMessageLevel(type,level)
        else:
            raise Exception('setMessageLevel: wrong type')
        
        xg.setOptionVarInt( self.optionVars[type], level )

    def updateMessageLevel( self ):
        """ update message level from option vars """
        val = self.getMessageLevel( 'warning' )
        self.setMessageLevel( 'warning', val )
        val = self.getMessageLevel( 'debug' )
        self.setMessageLevel( 'debug', val )
        val = self.getMessageLevel( 'stats' )
        self.setMessageLevel( 'stats', val )

    def _showHelp(self):
        cmds.showHelp("XGen")

    def quit(self):
        QCoreApplication.quit()
    
       

def createDescriptionEditor(showIt=True):
    """Create a description editor."""

    if xgg.DescriptionEditor is None:
        cmds.waitCursor(state=1)

        DescriptionEditorUI()
        # delete the previous dock control if there is one
        if cmds.dockControl("XGenDockableWidget", q=True, ex=True):
            cmds.deleteUI("XGenDockableWidget")

        # to set it up in Maya as a panel,  it'll need an object name 
        descui =  xgg.DescriptionEditor
        descui.setObjectName("XGenDescriptionEditor")

        cmds.waitCursor(state=0)

    if showIt:
        # show it in the dock
        # if the user hit the close button, it actually only hides the widget, so we both raise it and make sure it's visible.
        if cmds.workspaceControl('XGenDockableWidget', q=True, ex=True):
            cmds.workspaceControl('XGenDockableWidget', e=True, vis=True, r=True)
        else:
            LEcomponent = mel.eval('getUIComponentDockControl("Channel Box / Layer Editor", false);')
            cmds.workspaceControl('XGenDockableWidget',
                                  requiredPlugin='xgenToolkit',
                                  tabToControl=(LEcomponent, -1),
                                  initialWidth=cmds.optionVar( q='workspacesWidePanelInitialWidth' ),
                                  minimumWidth=cmds.optionVar( q='workspacesWidePanelInitialWidth' ),
                                  label=maya.stringTable[u'y_xgenm_ui_xgDescriptionEditor.kXgen' ],
                                  uiScript='''import maya.cmds as xguibootstrap
if not xguibootstrap.pluginInfo('xgenToolkit', q=True, loaded=True):
    xguibootstrap.loadPlugin('xgenToolkit')
del xguibootstrap
xgui.createDockControl()''')
            cmds.workspaceControl('XGenDockableWidget', e=True, r=True)

    return xgg.DescriptionEditor


def refreshDescriptionEditor():
    """Refresh the description editor after scene changes."""
    if xgg.DescriptionEditor is None:
        return

    xgg.DescriptionEditor.refresh("Full")

def createDockControl():
    ''' Add the Description Editor widget to Maya workspace control '''
    if xgg.DescriptionEditor is None:
        # Create the Description Editor if not exists
        cmds.waitCursor(state=1)
        DescriptionEditorUI()
        descui =  xgg.DescriptionEditor
        descui.setObjectName("XGenDescriptionEditor")
        cmds.waitCursor(state=0)
        
    if xgg.Maya and xgg.DescriptionEditor:
        # Get the layout of the parent workspace control and Description Editor widget
        parent = mui.MQtUtil.getCurrentParent()
        widget = mui.MQtUtil.findControl('XGenDescriptionEditor')

        # Add the Description Editor to workspace control layout
        mui.MQtUtil.addWidgetToMayaLayout(long_type(widget), long_type(parent))
        xgg.DescriptionEditor.refresh("Full")

        # Maya workspace control should never delete its content widget when
        # retain flag is true. But it still deletes in certain cases. We avoid
        # deleting the global widget by removing it from its parent's children.
        # destroyed signal is emitted right before deleting children.
        parentWidget = wrapInstance(long_type(parent), QWidget)
        if parentWidget:
            parentWidget.destroyed.connect(xgg.DescriptionEditor.detachMe)

def _refreshCB(param):
    refreshDescriptionEditor()

def postPaletteDeleteCB(pal):
    if xgg.DescriptionEditor is None:
        return
    xgg.DescriptionEditor.onPaletteDelete(pal)

