from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from shiboken2 import wrapInstance

import xgenm as xg
import xgenm.ui as xgui
import xgenm.xgGlobal as xgg

import maya.cmds as cmds
import maya.mel as mel
import maya
import maya.utils as utils
from maya import OpenMayaUI as omui

from xgenm.ui.widgets.xgIgValueSliderUI import *
from xgenm.ui.widgets.xgTextUI import TextUI
from xgenm.ui.util.xgUtil import DpiScale

def ConvertSplineToGeometry():
	cmds.xgmSplineGeometryConvert()



# ===========================================================================
# Copyright 2021 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
