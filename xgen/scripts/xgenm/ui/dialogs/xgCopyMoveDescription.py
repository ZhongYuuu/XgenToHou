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
# @file xgCopyMoveDescription.py
# @brief Contains the Copy or Move description UI.
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
# @version Created 07/07/09
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
from xgenm.ui.util.xgUtil import *
from xgenm.ui.util.xgComboBox import _ComboBoxUI


class CopyMoveDescriptionUI(QDialog):
    """A dialog to allow copying a description.

    This provides combo boxes to pick the palette and description to
    copy, the palette to copy into, and a text field for the name of the
    new description. Buttons to copy or cancel are supplied.
    """
    def __init__(self,type,isMove):
        QDialog.__init__(self)
        self.type = type
        if(isMove):
            self.setWindowTitle(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCopyMoveDescription.kMoveDescription'  ])
        else:
            self.setWindowTitle(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCopyMoveDescription.kDuplicateDescription'  ])
        self.setSizeGripEnabled(True)
        self.setMinimumWidth(DpiScale(550))
        layout = QVBoxLayout()

        # create a grid for the input widgets
        grid = QWidget()
        gridLayout = QGridLayout()
        gridLayout.setSpacing(DpiScale(10))
        gridLayout.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))
        grid.setLayout(gridLayout)
        layout.addWidget(grid)

        # row for labels
        if(isMove):
            label = QLabel(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCopyMoveDescription.kMoveFrom'  ])
        else:
            label = QLabel(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCopyMoveDescription.kFrom'  ])
        label.setAlignment(QtCore.Qt.AlignLeft)
        gridLayout.addWidget(label,0,0)
        gridLayout.setColumnMinimumWidth(0,DpiScale(220))
        gridLayout.setColumnStretch(0,50)
        label = QLabel(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCopyMoveDescription.kTo'  ])
        label.setAlignment(QtCore.Qt.AlignLeft)
        gridLayout.addWidget(label,0,1)
        gridLayout.setColumnMinimumWidth(1,DpiScale(220))
        gridLayout.setColumnStretch(1,50)
        
        # row for palettes
        self.fromPalette = _ComboBoxUI()
        palettes = xg.palettes()
        for pal in palettes:
            self.fromPalette.addItem(pal)
        self.connect(self.fromPalette, 
                     QtCore.SIGNAL("activated(const QString&)"), 
                     self.refresh)
        self.fromPalette.setMinimumWidth(DpiScale(220))
        gridLayout.addWidget(self.fromPalette,1,0)
        self.toPalette = _ComboBoxUI()
        self.toPalette.setToolTip(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCopyMoveDescription.kNewCollectionAnn'  ])
        self.toPalette.setMinimumWidth(DpiScale(220))
        gridLayout.addWidget(self.toPalette,1,1)

        # row for descriptions
        self.fromDescr = _ComboBoxUI()
        self.fromDescr.setMinimumWidth(DpiScale(220))
        gridLayout.addWidget(self.fromDescr,2,0)
        self.toDescr = QLineEdit()
        self.toDescr.setMinimumWidth(DpiScale(220))
        rx = QRegExp("[A-Za-z]+[A-Za-z0-9_]*")
        self.toDescr.setValidator(QRegExpValidator(rx,self))
        if(isMove):
            self.toDescr.setToolTip(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCopyMoveDescription.kNewNameMoveAnn'  ])
        else:
            self.toDescr.setToolTip(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCopyMoveDescription.kNewNameAnn'  ])
        
        gridLayout.addWidget(self.toDescr,2,1)
        fpal = str(self.fromPalette.currentText())
        descrs = xg.descriptions(fpal)
        if(isMove):
            descr = descrs[0]
        else:
            descr = descrs[0]+"_copy"
        self.toDescr.setText(descr)

        # row for description only check box
        self.descrOnly = QCheckBox(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCopyMoveDescription.kDescriptionOnly'  ])
        self.descrOnly.setChecked(True)
        self.descrOnly.setToolTip(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCopyMoveDescription.kIncludePatchBindingsAnn'  ])
        gridLayout.addWidget(self.descrOnly,3,0,1,2)

        # create row of buttons
        row = QWidget()
        hbox = QHBoxLayout()
        QLayoutItem.setAlignment(hbox, QtCore.Qt.AlignRight)
        hbox.setSpacing(DpiScale(15))
        hbox.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
        self.applyButton = QPushButton(type)
        self.applyButton.setDefault(True)
        self.applyButton.setAutoRepeat(False)
        self.applyButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCopyMoveDescription.kApplyAnn'  ] % type)
        self.connect(self.applyButton, QtCore.SIGNAL("clicked()"),self.applyCB)
        hbox.addWidget(self.applyButton)
        self.cancelButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCopyMoveDescription.kCancel'  ])
        self.cancelButton.setAutoRepeat(False)
        if(isMove):
            self.cancelButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCopyMoveDescription.kCancelAnn'  ])
        else:
            self.cancelButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCopyMoveDescription.kCancelDuplicationAnn'  ])
        self.connect(self.cancelButton, QtCore.SIGNAL("clicked()"),self.reject)
        hbox.addWidget(self.cancelButton)
        row.setLayout(hbox)
        layout.addWidget(row)
        self.setLayout(layout)
        self.refresh()

    def refresh(self):
        # put all palettes but the fromPalette into toPalette
        self.toPalette.clear()
        fpal = str(self.fromPalette.currentText())
        palettes = xg.palettes()
        for pal in palettes:
            if self.type == "Copy" or pal != fpal:
                self.toPalette.addItem(pal)
        # put all the descriptions for fromPalette into fromDescr
        self.fromDescr.clear()
        descrs = xg.descriptions(fpal)
        for descr in descrs:
            self.fromDescr.addItem(descr)
            
    def checkValid(self):
        if self.getToDescription() == "":
            tellem = QMessageBox()
            tellem.setText(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCopyMoveDescription.kYouMustSpecifyADestinationDescriptionName'  ])
            tellem.exec_()
            return False
        if ( self.type == "Copy" and
             self.getFromPalette() == self.getToPalette() and
             self.getFromDescription() == self.getToDescription() ):
            tellem = QMessageBox()
            tellem.setText(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCopyMoveDescription.kYouMustSpecifyADifferentName'  ])
            tellem.exec_()
            return False
        if ( cmds.objExists( self.getToDescription() ) and
             ( self.type == "Copy" or
               ( self.type == "Move" and
                 self.getToDescription() != self.getFromDescription() ) ) ):
            tellem = QMessageBox()
            tellem.setText(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCopyMoveDescription.kNameGivenForDescriptionAlreadyExitsInTheScene'  ])
            tellem.exec_()
            return False
        return True

    def applyCB(self):
        if self.checkValid():
            self.accept()
        
    def getFromPalette(self):
        return str(self.fromPalette.currentText())

    def getToPalette(self):
        return str(self.toPalette.currentText())

    def getFromDescription(self):
        return str(self.fromDescr.currentText())

    def getToDescription(self):
        return str(self.toDescr.text())

    def getDescriptionOnly(self):
        return not self.descrOnly.isChecked()


def copyDescription():
    """Function to copy a description using a dialog.
    """
    if len(xg.descriptions()) == 0:
        tellem = QMessageBox()
        tellem.setText(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCopyMoveDescription.kThereAreNoDescriptionsToCopy'  ])
        tellem.exec_()
        return
    # Save the scene before copy.
    # Copying description requires to export the original description.
    # When export a description with initial unsaved scene,
    # textures of xgen's map are not resolved. As we support
    # to export map, their texture (ptex) should be resolved before export.
    sceneName = saveScene()
    if len(sceneName) == 0:
        return

    dialog = CopyMoveDescriptionUI(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCopyMoveDescription.kDuplicate'  ],False)
    result = dialog.exec_()
    if result == QDialog.Accepted:
        pal = dialog.getToPalette()
        desc = dialog.getFromDescription()
        name = dialog.getToDescription()
        deo = dialog.getDescriptionOnly()
        if xgg.Maya:
            cmd = 'xgmCopyDescription -deo '+\
                  xg.boolToString(deo)+' -n "'+name+'" -p "'+pal+'" "'+desc+'"'
            mel.eval(cmd)
            if (xgg.DescriptionEditor != 0 ):
                xgg.DescriptionEditor.refresh("Full")
        else:
            goPort = QMessageBox()
            goPort.setText(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCopyMoveDescription.kCopyDescriptionOnlyAvailableInMaya'  ])
            goPort.exec_()

                
def moveDescription():
    """Function to move a description using a dialog.
    """
    if len(xg.descriptions()) == 0 or len(xg.palettes()) < 2:
        tellem = QMessageBox()
        tellem.setText(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCopyMoveDescription.kThereAreNoDescriptionsThatCanBeMoved'  ])
        tellem.exec_()
        return

    # Save the scene before move.
    # Moving description requires to export the original description.
    # When export a description with initial unsaved scene,
    # textures of xgen's map are not resolved. As we support
    # to export map, their texture (ptex) should be resolved before export.
    sceneName = saveScene()
    if len(sceneName) == 0:
        return

    dialog = CopyMoveDescriptionUI(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCopyMoveDescription.kMove'  ],True)
    result = dialog.exec_()

    if result == QDialog.Accepted:
        pal = dialog.getToPalette()
        desc = dialog.getFromDescription()
        name = dialog.getToDescription()
        deo = dialog.getDescriptionOnly()
        if xgg.Maya:
            cmd = 'xgmMoveDescription -deo '+ xg.boolToString(deo)+' -n "'+name+'" -p "'+pal+'" "'+desc+'"'
            mel.eval(cmd)
            if (xgg.DescriptionEditor != 0 ):
                xgg.DescriptionEditor.refresh("Full")
        else:
            goPort = QMessageBox()
            goPort.setText(maya.stringTable[ u'y_xgenm_ui_dialogs_xgCopyMoveDescription.kMoveDescriptionOnlyAvailableInMaya'  ])
            goPort.exec_()


