from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *

	
# QToolButton flat style
ToolButtonFlatStyle = r'QToolButton { border: none; }'

# QToolButton push button like flat style
ToolButtonPushFlatStyle = (r'''
    QToolButton
    {
        background-color: #5D5D5D;
        border: 1px solid #626262;
    }
    QToolButton::hover
    {
        background-color: #707070;
        border: 1px solid #757575;
    }
    QToolButton::pressed
    {
        color: #EEEEEE;
        background-color: #1D1D1D;
        border: 1px solid #191919;
    }
    QToolButton::disabled
    {
        color: #808080;
        background-color: #4B4B4B;
        border: 1px solid #4D4D4D;
    }
    QToolButton::menu-indicator
    {
        image: url(:/empty.png);
    }
''')

# QTreeWidget header style
TreeWidgetHeaderFlatStyle = (r'''
    QHeaderView::section:horizontal
    {
        border: 1px solid #2B2B2B;
        border-right-style: none;
        padding: 1px;
    }
    QHeaderView::section:horizontal::last
    {
        border-right-style: solid;
    }''')

# Shelf buttons (QToolButton)
ShelfToolButtonSize = QSize(42, 41)

# Tab buttons (QToolButton)
TabToolButtonSize = QSize(22, 21)

# Groom brush buttons (QToolButton)
GroomBrushButtonSize = QSize(55, 41)
GroomEditButtonSize  = QSize(80, 41)

# Interactive Groom Spline brush buttons (QToolButton)
IgGroomBrushButtonSize = QSize(55, 41)


# ===========================================================================
# Copyright 2021 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
