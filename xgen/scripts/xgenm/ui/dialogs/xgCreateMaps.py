from __future__ import division
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



import string
import os

from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *
import xgenm as xg
import xgenm.xgGlobal as xgg
from xgenm.ui.util.xgUtil import *
from xgenm.ui.widgets.xgBrowseUI import *
from xgenm.ui.widgets.xgFloatUI import *
from xgenm.ui.util.xgUtil import labelWidth
from xgenm.ui.util.xgComboBox import _ComboBoxUI
from xgenm.ui.widgets.xgFloatUI import _sliderNumSteps

import maya.cmds as cmds
import maya.mel as mel

MAINDIR = str("${DESC}/paintmaps")

class CreateMapsUI(QDialog):
    startColorCombo = "basedOnAttribute"
    mapResolution = 5.0
    createDir = False
    cleanFoldername = ""
    """A dialog to specify the options for creating an XGen expression map. """
    def __init__(self,attr,defaultFolder="",useRGB=False):
        QDialog.__init__(self)
        self.setWindowTitle(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCreateMaps.kCreateMap'  ])
        self.setSizeGripEnabled(True)
        self.setMinimumWidth(DpiScale(550))
        self.layout = QVBoxLayout()
        QLayoutItem.setAlignment(self.layout, QtCore.Qt.AlignTop)
        self.desc = xgg.DescriptionEditor.currentDescription()
        self.exprAttr = attr
        self.defaultFolder = defaultFolder
        self.isBrowseMode = True if defaultFolder != "" else False
        self.isRGB = useRGB

        # change some defaults if in browse ui mode or RGB mode
        global MAINDIR
        if self.isRGB:
            CreateMapsUI.startColorCombo = "red"
        else:
            CreateMapsUI.startColorCombo = "white"

        if self.isBrowseMode:
            MAINDIR = str("${DESC}")            
        else:
            MAINDIR = str("${DESC}/paintmaps")
        
        self.createUI()
        self.setLayout(self.layout)

    def createUI(self):

        # clean the foldername of unwanted brackets that may come from custom expressions
        self.exprAttr = self.exprAttr.replace('[','_')
        self.exprAttr = self.exprAttr.replace(']','_')

        if self.defaultFolder == "":
            foldername = self.exprAttr
            bareFoldername = self.exprAttr
        else:
            foldername = self.defaultFolder
            bareFoldername = self.defaultFolder

        path = fullPath(MAINDIR)
        if ( not dirExists() ): 
            CreateMapsUI.createDir = True
        else:
            if os.path.isdir(path):
                folders = os.listdir( path )
                
                # search if foldername already exists, increment if it does
                suffix = 1
                for folder in sorted(folders):
                    if foldername == folder:
                        foldername = bareFoldername + str(suffix)
                        suffix += 1

        CreateMapsUI.cleanFoldername = foldername

        # Map name
        maprow = QWidget()
        maplayout = QHBoxLayout()
        QLayoutItem.setAlignment(maplayout, QtCore.Qt.AlignLeft)
        maplayout.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
        self.mapLabel = QLabel(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCreateMaps.kMapName'  ])
        self.mapLabel.setFixedWidth(labelWidth())
        self.mapLabel.setAlignment(QtCore.Qt.AlignRight)
        self.mapLabel.setIndent(DpiScale(10))
        maplayout.addWidget(self.mapLabel)
        self.mapEdit = QLineEdit()
        rx = QRegExp("[A-Za-z]+[A-Za-z0-9_]*")
        self.mapEdit.setValidator(QRegExpValidator(rx,self))
        self.mapEdit.setText(CreateMapsUI.cleanFoldername)
        self.connect(self.mapEdit, QtCore.SIGNAL("editingFinished()"), self.editTextBox )
        maplayout.addWidget(self.mapEdit)
        maprow.setLayout(maplayout)
        self.layout.addWidget(maprow)

        # Map Resolution
        self.resSlider = FloatUI(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCreateMaps.kMapResolution'  ],
             maya.stringTable[ u'y_xgenm_ui_dialogs_xgCreateMaps.kMapResolutionAnn'  ],
             "",0,)
        self.resSlider.setValue(CreateMapsUI.mapResolution)
        self.resSlider.editChanged()
        # set the slider to update the static member
        self.connect(self.resSlider.slider, QtCore.SIGNAL("valueChanged(int)"), self.sliderChanged )
        self.layout.addWidget(self.resSlider)
        
        # Help Text
        # TO-DO: Make dynamic to object?
        self.texelHelp = QLabel(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCreateMaps.kTotalResolutionHelp'  ])
        self.texelHelp.setAlignment(QtCore.Qt.AlignLeft)
        self.texelHelp.setIndent(labelWidth())
        #self.layout.addWidget(self.texelHelp)

        # Combo box
        comborow = QWidget()
        combobox = QHBoxLayout()
        QLayoutItem.setAlignment(combobox, QtCore.Qt.AlignLeft)
        combobox.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
        self.colorLabel = QLabel(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCreateMaps.kStartColor'  ])
        self.colorLabel.setToolTip(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCreateMaps.kStartColorAnn'  ])
        self.colorLabel.setFixedWidth(labelWidth())
        self.colorLabel.setAlignment(QtCore.Qt.AlignRight)
        self.colorLabel.setIndent(DpiScale(10))
        combobox.addWidget(self.colorLabel)
        self.startColorCB = _ComboBoxUI()
        # choose if maps will be coloured or monochrome
        if self.isRGB:
            self.startColorCB.addItem(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCreateMaps.kRed'  ], "red")
            self.startColorCB.addItem(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCreateMaps.kGreen'  ], "green")
            self.startColorCB.addItem(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCreateMaps.kBlue'  ], "blue")
        else:
            if not self.isBrowseMode:
                self.startColorCB.addItem(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCreateMaps.kBasedOnAttribute'  ],"basedOnAttribute")
            self.startColorCB.addItem(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCreateMaps.kWhite'  ], "white")
            self.startColorCB.addItem(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCreateMaps.kBlack'  ], "black")
            self.startColorCB.addItem(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCreateMaps.kGrey'  ], "grey")
        self.startColorCB.setCurrentIndex(self.startColorCB.findData(CreateMapsUI.startColorCombo))
        self.connect(self.startColorCB, QtCore.SIGNAL("activated(int)"),self.typeUIChangedSlot)
        combobox.addWidget(self.startColorCB)
        comborow.setLayout(combobox)
        self.layout.addWidget(comborow)

        buttonRow = QWidget()
        buttonLayout = QHBoxLayout()
        QLayoutItem.setAlignment(buttonLayout, QtCore.Qt.AlignRight)
        buttonLayout.setSpacing(DpiScale(3))
        buttonLayout.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
        self.createButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCreateMaps.kCreate'  ])
        self.connect(self.createButton, QtCore.SIGNAL("clicked()"),self.accept)
        buttonLayout.addWidget(self.createButton)
        self.cancelButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCreateMaps.kCancel'  ])
        self.connect(self.cancelButton, QtCore.SIGNAL("clicked()"),self.reject)
        buttonLayout.addWidget(self.cancelButton)
        buttonRow.setLayout(buttonLayout)

        self.layout.addWidget(buttonRow)

    def typeUIChangedSlot(self,pos):
        CreateMapsUI.startColorCombo = str(self.startColorCB.itemData(pos))
        self.startColorCB.setCurrentIndex(pos)

    def editTextBox(self):
        CreateMapsUI.cleanFoldername = self.mapEdit.text()

    def sliderChanged(self,val):
        CreateMapsUI.mapResolution = val/float(_sliderNumSteps)
        self.resSlider.editChanged()

def fullPath(path):
    desc = xgg.DescriptionEditor.currentDescription()
    if desc == "":
        return
    return xg.expandFilepath( MAINDIR, desc )

def dirExists():
    dir = fullPath(MAINDIR)
    return True if os.path.exists(dir) else False
 

def createDir():
    dir = fullPath(MAINDIR)
    if not os.path.exists(dir):
        os.makedirs(dir)

def createMap(attr,ptexBaker,defaultFolder="",isRGB=False):
    dialog = CreateMapsUI(attr,defaultFolder,isRGB)
    result = dialog.exec_()

    if result == QDialog.Accepted:
        if CreateMapsUI.createDir:
            createDir()
        newAttr = CreateMapsUI.cleanFoldername
        tpu = CreateMapsUI.mapResolution
        startcolor = CreateMapsUI.startColorCombo

        cpal = xgg.DescriptionEditor.currentPalette()
        cdesc = xgg.DescriptionEditor.currentDescription()
        geoms = xg.boundGeometry(cpal,cdesc)

        path = MAINDIR+"/"+newAttr
        expr = str("$a=map('"+path+"');#3dpaint,"+str(tpu)+"\\n$a\\n")
        return (startcolor, expr, newAttr, path)
    else:
        return (0,"","","")
