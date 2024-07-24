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
# @file igImport.py
# @brief igroom import dialog
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *
import xgenm as xg
import xgenm.xgGlobal as xgg
import xgenm.xgLog as xglog
import maya.cmds as cmds
import maya.mel as mel
from xgenm.ui.util.xgUtil import *
from xgenm.ui.widgets import *

__all__ = [ 'igImportFile' ]

class igImportUI(QDialog):       
    class MapImporter(QWidget):
        def __init__(self, tabs):
            QWidget.__init__(self)
            vbox = QVBoxLayout()
            QLayoutItem.setAlignment(vbox, QtCore.Qt.AlignTop)
            self.setLayout(vbox)

            expDir = xg.getOptionVarString( 'igAutoExportFolder' )
            self.path = FileBrowserUI(maya.stringTable[ u'y_xgenm_ui_dialogs_igImport.kFolderPathMapImport'  ],
                                    maya.stringTable[ u'y_xgenm_ui_dialogs_igImport.kFolderPathMapImportAnn'  ])
            self.path.optionButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_dialogs_igImport.kBrowseForAFolder'  ])
            self.path.setValue( expDir )
            vbox.addWidget(self.path)

            scrollArea = QScrollArea()
            scrollArea.setWidget(self)
            scrollArea.setWidgetResizable(True)
            tabs.addTab(scrollArea,maya.stringTable[ u'y_xgenm_ui_dialogs_igImport.kAttributeMaps'  ])

        def doIt(self):
            path = self.path.value()
            desc = xgg.DescriptionEditor.currentDescription()
            igDescr = xg.igDescription( desc )

            expandedPath = FileBrowserUI.folderExists(path,desc,self)
            if not expandedPath:
                return False

            try:
                cmds.waitCursor( state=True )
                mel.eval( 'iGroom -im "%s" -d "%s";' % (expandedPath,igDescr) )
            finally:
                cmds.waitCursor( state=False )

            xglog.XGWarning(maya.stringTable[u'y_xgenm_ui_dialogs_igImport.kIgImportUIAttrMapsFrom' ] % (desc,expandedPath) )
            return True

    class MaskImporter(QWidget):
        def __init__( self, tabs ):
            QWidget.__init__(self)
            vbox = QVBoxLayout()
            QLayoutItem.setAlignment(vbox, QtCore.Qt.AlignTop)
            self.setLayout(vbox)

            expDir = xg.getOptionVarString( 'igAutoExportFolder' )
            self.path = FileBrowserUI(maya.stringTable[ u'y_xgenm_ui_dialogs_igImport.kFolderPathMaskImporter'  ],
                                    maya.stringTable[ u'y_xgenm_ui_dialogs_igImport.kFolderPathMaskImporterAnn'  ])
            self.path.optionButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_dialogs_igImport.kBrowseForAFolder2'  ])
            self.path.setValue( expDir )
            vbox.addWidget(self.path)

            scrollArea = QScrollArea()
            scrollArea.setWidget(self)
            scrollArea.setWidgetResizable(True)
            tabs.addTab(scrollArea,maya.stringTable[ u'y_xgenm_ui_dialogs_igImport.kMask'  ])

        def doIt(self):
            path = self.path.value()
            desc = xgg.DescriptionEditor.currentDescription()
            igDescr = xg.igDescription( desc )

            expandedPath = FileBrowserUI.folderExists(path,desc,self)
            if not expandedPath:
                return False

            try:
                cmds.waitCursor( state=True )
                mel.eval( 'iGroom -ik "%s" -d "%s";' % (expandedPath,igDescr) )
            finally:
                cmds.waitCursor( state=False )

            xglog.XGWarning(maya.stringTable[u'y_xgenm_ui_dialogs_igImport.kIgImportUIMaskMapsFrom' ] % (desc,expandedPath) )
            return True

    class RegionImporter(QWidget):
        def __init__( self, tabs ):
            QWidget.__init__(self)
            vbox = QVBoxLayout()
            QLayoutItem.setAlignment(vbox, QtCore.Qt.AlignTop)
            self.setLayout(vbox)

            expDir = xg.getOptionVarString( 'igAutoExportFolder' )
            self.path = FileBrowserUI(maya.stringTable[ u'y_xgenm_ui_dialogs_igImport.kFolderPathRegionImporter'  ],
                                 maya.stringTable[ u'y_xgenm_ui_dialogs_igImport.kFolderPathRegionImporterAnn'  ])
            self.path.optionButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_dialogs_igImport.kBrowseForAFolder3'  ])
            self.path.setValue( expDir )
            vbox.addWidget(self.path)

            scrollArea = QScrollArea()
            scrollArea.setWidget(self)
            scrollArea.setWidgetResizable(True)
            tabs.addTab(scrollArea,maya.stringTable[ u'y_xgenm_ui_dialogs_igImport.kRegionMap'  ])

        def doIt(self):
            path = self.path.value()
            desc = xgg.DescriptionEditor.currentDescription()
            igDescr = xg.igDescription( desc )

            expandedPath = FileBrowserUI.folderExists(path,desc,self)
            if not expandedPath:
                return False

            try:
                cmds.waitCursor( state=True )
                mel.eval( 'iGroom -ir "%s" -d "%s";' % (expandedPath,igDescr) )
            finally:
                cmds.waitCursor( state=False )

            xglog.XGWarning(maya.stringTable[u'y_xgenm_ui_dialogs_igImport.kIgImportUIRegionMapsFrom' ] % (desc,expandedPath) )
            return True            

    # Dialog init
    def __init__(self):
        QDialog.__init__(self)
        self.setWindowTitle(maya.stringTable[ u'y_xgenm_ui_dialogs_igImport.kIgroomImport'  ])
        self.setSizeGripEnabled(True)
        self.setMinimumWidth(DpiScale(400))

        layout = QVBoxLayout()
        QLayoutItem.setAlignment(layout, QtCore.Qt.AlignTop)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        igImportUI.MapImporter( self.tabs )
        igImportUI.MaskImporter( self.tabs )
        igImportUI.RegionImporter( self.tabs )

        self.buttons(layout)
        self.setLayout(layout)

    def buttons(self,layout):
        row = QWidget()
        hbox = QHBoxLayout()
        QLayoutItem.setAlignment(hbox, QtCore.Qt.AlignRight)
        hbox.setSpacing(DpiScale(3))
        hbox.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
        self.importButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_dialogs_igImport.kImport'  ])
        self.importButton.setFixedWidth(DpiScale(100))
        self.importButton.setAutoRepeat(False)
        self.connect(self.importButton, QtCore.SIGNAL("clicked()"), self.importCB)
        hbox.addWidget(self.importButton)
        self.cancelButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_dialogs_igImport.kCancel'  ])
        self.cancelButton.setFixedWidth(DpiScale(100))
        self.cancelButton.setAutoRepeat(False)
        self.cancelButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_dialogs_igImport.kCancelAnn'  ])
        self.connect(self.cancelButton, QtCore.SIGNAL("clicked()"), self.reject)
        hbox.addWidget(self.cancelButton)
        row.setLayout(hbox)
        layout.addWidget(row)
        self.setLayout(layout)
                       
    def importer(self):
        # tabs -> scroll widget -> exporter
        return self.tabs.currentWidget().widget()

    def importCB(self):
        importer = self.importer()
        if importer.doIt():
            # done, accept/close dialog
            self.accept()
                  
def igImportFile():
    if len(xg.palettes()) == 0:
        tellem = QMessageBox()
        tellem.setText(maya.stringTable[ u'y_xgenm_ui_dialogs_igImport.kThereIsNothingToImport'  ])
        tellem.exec_()
        return

    igImportUI().exec_()
