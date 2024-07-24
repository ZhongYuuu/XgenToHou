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
# @file xgSplinePrimitiveTab.py
# @brief Contains the UI for Spline Primitive tab
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
from xgenm.ui.tabs.xgPrimitiveTab import *
from xgenm.ui.dialogs.xgTubeGroom import *
from xgenm.ui.util.xgUtil import DpiScale


class SplinePrimitiveTabUI(PrimitiveTabUI):
    def __init__(self):
        PrimitiveTabUI.__init__(self,'Spline',maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kSpline'  ])
        # Widgets
        self.baseTopUI()
        # Dont pass the object for attCVCount to avoid the auto-connect
        self.attrCount = IntegerUI("Attr CV Count",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kAttrCVCountAnn'  ],
             "",3,99,maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kAttrCvCount'  ])
        self.attrCount.object = "SplinePrimitive"
        self.attrCount.intValue.connect(self.attrCount.intValue,
                                        QtCore.SIGNAL("editingFinished()"),
                                        self.attrCVChange)
        self.layout().addWidget(self.attrCount)
        self.fxCount = IntegerUI("fxCVCount",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kFxCountAnn'  ],
             "SplinePrimitive",3,1e7,maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kFxCvCount'  ])
        self.layout().addWidget(self.fxCount)
        self.uniformCV = CheckBoxUI(maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kUniformCvs'  ], "uniformCVs",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kUniformCvsAnn'  ],
             "SplinePrimitive")
        self.layout().addWidget(self.uniformCV)
        self.lengthExpr = ExpressionUI("length",maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kLengthAnn'  ]
            ,"SplinePrimitive",maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kLength'  ])
        self.layout().addWidget(self.lengthExpr)
        self.widthExpr = ExpressionUI("width",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kWidthAnn'  ],
             "SplinePrimitive",maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kWidth'  ])
        self.layout().addWidget(self.widthExpr)
        self.widthRamp = RampUI("widthRamp",
            maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kWidthRampAnn'  ],
            "SplinePrimitive",maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kWidthRamp'  ])
        self.layout().addWidget(self.widthRamp)
        self.taperExpr = ExpressionUI("taper",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kTaperANn'  ],
             "SplinePrimitive",maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kTaper'  ])
        self.layout().addWidget(self.taperExpr)
        self.taperStartExpr = ExpressionUI("taperStart",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kTaperStartAnn'  ],
             "SplinePrimitive",maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kTaperStart'  ])
        self.layout().addWidget(self.taperStartExpr)
        self.offUExpr = ExpressionUI("offU",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kTiltUAnn'  ],
             "SplinePrimitive",maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kTiltU'  ])
        self.layout().addWidget(self.offUExpr)
        self.offVExpr = ExpressionUI("offV",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kTiltVAnn'  ],
             "SplinePrimitive",maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kTiltV'  ])
        self.layout().addWidget(self.offVExpr)
        self.offNExpr = ExpressionUI("offN",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kTiltNAnn'  ],
             "SplinePrimitive",maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kTiltN'  ])
        self.layout().addWidget(self.offNExpr)
        self.aboutNExpr = ExpressionUI("aboutN",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kAroundNAnn' ],
             "SplinePrimitive",maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kAroundN'  ])
        self.layout().addWidget(self.aboutNExpr)
        self.bendParam = []
        self.bendU = []
        self.bendV = []
        self.addJoints()
        self.optionsBox = CheckBoxUI(maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kOptions'  ],["displayWidth","faceCamera","tubeShade"],
             maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kOptionsAnn'  ],
             "SplinePrimitive",0,0,
             [maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kDisplayWidth'  ],
              maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kFaceCamera'  ],
              maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kTubeShade'  ]])
        self.optionsBox.boxValue[0].setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kDisplayWidthAnn'  ])
        self.optionsBox.boxValue[1].setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kFaceCameraAnn'  ])
        self.optionsBox.boxValue[2].setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kTubeShadeAnn'  ])
        
        self.optionsBox.boxValue[0].connect(self.optionsBox.boxValue[0],
                                 QtCore.SIGNAL("clicked(bool)"),
                                 lambda x:
                                 self.updateGuideDisplay("displayWidth",x))
        self.optionsBox.boxValue[1].connect(self.optionsBox.boxValue[1],
                                 QtCore.SIGNAL("clicked(bool)"),
                                 lambda x:
                                 self.updateGuideDisplay("faceCamera",x))
        self.layout().addWidget(self.optionsBox)
        if xgg.Maya:
            self.addTools()
        self.baseBottomUI()

    def addTools(self):
        # Add buttons for common tools (a better ui is needed)
        row = QWidget()
        hbox = QHBoxLayout()
        QLayoutItem.setAlignment(hbox, QtCore.Qt.AlignLeft)
        hbox.setSpacing(DpiScale(3))
        hbox.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
        self.glabel = QLabel(maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kGuideTools'  ])
        self.glabel.setFixedWidth(labelWidth())
        self.glabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        self.glabel.setIndent(DpiScale(10))
        hbox.addWidget(self.glabel)

        self.rebuildButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kRebuild'  ])
        self.rebuildButton.setAutoRepeat(False)
        self.rebuildButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kRebuildAnn'  ])
        self.connect(self.rebuildButton, QtCore.SIGNAL("clicked()"),
                     self.rebuildGuides)
        hbox.addWidget(self.rebuildButton)
        
        self.normalizeButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kNormalize'  ])
        self.normalizeButton.setAutoRepeat(False)
        self.normalizeButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kNormalizeAnn'  ])
        self.connect(self.normalizeButton, QtCore.SIGNAL("clicked()"),
                     self.normalizeGuides)
        hbox.addWidget(self.normalizeButton)
        
        filler = QWidget()
        hbox.addWidget(filler)
        row.setLayout(hbox)
        self.layout().addWidget(row)
        
        row = QWidget()
        hbox = QHBoxLayout()
        QLayoutItem.setAlignment(hbox, QtCore.Qt.AlignLeft)
        hbox.setSpacing(DpiScale(3))
        hbox.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
        label = QLabel("")
        label.setFixedWidth(labelWidth())
        label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        label.setIndent(DpiScale(10))
        hbox.addWidget(label)
        
        self.setLengthButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kSetLength'  ])
        self.setLengthButton.setAutoRepeat(False)
        self.setLengthButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kSetLengthAnn'  ])
        self.connect(self.setLengthButton, QtCore.SIGNAL("clicked()"),
                     self.setLengthGuides)
        hbox.addWidget(self.setLengthButton)
        
        self.tubeButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kTubeGroom'  ])
        self.tubeButton.setAutoRepeat(False)
        self.tubeButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kTubeGroomAnn'  ])
        self.connect(self.tubeButton, QtCore.SIGNAL("clicked()"),
                     self.tubeGuides)
        hbox.addWidget(self.tubeButton)
        
        filler = QWidget()
        hbox.addWidget(filler)
        row.setLayout(hbox)
        self.layout().addWidget(row)
        
    def attrCVChange(self):
        value = self.attrCount.value()
        de = xgg.DescriptionEditor
        de.setAttrCmd( "SplinePrimitive", "attrCVCount", value)
        self.refresh()
        
    def addJoints(self):
        self.joints = QWidget()
        vbox = QVBoxLayout()
        QLayoutItem.setAlignment(vbox, QtCore.Qt.AlignTop)
        vbox.setSpacing(DpiScale(0))
        vbox.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))
        self.joints.setLayout(vbox)
        self.layout().addWidget(self.joints)

    def refreshJoints(self):
        de = xgg.DescriptionEditor
        value = xg.getAttr('attrCVCount',de.currentPalette(),
                           de.currentDescription(),'SplinePrimitive')
        for i in range(len(self.bendParam),int(value)-2):
            self.bendParamUI = ExpressionUI("bendParam["+str(i)+"]",
                                            maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kBendParamAnn'  ],
                                            "SplinePrimitive",maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kBendParam'  ] % str(i))
    
            self.bendParam.append(self.bendParamUI)
            self.joints.layout().addWidget(self.bendParam[i])
            self.bendUUI = ExpressionUI("bendU["+str(i)+"]",
                                        maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kBendUAnn'  ],
                                        "SplinePrimitive",maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kBendU'  ] % str(i))
            
            self.bendU.append(self.bendUUI)
            self.joints.layout().addWidget(self.bendU[i])
            self.bendVUI = ExpressionUI("bendV["+str(i)+"]",
                                        maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kBendVAnn'  ],
                                        "SplinePrimitive",maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kBendV'  ] % str(i))

            self.bendV.append(self.bendVUI)
            self.joints.layout().addWidget(self.bendV[i])
        for i in range(int(value)-2):
            self.bendParam[i].refresh()
            self.bendParam[i].setVisible(True)
            self.bendU[i].refresh()
            self.bendU[i].setVisible(True)
            self.bendV[i].refresh()
            self.bendV[i].setVisible(True)
        for i in range(int(value)-2,len(self.bendParam)):
            self.bendParam[i].setVisible(False)
            self.bendU[i].setVisible(False)
            self.bendV[i].setVisible(False)

    def rebuildGuides(self):
        (res,ok) = QInputDialog.getInt(self,maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kRebuildGuides'  ],
                    maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kCvCount'  ],5,3)
        if ok:
            mel.eval("xgmChangeCVCount("+str(res)+")")
    
    def normalizeGuides(self):
        mel.eval("xgmNormalizeGuides()")
    
    def setLengthGuides(self):
        (res,ok) = QInputDialog.getDouble(self,maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kSetGuideLength'  ],
                    maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kSetGuideLengthAnn'  ],
                    1.0,0.01,5000,2)
        if ok:
            mel.eval("xgmSetGuideLength("+str(res)+")")

    def tubeGuides(self):
        dialog = TubeGroomUI("SplinePrimitive")
        dialog.show() # Using show() to get a non modal dialog to allow the edit point context tool to interact with the viewport.

    def setMethod(self,method):
        PrimitiveTabUI.setMethod(self,method)
        if method == 0:
            self.lengthExpr.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kLengthOfTheSplinePrimitive'  ])
            self.attrCount.setVisible(True)
            self.offUExpr.setVisible(True)
            self.offVExpr.setVisible(True)
            self.joints.setVisible(True)
            if xgg.Maya:
                self.glabel.setVisible(False)
                self.rebuildButton.setVisible(False)
                self.normalizeButton.setVisible(False)
                self.setLengthButton.setVisible(False)
                self.tubeButton.setVisible(False)
        else:
            self.lengthExpr.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgSplinePrimitiveTab.kLengthExprAnn'  ])
            self.attrCount.setVisible(False)
            self.offUExpr.setVisible(False)
            self.offVExpr.setVisible(False)
            self.joints.setVisible(False)
            if xgg.Maya:
                self.glabel.setVisible(True)
                self.rebuildButton.setVisible(True)
                self.normalizeButton.setVisible(True)
                self.setLengthButton.setVisible(True)
                self.tubeButton.setVisible(True)

    def updateGuideDisplay(self,option,val):
        if not xgg.Maya:
            return
        de = xgg.DescriptionEditor
        guides = xg.descriptionGuides(de.currentDescription())
        for guide in guides:
            cmds.setAttr(guide+"."+option,val)
        
    def refresh(self):
        PrimitiveTabUI.refresh(self)
        de = xgg.DescriptionEditor
        value = de.getAttr("SplinePrimitive","attrCVCount")
        self.attrCount.setValue(value)
        self.fxCount.refresh()
        self.uniformCV.refresh()
        self.lengthExpr.refresh()
        self.widthExpr.refresh()
        self.widthRamp.refresh()
        self.taperExpr.refresh()
        self.taperStartExpr.refresh()
        self.offUExpr.refresh()
        self.offVExpr.refresh()
        self.offNExpr.refresh()
        self.aboutNExpr.refresh()
        self.refreshJoints()
        self.optionsBox.refresh()
