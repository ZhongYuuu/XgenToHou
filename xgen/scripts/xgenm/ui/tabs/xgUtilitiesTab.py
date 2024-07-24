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

##
# @file xgGeneratorTab.py
# @brief Contains the UI for Generator tab
##
from builtins import range
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *
import xgenm as xg
import xgenm.xgGlobal as xgg
if xgg.Maya:
    import maya.mel as mel
from xgenm.ui.util.xgUtil import *
import weakref

class ToolIconView(QListWidget):
    def __init__( self, parentTab ):
        QListWidget.__init__( self )
        self.parentTab = weakref.proxy(parentTab)
        self.freezeNotifications = False
        
    def  selectionChanged(self, selected, deselected):
        super(ToolIconView,self).selectionChanged(selected,deselected)
        
        if not self.freezeNotifications:
            model = self.model()
    
            changes = []
            for item in selected.indexes():
                changes.append(model.data(item,QtCore.Qt.UserRole))
            if len(changes) > 0 :
                self.parentTab.toolAddedCallback(changes)
            
            changes = []
            for item in deselected.indexes():
                changes.append(model.data(item,QtCore.Qt.UserRole))
            if len(changes) > 0 :
                self.parentTab.toolRemovedCallback(changes)

    def setSelectionFromUserRoles(self,itemList):
        self.freezeNotifications = True
        self.clearSelection()
        count = self.count()
        for i in range(0,count):
            item = self.item(i)
            if (item.data(QtCore.Qt.UserRole) in itemList):
                item.setSelected(True)
        self.freezeNotifications = False

class UtilitiesTabUI( QWidget ):
    """ tab that presents what is internally called "xgen tool" and the xgen tool manager
    """
    def __init__( self ):
        QWidget.__init__( self )
        self.createUI = True

    def doCreateUI( self ):
        layout = QVBoxLayout()
        QLayoutItem.setAlignment(layout, QtCore.Qt.AlignTop )
        layout.setSpacing(DpiScale(0))
        layout.setContentsMargins(DpiScale(3),DpiScale(3),DpiScale(3),DpiScale(3)) 
        self.setLayout( layout )

        self.splitter = QSplitter( QtCore.Qt.Vertical )
        layout.addWidget( self.splitter )
        
        if xgg.Maya:
            self.splitter.addWidget(self.createIconView())
            self.splitter.addWidget(self.createEditorArea())

        self.splitter.setSizes([DpiScale(200),DpiScale(800)])
        if xgg.Maya:
            self.tmRestoreStateFromOptionVars()

    def createIconView(self):
        # if in localized mode, build tab in horizontal layout to
        # accomodate japanese text better 
        isLocalized = mel.eval("about -uiLanguageIsLocalized;")
        self.iconView = ToolIconView(self)
        self.iconView.setSelectionMode( QAbstractItemView.MultiSelection )
        self.iconView.setMovement(QListView.Static)
        self.iconView.setResizeMode(QListView.Adjust)
        self.iconView.setWordWrap(True)
        if isLocalized == 1:
            self.iconView.setViewMode(QListView.ListMode)
            self.iconView.setWrapping(True)
            self.iconView.setFlow(QListView.LeftToRight)
            self.iconView.setIconSize(QSize(DpiScale(50),DpiScale(50)))
        else:
            self.iconView.setViewMode(QListView.IconMode)
            self.iconView.setGridSize(QSize(DpiScale(56),DpiScale(86)))
        self.iconView.itemDoubleClicked.connect(self.toolDoubleClicked)

        toolNameList = mel.eval('lookupTableGetColumn($gXgmTMLookupTable,"toolName");')
        toolIconList = mel.eval('lookupTableGetColumn($gXgmTMLookupTable,"toolIcon");')
        toolDescList = mel.eval('lookupTableGetColumn($gXgmTMLookupTable,"toolDescr");')
        toolCreateFunc = mel.eval('lookupTableGetColumn($gXgmTMLookupTable,"toolCreateUIMethod");')


        for i in range(0,len(toolNameList)):            
            iconPath =  path = xg.iconDir()+toolIconList[i]
            icon = CreateIcon(iconPath)
            item = QListWidgetItem(icon, toolNameList[i])
            item.setToolTip(toolDescList[i])
            item.setData(QtCore.Qt.UserRole,toolCreateFunc[i])
            if isLocalized == 1:
                item.setSizeHint(QSize(DpiScale(110),DpiScale(50)))
                item.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            self.iconView.addItem(item)

        return self.iconView

    def createEditorArea(self):
        self.editorArea = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))
        layout.setObjectName("XGenToolEditorAreaParent")
        self.editorArea.setLayout(layout)
        mel.eval('columnLayout -parent "XGenToolEditorAreaParent"-adjustableColumn true XGenToolEditorArea;')

        return createScrollArea(self.editorArea)

    def paintEvent(self,event):
        super(UtilitiesTabUI,self).paintEvent(event)
        if self.createUI:
            self.createUI = False
            self.doCreateUI() 

    def toolAddedCallback(self, toolNameList ):
        for tool in toolNameList:
            self.tmLoadTool(tool)

    def toolRemovedCallback(self, toolNameList ):
        for tool in toolNameList:
            self.tmUnloadTool(tool)

    def toolDoubleClicked(self,listWidgetItem ):
       self.iconView.clearSelection()
       listWidgetItem.setSelected(True) 

    def tmLoadTool(self, toolName):
        melCommand = 'tmLoadTool("XGenToolEditorArea","' + toolName + '", false);'
        mel.eval(melCommand)
        self.tmUpdateOptionVars()

    def tmUnloadTool(self, toolName):
        melCommand = 'tmUnloadTool("XGenToolEditorArea","' + toolName + '");'
        mel.eval(melCommand)
        self.tmUpdateOptionVars()
        
    def tmRestoreStateFromOptionVars(self):
        toolNameList = mel.eval('tmRestoreStateFromOptionVars("XGenToolEditorArea");')

        # the tool's UI has been created, now we just need to update the iconView
        self.iconView.setSelectionFromUserRoles(toolNameList)

    def tmUpdateOptionVars(self):
         mel.eval('tmUpdateOptionVars("XGenToolEditorArea");');
