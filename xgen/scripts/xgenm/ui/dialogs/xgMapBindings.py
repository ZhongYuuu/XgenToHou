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
# @file xgMapBinding.py
# @brief Contains the dialog for chosing map directory for map binding.
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
# @version Created 03/10/11
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
from xgenm.ui.util.xgUtil import *
from xgenm.ui.util.xgComboBox import _ComboBoxUI


class MapBindingsUI(QDialog):
    modifyBindingBox = 0
    """Function to modify patch bindings via map using a dialog.

    This provides a simple dialog to accept the directory name and a check
    box for optionally inverting the map. The user can use a browser to
    search for the directory.
    """
    def __init__(self):
        QDialog.__init__(self)
        self.setWindowTitle(maya.stringTable[ u'y_xgenm_ui_dialogs_xgMapBindings.kBindFacesBasedOnMap'  ])
        self.setSizeGripEnabled(True)
        self.setMinimumWidth(DpiScale(550))
        self.de = xgg.DescriptionEditor
        layout = QVBoxLayout()
        self.dirName = BrowseUI(maya.stringTable[ u'y_xgenm_ui_dialogs_xgMapBindings.kMapDirectory'  ],
                                maya.stringTable[ u'y_xgenm_ui_dialogs_xgMapBindings.kMapDirectoryAnn'  ])
        self.dirName.optionButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_dialogs_xgMapBindings.kBrowseUIAnn'  ])
        self.dirName.setValue("xgen/density/")
        layout.addWidget(self.dirName)

        comborow = QWidget()
        combobox = QHBoxLayout()
        QLayoutItem.setAlignment(combobox, QtCore.Qt.AlignRight)
        combobox.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
        self.colourLabel = QLabel(maya.stringTable[ u'y_xgenm_ui_dialogs_xgMapBindings.kBindToFacesWhereMapIs'  ])
        combobox.addWidget(self.colourLabel)
        self.whiteOrBlackcb = _ComboBoxUI()
        self.whiteOrBlackcb.addItem(maya.stringTable[ u'y_xgenm_ui_dialogs_xgMapBindings.kWhite'  ])
        self.whiteOrBlackcb.addItem(maya.stringTable[ u'y_xgenm_ui_dialogs_xgMapBindings.kBlack'  ])
        self.whiteOrBlackcb.setCurrentIndex(MapBindingsUI.modifyBindingBox)
        self.connect(self.whiteOrBlackcb, QtCore.SIGNAL("activated(int)"),self.typeUIChangedSlot)
        combobox.addWidget(self.whiteOrBlackcb)
        comborow.setLayout(combobox)
        layout.addWidget(comborow)
        
        row = QWidget()
        hbox = QHBoxLayout()
        QLayoutItem.setAlignment(hbox, QtCore.Qt.AlignRight)
        hbox.setSpacing(DpiScale(3))
        hbox.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
        self.bindButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_dialogs_xgMapBindings.kBind'  ])
        self.bindButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_dialogs_xgMapBindings.kBindAnn'  ])
        self.bindButton.setAutoRepeat(False)
        self.connect(self.bindButton, QtCore.SIGNAL("clicked()"),
                     self.accept)
        hbox.addWidget(self.bindButton)
        self.cancelButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_dialogs_xgMapBindings.kCancel'  ])
        self.cancelButton.setAutoRepeat(False)
        self.cancelButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_dialogs_xgMapBindings.kCancelAnn'  ])
        self.connect(self.cancelButton, QtCore.SIGNAL("clicked()"),
                     self.reject)
        hbox.addWidget(self.cancelButton)
        row.setLayout(hbox)
        layout.addWidget(row)
        self.setLayout(layout)

    def getDirName(self):
        return str(self.dirName.value())
    
    def getInvert(self):
        return MapBindingsUI.modifyBindingBox

    def typeUIChangedSlot(self, pos):
        MapBindingsUI.modifyBindingBox = pos
        self.whiteOrBlackcb.setCurrentIndex(pos)

def mapBindings(cpal,cdesc):
    """Function to modify patch bindings via map using a dialog.

    This provides a simple dialog to accept the directory name and a check
    box for optionally inverting the map. The user can use a browser to
    search for the directory.
    """
    dialog = MapBindingsUI()
    result = dialog.exec_()
    if result == QDialog.Accepted:
        mapDir = dialog.getDirName()
        invert = dialog.getInvert()
        if len(mapDir):
            if xgg.Maya:
                xg.modifyFaceBinding(cpal,cdesc,"Map",mapDir,invert)
            else:
                goPort = QMessageBox()
                goPort.setText(maya.stringTable[ u'y_xgenm_ui_dialogs_xgMapBindings.kMapBasedBindingOnlyAvailableInMaya'  ])
                goPort.exec_()
                
