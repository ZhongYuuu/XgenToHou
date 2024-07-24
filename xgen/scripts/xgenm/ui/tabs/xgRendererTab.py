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
# @file xgRendererTab.py
# @brief Contains the UI for Renderer tab
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
from xgenm.ui.util.xgUtil import *
from xgenm.ui.util.xgComboBox import _ComboBoxUI
from xgenm.ui.widgets import *


class RendererTabUI(QWidget):
    def __init__(self,selfType):
        QWidget.__init__(self)
        self.type = selfType
        # A single VBox layout provides control over the tab.
        layout = QVBoxLayout()
        QLayoutItem.setAlignment(layout, QtCore.Qt.AlignTop)
        layout.setSpacing(DpiScale(0))
        layout.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))
        self.setLayout(layout)

    def baseTopUI(self, percent=True):
        # Control over the type
        self.typeUI()
        if percent:
            self.percent = FloatUI("percent",
                 maya.stringTable[ u'y_xgenm_ui_tabs_xgRendererTab.kPercentAnn'  ],
                 self.type+"Renderer",0.0,100.0,-1000,1000,maya.stringTable[ u'y_xgenm_ui_tabs_xgRendererTab.kPercent'  ])
            self.layout().addWidget(self.percent)
        else:
            self.percent = None

    def typeUI(self):
        # Horizontal layout
        row = QWidget()
        hbox = QHBoxLayout()
        hbox.setSpacing(DpiScale(3))
        hbox.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
        label = QLabel(maya.stringTable[ u'y_xgenm_ui_tabs_xgRendererTab.kRendererType'  ])
        label.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgRendererTab.kRendererTypeAnn'  ])
        label.setFixedWidth(labelWidth())
        label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        label.setIndent(DpiScale(10))
        hbox.addWidget(label)
        self.active = _ComboBoxUI()
        index, found = 0, 0
        for type in xgg.RendererTypes():
            self.getRendererUIName(type)
            if type == self.type:
                found = index
            index = index+1
        self.active.setCurrentIndex(found)
        #self.active.setFixedWidth(labelWidth())
        self.connect(self.active, QtCore.SIGNAL("activated(int)"),self.typeUIChangedSlot)
        hbox.addWidget(self.active)
        filler = QWidget()
        hbox.addWidget(filler)
        row.setLayout(hbox)
        self.layout().addWidget(row)

    # Create localized strings for all types that are currently known.                       
    # Allow for non-known types to go through for extention.    
    def getRendererUIName( self, type ):
        """ Overload the names to display in the renderer type combo box """
        if( type == "File" ):
            typename = maya.stringTable[ u'y_xgenm_ui_tabs_xgRendererTab.kFile'  ]
        elif( type == "Geometry" ):
            typename = maya.stringTable[ u'y_xgenm_ui_tabs_xgRendererTab.kGeometry'  ]
        elif( type == "Guide" ):
            typename = maya.stringTable[ u'y_xgenm_ui_tabs_xgRendererTab.kGuide'  ]
        elif( type == "Mel" ):
            typename = maya.stringTable[ u'y_xgenm_ui_tabs_xgRendererTab.kMel'  ]
        elif( type == "Particle" ):
            typename = maya.stringTable[ u'y_xgenm_ui_tabs_xgRendererTab.kParticle'  ]
        elif( type == "Point" ):
            typename = maya.stringTable[ u'y_xgenm_ui_tabs_xgRendererTab.kPoint'  ]
        elif( type == "Renderman" ):
            typename = maya.stringTable[ u'y_xgenm_ui_tabs_xgRendererTab.kRender'  ]
        else:
            typename = type
        
        self.active.addItem(typename,type)

    def setActiveByTypeName(self,typename):
        count = self.active.count()
        found = False
        for i in range(count):
            if self.active.itemData(i) == typename:
                self.active.setCurrentIndex(i)
                found = True
                break
        if not found:
            raise ValueError(maya.stringTable[u'y_xgenm_ui_tabs_xgRendererTab.kRendererTabUnknownType' ] % typename)

    def typeUIChangedSlot(self,index):
        xgg.DescriptionEditor.setActive('Renderer', str(self.active.itemData(index)))
        

    def refresh(self):
        if self.percent:
            self.percent.refresh()


class RendererTabBlankUI(RendererTabUI):
    """
    Convenience class that prints out a UI with no additional attributes, and a
    label saying there are no attributes.

    Example:
        class MyWonderfulRendererTabUI(RendererTabBlankUI):
            def __init__(self):
               MyWonderfulRendererTabUI.__init__("MyWonderful", "my wonderful")
    """
    def __init__(self, typename, printablename = None):
        RendererTabUI.__init__(self, "%sRenderer" % typename)
        self.baseTopUI()
        self.layout().addSpacing(DpiScale(5))
        if printablename:
            labeltext = printablename
        else:
            labeltext = typename
        label = QLabel(maya.stringTable[ u'y_xgenm_ui_tabs_xgRendererTab.kNoExtraAttributesForRenderer'  ] % labeltext)
        label.setIndent(DpiScale(135))
        label.font().setItalic(True)
        self.layout().addWidget(label)