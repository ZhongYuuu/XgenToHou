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
# @file xgMeshCutFXModuleTab.py
# @brief Contains the MeshCut FX Module UI.
#
# <b>CONFIDENTIAL INFORMATION: This software is the confidential and
# proprietary information of Walt Disney Animation Studios ("WDAS").
# This software may not be used, disclosed, reproduced or distributed
# for any purpose without prior written authorization and license
# from WDAS. Reproduction of any section of this software must include
# this legend and all copyright notices.
# Copyright Disney Enterprises, Inc. All rights reserved.</b>
#
# @author Arthur Shek
# @author Thomas V Thompson II
#
# @version Created 06/26/09
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
from xgenm.ui.fxmodules.xgFXModuleTab import *
from xgenm.ui.util.xgProgressBar import setProgressInfo
from xgenm.ui.util.xgUtil import DpiScale


class MeshCutFXModuleTabUI(FXModuleTabUI):
    def __init__(self,name):
        FXModuleTabUI.__init__(self,name,maya.stringTable[ u'y_xgenm_ui_fxmodules_xgMeshCutFXModuleTab.kMeshCutModifier'  ])
        # Widgets
        self.baseTopUI()
        
        self.meshFile = BrowseUI("meshFile",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgMeshCutFXModuleTab.kMeshFileAnn'  ],
             self.name,"*.caf *.abc","in",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgMeshCutFXModuleTab.kMeshFile'  ])
        self.layout().addWidget(self.meshFile)
        
        self.testsPerPrim = IntegerUI("testsPerPrim",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgMeshCutFXModuleTab.kTestsPerPrimAnn'  ],
             self.name,-1e7,1e7,
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgMeshCutFXModuleTab.kTestsPerPrim'  ])
        self.layout().addWidget(self.testsPerPrim)

        self.offset = ExpressionUI("offset",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgMeshCutFXModuleTab.kOffsetAnn'  ],
             self.name,
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgMeshCutFXModuleTab.kOffset'  ])
        self.layout().addWidget(self.offset)

        self.cutType = RadioUI("cutType",
                               [maya.stringTable[ u'y_xgenm_ui_fxmodules_xgMeshCutFXModuleTab.kKeepParam'  ],
                                maya.stringTable[ u'y_xgenm_ui_fxmodules_xgMeshCutFXModuleTab.kReparam'  ],
                                maya.stringTable[ u'y_xgenm_ui_fxmodules_xgMeshCutFXModuleTab.kCull'  ]],
                               maya.stringTable[ u'y_xgenm_ui_fxmodules_xgMeshCutFXModuleTab.kCutTypeAnn'  ],
                               self.name,
                               maya.stringTable[ u'y_xgenm_ui_fxmodules_xgMeshCutFXModuleTab.kCutType'  ])
        self.layout().addWidget(self.cutType)
        
        self.modeExpand = ExpandUI(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgMeshCutFXModuleTab.kBakeOptions'  ], False)
        self.layout().addWidget(self.modeExpand)

        self.mode = RadioUI("mode",
             [maya.stringTable[ u'y_xgenm_ui_fxmodules_xgMeshCutFXModuleTab.kLiveCut'  ],
              maya.stringTable[ u'y_xgenm_ui_fxmodules_xgMeshCutFXModuleTab.kUseBakedCut'  ]],
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgMeshCutFXModuleTab.kModeAnn'  ],
             self.name,
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgMeshCutFXModuleTab.kMode'  ])
        self.modeExpand.addWidget(self.mode)

        self.bakeDir = BrowseUI("bakeDir",
                                maya.stringTable[ u'y_xgenm_ui_fxmodules_xgMeshCutFXModuleTab.kBakeDirAnn'  ],
                                self.name,"","in",
                                maya.stringTable[ u'y_xgenm_ui_fxmodules_xgMeshCutFXModuleTab.kBakeDir'  ])
        self.modeExpand.addWidget(self.bakeDir)
        
        if ( xgg.Maya ):
            buttonBox = QWidget()
            buttonLayout = QHBoxLayout()
            QLayoutItem.setAlignment(buttonLayout, QtCore.Qt.AlignRight)
            buttonLayout.setSpacing(DpiScale(3))
            buttonLayout.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
            buttonBox.setLayout(buttonLayout)
            bakeButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgMeshCutFXModuleTab.kBakeCutData'  ])
            buttonLayout.addWidget(bakeButton)
            self.modeExpand.addWidget(buttonBox)
            self.connect(bakeButton, QtCore.SIGNAL("clicked()"),
                         self.bakeSlot)

    def bakeSlot(self):
        de = xgg.DescriptionEditor
        # temporarily turn off lod so we dont bake it in
        lod = de.getAttr("Description","lodFlag")
        de.setAttr("Description","lodFlag","False")
        # change mode to bake
        state = de.getAttr(self.name,"mode")
        de.setAttr(self.name,"mode","2")
        # bake the cut
        setProgressInfo(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgMeshCutFXModuleTab.kBakingPrimProgress'  ])
        cmd = 'xgmNullRender -pb "'+de.currentDescription()+'"'
        mel.eval(cmd)
        # restore everything
        de.setAttr(self.name,"mode",state)
        de.setAttr("Description","lodFlag",lod)

    def refresh(self):
        FXModuleTabUI.refresh(self)
        self.meshFile.refresh()
        self.testsPerPrim.refresh()
        self.offset.refresh()
        self.cutType.refresh()
        self.mode.refresh()
        self.bakeDir.refresh()
