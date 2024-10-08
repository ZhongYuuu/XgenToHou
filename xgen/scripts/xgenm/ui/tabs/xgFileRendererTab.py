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
# @file xgFileRendererTab.py
# @brief Contains the UI for File Renderer tab
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

import string
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *
import xgenm as xg
import xgenm.xgGlobal as xgg
if xgg.Maya:
    import maya.mel as mel
from xgenm.ui.widgets import *
from xgenm.ui.tabs.xgRendererTab import *
from xgenm.ui.util.xgProgressBar import setProgressInfo
from xgenm.ui.util.xgUtil import DpiScale


class FileRendererTabUI(RendererTabUI):
    def __init__(self):
        RendererTabUI.__init__(self,'File')
        # Widgets
        self.baseTopUI()
        self.outputDir = BrowseUI("outputDir",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgFileRendererTab.kOutputDirAnn'  ],
             "FileRenderer","","out", maya.stringTable[ u'y_xgenm_ui_tabs_xgFileRendererTab.kOutputDir'  ])
        self.layout().addWidget(self.outputDir)

        if ( xgg.Maya ):
            self.layout().addSpacing(DpiScale(10))
            row = QWidget()
            hbox = QHBoxLayout()
            QLayoutItem.setAlignment(hbox, QtCore.Qt.AlignLeft)
            hbox.setSpacing(DpiScale(3))
            hbox.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))
            hbox.addSpacing(labelWidth()+DpiScale(3))
            self.p3dButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_tabs_xgFileRendererTab.kCreateXpdFile'  ])
            self.p3dButton.setFixedWidth(DpiScale(160))
            self.p3dButton.setAutoRepeat(False)
            self.p3dButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgFileRendererTab.kCreateXPDFileAnn'  ])
            self.connect(self.p3dButton, QtCore.SIGNAL("clicked()"), self.p3dExport)
            hbox.addWidget(self.p3dButton)
            row.setLayout(hbox)
            self.layout().addWidget(row)
        
    def p3dExport(self):
        de = xgg.DescriptionEditor
        desc = de.currentDescription()
        setProgressInfo(maya.stringTable[ u'y_xgenm_ui_tabs_xgFileRendererTab.kXPDProgressInfo'  ])
        cmd = 'xgmFileRender -pb -object {"'+desc+'"}'
        results = mel.eval(cmd)
        print(maya.stringTable[ u'y_xgenm_ui_tabs_xgFileRendererTab.kTheFollowingFilesWereRendered'  ])
        for result in results:
            print("  - ", result)

    def rangeExport(self):
        print(maya.stringTable[ u'y_xgenm_ui_tabs_xgFileRendererTab.kFrameRangeRenderNotYetSupported'  ])
        pass
    
    def refresh(self):
        RendererTabUI.refresh(self)
        self.outputDir.refresh()

