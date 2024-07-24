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
# @file xgNoiseFXModuleTab.py
# @brief Contains the Noise FX Module UI.
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
# @version Created 06/22/09
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


class NoiseFXModuleTabUI(FXModuleTabUI):
    def __init__(self,name):
        FXModuleTabUI.__init__(self,name,maya.stringTable[ u'y_xgenm_ui_fxmodules_xgNoiseFXModuleTab.kNoiseModifier'  ])
        # Widgets
        self.baseTopUI()

        self.frequency = ExpressionUI("frequency",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgNoiseFXModuleTab.kFrequencyAnn'  ],
             self.name,
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgNoiseFXModuleTab.kFrequency'  ])
        self.layout().addWidget(self.frequency)
        
        self.magnitude = ExpressionUI("magnitude",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgNoiseFXModuleTab.kMagnitudeAnn'  ],
             self.name,
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgNoiseFXModuleTab.kMagnitude'  ])
        self.layout().addWidget(self.magnitude)

        self.magScale = RampUI("magnitudeScale",
                           maya.stringTable[ u'y_xgenm_ui_fxmodules_xgNoiseFXModuleTab.kMagnitudeScaleAnn'  ],
                           self.name,
                           maya.stringTable[ u'y_xgenm_ui_fxmodules_xgNoiseFXModuleTab.kMagnitudeScale'  ])
        self.layout().addWidget(self.magScale)
        
        self.correlation = ExpressionUI("correlation",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgNoiseFXModuleTab.kCorrelationAnn'  ],
             self.name,
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgNoiseFXModuleTab.kCorrelation'  ])
        self.layout().addWidget(self.correlation)
        
        self.plength = ExpressionUI("preserveLength",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgNoiseFXModuleTab.kPreserveLengthAnn'  ],
             self.name,
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgNoiseFXModuleTab.kPreserveLength'  ])
        self.layout().addWidget(self.plength)

        self.modeExpand = ExpandUI(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgNoiseFXModuleTab.kBakeOptions'  ], False)
        self.layout().addWidget(self.modeExpand)

        self.mode = RadioUI("mode",
             [maya.stringTable[ u'y_xgenm_ui_fxmodules_xgNoiseFXModuleTab.kLive'  ], 
              maya.stringTable[ u'y_xgenm_ui_fxmodules_xgNoiseFXModuleTab.kBaked'  ]],
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgNoiseFXModuleTab.kModeAnn'  ],
             self.name,
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgNoiseFXModuleTab.kMode'  ])
        self.modeExpand.addWidget(self.mode)

        self.bakeDir = BrowseUI("bakeDir",
                                maya.stringTable[ u'y_xgenm_ui_fxmodules_xgNoiseFXModuleTab.kBakeDirAnn'  ],
                                self.name,"","in",
                                maya.stringTable[ u'y_xgenm_ui_fxmodules_xgNoiseFXModuleTab.kBakeDir'  ])
        self.modeExpand.addWidget(self.bakeDir)
        
        if ( xgg.Maya ):
            buttonBox = QWidget()
            buttonLayout = QHBoxLayout()
            QLayoutItem.setAlignment(buttonLayout, QtCore.Qt.AlignRight)
            buttonLayout.setSpacing(DpiScale(3))
            buttonLayout.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
            buttonBox.setLayout(buttonLayout)
            bakeButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgNoiseFXModuleTab.kBakeNoiseData'  ])
            buttonLayout.addWidget(bakeButton)
            self.modeExpand.addWidget(buttonBox)
            self.connect(bakeButton, QtCore.SIGNAL("clicked()"),
                         self.bakeSlot)

        # Fix for the expanding ramp ui
        filler = QWidget()
        self.layout().addWidget(filler)
        self.layout().setStretchFactor(filler,100)
        
    def bakeSlot(self):
        de = xgg.DescriptionEditor
        # temporarily turn off lod so we dont bake it in
        lod = de.getAttr("Description","lodFlag")
        de.setAttr("Description","lodFlag","False")
        # change mode to bake
        state = de.getAttr(self.name,"mode")
        de.setAttr(self.name,"mode","2")
        # bake the noise
        setProgressInfo(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgNoiseFXModuleTab.kBakingProgress'  ])
        cmd = 'xgmNullRender -pb "'+de.currentDescription()+'"'
        mel.eval(cmd)
        # restore everything
        de.setAttr(self.name,"mode",state)
        de.setAttr("Description","lodFlag",lod)

    def refresh(self):
        FXModuleTabUI.refresh(self)
        self.frequency.refresh()
        self.magnitude.refresh()
        self.magScale.refresh()
        self.correlation.refresh()
        self.plength.refresh()
        self.mode.refresh()
        self.bakeDir.refresh()
