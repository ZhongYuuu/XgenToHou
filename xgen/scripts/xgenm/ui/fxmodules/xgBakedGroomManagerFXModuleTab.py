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
# @file xgBakedGroomManagerFXModuleTab.py
# @brief Contains the BakedGroomManager FX Module UI.
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
from xgenm.ui.widgets import *
from xgenm.ui.fxmodules.xgFXModuleTab import *
from xgenm.ui.util.xgProgressBar import setProgressInfo
from xgenm.ui.util.xgUtil import DpiScale


class BakedGroomManagerFXModuleTabUI(FXModuleTabUI):
    def __init__(self,name):
        FXModuleTabUI.__init__(self,name,maya.stringTable[ u'y_xgenm_ui_fxmodules_xgBakedGroomManagerFXModuleTab.kGroomBakeModifier'  ])
        # Widgets
        self.baseTopUI()
        self.maskExpr.hide()

        self.bakeDir = BrowseUI("bakeDir",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgBakedGroomManagerFXModuleTab.kBakeDirAnn'  ],
             self.name,"","in",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgBakedGroomManagerFXModuleTab.kBakeDir'  ])
        self.layout().addWidget(self.bakeDir)

        if ( xgg.Maya ):
            self.layout().addSpacing(DpiScale(10))
            buttonBox = QWidget()
            buttonLayout = QHBoxLayout()
            QLayoutItem.setAlignment(buttonLayout, QtCore.Qt.AlignRight)
            buttonLayout.setSpacing(DpiScale(3))
            buttonLayout.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
            buttonBox.setLayout(buttonLayout)
            self.bakeButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgBakedGroomManagerFXModuleTab.kBakeXpdGroom'  ])
            self.bakeButton.setFixedWidth(DpiScale(120))
            buttonLayout.addWidget(self.bakeButton)
            self.layout().addWidget(buttonBox)
            self.connect(self.bakeButton, QtCore.SIGNAL("clicked()"),
                         self.bakeSlot)
        self.activeUpdate()

    def activeUpdate(self):
        isActive = xg.stringToBool( xgg.DescriptionEditor.getAttr(self.name,"active") )
        if isActive:
            self.bakeDir.setEnabled(True)
            #de = xgg.DescriptionEditor
            #de.generatorTab.setEnabled(False)
            if ( xgg.Maya ):
                self.bakeButton.setEnabled(True)
        else:
            self.bakeDir.setEnabled(False)
            #de = xgg.DescriptionEditor
            #de.generatorTab.setEnabled(True)
            if ( xgg.Maya ):
                self.bakeButton.setEnabled(False)
        
    def bakeSlot(self):
        de = xgg.DescriptionEditor
        setProgressInfo(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgBakedGroomManagerFXModuleTab.kBakingPrimitivesIntoXpdFilesProgress'  ])
        xg.bakedGroomManagerBake(de.currentPalette(),
                                 de.currentDescription(), True)
        
    def refresh(self):
        FXModuleTabUI.refresh(self)
        self.bakeDir.refresh()
        self.activeUpdate()
