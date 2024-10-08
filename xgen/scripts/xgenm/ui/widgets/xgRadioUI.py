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
# @file xgRadioUI.py
# @brief Contains the UI for radio buttons.
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
# @version Created 06/30/09
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


class RadioUI(QWidget):
    """A widget for selecting amoung values via radio buttons.

    This provides for the label and the radio buttons.
    """
    def __init__(self,attr,values,help="",object="",mainlabel=""):
        QWidget.__init__(self)
        self.attr = attr
        self.object = object
        
        self.setAccessibleName(r'XgRadioUI')
        
        # Widgets
        if mainlabel != "":
            self.label = QLabel(mainlabel)

        elif object == "":
            self.label = QLabel(attr)

        else:
            self.label = QLabel(makeLabel(attr))
        self.label.setFixedWidth(labelWidth())
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        self.label.setIndent(DpiScale(10))
        # Horizontal layout
        layout = QHBoxLayout()
        QLayoutItem.setAlignment(layout, QtCore.Qt.AlignLeft)
        layout.setSpacing(DpiScale(3))
        layout.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
        layout.addWidget(self.label)
        # Add buttons
        self.buttons = []
        for value in values:
            self.buttons.append( QRadioButton(value) )
            layout.addWidget(self.buttons[len(self.buttons)-1])
        self.setLayout(layout)
        self.setToolTip(help)
        self.connectIt()

    def value(self):
        index = 0
        while not self.buttons[index].isChecked():
            index = index+1
        return str(index)

    def setValue(self,value):
        index = int(value)
        self.buttons[index].setChecked(True)

    def toggleChanged(self,state):
        if state:
            xgg.DescriptionEditor.setAttrCmd(self.object,self.attr,self.value())
            xgg.DescriptionEditor.playblast()

    def connectIt(self):
        if self.object=="" or xgg.DescriptionEditor is None:
            return
        # Only need to connect one since we are tracking toggled
        for i in range(len(self.buttons)):
            self.connect(self.buttons[i],QtCore.SIGNAL("toggled(bool)"), self.toggleChanged)

    def refresh(self):
        if self.object=="" or xgg.DescriptionEditor is None:
            return
        de = xgg.DescriptionEditor
        value = de.getAttr(self.object,self.attr)
        self.setValue(value)

