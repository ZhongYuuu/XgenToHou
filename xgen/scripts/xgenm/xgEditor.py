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

#!/usr/bin/env python
#
# @file xgEditor.py
# @brief Contains the Stand-alone XGen Description Editor.
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
# @version Created 05/05/10

import sys
import optparse
import signal
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *
import xgenm as xg
import xgenm.ui.xgDescriptionEditor

#
# The basics for this came from /home/fahome/bwherry/python/styleitdark.py
# to match dlight, which is to match maya
#

def getDefaultFont():
    return QFont("Arial", 10)
def getPlastiqueStyle():
    return QStyleFactory.create('Plastique')
def getDarkColorPalette():
    ''' Light text on dark background.
    '''
    pal = QPalette()
    # active and inactive colors (same)
    for group in [QPalette.Active, QPalette.Inactive]:
        pal.setColor(group, QPalette.Window, QColor(68, 68, 68, 255))
        pal.setColor(group, QPalette.WindowText, QColor(200, 200, 200, 255))
        pal.setColor(group, QPalette.Base, QColor(42, 42, 42, 255))
        pal.setColor(group, QPalette.AlternateBase, QColor(59, 59, 59, 255))
        pal.setColor(group, QPalette.ToolTipBase, QColor(246, 255, 210, 255))
        pal.setColor(group, QPalette.ToolTipText, QColor(0, 0, 0, 255))
        pal.setColor(group, QPalette.Text, QColor(200, 200, 200, 255))
        pal.setColor(group, QPalette.ButtonText, QColor(200, 200, 200, 255))
        pal.setColor(group, QPalette.BrightText, QColor(254, 254, 254, 255))
        pal.setColor(group, QPalette.Light, QColor(81, 81, 81, 255))
        pal.setColor(group, QPalette.Midlight, QColor(71, 71, 71, 255))
        pal.setColor(group, QPalette.Button, QColor(96, 96, 96, 255))
        pal.setColor(group, QPalette.Mid, QColor(45, 45, 45, 255))
        pal.setColor(group, QPalette.Dark, QColor(30, 30, 30, 255))
        pal.setColor(group, QPalette.Shadow, QColor(0, 0, 0, 255))
        pal.setColor(group, QPalette.Highlight, QColor(103, 95, 92, 255))
        pal.setColor(group, QPalette.HighlightedText, QColor(252, 252, 252, 255))
    # disabled colors
    pal.setColor(QPalette.Disabled, QPalette.Window, QColor(68, 68, 68, 255))
    pal.setColor(QPalette.Disabled, QPalette.WindowText, QColor(200, 200, 200, 128))
    pal.setColor(QPalette.Disabled, QPalette.Base, QColor(42, 42, 42, 255))
    pal.setColor(QPalette.Disabled, QPalette.AlternateBase, QColor(59, 59, 59, 255))
    pal.setColor(QPalette.Disabled, QPalette.ToolTipBase, QColor(246, 255, 164, 255))
    pal.setColor(QPalette.Disabled, QPalette.ToolTipText, QColor(0, 0, 0, 255))
    pal.setColor(QPalette.Disabled, QPalette.Text, QColor(200, 200, 200, 128))
    pal.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(200, 200, 200, 128))
    pal.setColor(QPalette.Disabled, QPalette.BrightText, QColor(254, 254, 254, 128))
    pal.setColor(QPalette.Disabled, QPalette.Light, QColor(81, 81, 81, 255))
    pal.setColor(QPalette.Disabled, QPalette.Midlight, QColor(71, 71, 71, 255))
    pal.setColor(QPalette.Disabled, QPalette.Button, QColor(96, 96, 96, 255))
    pal.setColor(QPalette.Disabled, QPalette.Mid, QColor(45, 45, 45, 255))
    pal.setColor(QPalette.Disabled, QPalette.Dark, QColor(30, 30, 30, 255))
    pal.setColor(QPalette.Disabled, QPalette.Shadow, QColor(0, 0, 0, 128))
    pal.setColor(QPalette.Disabled, QPalette.Highlight, QColor(103, 95, 92, 255))
    pal.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(252, 252, 252, 128))

    return pal


def importFile( option, opt_str, value, parser ):
    xg.importPalette(value,parser.values.delta,parser.values.nameSpace)
    parser.values.delta = []
    parser.values.nameSpace = ""
    

if __name__ == "__main__":

    # instatiate an option parser
    parser = optparse.OptionParser(usage="usage: %prog [[-n <nameSpace>] [-d <delta.xgd>]+ -f <file.xgen>]+")
    parser.add_option(
        '-n','--nameSpace',
        dest='nameSpace',
        default="",
        help='nameSpace for collection',
        metavar='string')
    parser.add_option(
        '-d','--delta',
        dest='delta',
        action="append",
        default=[],
        help='delta to apply onto collection',
        metavar='FILE')
    parser.add_option(
        '-f','--fileName',
        action="callback",
        type="string",
        callback=importFile,
        help='XGen collection file',
        metavar='FILE')
    parser.parse_args()  # no need to grab results since handled in callback
    
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    QApplication.setDesktopSettingsAware(False)
    app = QApplication(sys.argv)
    app.setStyle(getPlastiqueStyle())
    app.setPalette(getDarkColorPalette())
    app.setFont(getDefaultFont())
    xg.ui.createDescriptionEditor()
    sys.exit(app.exec_())
