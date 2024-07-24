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
# @file xgArchivePrimitiveTab.py
# @brief Contains the UI for archive primitive tab
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
# @version Created 06/04/09
#
from builtins import range
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *

import maya.cmds as cmds
import xgenm as xg
import xgenm.xgGlobal as xgg
import xgenm.xgCmds as xgcmds
from xgenm.ui.widgets import *
from xgenm.ui.util import xgUtil
from xgenm.ui.tabs.xgPrimitiveTab import *
from xgenm.ui.util.xgProgressBar import setProgressInfo
from xgenm.ui.util.xgUtil import DpiScale
from xgenm.ui.util.xgUtil import labelWidth


class ArchivePrimitiveTabUI(PrimitiveTabUI):
    def __init__(self):
        # Widgets
        PrimitiveTabUI.__init__(self,'Archive',maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kArchive'  ])
        self.baseTopUI(True)
        
        self.lengthExpr = ExpressionUI("length","",
            "ArchivePrimitive",maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kLength'  ])
        self.attrGroup.addWidget(self.lengthExpr)
        self.widthExpr = ExpressionUI("width","","ArchivePrimitive",maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kWidth'  ])
        self.attrGroup.addWidget(self.widthExpr)
        self.depthExpr = ExpressionUI("depth","","ArchivePrimitive",maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kDepth'  ])
        self.attrGroup.addWidget(self.depthExpr)
        self.offUExpr = ExpressionUI("offU",
            maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kTiltUAnn'  ],
            "ArchivePrimitive",maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kTiltU'  ])
        self.attrGroup.addWidget(self.offUExpr)
        self.offVExpr = ExpressionUI("offV",
            maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kTiltVAnn'  ],
            "ArchivePrimitive",maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kTiltV'  ])
        self.attrGroup.addWidget(self.offVExpr)
        self.twistExpr = ExpressionUI("twist",
            maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kTwistAnn'  ],
            "ArchivePrimitive",maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kTwist'  ])
        self.attrGroup.addWidget(self.twistExpr)
        self.offNExpr = ExpressionUI("offN",
            maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kTiltNAnn'  ],
            "ArchivePrimitive",maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kTiltN'  ])
        self.attrGroup.addWidget(self.offNExpr)
        self.aboutNExpr = ExpressionUI("aboutN",
            maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kAroundNAnn' ],
            "ArchivePrimitive",maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kAroundN'  ])
        self.attrGroup.addWidget(self.aboutNExpr)
        
        self.aIndexExpr = ExpressionUI("aIndex",
                            maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kIndexAnn'  ],
                            "ArchivePrimitive", maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kIndex'  ])
        self.attrGroup.addWidget(self.aIndexExpr)
        
        self.frameExpr = ExpressionUI("frame",
                            maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kFrameAnn'  ],
                            "ArchivePrimitive", maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kFrame'  ])
        self.attrGroup.addWidget(self.frameExpr)
        self.aLODExpr = ExpressionUI("aLOD",
                            "",
                            "ArchivePrimitive",maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kLod'  ])
        self.attrGroup.addWidget(self.aLODExpr)
        
        self.archiveFilesUI()
        self.expressionsUI()  
        self.advancedUI()
        self.baseBottomUI()
    
    def syncDRABBoxValues(self):
        """Sync the DRA Size and Primitive Bounds"""
        de = xgg.DescriptionEditor
        pal = de.currentPalette()
        desc = de.currentDescription()

        setProgressInfo(maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kFindingDraSize'  ])
        xgcmds.syncArchiveSize(pal, desc)

        self.archiveSize.refresh()

        size = xg.getAttr('archiveSize', pal, desc, 'ArchivePrimitive')
        

        msg = maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kTheBoundingBoxValuesHaveBeenUpdated'  ]
        info = (maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kDraSize'  ] % (size))
        xgUtil.information(self, maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kXgenArchivePrimitive'  ], msg, informative_text=info)
        
        # refresh preview
        cmds.xgmPreview()


    def saveFile(self):
        dialog = SavePilFileUI()
        result = dialog.exec_()
        if result == QDialog.Accepted:
            fileName = dialog.getFileName()
            if len(fileName):
                path = os.path.dirname(fileName)
                if path and not os.access(path,os.F_OK):
                    os.makedirs(path)
                f = open(fileName,'w')
                val = self.files.textEdit.toPlainText()
                f.write(val)
                f.write("\n")
                f.close()

    def customMenu(self,point):
        m = self.files.textEdit.createStandardContextMenu(point)
        doc = self.files.textEdit.document()
        count = doc.characterCount();
        act = QAction(maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kSavePilFile'  ],self.files.textEdit)
        if ( count <= 1 ):
            act.setEnabled(False)
        self.connect(act,QtCore.SIGNAL("triggered(bool)"),
                    lambda x: self.saveFile())
        m.addAction(act)
        m.exec_(self.files.textEdit.mapToGlobal(point))
        

    def lodControl(self,archiveLayout,attr):
        val = QLineEdit()
        val.setValidator(QIntValidator(0,1e7,val))
        val.setFixedWidth(DpiScale(48))
        if attr.find("Upper") != -1:
            type = "Upper"
        else:
            type = "Lower"
        val.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kImageResolutionAnn'  ] % type)
        archiveLayout.addWidget(val)
        de = xgg.DescriptionEditor
        self.connect(val,QtCore.SIGNAL("editingFinished()"),
                    lambda: de.setAttrCmd("ArchivePrimitive",attr, str(val.text())) )
        return val

    def lodRow( self, exprName, exprText, lodPrefix="", mainlabel = "" ):
                if lodPrefix != "":
                        lodIndex = ExpressionUI(exprName,exprText,"ArchivePrimitive")
                        if mainlabel != "":
                            lodIndex.label.setText(mainlabel)
                        
                        row = QWidget()
                        layout = QHBoxLayout()
                        QLayoutItem.setAlignment(layout, QtCore.Qt.AlignLeft)
                        layout.addWidget(lodIndex)
                        layout.setSpacing(DpiScale(0))
                        layout.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))
                        row.setLayout( layout )
                        layout.addSpacing(DpiScale(4))
                        lodUpper = self.lodControl(layout, lodPrefix + "Upper")
                        lodLower = self.lodControl(layout, lodPrefix + "Lower")
                        self.archiveLODGroup.addWidget(row)
                        return [ lodIndex, lodUpper, lodLower ]
                else:
                        lodIndex = ExpressionUI(exprName,exprText,"ArchivePrimitive")
                        if mainlabel != "":
                            lodIndex.label.setText(mainlabel)
                        self.archiveLODGroup.addWidget(lodIndex)
                        return lodIndex

    def lodRefresh(self,lod,attr):
        de = xgg.DescriptionEditor
        value = xg.getAttr(attr,de.currentPalette(),
                        de.currentDescription(),'ArchivePrimitive')
        lod.setText(value)

    def archiveFilesUI(self):
        self.archiveFilesGroup = ExpandUI(maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kArchivesFiles'  ])
        self.actualLayout().addWidget(self.archiveFilesGroup)
        
        # Archive Files List.
        self.files = ArchiveFilesUI("files",
            maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kArchivesWithEachRowHoldingTheIndexAndPathToFile'  ],
            "ArchivePrimitive")
        self.files.label.setText(maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kArchivesFiles2'  ])
        self.files.RefreshCustomParams.connect( self.refreshCustomParams )
        self.archiveFilesGroup.addWidget(self.files)

        # Archive Size List.
        self.archiveSize = FloatUI("archiveSize",
                maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kArchiveSizeAnn'  ],
                "ArchivePrimitive",0.0,1000000,0.0,100.0,maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kSize'  ])
        self.archiveFilesGroup.addWidget(self.archiveSize)
        hbox = self.archiveSize.layout();
        self.pbButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kAutoSet'  ])
        self.pbButton.setFixedWidth(DpiScale(80))
        self.pbButton.setAutoRepeat(False)
        self.pbButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kAutoSetAnn'  ])
        hbox.addWidget(self.pbButton)
        self.connect(self.pbButton, QtCore.SIGNAL("clicked()"), self.syncDRABBoxValues)
        
    def advancedUI(self):
        
        self.archiveLODGroup = ExpandUI(maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kAdvanced'  ])
        self.actualLayout().addWidget(self.archiveLODGroup)
        
        [self.hiIndex,  self.lodHiUpper,  self.lodHiLower]  = self.lodRow( "hiIndex", maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kIndexToTheHighResArchive'  ], "lodHi", maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kHiIndex'  ] )
        [self.medIndex, self.lodMedUpper, self.lodMedLower] = self.lodRow( "medIndex", maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kIndexToTheMediumResArchive'  ], "lodMed", maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kMedIndex'  ] )
        [self.loIndex,  self.lodLoUpper,  self.lodLoLower]  = self.lodRow( "loIndex", maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kIndexToTheLowResArchive'  ], "lodLo", maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kLoIndex'  ] )
        self.proxyIndex                                     = self.lodRow( "proxyIndex", maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kIndexToTheProxyArchive'  ],"", maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kProxyIndex'  ] )
        

    def setMethod(self,method):
        PrimitiveTabUI.setMethod(self,method)
        if method == 0:
            self.lengthExpr.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kLengthAnn'  ])
            self.widthExpr.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kWidthAnn'  ])
            self.depthExpr.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kDepthAnn'  ])
            self.offUExpr.setVisible(True)
            self.offVExpr.setVisible(True)
        else:
            self.lengthExpr.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kLengthExprAnn'  ])
            self.widthExpr.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kWidthExprAnn'  ])
            self.depthExpr.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kDepthExprAnn'  ])
            self.offUExpr.setVisible(False)
            self.offVExpr.setVisible(False)

    def expressionsUI(self):
        self.expressionsGroup = ExpandUI(maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kArchiveExpressions'  ])
        self.actualLayout().addWidget(self.expressionsGroup)
        
        # Empty layout for custom params
        box = QWidget()
        self.customLayout = QVBoxLayout()
        QLayoutItem.setAlignment(self.customLayout, QtCore.Qt.AlignTop)
        self.customLayout.setSpacing(DpiScale(0))
        self.customLayout.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))
        box.setLayout(self.customLayout)
        self.expressionsGroup.addWidget(box)
        
        # UI for adding/deleting attributes
        label = QLabel(maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kName'  ])
        label.setFixedWidth(DpiScale(50))
        label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        label.setIndent(DpiScale(10))
        label.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kNameAnn'  ])
        self.cattrName = QLineEdit()
        self.cattrName.setFixedWidth(DpiScale(150))
        self.cattrName.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kNameAnn2'  ])
        rx = QRegExp("[A-Za-z]+[A-Za-z0-9_]*(\[[0-9]+\])?")
        self.cattrName.setValidator(QRegExpValidator(rx,self))
        self.cattrAddButton = QToolButton()
        self.cattrAddButton.setText("+")
        self.cattrAddButton.setFixedSize(DpiScale(20),DpiScale(25))
        self.cattrAddButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kAddCustomAnn'  ])
        self.connect(self.cattrAddButton, 
                     QtCore.SIGNAL("clicked()"), 
                     self.addCustomAttr)
        self.cattrRemButton = QToolButton()
        self.cattrRemButton.setText("-")
        self.cattrRemButton.setFixedSize(DpiScale(20),DpiScale(25))
        self.cattrRemButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kRemoveCustomAnn'  ])
        self.connect(self.cattrRemButton, 
                     QtCore.SIGNAL("clicked()"), 
                     self.remCustomAttr)
        # Put it all on one row
        row = QWidget()
        layout = QHBoxLayout()
        QLayoutItem.setAlignment(layout, QtCore.Qt.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(self.cattrName)
        layout.addSpacing(DpiScale(10))
        layout.addWidget(self.cattrAddButton)
        layout.addWidget(self.cattrRemButton)
        layout.setSpacing(DpiScale(3))
        layout.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
        row.setLayout(layout)
        self.expressionsGroup.addWidget(row)

    def refreshCustomParams(self):
        while True:
            item = self.customLayout.takeAt(0)
            if not item:
                break
            else:
                destroyWidget(item.widget())
        de = xgg.DescriptionEditor
        params = xg.customAttrs(de.currentPalette(),
                                de.currentDescription(),
                                "ArchivePrimitive")
        for param in params:
            if not param.startswith( "archive__aColor[" ): # Skip aColor
                item = ExpressionUI(param,maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kCustomAttribute'  ] % param,
                                    "ArchivePrimitive",isColor=True)
                item.refresh()
                self.customLayout.addWidget(item)

    def addCustomAttr(self):
        if self.cattrName.text()=="":
            return
        de = xgg.DescriptionEditor
        pal = de.currentPalette()
        desc = de.currentDescription()
        count = xg.getAttr('aCount', pal, desc, 'ArchivePrimitive')
        attr = "archive__"+ str(self.cattrName.text())+"["+ str(count) +"]"        
        if( not xg.attrExists(attr, de.currentPalette(), de.currentDescription(), "ArchivePrimitive") ):
            xg.addCustomAttr(attr,
                             de.currentPalette(),
                             de.currentDescription(),
                             "ArchivePrimitive")
            # Check if the attr exist 
            baseAttrName = str(self.cattrName.text())
            if( xg.attrExists(baseAttrName,
                             de.currentPalette(),
                             de.currentDescription(),
                             "ArchivePrimitive") ):
                value = de.getAttr("ArchivePrimitive",baseAttrName)
                #TODO: get the real archive index instead of presuming it is 0 to range
                for index in range(0,  int(count)):
                    attr = "archive__"+ str(self.cattrName.text())+"["+ str(index) +"]" 
                    de.setAttr("ArchivePrimitive",attr, value )

        self.cattrName.setText("")
        self.refreshCustomParams()
        
    def remCustomAttr(self):
        if self.cattrName.text()=="":
            return
        de = xgg.DescriptionEditor
        pal = de.currentPalette()
        desc = de.currentDescription()            
        count = xg.getAttr('aCount', pal, desc, 'ArchivePrimitive')
        attr = "archive__"+ str(self.cattrName.text())+"["+ str(count) +"]"
        xg.remCustomAttr(attr,
                         de.currentPalette(),
                         de.currentDescription(),
                         "ArchivePrimitive")
        self.cattrName.setText("")
        self.refreshCustomParams()


    def refresh(self):
        PrimitiveTabUI.refresh(self)
        self.lengthExpr.refresh()
        self.widthExpr.refresh()
        self.depthExpr.refresh()
        self.offUExpr.refresh()
        self.offVExpr.refresh()
        self.twistExpr.refresh()
        self.offNExpr.refresh()
        self.aboutNExpr.refresh()
        self.frameExpr.refresh()
        self.archiveSize.refresh()
        self.files.refresh()
        self.hiIndex.refresh()
        self.lodRefresh(self.lodHiUpper,"lodHiUpper")
        self.lodRefresh(self.lodHiLower,"lodHiLower")
        self.medIndex.refresh()
        self.lodRefresh(self.lodMedUpper,"lodMedUpper")
        self.lodRefresh(self.lodMedLower,"lodMedLower")
        self.loIndex.refresh()
        self.lodRefresh(self.lodLoUpper,"lodLoUpper")
        self.lodRefresh(self.lodLoLower,"lodLoLower")
        self.proxyIndex.refresh()
        self.aIndexExpr.refresh()
        self.aLODExpr.refresh()
        self.refreshCustomParams()        

class SavePilFileUI(QDialog):
    """Function to save the contents of the files list as a pil file.

    This provides a simple dialog to accept the file name. The user can use
    a browser to search for the file.
    """
    def __init__(self):
        QDialog.__init__(self)
        self.setWindowTitle(maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kXgenSavePilFile'  ])
        self.setSizeGripEnabled(True)
        self.setMinimumWidth(DpiScale(50))
        layout = QVBoxLayout()
        self.fileName = BrowseUI("Pil File",
                                maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kPilFileAnn'  ],"",
                                "*.pil","out",maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kPilFile'  ])
        self.fileName.setValue("pil/archiveFiles.pil")
        layout.addWidget(self.fileName)
        row = QWidget()
        hbox = QHBoxLayout()
        QLayoutItem.setAlignment(hbox, QtCore.Qt.AlignRight)
        hbox.setSpacing(DpiScale(3))
        hbox.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
        self.saveButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kSaveFile'  ])
        self.saveButton.setFixedWidth(DpiScale(100))
        self.saveButton.setAutoRepeat(False)
        self.saveButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kSaveFileAnn'  ])
        self.connect(self.saveButton, QtCore.SIGNAL("clicked()"),
                    self.accept)
        hbox.addWidget(self.saveButton)
        self.cancelButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kCancel'  ])
        self.cancelButton.setFixedWidth(DpiScale(100))
        self.cancelButton.setAutoRepeat(False)
        self.cancelButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgArchivePrimitiveTab.kCancelSaveAnn'  ])
        self.connect(self.cancelButton, QtCore.SIGNAL("clicked()"),
                    self.reject)
        hbox.addWidget(self.cancelButton)
        row.setLayout(hbox)
        layout.addWidget(row)
        self.setLayout(layout)

    def getFileName(self):
        return str(self.fileName.value())
