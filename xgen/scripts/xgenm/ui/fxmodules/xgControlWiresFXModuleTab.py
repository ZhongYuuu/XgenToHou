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
# @file xgControlWiresFXModuleTab.py
# @brief Contains the ControlWires FX Module UI.
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
# @author Ying Liu
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
    import maya.cmds as cmds
from xgenm.ui.widgets import *
from xgenm.ui.fxmodules.xgFXModuleTab import *
from xgenm.ui.util.xgUtil import DpiScale


class ControlWiresFXModuleTabUI(FXModuleTabUI):
    def __init__(self,name):
        FXModuleTabUI.__init__(self,name,maya.stringTable[ u'y_xgenm_ui_fxmodules_xgControlWiresFXModuleTab.kControlWiresModifier'  ])
        # Widgets
        self.baseTopUI()
        
        self.magnitude = ExpressionUI("magnitude",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgControlWiresFXModuleTab.kMagnitudeAnn'  ],
             self.name,
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgControlWiresFXModuleTab.kMagnitude'  ])
        self.layout().addWidget(self.magnitude)

        self.magScale = RampUI("magnitudeScale",
                           maya.stringTable[ u'y_xgenm_ui_fxmodules_xgControlWiresFXModuleTab.kMagnitudeScaleAnn'  ],
                           self.name,
                           maya.stringTable[ u'y_xgenm_ui_fxmodules_xgControlWiresFXModuleTab.kMagnitudeScale'  ])
        self.layout().addWidget(self.magScale)                
        
        self.smoothness = ExpressionUI("smoothness",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgControlWiresFXModuleTab.kSmoothnessAnn'  ],
             self.name,
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgControlWiresFXModuleTab.kSmoothness'  ])
        self.layout().addWidget(self.smoothness)
        
        self.breakage = ExpressionUI("breakage",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgControlWiresFXModuleTab.kBreakageAnn'  ],
             self.name,
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgControlWiresFXModuleTab.kBreakage'  ])
        self.layout().addWidget(self.breakage)

        #***********************************#
        group = QGroupBox(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgControlWiresFXModuleTab.kMode'  ])
        group.setAlignment(QtCore.Qt.AlignLeft)
        groupFont = group.font()
        groupFont.setBold(True)
        group.setFont(groupFont)        
        layout = QVBoxLayout()

        self.liveMode = CheckBoxUI(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgControlWiresFXModuleTab.kLiveMode'  ], "liveMode",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgControlWiresFXModuleTab.kLiveModeAnn'  ], 
             self.name)
        layout.addWidget(self.liveMode)
        self.connect(self.liveMode.boxValue[0], QtCore.SIGNAL("clicked(bool)"),
                     lambda x: self.liveModeUpdate())

        self.wiresFile = BrowseUI("wiresFile",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgControlWiresFXModuleTab.kWiresFileAnn'  ],
             self.name,"*.caf *.abc","in",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgControlWiresFXModuleTab.kWiresFile'  ])
        layout.addWidget(self.wiresFile)

        self.refWiresFrame = IntegerUI("refWiresFrame",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgControlWiresFXModuleTab.kRefWiresFrameAnn'  ],
             self.name,-1e7,1e7,
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgControlWiresFXModuleTab.kRefWiresFrame'  ])
        layout.addWidget(self.refWiresFrame)

        group.setLayout(layout)
        self.layout().addWidget(group)
        self.layout().addSpacing(DpiScale(10))
        #***********************************#
        if ( xgg.Maya ):
            self.layout().addSpacing(DpiScale(10))
            buttonBox = QWidget()
            buttonLayout = QHBoxLayout()
            QLayoutItem.setAlignment(buttonLayout, QtCore.Qt.AlignRight)
            buttonLayout.setSpacing(DpiScale(3))
            buttonLayout.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
            buttonBox.setLayout(buttonLayout)
            attachButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgControlWiresFXModuleTab.kAttachHairSystem'  ])
            attachButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgControlWiresFXModuleTab.kHairSystemAnn'  ])        
            attachButton.setFixedWidth(DpiScale(145))
            buttonLayout.addWidget(attachButton)
            self.layout().addWidget(buttonBox)
            self.connect(attachButton, QtCore.SIGNAL("clicked()"),
                         self.attachSlot)

        # Fix for the expanding ramp ui
        filler = QWidget()
        self.layout().addWidget(filler)
        self.layout().setStretchFactor(filler,100)


    def liveModeUpdate(self):
        value = self.liveMode.value()
        if value:
            self.wiresFile.setEnabled(False)
        else:
            self.wiresFile.setEnabled(True)

    def attachSlot(self):
        de = xgg.DescriptionEditor
        cmd = 'xgmFindAttachment'
        cmd += ' -description "'+de.currentDescription()+'"'
        if de.getAttr(self.name,"liveMode") == "false":  
            cmd += ' -file "'+de.getAttr(self.name,"wiresFile")+'"'
            cmd += ' -frame '+de.getAttr(self.name,"refWiresFrame")
            cmd += ' -module "'+self.name+'"'
            mel.eval(cmd)
        else:
            sel = cmds.ls(sl=True,ni=True,dag=True,type='nurbsCurve')
            if not sel:                        
                mel.eval("xgmSelectCurvesFromHairSystem")
            
            sel = cmds.ls(sl=True,ni=True,dag=True,type='nurbsCurve')
            if sel:                        
                cmd += ' -frame '+de.getAttr(self.name,"refWiresFrame")
                cmd += ' -module "'+self.name+'"'
                mel.eval(cmd)
                print(maya.stringTable[u'y_xgenm_ui_fxmodules_xgControlWiresFXModuleTab.kControlWiresCurvesAttached' ], sel)            
            else:
                warn = QMessageBox()
                warn.setText(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgControlWiresFXModuleTab.kNoCurvesSelectedNothingToAttach'  ])
                warn.exec_()            

        
    def refresh(self):
        FXModuleTabUI.refresh(self)
        self.magnitude.refresh()
        self.wiresFile.refresh()
        self.refWiresFrame.refresh()
        self.smoothness.refresh()
        self.breakage.refresh()
        self.magScale.refresh()
        self.liveMode.refresh()        
        self.liveModeUpdate()        
