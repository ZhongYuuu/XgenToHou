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
# @file xgPlaneForceFXModuleTab.py
# @brief Contains the Plane Force FX Module UI.
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


class PlaneForceFXModuleTabUI(FXModuleTabUI):
    def __init__(self,name):
        FXModuleTabUI.__init__(self,name,maya.stringTable[ u'y_xgenm_ui_fxmodules_xgPlaneForceFXModuleTab.kPlaneForceModifier'  ])
        # Widgets
        self.baseTopUI()

        self.point1 = ExpressionUI("point1",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgPlaneForceFXModuleTab.kPointOneAnn'  ],
             self.name,
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgPlaneForceFXModuleTab.kPoint1'  ])
        self.layout().addWidget(self.point1)
                        
        self.point2 = ExpressionUI("point2",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgPlaneForceFXModuleTab.kPointTwoAnn'  ],
             self.name,
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgPlaneForceFXModuleTab.kPoint2'  ])
        self.layout().addWidget(self.point2)

        self.point3 = ExpressionUI("point3",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgPlaneForceFXModuleTab.kPointThreeAnn'  ],
             self.name,
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgPlaneForceFXModuleTab.kPoint3'  ])
        self.layout().addWidget(self.point3)

        self.point4 = ExpressionUI("point4",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgPlaneForceFXModuleTab.kPointFourAnn'  ],
             self.name,
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgPlaneForceFXModuleTab.kPoint4'  ])
        self.layout().addWidget(self.point4)

        self.depth = ExpressionUI("depth",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgPlaneForceFXModuleTab.kDepthAnn'  ],
             self.name,
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgPlaneForceFXModuleTab.kDepth'  ])
        self.layout().addWidget(self.depth)

        self.magnitude = ExpressionUI("magnitude",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgPlaneForceFXModuleTab.kMagnitudeAnn'  ],
             self.name,
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgPlaneForceFXModuleTab.kMagnitude'  ])
        self.layout().addWidget(self.magnitude)

        self.falloff = ExpressionUI("falloff",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgPlaneForceFXModuleTab.kFalloffAnn'  ],
             self.name,
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgPlaneForceFXModuleTab.kFalloff'  ])
        self.layout().addWidget(self.falloff)

    def refresh(self):
        FXModuleTabUI.refresh(self)
        self.point1.refresh()
        self.point2.refresh()
        self.point3.refresh()
        self.point4.refresh()
        self.depth.refresh()
        self.magnitude.refresh()
        self.falloff.refresh()
