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
# @file xgPrimitiveTab.py
# @brief Contains the UI for Primitive tab
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

from builtins import range
import string
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *
import xgenm as xg
import xgenm.xgGlobal as xgg
import xgenm.xgLog as xglog
if xgg.Maya:
    import maya.cmds as cmds
    import maya.mel as mel
from xgenm.ui.util.xgUtil import *
from xgenm.ui.util.xgComboBox import _ComboBoxUI
from xgenm.ui.widgets import *


class PrimitiveTabUI(QWidget):
    def __init__(self,selfType,printableName=""):
        QWidget.__init__(self)
        self.type = selfType
        # A single VBox layout provides control over the tab.
        layout = QVBoxLayout()
        QLayoutItem.setAlignment(layout, QtCore.Qt.AlignTop)
        layout.setSpacing(DpiScale(0))
        layout.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))
        self.setLayout(layout)

        self.topExpandUI = ExpandUI(maya.stringTable[ u'y_xgenm_ui_tabs_xgPrimitiveTab.kPrimitiveAttributes' ] )
        layout.addWidget(self.topExpandUI)

    # redefine for derived class
    def layout(self):
        return self.topExpandUI

    def actualLayout(self):
        return QWidget.layout(self)

    def baseTopUI(self,attrGroup=False):
        # Control over the type
        self.typeUI()
        self.methodUI()
        if attrGroup:
            # don't use an expand ui, it's too big
            # instead, just let the derive class add to our window
            self.attrGroup = self.layout()
            #self.attrGroup = ExpandUI(self.type)
            #self.layout().addWidget(self.attrGroup)

    def baseBottomUI(self):
        self.regionControlUI()
        self.animationUI()
        
    def typeUI(self):
        # Horizontal layout
        row = QWidget()
        hbox = QHBoxLayout()
        hbox.setSpacing(DpiScale(3))
        hbox.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
        hbox.setSizeConstraint( QLayout.SetFixedSize )

        label = QLabel(maya.stringTable[ u'y_xgenm_ui_tabs_xgPrimitiveTab.kPrimitiveType'  ])
        label.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgPrimitiveTab.kPrimitiveTypeAnn'  ])
        label.setFixedWidth(labelWidth())
        label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        label.setIndent(DpiScale(10))
        hbox.addWidget(label)
        self.active = _ComboBoxUI()
        index, found = 0, 0
        for type in xgg.PrimitiveTypes():
            self.createActiveItem(type)
            if type == self.type:
                found = index
            index = index+1 
        self.active.setCurrentIndex(found)
        self.active.setFixedWidth(labelWidth())
        self.connect(self.active, QtCore.SIGNAL("activated(int)"),self.typeUIChangedSlot)
        hbox.addWidget(self.active)

        filler = QWidget()
        hbox.addWidget(filler)

        row.setLayout(hbox)
        self.layout().addWidget(row)

    # Create localized strings for all types that are currently known.
    # Allow for non-known types to go through for extention. 
    def createActiveItem(self,type):
        if type == "Archive":
            typename = maya.stringTable[ u'y_xgenm_ui_tabs_xgPrimitiveTab.kArchive'  ]
        elif type == "Card":
            typename = maya.stringTable[ u'y_xgenm_ui_tabs_xgPrimitiveTab.kCard'  ]
        elif type == "Sphere":
            typename = maya.stringTable[ u'y_xgenm_ui_tabs_xgPrimitiveTab.kSphere'  ]
        elif type == "Spline":
            typename = maya.stringTable[ u'y_xgenm_ui_tabs_xgPrimitiveTab.kSpline'  ]
        else:
            typename = type
        self.active.addItem(typename,type)
        
    def typeUIChangedSlot(self,index):
        xgg.DescriptionEditor.setActive('Primitive', str(self.active.itemData(index)))
        xgg.DescriptionEditor.previewerTab.widget().refresh()

    def setActiveByTypeName(self,typename):
        count = self.active.count()
        found = False
        for i in range(count):
            if self.active.itemData(i) == typename:
                self.active.setCurrentIndex(i)
                found = True
                break
        if not found:
            raise ValueError(maya.stringTable[u'y_xgenm_ui_tabs_xgPrimitiveTab.kPrimTabUnknownType' ] % typename)
        
    def methodUI(self):
        # Horizontal layout
        row = QWidget()
        hbox = QHBoxLayout()
        hbox.setSpacing(DpiScale(3))
        hbox.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
        label = QLabel( maya.stringTable[u'y_xgenm_ui_tabs_xgPrimitiveTab.kControlUsing' ])
        label.setToolTip( maya.stringTable[u'y_xgenm_ui_tabs_xgPrimitiveTab.kControlUsingAnn' ] )
        label.setFixedWidth(labelWidth())
        label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        label.setIndent(DpiScale(10))
        hbox.addWidget(label)
        self.method = _ComboBoxUI()
        self.method.addItem(maya.stringTable[ u'y_xgenm_ui_tabs_xgPrimitiveTab.kAttribute'  ])
        self.method.addItem(maya.stringTable[ u'y_xgenm_ui_tabs_xgPrimitiveTab.kGuides'  ])
        self.method.setFixedWidth(labelWidth())
        self.method.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgPrimitiveTab.kMethodAnn'  ])
        self.connect(self.method, QtCore.SIGNAL("activated(int)"), lambda x: self.setMethod(int(x)))
        hbox.addWidget(self.method)
        filler = QWidget()
        hbox.addWidget(filler)
        row.setLayout(hbox)
        self.layout().addWidget(row)

    def regionControlUI(self):
        self.regionControlGroup = ExpandUI(maya.stringTable[ u'y_xgenm_ui_tabs_xgPrimitiveTab.kRegionControl'  ])
        self.actualLayout().addWidget(self.regionControlGroup)
        
        self.regionMaskExpr = ExpressionUI("regionMask",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgPrimitiveTab.kRegionMaskAnn'  ],self.type+"Primitive",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgPrimitiveTab.kRegionMask'  ])
        self.regionControlGroup.addWidget(self.regionMaskExpr)
        self.regionMapDir = ExpressionUI("regionMap",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgPrimitiveTab.kRegionMapAnn'  ],
             self.type+"Primitive",maya.stringTable[ u'y_xgenm_ui_tabs_xgPrimitiveTab.kRegionMap'  ],True,"Region", "xgRegionMap3dPaintContext")
        self.regionControlGroup.addWidget(self.regionMapDir)
        
    def animationUI(self):
        self.animationGroup = ExpandUI(maya.stringTable[u'y_xgenm_ui_tabs_xgPrimitiveTab.kGuideAnimation'])
        self.actualLayout().addWidget(self.animationGroup)
        
        self.useAnimBox = CheckBoxUI(maya.stringTable[ u'y_xgenm_ui_tabs_xgPrimitiveTab.kUseAnimation'  ],"useCache",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgPrimitiveTab.kUseAnimAnn'  ],self.type+"Primitive")
        self.animationGroup.addWidget(self.useAnimBox)

        self.cacheFileDir = BrowseUI("cacheFileName",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgPrimitiveTab.kCacheFileNameAnn'  ],self.type+"Primitive",
             "*.caf *.abc","in",maya.stringTable[ u'y_xgenm_ui_tabs_xgPrimitiveTab.kCacheFileName'  ])
        self.animationGroup.addWidget(self.cacheFileDir)

        buttonBox = QWidget()
        buttonLayout = QHBoxLayout()
        buttonLayout.setSpacing(DpiScale(3))
        buttonLayout.setContentsMargins(DpiScale(0),DpiScale(1),DpiScale(1),DpiScale(1))
        buttonBox.setLayout(buttonLayout)            

        self.liveMode = CheckBoxUI(maya.stringTable[ u'y_xgenm_ui_tabs_xgPrimitiveTab.kLiveMode'  ], "liveMode",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgPrimitiveTab.kLiveModeAnn'  ], 
             self.type+"Primitive")
        buttonLayout.addWidget(self.liveMode)        

        self.exportGuidesButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_tabs_xgPrimitiveTab.kCreateHairSystem'  ])
        self.exportGuidesButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgPrimitiveTab.kCreateHairSystemAnn'  ])
        self.exportGuidesButton.setFixedWidth(DpiScale(115))
        buttonLayout.addWidget(self.exportGuidesButton)                    

        self.attachButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_tabs_xgPrimitiveTab.kAttachHairSystem'  ])
        self.attachButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgPrimitiveTab.kAttachHairSystemAnn'  ])
        self.attachButton.setFixedWidth(DpiScale(145))
        buttonLayout.addWidget(self.attachButton)
        self.animationGroup.addWidget(buttonBox)

        if ( xgg.Maya ):
            self.connect(self.useAnimBox.boxValue[0],
                         QtCore.SIGNAL("clicked(bool)"),
                         lambda x: self.useAnimUpdate())

            self.connect(self.liveMode.boxValue[0], 
                         QtCore.SIGNAL("clicked(bool)"),
                         lambda x: self.liveModeUpdate())

            self.connect(self.attachButton, QtCore.SIGNAL("clicked()"),
                         self.attachSlot)

            self.connect(self.exportGuidesButton, QtCore.SIGNAL("clicked()"),
                         self.createHairSystem)

    def createHairSystem(self):
        de = xgg.DescriptionEditor
        desc = de.currentDescription()
        guides = xg.descriptionGuides(desc)
        if guides:
            cmds.select( guides )
            cmd = 'xgmNDynamicGuidesToolCreate'
            mel.eval(cmd)
        else:
            xglog.XGWarning(maya.stringTable[ u'y_xgenm_ui_tabs_xgPrimitiveTab.kThereIsNoGuidesWarning'  ])

    def attachSlot(self):
        sel = cmds.ls(sl=True,ni=True,dag=True,type='nurbsCurve')
        if not sel:                        
            mel.eval("xgmSelectCurvesFromHairSystem")
        
        sel = cmds.ls(sl=True,ni=True,dag=True,type='nurbsCurve')
        if sel:                
            de = xgg.DescriptionEditor
            cmd = 'xgmFindAttachment'
            cmd += ' -description "'+de.currentDescription()+'"'
            cmd += ' -module "'+self.type+"Primitive"+'"'
            mel.eval(cmd)
            print(maya.stringTable[ u'y_xgenm_ui_tabs_xgPrimitiveTab.kAttachedCurves'  ], sel)
        else:
            warn = QMessageBox()
            warn.setText(maya.stringTable[ u'y_xgenm_ui_tabs_xgPrimitiveTab.kNoCurvesSelected'  ])
            warn.exec_()


    def useAnimUpdate(self):
        self.liveModeUpdate()
        value = self.useAnimBox.value(0)
        if value:
            self.liveMode.setEnabled(True) 
        else:
            self.liveMode.setEnabled(False)
            self.cacheFileDir.setEnabled(False)
            self.attachButton.setEnabled(False)
            self.exportGuidesButton.setEnabled(False)

    def liveModeUpdate(self):
        value = self.liveMode.value()
        if value:
            self.cacheFileDir.setEnabled(False)
            self.attachButton.setEnabled(True)
            self.exportGuidesButton.setEnabled(True)
        else:
            self.cacheFileDir.setEnabled(True)                    
            self.attachButton.setEnabled(False)
            self.exportGuidesButton.setEnabled(False)
        
    def setMethod(self,method):
        de = xgg.DescriptionEditor
        if method == 0:
            self.method.setCurrentIndex(0)
            self.animationGroup.setVisible(False)
            self.useAnimBox.setVisible(False)
            self.cacheFileDir.setVisible(False)
            self.liveMode.setVisible(False)
            self.attachButton.setVisible(False)
            self.exportGuidesButton.setVisible(False)        
            xg.setAttr("iMethod","0",de.currentPalette(),
                       de.currentDescription(),self.type+'Primitive')
        else:
            self.method.setCurrentIndex(1)
            self.animationGroup.setVisible(True)
            self.useAnimBox.setVisible(True)
            self.cacheFileDir.setVisible(True)
            self.liveMode.setVisible(True)
            self.attachButton.setVisible(True)
            self.exportGuidesButton.setVisible(True)        
            xg.setAttr("iMethod","1",de.currentPalette(),
                       de.currentDescription(),self.type+'Primitive')
        xgg.DescriptionEditor.previewerTab.widget().refresh()
            
    def refresh(self):
        de = xgg.DescriptionEditor
        value = xg.getAttr('iMethod',de.currentPalette(),
                           de.currentDescription(),self.type+'Primitive')
        if value=="0":
            self.setMethod(0)
        else:
            self.setMethod(1)
        self.regionMaskExpr.refresh()
        self.regionMapDir.refresh()
        self.useAnimBox.refresh()
        self.liveMode.refresh()
        self.cacheFileDir.refresh()
        self.useAnimUpdate()

class PrimitiveTabBlankUI(PrimitiveTabUI):
    """
    Convenience class that prints out a UI with no additional attributes, and a
    label saying there are no attributes.

    Example:
        class MyWonderfulPrimitiveTabUI(PrimitiveTabBlankUI):
            def __init__(self):
               MyWonderfulPrimitiveTabUI.__init__("MyWonderful", "my wonderful")
    """
    def __init__(self, typename, printablename = None):
        PrimitiveTabUI.__init__(self, typename)
        self.baseTopUI()
        if printablename:
            labeltext = printablename
        else:
            labeltext = typename
        label = QLabel(maya.stringTable[ u'y_xgenm_ui_tabs_xgPrimitiveTab.kNoExtraAttributesForSPrimitive'  ] % labeltext)
        label.setIndent(DpiScale(135))
        label.font().setItalic(True)
        self.layout().addWidget(label)
        self.baseBottomUI()
