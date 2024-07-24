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

##
# @file xgTextEditUI.py
# @brief Contains the UI for text editor
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
# @version Created 02/15/11
#

import string
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *
import xgenm as xg
import xgenm.xgGlobal as xgg
from xgenm.ui.util.xgUtil import *


class TextEditUI(QWidget):
    """A widget for editing a text value.

    This provides for the label and an text entry box.
    """
    def __init__(self,attr,help="",object="",width=0,mainlabel=""):
        QWidget.__init__(self)
        
        self.setAccessibleName(r'XgTextEditUI')
        
        self.attr = attr
        self.object = object
        self.dirty = False
        # Widgets
        if mainlabel != "":
            label = QLabel(mainlabel)
        elif object == "":
            label = QLabel(attr)
        else:
            label = QLabel(makeLabel(attr))
        label.setFixedWidth(labelWidth())
        label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop)
        label.setIndent(DpiScale(10))
        self.textEdit = QTextEdit()
        self.textEdit.setUndoRedoEnabled(True)
        self.textEdit.setWordWrapMode(QTextOption.NoWrap)
        self.textEdit.setAcceptRichText(False)
        if width:
            self.textEdit.setFixedWidth(DpiScale(width))
        filler = QWidget()
        # Horizontal layout
        layout = QHBoxLayout()
        QLayoutItem.setAlignment(layout, QtCore.Qt.AlignLeft)
        layout.addWidget(label)
        layout.addWidget(self.textEdit)
        layout.setSpacing(DpiScale(3))
        layout.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
        self.setLayout(layout)
        self.setToolTip(help)
        self.connectIt()

    def value(self):
        return xg.prepForAttribute(str(self.textEdit.toPlainText()))

    def setValue(self,value):
        self.textEdit.setPlainText(xg.prepForEditor(str(value)))

    def connectIt(self):
        if self.object=="" or xgg.DescriptionEditor is None:
            return
        de = xgg.DescriptionEditor
        # track when the value has changed and therefore dirty
        self.connect(self.textEdit,QtCore.SIGNAL("textChanged()"),
                     lambda: self.setDirty())
        # Warning: override the default focusOutEvent method on the embedded
        # textEdit widget. the more correct way to do this would be to derive
        # our own textEdit and implement the method. 
        self.textEdit.focusOutEvent = self.updateValue

    def refresh(self):
        if self.object=="" or xgg.DescriptionEditor is None:
            return
        de = xgg.DescriptionEditor
        value = de.getAttr(self.object,self.attr)
        self.setValue(value)

    def setDirty(self):
        self.dirty = True

    def updateValue(self,event):
        if self.dirty:
            de = xgg.DescriptionEditor
            de.setAttrCmd( self.object, self.attr, self.value() )
            self.dirty=False
        QTextEdit.focusOutEvent(self.textEdit,event)
