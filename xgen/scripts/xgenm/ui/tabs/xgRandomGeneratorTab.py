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
# @file xgRandomGeneratorTab.py
# @brief Contains the UI for Random Generator tab
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
# @author Ying Liu
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
    import maya.cmds as cmds
from xgenm.ui.widgets import *
from xgenm.ui.util.xgProgressBar import setProgressInfo
from xgenm.ui.dialogs.xgPointsBase import *
from xgenm.ui.tabs.xgGeneratorTab import *
from xgenm.ui.util.xgUtil import DpiScale

class RandomGeneratorTabUI(GeneratorTabUI):
    def __init__(self):
        GeneratorTabUI.__init__(self,'Random',maya.stringTable[ u'y_xgenm_ui_tabs_xgRandomGeneratorTab.kRandom'  ])
        # Widgets
        self.baseTopUI()
        self.density = FloatUI("density",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgRandomGeneratorTab.kDensityAnn'  ],
             "RandomGenerator",0.000001,1000000.0, 0.01, 100, maya.stringTable[ u'y_xgenm_ui_tabs_xgRandomGeneratorTab.kDensity'  ] )
        self.layout().addWidget(self.density)
        self.maskExpr = ExpressionUI("mask",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgRandomGeneratorTab.kMaskAnn'  ],
             "RandomGenerator", maya.stringTable[ u'y_xgenm_ui_tabs_xgRandomGeneratorTab.kMask'  ])
        self.layout().addWidget(self.maskExpr)

        self.extraPointsBox = CheckBoxUI(maya.stringTable[ u'y_xgenm_ui_tabs_xgRandomGeneratorTab.kMorePrimitivesAt'  ],"usePoints",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgRandomGeneratorTab.kMorePrimitivesAtAnn'  ],
             "RandomGenerator")
        self.connect(self.extraPointsBox.boxValue[0],
                     QtCore.SIGNAL("clicked(bool)"),
                     lambda x: self.epUpdate())
        if ( xgg.Maya ):
            hbox = self.extraPointsBox.layout()
            hbox.addSpacing(DpiScale(5))
            self.editButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_tabs_xgRandomGeneratorTab.kSpecifyPoints'  ])
            #self.editButton.setFixedWidth(DpiScale(80))
            self.editButton.setAutoRepeat(False)
            self.editButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgRandomGeneratorTab.kSpecifyPointsAnn'  ])
            self.connect(self.editButton, QtCore.SIGNAL("clicked()"),self.editPoints)
            hbox.addWidget(self.editButton)
            filler = QWidget()
            hbox.addWidget(filler)
        self.layout().addWidget(self.extraPointsBox)
        
        self.scBox = CheckBoxUI(maya.stringTable[ u'y_xgenm_ui_tabs_xgRandomGeneratorTab.kCompensateForShapeStretching'  ],"scFlag",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgRandomGeneratorTab.kCompensateAnn'  ],
             "RandomGenerator")
        self.layout().addWidget(self.scBox)
        
        self.dcBox = CheckBoxUI(maya.stringTable[ u'y_xgenm_ui_tabs_xgRandomGeneratorTab.kCompensateForUnevenParameterization'  ],"dcFlag",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgRandomGeneratorTab.kCompensateUnevenAnn'  ],
             "RandomGenerator")
        self.connect(self.dcBox.boxValue[0],
                     QtCore.SIGNAL("clicked(bool)"),
                     lambda x: self.dcUpdate())
        self.layout().addWidget(self.dcBox)
        
        buttonBox = QWidget()
        buttonLayout = QHBoxLayout()
        buttonLayout.addSpacing(labelWidth())
        QLayoutItem.setAlignment(buttonLayout, QtCore.Qt.AlignLeft)
        buttonLayout.setSpacing(DpiScale(3))
        buttonLayout.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
        buttonBox.setLayout(buttonLayout)
        self.genButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_tabs_xgRandomGeneratorTab.kGenerate'  ])
        self.genButton.setAutoRepeat(False)
        self.genButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgRandomGeneratorTab.kGenerateAnn'  ])
        self.connect(self.genButton, QtCore.SIGNAL("clicked()"),
                     self.generateDC)
        buttonLayout.addWidget(self.genButton)
        self.layout().addWidget(buttonBox)

        self.dcUpdate()
        self.epUpdate()
        self.baseBottomUI()

        # connect to the grooming density
        if xgg.DescriptionEditor.brushTab:
            xgg.DescriptionEditor.brushTab.densityChanged.connect(self.onGroomingDensityChanged)

    def onGroomingDensityChanged(self, val ):
        # update the density with the grooming value
        self.density.setAttr(val)        
        
    def dcUpdate(self):
        value = self.dcBox.value(0)
        if value:
            self.genButton.setEnabled(True)
        else:
            self.genButton.setEnabled(False)

    def epUpdate(self):
        if ( xgg.Maya ):
            value = self.extraPointsBox.value()
            if value:
                self.editButton.setEnabled(True)
            else:
                self.editButton.setEnabled(False)

    def generateDC(self):
        de = xgg.DescriptionEditor
        setProgressInfo(maya.stringTable[ u'y_xgenm_ui_tabs_xgRandomGeneratorTab.kCalculatingDensityCompensationMaps'  ])
        cmd = 'xgmDensityComp -f -pb {"'+de.currentDescription()+'"}'
        mel.eval(cmd)
        
    def editPoints(self):
        dialog = EditExtraPointsUI()
        dialog.show() # Using show() to get a non modal dialog to allow the edit point context tool to interact with the viewport.

    def refresh(self):
        GeneratorTabUI.refresh(self)
        self.density.refresh()
        self.maskExpr.refresh()
        self.scBox.refresh()
        self.dcBox.refresh()
        self.extraPointsBox.refresh()
        self.dcUpdate()
        self.epUpdate()
        

