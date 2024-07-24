#**************************************************************************/
# Copyright (c) 2013 Autodesk, Inc.
# All rights reserved.
#
# These coded instructions, statements, and computer programs contain
# unpublished proprietary information written by Autodesk, Inc., and are
# protected by Federal copyright law. They may not be disclosed to third
# parties or copied or duplicated in any form, in whole or in part, without
# the prior written consent of Autodesk, Inc.
#**************************************************************************/

from builtins import range
import string
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *
import xgenm as xg
from xgenm.ui.util.xgUtil import *


class ExpandUIHeader(QWidget):
    """implements the clickable title part of collapsible frame
    """

    # Height of the header frame
    headerHeight = 20

    def __init__(self, expanded, text):
        QWidget.__init__(self)
        self.setAccessibleName(r'XgExpandUIHeader')

        # Compute the height from the current font height
        self.headerHeight = self.fontMetrics().height() + 9

        self.setMinimumHeight(self.headerHeight)
        self.setMinimumWidth(DpiScale(32))
        self.expanded = expanded
        self.text = text

    def setExpanded(self, expanded):
        self.expanded = expanded
        self.update()
        
    def paintEvent(self,event):
        ''' Paint the header of the frame layout '''
        painter         = QStylePainter(self)
        rectangle       = self.rect()
        rectangle.setHeight(self.headerHeight)
        
        # Draw the frame layout header
        palette = self.palette()
        brush   = QBrush(Qt.SolidPattern)
        brush.setColor(palette.button().color())
        painter.setBrush(brush)
        painter.setPen(QtCore.Qt.NoPen)

        rad = 2 #self.style().styleHint(self.SH_MayaRoundedRectRadius)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.drawRoundedRect(rectangle.adjusted(0,1,0,-1), rad, rad)
        
        # Draw the collapse indicator
        arrowIcon = QStyle.PE_IndicatorArrowDown if self.expanded else QStyle.PE_IndicatorArrowRight
        option = QStyleOptionButton()
        option.initFrom(self)
        option.rect.setHeight(self.headerHeight-2)
        option.rect.setWidth(self.headerHeight-2)
        option.rect.setLeft(self.style().pixelMetric(QStyle.PM_ButtonMargin))
        painter.drawPrimitive(arrowIcon, option)
        
        # Draw the frame text
        rectangle.setLeft(rectangle.left() +
            self.style().pixelMetric(QStyle.PM_ButtonMargin) + self.headerHeight)
        penText  = QPen( palette.color( QPalette.Normal if self.isEnabled() else QPalette.Disabled, QPalette.WindowText ) )
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(penText)
        painter.drawText(rectangle, Qt.AlignLeft | Qt.AlignVCenter, self.text)

    def mouseReleaseEvent(self, mouseEvent):
        self.parentWidget().expandSlot(self.expanded)
        
class ExpandUIFrame(QFrame):
    """Implements the frame with shaded background
    """
    kFrameLayoutBackgroundShade = QColor(73, 73, 73)
    
    def __init__(self):
        QFrame.__init__(self)
        
        self.setAccessibleName(r'XgExpandUIFrame')
        
    def paintEvent(self, event):
        ''' Paint the frame body of the frame layout '''

        painter     = QStylePainter(self)
        brush       = QBrush(Qt.SolidPattern)
        brush.setColor(self.kFrameLayoutBackgroundShade)
        painter.fillRect(self.rect().adjusted(2,2,-2,-2), brush)
        
        QFrame.paintEvent(self, event)

class ExpandUI(QWidget):
    """A widget for collapsible frames.
    """
    def __init__(self, text, expanded=True):
        QWidget.__init__(self)
        self.expanded = expanded
        self.setAccessibleName(r'XgExpandUI')

        # Ensure global app exists, this will create it if it does not yet, ExpandUIHeader depends on it
        # and may get assigned an invalid style which can result on crash on refresh
        QApplication.instance()

        # Layout for expandable layout contents
        self.contents = ExpandUIFrame()
        self.contents.setFrameStyle(QFrame.NoFrame)
        self.contentsLayout = QVBoxLayout()
        self.contentsLayout.setSpacing(DpiScale(0))
        self.contentsLayout.setContentsMargins(DpiScale(2),DpiScale(2),DpiScale(2),DpiScale(2))
        self.contents.setLayout(self.contentsLayout)

        # Pull it all together
        mainLayout = QVBoxLayout()
        mainLayout.setSpacing(DpiScale(0))
        mainLayout.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))
        self.header = ExpandUIHeader(self.expanded,text)
        mainLayout.addWidget(self.header)
        mainLayout.addWidget(self.contents)
        self.setLayout(mainLayout)

        self.setExpanded(expanded)

    def refresh(self):
        return

    def addWidget(self, widget):
        self.contentsLayout.addWidget(widget)
        if not self.expanded:
            self.contents.hide()
            
    def addSpacing(self, s):
        self.contentsLayout.addSpacing(DpiScale(s))
        if not self.expanded:
            self.contents.hide()

    def expandSlot(self, checked):
        self.setExpanded(not self.expanded)

    def setExpanded(self, expand):
        if self.expanded == expand:
            return
        self.header.setExpanded(expand)
        if expand:
            self.contents.show()
        else:
            self.contents.hide()
        self.expanded = expand

    def cleanScriptJob(self):        
        for i in range( self.contentsLayout.count() ):  
            try:
                self.contentsLayout.itemAt(i).widget().cleanScriptJob()
            except:
                pass            
