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
# @file xgToolBarUI.py
# @brief Contains a simplified replacement for QToolBar 
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

import string
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *

import xgenm as xg
import xgenm.xgGlobal as xgg
from xgenm.ui.util.xgUtil import *


class ToolBarUI(QWidget):
    """A simplified replacement for QToolBar.

    This better allows control over the buttons so that menus can be
    added, icons sized, and the spcing controled.
    """
    def __init__(self,iconSize,spacing=0):
        QWidget.__init__(self)
        
        self.setAccessibleName(r'XgToolBarUI')
        
        layout = QHBoxLayout()
        layout.setSpacing(DpiScale(spacing))
        layout.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))
        QLayoutItem.setAlignment(layout, QtCore.Qt.AlignLeft)
        layout.setSizeConstraint( QLayout.SetFixedSize )
        self.setLayout(layout)
        self.iconSize = iconSize
        self.setMinimumWidth(DpiScale(100))

    def addButton(self,icon,tip,callable):
        self.button = ToolBarButton()
        self.button.setIcon(CreateIcon(icon))
        self.button.setIconSize(DpiScalesz(self.iconSize))
        self.button.setToolTip(tip)
        self.button.setAutoRaise(True)
        self.button.setPopupMode(QToolButton.DelayedPopup)
        self.connect(self.button,
                     QtCore.SIGNAL("clicked()"),
                     callable)
        self.layout().addWidget(self.button)
        return self.button
    

'''
    Custom QToolButton to handle more events
'''
class ToolBarButton(QToolButton):
    
    # Signals
    doubleClicked = QtCore.Signal()
    
    def __init__(self, parent=None):
        ''' Constructor '''
        QToolButton.__init__(self, parent)
        
        self.setAccessibleName(r'XgToolBarButton')
        
    def mouseDoubleClickEvent(self, event):
        ''' Invoked when double clicked '''
        QToolButton.mouseDoubleClickEvent(self, event)
        
        # Emit doubleClicked signal
        self.doubleClicked.emit()
        