class EditExtraPointsUI(PointsBaseUI):
    """A dialog to control editing of extra points for the Random Generator.

    This provides fields for editing the xuv point directory and buttons
    to control loading, clearing, saving, and canceling the process. Actual
    editing of the points is done via the xgmPointsContext brush.
    """
    def __init__(self):
        PointsBaseUI.__init__(self,maya.stringTable[ u'y_xgenm_ui_tabs_xgRandomGeneratorTab.kSpecifyPointsTool'  ])
        
        self.toolDescription=QLabel(maya.stringTable[ u'y_xgenm_ui_tabs_xgRandomGeneratorTab.kToolDescription'  ])
        
        self.layout().addWidget(self.toolDescription)
        self.layout().addSpacing(DpiScale(5))

        self.pointDirUI(self.layout(),
                        "pointDir",
                        maya.stringTable[ u'y_xgenm_ui_tabs_xgRandomGeneratorTab.kPointDirAnn'  ],
                        "RandomGenerator",
                        maya.stringTable[ u'y_xgenm_ui_tabs_xgRandomGeneratorTab.kPointFileFolder'  ])
        

        self.ptLengthUI(self.layout(),
                        "RandomGenerator")

        self.layout().addSpacing(DpiScale(5))
        ptButtonBox = QWidget()
        ptButtonLayout = QHBoxLayout()
        QLayoutItem.setAlignment(ptButtonLayout, QtCore.Qt.AlignRight)
        ptButtonLayout.setSpacing(DpiScale(10))
        ptButtonLayout.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
        ptButtonBox.setLayout(ptButtonLayout)
        ptLoadButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_tabs_xgRandomGeneratorTab.kLoad'  ])
        ptLoadButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgRandomGeneratorTab.kRevertToLastSavedAnn'  ])
        ptLoadButton.setAutoDefault(False)
        ptLoadButton.setDefault(False)
        ptButtonLayout.addWidget(ptLoadButton)
        ptClrButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_tabs_xgRandomGeneratorTab.kClear'  ])
        ptClrButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgRandomGeneratorTab.kClearAnn'  ])
        ptClrButton.setAutoDefault(False)
        ptClrButton.setDefault(False)
        ptButtonLayout.addWidget(ptClrButton)
        ptSaveButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_tabs_xgRandomGeneratorTab.kSave'  ])
        ptSaveButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgRandomGeneratorTab.kSaveNCloseAnn'  ])
        ptSaveButton.setAutoDefault(False)
        ptSaveButton.setDefault(False)
        ptButtonLayout.addWidget(ptSaveButton)
        ptCancelButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_tabs_xgRandomGeneratorTab.kCancel'  ])
        ptCancelButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgRandomGeneratorTab.kCloseAnn'  ])
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
