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
# @file xgGeneratorTab.py
# @brief Contains the UI for Generator tab
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
# @version Created 04/08/09
#

from builtins import range
import sys
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *
import xgenm as xg
import xgenm.xgGlobal as xgg
import xgenm.xgLog as xglog
if xgg.Maya:
    import maya.mel as mel
    import maya.cmds as cmds

from xgenm.ui.util.xgUtil import *
from xgenm.ui.util.xgComboBox import _ComboBoxUI
from xgenm.ui.widgets import *

from maya.internal.common.qt.doubleValidator import MayaQclocaleDoubleValidator

def createSubControlHolder(labelText,widget):
    holder = QWidget()
    layout = QHBoxLayout()
    holder.setLayout(layout)
    layout.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))
    layout.addSpacing(labelWidth()+DpiScale(32))
    layout.addWidget(QLabel(labelText))
    layout.addWidget(widget)
    filler = QWidget()
    layout.addWidget(filler)
    layout.setStretchFactor(filler,100)
    return holder

class GeneratorTabUI(QWidget):
    def __init__(self,selfType,printableName = ""):
        QWidget.__init__(self)
        self.type = selfType
        # A single VBox layout provides control over the tab.
        layout = QVBoxLayout()
        QLayoutItem.setAlignment(layout, QtCore.Qt.AlignTop)
        layout.setSpacing(DpiScale(0))
        layout.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))
        self.setLayout(layout)

        self.topExpandUI = ExpandUI(maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kGeneratingPrimitives' ] )
        
        layout.addWidget(self.topExpandUI)

    # redefine for derived class
    def layout(self):
        return self.topExpandUI

    def actualLayout(self):
        return QWidget.layout(self)

    def baseTopUI(self):
        # Control over the type
        self.typeUI()

    def basePrimitiveUI(self):
        self.primLayout = QGridLayout()
        self.primLayout.setSpacing(DpiScale(0))
        self.primLayout.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))
        self.primLayout.addWidget(QWidget(), 0,0)
        row = QWidget()
        row.setLayout(self.primLayout)
        self.actualLayout().addWidget(row)

    def baseBottomUI(self):
        self.basePrimitiveUI()
        # displacement options
        displacementText = maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kDisplacement'  ]
        expand = ExpandUI(displacementText)
        self.actualLayout().addWidget(expand)
        
        self.displacementExpr = ExpressionUI("displacement",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kDisplacementAnn'  ],
             self.type+"Generator",displacementText)
        expand.addWidget(self.displacementExpr)
        self.vecDispBox = CheckBoxUI(maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kUseVectorDisplacementForMaps'  ],"vectorDisplacement",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kVectorDisplacementAnn'  ],
             self.type+"Generator")
        expand.addWidget(self.vecDispBox)
        self.bumpExpr = ExpressionUI("bump",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kBumpAnn'  ],
             self.type+"Generator",maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kBump'  ])
        expand.addWidget(self.bumpExpr)
        self.offsetExpr = ExpressionUI("offset",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kOffsetAnn'  ],
             self.type+"Generator",maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kOffset'  ])
        expand.addWidget(self.offsetExpr)

        # culling options
        self.cullOptions = ExpandUI(maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kCulling'  ])
        self.actualLayout().addWidget(self.cullOptions)

        self.cullFlag = CheckBoxUI(maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kEnableCulling'  ], "cullFlag",
                                   maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kEnableCullingAnn'  ],
                                   self.type+"Generator")
        self.cullOptions.addWidget(self.cullFlag)
        self.connect(self.cullFlag.boxValue[0], QtCore.SIGNAL("clicked(bool)"),
                     lambda x: self.cullUpdate())

        self.dispCull = CheckBoxUI(maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kDisplayCulledPrimitives'  ],"culled",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kDisplayCulledPrimAnn'  ],"GLRenderer")
        self.cullOptions.addWidget(self.dispCull)
        if ( xgg.Maya ):
            self.connect(self.dispCull.boxValue[0],
                         QtCore.SIGNAL("clicked(bool)"),
                         lambda: mel.eval("refresh -force"))
        self.connect(self.dispCull.boxValue[0],
                         QtCore.SIGNAL("clicked(bool)"),
                         self.previewerRefresh)
        self.backface = CheckBoxUI(maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kCullPrimitivesOnBackFaces'  ], "cullBackface",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kCullBackFacesAnn'  ],
             self.type+"Generator")
        self.cullOptions.addWidget(self.backface)
        self.connect(self.backface.boxValue[0], QtCore.SIGNAL("clicked(bool)"),
                     lambda x: self.cullUpdate())

        self.backfaceAngle = QLineEdit()
        self.backfaceAngle.setValidator(MayaQclocaleDoubleValidator(0,90,6,self.backfaceAngle))
        self.backfaceAngle.setFixedWidth(DpiScale(70))
        self.backfaceAngle.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kBackfaceCullAnn'  ])
        self.connect(self.backfaceAngle,QtCore.SIGNAL("editingFinished()"),
                     lambda: self.setAttr("cullAngleBF",self.backfaceAngle))
        
        paddingAngleText = maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kPaddingAngle'  ]
        widget = createSubControlHolder(paddingAngleText, self.backfaceAngle)
        widget.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kPaddingAngleAnn'  ])        
        self.cullOptions.addWidget(widget)

        self.frustum = CheckBoxUI(maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kCullPrimitivesOutsideTheView'  ],"cullFrustrum",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kCullOutsideViewAnn'  ],
             self.type+"Generator")
        self.cullOptions.addWidget(self.frustum)
        self.connect(self.frustum.boxValue[0], QtCore.SIGNAL("clicked(bool)"),
                     lambda x: self.cullUpdate())
        
        self.frustumAngle = QLineEdit()
        self.frustumAngle.setValidator(MayaQclocaleDoubleValidator(0,90,6,self.frustumAngle))
        self.frustumAngle.setFixedWidth(DpiScale(70))
        self.frustumAngle.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kFrustumCulling'  ])
        self.frustum.layout().addWidget(self.frustumAngle)
        self.connect(self.frustumAngle,QtCore.SIGNAL("editingFinished()"),
                     lambda: self.setAttr("cullAngleF",self.frustumAngle))

        widget = createSubControlHolder(paddingAngleText, self.frustumAngle)
        widget.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kPaddingAngleAnn2'  ])        
        self.cullOptions.addWidget(widget)

        self.cullExpr = ExpressionUI("cullExpr",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kCullExprAnn'  ],
             self.type+"Generator",maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kCullExpr'  ])
        self.cullOptions.addWidget(self.cullExpr)

        if ( xgg.Maya ):
            buttonBox = QWidget()
            buttonLayout = QHBoxLayout()
            buttonLayout.addSpacing(labelWidth())
            QLayoutItem.setAlignment(buttonLayout, QtCore.Qt.AlignLeft)
            buttonLayout.setSpacing(DpiScale(3))
            buttonLayout.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
            buttonBox.setLayout(buttonLayout)
            cullButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kCullSelectedPrimitives'  ])
            cullButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kCullSelectedPrimitivesAnn'  ])        
            buttonLayout.addWidget(cullButton)
            self.connect(cullButton, QtCore.SIGNAL("clicked()"),
                         self.cullSlot)
            uncullButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kUncull'  ])
            uncullButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kUncullAnn'  ])                    
            buttonLayout.addWidget(uncullButton)
            self.connect(uncullButton, QtCore.SIGNAL("clicked()"),
                         self.uncullSlot)
            promoteStr = xg.promoteFunc()
            if promoteStr:
                promoteButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kPromote'  ])
                buttonLayout.addWidget(promoteButton)
                self.connect(promoteButton, QtCore.SIGNAL("clicked()"),
                             self.promoteSlot)
            self.cullOptions.addWidget(buttonBox)

        self.cullUpdate()

    def setAttr(self,attr,lineEdit):        
        value = str(lineEdit.text())
        de = xgg.DescriptionEditor
        de.setAttrCmd( self.type+"Generator", attr, value )

    def activateManual(self,value):
        if self.manual.expanded:
            cmd = "xgmPrimSelectionContext -q -ex xgenPrimCullInstance"
            if not mel.eval(cmd):
                cmd = "xgmPrimSelectionContext xgenPrimCullInstance"
                mel.eval(cmd)
            cmds.setToolTo("xgenPrimCullInstance")
        else:
            cmds.setToolTo("selectSuperContext")

    def typeUI(self):
        # Horizontal layout
        row = QWidget()
        hbox = QHBoxLayout()
        hbox.setSpacing(DpiScale(3))
        hbox.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
        self.layout().addSpacing(DpiScale(10))
        label = QLabel(maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kGeneratePrimitives'  ])
        label.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kGeneratePrimitivesAnn'  ])
        label.setFixedWidth(labelWidth())
        label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        label.setIndent(DpiScale(10))
        hbox.addWidget(label)
        self.active = _ComboBoxUI()
        '''
        index, found = 0, 0
        for type in xgg.GeneratorTypes():
            self.active.addItem(type,type)
            if type == self.type:
                found = index
            index = index+1
        '''
        # we're selecting only a subset of the generators, and giving them different names
        longnames = [maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kRandomlyAcrossTheSurface'  ],
                     maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kInUniformRowsAndColumns'  ],
                     maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kAtSpecifiedLocations'  ],
                     maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kAtGuideLocations' ],
                     maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kFromXPDFile'  ]]
        typenames = ["Random","Uniform","Point","Guide","File"]
        for i in range(len(typenames)):
            self.active.addItem(longnames[i],typenames[i])

        # add the custom generator
        for type in xgg.GeneratorTypes():
            if not type in typenames:
                self.active.addItem(type,type)
        
        self.connect(self.active, QtCore.SIGNAL("activated(int)"),self.typeUIChangedSlot)
        hbox.addWidget(self.active)
        filler = QWidget()
        hbox.addWidget(filler)
        row.setLayout(hbox)
        self.layout().addWidget(row)


        self.generatorSeed = IntegerUI("descriptionId",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kGenerateSeedAnn'  ],
             "Description",0,1e7,maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kGeneratorSeed'  ])
        self.layout().addWidget(self.generatorSeed)

        self.generatorFlip = CheckBoxUI( maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kGenerateOnBackFaces'  ], "flipNormals", maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kGenerateOnBackFacesAnn'  ], "Description" )
        self.layout().addWidget(self.generatorFlip)

    def setActiveByTypeName(self,typename):
        count = self.active.count()
        found = False
        for i in range(count):
            if self.active.itemData(i) == typename:
                self.active.setCurrentIndex(i)
                found = True
                break
        if not found:
            raise ValueError(maya.stringTable[u'y_xgenm_ui_tabs_xgGeneratorTab.kGeneratorTabUnknownType' ] % typename)


    def typeUIChangedSlot(self,index):
        xgg.DescriptionEditor.setActive('Generator', str(self.active.itemData(index)))

    def promoteSlot(self):
        de = xgg.DescriptionEditor
        mel.eval('xgmPromoteRender -pb "'+de.currentDescription()+'"')
        promoteStr = xg.promoteFunc()
        pos = promoteStr.find(".")
        if pos > -1:
            promoteModule = promoteStr[0:pos]
            promoteFunction = promoteStr
            if promoteModule == "xg":
                promoteModule = ""
                promoteFunction = promoteStr
        else:
            promoteModule = ""
            promoteFunction = promoteStr
        # Import the promote module if one was given
        if promoteModule:
            try:
                # See if the module has been imported already
                sys.modules[promoteModule]
            except:
                try:
                    __import__(promoteModule)
                    mod = sys.modules[promoteModule]
                    globals().update(vars(mod))
                except:
                    xglog.XGError(maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kPromoteModuleDoesNotExist'  ] % promoteModule)
        # Try to call the promotion function
        try:
            import tempfile
            filename = tempfile.gettempdir()+"/"+de.currentDescription()+".pmt"
            # Call the registered promotion function
            eval(promoteFunction+"(filename)")
        except:
            import traceback
            print(traceback.print_exc())
            xglog.XGError(maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kPromoteFunctionDoesNotExist'  ] % promoteFunction)
    
    def cullSlot(self):
        de = xgg.DescriptionEditor
        mel.eval('xgmSelectedPrims -c "'+de.currentDescription()+'"')
    
    def uncullSlot(self):
        de = xgg.DescriptionEditor
        mel.eval('xgmSelectedPrims -u "'+de.currentDescription()+'"')

    def cullUpdate(self):
        self.backface.setEnabled(self.cullFlag.value())
        self.frustum.setEnabled(self.cullFlag.value())
        if self.cullFlag.value(): 
            self.backfaceAngle.parentWidget().setEnabled(self.backface.value())
            self.frustumAngle.parentWidget().setEnabled(self.frustum.value())
        else:
            self.backfaceAngle.parentWidget().setEnabled(self.cullFlag.value())
            self.frustumAngle.parentWidget().setEnabled(self.cullFlag.value())            
        

    def previewerRefresh(self):
        xgg.DescriptionEditor.previewerTab.widget().refresh()

    def refresh(self):
        self.primLayout.addWidget( xgg.DescriptionEditor.primitiveTab, 0,0 )
        xgg.DescriptionEditor.primitiveTab.setVisible(True)
        xgg.DescriptionEditor.primitiveTab.widget().refresh()
        self.generatorSeed.refresh()
        self.generatorFlip.refresh()
        self.vecDispBox.refresh()
        self.displacementExpr.refresh()
        self.bumpExpr.refresh()
        self.offsetExpr.refresh()
        self.dispCull.refresh()

        self.cullFlag.refresh()

        self.backface.refresh()
        value = xgg.DescriptionEditor.getAttr(self.type+"Generator","cullAngleBF")
        self.backfaceAngle.setText(value)

        self.frustum.refresh()
        value = xgg.DescriptionEditor.getAttr(self.type+"Generator","cullAngleF")
        self.frustumAngle.setText(value)

        self.cullExpr.refresh()
        self.cullUpdate()


class GeneratorTabBlankUI(GeneratorTabUI):
    """
    Convenience class that prints out a UI with no additional attributes, and a
    label saying there are no attributes.

    Example:
        class MyWonderfulGeneratorTabUI(GeneratorTabBlankUI):
            def __init__(self):
               MyWonderfulGeneratorTabUI.__init__("MyWonderful", "my wonderful")
    """
    def __init__(self, typename, printablename = None):
        GeneratorTabUI.__init__(self, "%sGenerator" % typename)
        self.baseTopUI()
        self.layout().addSpacing(DpiScale(5))
        if printablename:
            labeltext = printablename
        else:
            labeltext = typename
        label = QLabel(maya.stringTable[ u'y_xgenm_ui_tabs_xgGeneratorTab.kNoExtraAttributesForGenerator'  ]
                             % labeltext)
        label.setIndent(DpiScale(135))
        label.font().setItalic(True)
        self.layout().addWidget(label)
        self.basePrimitiveUI()

    def refresh(self):
        pass
