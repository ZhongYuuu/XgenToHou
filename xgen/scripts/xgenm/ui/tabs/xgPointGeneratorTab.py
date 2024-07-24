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
# @file xgPointGeneratorTab.py
# @brief Contains the UI for Point Generator tab
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
from xgenm.ui.widgets import *
from xgenm.ui.dialogs.xgPointsBase import *
from xgenm.ui.tabs.xgGeneratorTab import *
from xgenm.ui.util.xgUtil import DpiScale


class PointGeneratorTabUI(GeneratorTabUI):
    def __init__(self):
        GeneratorTabUI.__init__(self,'Point',maya.stringTable[ u'y_xgenm_ui_tabs_xgPointGeneratorTab.kPoint'  ])
        # Widgets
        self.baseTopUI()
        if ( xgg.Maya ):
            row = QWidget()
            hbox = QHBoxLayout()
            QLayoutItem.setAlignment(hbox, QtCore.Qt.AlignLeft)
            hbox.setSpacing(DpiScale(3))
            hbox.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
            label = QLabel(maya.stringTable[ u'y_xgenm_ui_tabs_xgPointGeneratorTab.kPrimitiveLocations'  ])
            label.setFixedWidth(labelWidth())
            label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
            label.setIndent(DpiScale(10))
            hbox.addWidget(label)
            self.editButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_tabs_xgPointGeneratorTab.kEdit'  ])
            self.editButton.setAutoRepeat(False)
            self.editButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgPointGeneratorTab.kEditAnn'  ])
            self.connect(self.editButton, QtCore.SIGNAL("clicked()"),
                         self.editPoints)
            hbox.addWidget(self.editButton)
            filler = QWidget()
            hbox.addWidget(filler)
            row.setLayout(hbox)
            self.layout().addWidget(row)
        else:
            self.pointDir = BrowseUI("pointDir",
                                     maya.stringTable[ u'y_xgenm_ui_tabs_xgPointGeneratorTab.kPointDirAnn'  ],
                                     "PointGenerator","","in",maya.stringTable[ u'y_xgenm_ui_tabs_xgPointGeneratorTab.kPointFileFolder'  ])
            self.layout().addWidget(self.pointDir)
        self.baseBottomUI()
        self.editPointDialog = None
        
    def editPoints(self):
        if self.editPointDialog == None:
            self.editPointDialog = EditPointsUI()
            self.editPointDialog.show() # Using show() to get a non modal dialog to allow the edit point context tool to interact with the viewport.

            self.editPointDialog.finished.connect(self.editPointDialogClosed)
        
    def editPointDialogClosed(self,result):
        self.editPointDialog = None

    def refresh(self):
        GeneratorTabUI.refresh(self)
        if ( not xgg.Maya ):
            self.pointDir.refresh()


class EditPointsUI(PointsBaseUI):
    """A dialog to control editing of points for the Point Generator.

    This provides fields for editing the xuv point directory and buttons
    to control loading, clearing, saving, and canceling the process. Actual
    editing of the points is done via the xgmPointsContext brush.
    """
    def __init__(self):
        PointsBaseUI.__init__(self,maya.stringTable[ u'y_xgenm_ui_tabs_xgPointGeneratorTab.kEditExtraPoints'  ])


        self.toolDescription=QLabel(maya.stringTable[ u'y_xgenm_ui_tabs_xgPointGeneratorTab.kToolDescription'  ])
        self.layout().addWidget(self.toolDescription)
        self.layout().addSpacing(DpiScale(5))

        self.pointDirUI(self.layout(),
                        "pointDir",
                        maya.stringTable[ u'y_xgenm_ui_tabs_xgPointGeneratorTab.kPointDirAnn2'  ],
                        "PointGenerator",
                        maya.stringTable[ u'y_xgenm_ui_tabs_xgPointGeneratorTab.kPrimitiveLocations2'  ])

        self.ptLengthUI(self.layout(),
                        "PointGenerator")

        self.layout().addSpacing(DpiScale(5))
        ptButtonBox = QWidget()
        ptButtonLayout = QHBoxLayout()
        QLayoutItem.setAlignment(ptButtonLayout, QtCore.Qt.AlignRight)
        ptButtonLayout.setSpacing(DpiScale(10))
        ptButtonLayout.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
        ptButtonBox.setLayout(ptButtonLayout)
        ptLoadButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_tabs_xgPointGeneratorTab.kLoad'  ])
        ptLoadButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgPointGeneratorTab.kRevertToLastSavedAnn'  ])
        ptLoadButton.setAutoDefault(False)
        ptLoadButton.setDefault(False)
        ptButtonLayout.addWidget(ptLoadButton)
        ptClrButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_tabs_xgPointGeneratorTab.kClear'  ])
        ptClrButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgPointGeneratorTab.kClearAnn'  ])
        ptClrButton.setAutoDefault(False)
        ptClrButton.setDefault(False)
        ptButtonLayout.addWidget(ptClrButton)
        ptSaveButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_tabs_xgPointGeneratorTab.kSave'  ])
        ptSaveButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgPointGeneratorTab.kSaveNCloseAnn'  ])
        ptSaveButton.setAutoDefault(False)
        ptSaveButton.setDefault(False)
        ptButtonLayout.addWidget(ptSaveButton)
        ptCancelButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_tabs_xgPointGeneratorTab.kCancel'  ])
        ptCancelButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgPointGeneratorTab.kCloseAnn'  ])
        ptCancelButton.setAutoDefault(False)
        ptCancelButton.setDefault(False)
        ptButtonLayout.addWidget(ptCancelButton)
        self.layout().addWidget(ptButtonBox)
        self.connect(ptLoadButton, QtCore.SIGNAL("clicked()"),
                     self.loadPoints)
        self.connect(ptClrButton, QtCore.SIGNAL("clicked()"),
                     self.clearPoints)
        self.connect(ptSaveButton, QtCore.SIGNAL("clicked()"),
                     self.savePointsandClose)
        self.connect(ptCancelButton, QtCore.SIGNAL("clicked()"),
                     self.close)

        self.initDialog()
