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
# @file __init__.py
# @brief Package definition for widgets.
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
# @version Created 06/01/09
#

from .xgCheckBoxUI import CheckBoxUI
from .xgEnumUI import EnumUI
from .xgExpandUI import ExpandUI
from .xgFloatUI import FloatUI
from .xgIntegerUI import IntegerUI
from .xgRadioUI import RadioUI
from .xgTextEditUI import TextEditUI
from .xgTextUI import TextUI
from .xgToolBarUI import ToolBarUI

from .xgArchiveFilesUI import ArchiveFilesUI
from .xgAttrEdUI import AttrEdUI
from .xgAttrFloatFieldSliderUI import AttrFloatFieldSliderUI
from .xgBrowseUI import BrowseUI
from .xgBrowseUI import FileBrowserUI
from .xgExpressionUI import ExpressionUI
from .xgExpressionUI import ColorExpressionUI
from .xgFileBrowserUI import fileBrowserDlg
from .xgPlugWatcher import PlugWatcher
from .xgRampUI import RampUI
from .xgStackUI import StackUI

