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
# @file xgPreviewerTab.py
# @brief Contains the UI for Previewer tab
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
# @version Created 04/08/09
#

import string
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *
import xgenm as xg
import xgenm.xgGlobal as xgg
from xgenm.ui.util.xgUtil import *
from xgenm.ui.widgets import *


class PreviewerTabUI(QWidget):
    def __init__(self,selfType):
        QWidget.__init__(self)
        self.type = selfType
        # A single VBox layout provides control over the tab.
        layout = QVBoxLayout()
        QLayoutItem.setAlignment(layout, QtCore.Qt.AlignTop)
        layout.setSpacing(DpiScale(0))
        layout.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))
        self.setLayout(layout)

    def baseTopUI(self):
        self.startPercent = FloatUI("startPercent",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgPreviewerTab.kStartPercentAnn' ],
             self.type+"Renderer", 0.0, 100.0,-1000,1000,maya.stringTable[ u'y_xgenm_ui_tabs_xgPreviewerTab.kStartPercent'  ])
        self.layout().addWidget( self.startPercent )

        self.percent = FloatUI("percent",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgPreviewerTab.kPercentAnn'  ],
             self.type+"Renderer", 0.0, 100.0,-1000,1000,maya.stringTable[ u'y_xgenm_ui_tabs_xgPreviewerTab.kPercent'  ])
        self.layout().addWidget(self.percent)
 
    def refresh(self):
        self.startPercent.refresh()
        self.percent.refresh()

