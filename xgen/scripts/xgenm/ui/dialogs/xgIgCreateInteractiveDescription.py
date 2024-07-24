import maya
maya.utils.loadStringResourcesForModule(__name__)

from builtins import object
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from shiboken2 import wrapInstance
import xgenm as xg
import xgenm.ui as xgui
import xgenm.xgGlobal as xgg
if xgg.Maya:
    import maya.cmds as cmds
    import maya.mel as mel
    import maya
    import maya.utils as utils
    from maya import OpenMayaUI as omui

from xgenm.ui.widgets.xgIgValueSliderUI import *
from xgenm.ui.widgets.xgTextUI import TextUI
from xgenm.ui.util.xgUtil import DpiScale
import sys

long_type = int if sys.version_info[0] >= 3 else long

InteractiveSplineWnd = ""

# Class to hold the UI data
class CreateInteractiveSplineSetting(object):
    """A simple class to hold the data setting from UI.
    """
    def __init__(self):
        # default values
        self.loadDefaults()

        # keys for optionVar
        self.kNewDescriptionName = 'xgIgCreate_newDescriptionName'
        self.kGeneratorSeed       = 'xgIgCreate_generatorSeed'
        self.kDensity             = 'xgIgCreate_density'
        self.kLength              = 'xgIgCreate_length'
        self.kWidth               = 'xgIgCreate_width'
        self.kCvCountTypeIsGlobal = 'xgIgCreate_cvCountTypeIsGlobal'
        self.kCvCount             = 'xgIgCreate_cvCount'

    def debug(self):
        # For debug
        print("\n\n")
        print("newDescriptionName=%s\n" % self.newDescriptionName)
        print("generatorSeed=%d\n" % self.generatorSeed)
        print("density=%f\n" % self.density)
        print("length=%f\n" % self.length)
        print("width=%f\n" % self.width)
        print("cvCountTypeIsGlobal=%d\n" % self.cvCountTypeIsGlobal)
        print("cvCount=%d\n\n" % self.cvCount)


    def saveToMayaOptionVar(self):
        if cmds :
            cmds.optionVar(stringValue = (self.kNewDescriptionName, self.newDescriptionName))
            cmds.optionVar(intValue   = (self.kGeneratorSeed,       self.generatorSeed))
            cmds.optionVar(floatValue = (self.kDensity,             self.density))
            cmds.optionVar(floatValue = (self.kLength,              self.length))
            cmds.optionVar(floatValue = (self.kWidth,               self.width))
            cmds.optionVar(intValue   = (self.kCvCountTypeIsGlobal, self.cvCountTypeIsGlobal))
            cmds.optionVar(intValue   = (self.kCvCount ,            self.cvCount))

    def loadFromMayaOptionVar(self):
        if cmds :
            if cmds.optionVar(exists=self.kNewDescriptionName):
                self.newDescriptionName = cmds.optionVar(query=self.kNewDescriptionName)
            if cmds.optionVar(exists=self.kGeneratorSeed):
                self.generatorSeed = cmds.optionVar(query=self.kGeneratorSeed)
            if cmds.optionVar(exists=self.kDensity):
                self.density = cmds.optionVar(query=self.kDensity)
            if cmds.optionVar(exists=self.kLength):
                self.length = cmds.optionVar(query=self.kLength)
            if cmds.optionVar(exists=self.kWidth):
                self.width = cmds.optionVar(query=self.kWidth)
            if cmds.optionVar(exists=self.kCvCountTypeIsGlobal):
                self.cvCountTypeIsGlobal = cmds.optionVar(query=self.kCvCountTypeIsGlobal)
            if cmds.optionVar(exists=self.kCvCount):
                self.cvCount = cmds.optionVar(query=self.kCvCount)

    def loadDefaults(self):
        # default values
        self.newDescriptionName = "description1"
        self.generatorSeed       = 0
        self.density             = 10.0
        self.length              = 1.0
        self.width               = 0.1
        self.cvCountTypeIsGlobal = True
        self.cvCount             = 5

# UI
class InteractiveSplineWindow(QMainWindow):
    """A window for configuring interactive spline description creating.
    """

    def __init__(self):
        QMainWindow.__init__(self)

        self.area = 0.0
        self.jobId = -1

        # Main window used as a parent widget here
        mayaMainWindowPtr = omui.MQtUtil.mainWindow()
        mayaMainWindow = wrapInstance(long_type(mayaMainWindowPtr), QWidget)

        # Set window property
        self.setParent(mayaMainWindow)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Window)
        self.hide()
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        # Create an internal data for holding the UI data, initial data from optionVar
        self.initSetting = CreateInteractiveSplineSetting()
        self.initSetting.loadFromMayaOptionVar()

        # Window title
        self.setWindowTitle(maya.stringTable[ u'y_xgenm_ui_dialogs_xgIgCreateInteractiveDescription.kCreateInteractiveDescriptionTitle'  ])

        # Create menus
        self.__createMenus()

        # Fixed size
        self.setFixedSize(DpiScale(480), DpiScale(250))

        # Set Central widget with grid layout
        centralWidget = QWidget()
        gridLayout = QGridLayout()
        centralWidget.setLayout(gridLayout)
        self.setCentralWidget(centralWidget)

        # width for "label"+"edit"+"slider"
        textUIWidth   = 150
        editUIWidth   = 100
        sliderUIWidth = 180

        # New Description Name Label
        self.newDescriptionNameLabelUI = QLabel(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgCreateInteractiveDescription.kNewDescriptionName' ])
        #self.newDescriptionNameLabelUI.setToolTip(annotation)
        self.newDescriptionNameLabelUI.setFixedWidth(DpiScale(textUIWidth))
        self.newDescriptionNameLabelUI.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        gridLayout.addWidget(self.newDescriptionNameLabelUI, 0, 0)

        # New Description Name Value Field
        self.newDescriptionNameUI = QLineEdit()
        self.newDescriptionNameUI.setFixedWidth(DpiScale(160))
        self.newDescriptionNameUI.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        rx = QRegExp("[A-Za-z]+[A-Za-z0-9_]*")
        self.newDescriptionNameUI.setValidator(QRegExpValidator(rx,self))
        gridLayout.addWidget(self.newDescriptionNameUI, 0, 1, 1, 2)

        # Generator Seed - int
        self.genSeedIntUI = IgIntSliderUI(
                maya.stringTable[u'y_xgenm_ui_dialogs_xgIgCreateInteractiveDescription.kGeneratorSeed' ],
                maya.stringTable[u'y_xgenm_ui_dialogs_xgIgCreateInteractiveDescription.kGeneratorSeedAnno' ],
                False,
                0, 100000, 0, 10000,
                gridLayout, 1,
                textUIWidth, editUIWidth, sliderUIWidth)
        self.genSeedIntUI.setValue(self.initSetting.generatorSeed)

        # Density
        maxDensity = cmds.xgmCreateSplineDescription(q=True, maxDensity=True)
        self.densityFloatUI = IgFloatSliderUI(
                maya.stringTable[u'y_xgenm_ui_dialogs_xgIgCreateInteractiveDescription.kDensity' ],
                maya.stringTable[u'y_xgenm_ui_dialogs_xgIgCreateInteractiveDescription.kDensityAnno' ],
                True,
                0.0, maxDensity, 0.0, 100.0,
                gridLayout, 2,
                textUIWidth, editUIWidth, sliderUIWidth)
        self.densityFloatUI.setValue(self.initSetting.density)
        self.connect(self.densityFloatUI.sliderUI, QtCore.SIGNAL("valueChanged(int)"), self.__onDensityChanged)

        # Spline count Label
        self.splineCountLabelUI = QLabel(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgCreateInteractiveDescription.kApprSplinesCount' ])
        splineCountLabelAnno = maya.stringTable[u'y_xgenm_ui_dialogs_xgIgCreateInteractiveDescription.kSplinesCountAnno' ]
        self.splineCountLabelUI.setToolTip(splineCountLabelAnno)
        self.splineCountLabelUI.setFixedWidth(DpiScale(textUIWidth))
        self.splineCountLabelUI.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        gridLayout.addWidget(self.splineCountLabelUI, 3, 0)

        # Spline count 
        #read only
        self.splineCountUI = QLineEdit()
        self.splineCountUI.setFixedWidth(DpiScale(editUIWidth))
        self.splineCountUI.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        rx = QRegExp("[0-9]*")
        self.splineCountUI.setValidator(QRegExpValidator(rx,self))
        self.splineCountUI.setReadOnly(True)
        #TODO: update the text when density value is changed.
        self.splineCountUI.setText(r'0')
        self.splineCountUI.setStyleSheet("QLineEdit { background-color : rgb(64,64,64); }" )
        gridLayout.addWidget(self.splineCountUI, 3, 1)
        self.__onDensityChanged(0)

        # Length
        maxLength = cmds.xgmCreateSplineDescription(q=True, maxLength=True)
        self.lengthFloatUI = IgFloatSliderUI(
                maya.stringTable[u'y_xgenm_ui_dialogs_xgIgCreateInteractiveDescription.kLength' ],
                maya.stringTable[u'y_xgenm_ui_dialogs_xgIgCreateInteractiveDescription.kLengthAnno' ],
                True,
                0.0, maxLength, 0.0, 100.0,
                gridLayout, 4,
                textUIWidth, editUIWidth, sliderUIWidth)
        self.lengthFloatUI.setValue(self.initSetting.length)

        # Width
        self.widthFloatUI = IgFloatSliderUI(
                maya.stringTable[u'y_xgenm_ui_dialogs_xgIgCreateInteractiveDescription.kWidth' ],
                maya.stringTable[u'y_xgenm_ui_dialogs_xgIgCreateInteractiveDescription.kWidthAnno' ],
                True,
                0.0, 1000.0, 0.0, 1.0,
                gridLayout, 5,
                textUIWidth, editUIWidth, sliderUIWidth)
        self.widthFloatUI.setValue(self.initSetting.width)

        #TO DO: enable the feature if it's ready in the future.
        # CV Count
        maxCVCount = cmds.xgmCreateSplineDescription(q=True, maxCVs=True)
        self.cvCountIntUI = IgIntSliderUI(
                maya.stringTable[u'y_xgenm_ui_dialogs_xgIgCreateInteractiveDescription.kCVCount' ],
                maya.stringTable[u'y_xgenm_ui_dialogs_xgIgCreateInteractiveDescription.kCVCountAnno' ],
                False,
                0, maxCVCount, 0, 1000,
                gridLayout, 7,
                textUIWidth, editUIWidth, sliderUIWidth)
        self.cvCountIntUI.setValue(self.initSetting.cvCount)

        # Buttons
        buttonHeight = DpiScale(26)
        buttonRowWidget = QWidget()
        buttonRowHLayout = QHBoxLayout()
        buttonRowHLayout.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))
        buttonRowHLayout.setSpacing(DpiScale(3))
        buttonRowWidget.setLayout(buttonRowHLayout)

        self.createButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_dialogs_xgIgCreateInteractiveDescription.kCreate'  ])
        self.createButton.setFixedHeight(buttonHeight)
        self.connect(self.createButton, QtCore.SIGNAL("clicked()"), self.__onClickCreateButton)
        buttonRowHLayout.addWidget(self.createButton)

        self.applyButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_dialogs_xgIgCreateInteractiveDescription.kApply'  ])
        self.applyButton.setFixedHeight(buttonHeight)
        self.connect(self.applyButton, QtCore.SIGNAL("clicked()"), self.__onClickApplyButton)
        buttonRowHLayout.addWidget(self.applyButton)

        self.closeButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_dialogs_xgIgCreateInteractiveDescription.kClose'  ])
        self.closeButton.setFixedHeight(buttonHeight)
        self.connect(self.closeButton, QtCore.SIGNAL("clicked()"), self.__onClickCloseButton)
        buttonRowHLayout.addWidget(self.closeButton)

        gridLayout.addWidget(buttonRowWidget, 9, 0, 1, 3)

    def __createMenus(self):

        # Edit menu
        editMenu = self.menuBar().addMenu(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgCreateInteractiveDescription.kEdit' ])
        editMenu.addAction(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgCreateInteractiveDescription.kResetSettings' ], self.__onMenuResetSettings)

        # Help menu
        helpMenu = self.menuBar().addMenu(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgCreateInteractiveDescription.kHelp' ])
        helpMenu.addAction(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgCreateInteractiveDescription.kHelpMenu' ], self.__onMenuHelp)

    def __onMenuResetSettings(self):
        # Default Data ---> UI
        self.initSetting.loadDefaults()
        self.__refresh()

    def __onMenuHelp(self):
        # Navigate to an online help web page
        cmds.showHelp(r'CreateInteractiveGroomSplines')

    def __onDensityChanged(self, v):
        #update primitive count value
        self.splineCountUI.setText(str((int)(self.area * (float)(self.densityFloatUI.valueUI.text()))))

    def __onClickCreateButton(self):
        self.__onClickApplyButton()

        # Close window
        self.close()

    def __onClickApplyButton(self):
        # UI ---> Data && optionVar
        self.initSetting.newDescriptionName = str(self.newDescriptionNameUI.text())
        self.initSetting.generatorSeed       = int(self.genSeedIntUI.value())
        self.initSetting.density             = float(self.densityFloatUI.value())
        self.initSetting.length              = float(self.lengthFloatUI.value())
        self.initSetting.width               = float(self.widthFloatUI.value())
        self.initSetting.cvCount             = int(self.cvCountIntUI.value())
        self.initSetting.saveToMayaOptionVar()

        try:
            cmds.xgmCreateSplineDescription (
                createDefaultHair=True,
                name=self.initSetting.newDescriptionName,
                density=self.initSetting.density,
                length=self.initSetting.length,
                widthScale=self.initSetting.width,
                cvCount=self.initSetting.cvCount,
                generatorSeed=self.initSetting.generatorSeed)
        except:
            print(maya.stringTable[ u'y_xgenm_ui_dialogs_xgIgCreateInteractiveDescription.kNoBoundMesh'  ])
            pass
        xgui.createIgSplineEditor()

    def __onClickCloseButton(self):
        self.initSetting.loadFromMayaOptionVar()
        self.close()

    def closeEvent(self, event):
        if self.jobId >= 0:
            cmds.scriptJob(kill=self.jobId, force=True)
            jobId = -1
        event.accept()

    def __refresh(self):
        # Data ---> UI
        self.newDescriptionNameUI.setText(self.initSetting.newDescriptionName)
        self.genSeedIntUI.setValue(self.initSetting.generatorSeed)

        self.densityFloatUI.setValue(self.initSetting.density)
        self.lengthFloatUI.setValue(self.initSetting.length)
        self.widthFloatUI.setValue(self.initSetting.width)
        self.cvCountIntUI.setValue(self.initSetting.cvCount)

    def setCurArea(self, area):
        self.area = area
        self.__onDensityChanged(0)

    def run(self):
        self.__refresh()
        self.showNormal()

def updateSelChangedForGroomCreate():
    global InteractiveSplineWnd
    if InteractiveSplineWnd != "":
        area = cmds.xgmCreateSplineDescription (
            query=True,
            area=True)
        InteractiveSplineWnd.setCurArea(area)

def createSelChangedJob():
    """ Detect selection change.
    """
    global InteractiveSplineWnd
    InteractiveSplineWnd.jobId = cmds.scriptJob(event=["SelectionChanged", updateSelChangedForGroomCreate], killWithScene=True)

def createInteractiveSplineWindow():
    """Function to create the interactive spline window
    """

    area = cmds.xgmCreateSplineDescription (
            query=True,
            area=True)
    global InteractiveSplineWnd
    if InteractiveSplineWnd != "":
        InteractiveSplineWnd.setCurArea(area)
        createSelChangedJob()
        InteractiveSplineWnd.run()
    else:
        wnd = InteractiveSplineWindow()
        InteractiveSplineWnd = wnd
        InteractiveSplineWnd.setCurArea(area)
        createSelChangedJob()
        wnd.run()

def createInteractiveSplines():
    initSetting = CreateInteractiveSplineSetting()
    initSetting.loadFromMayaOptionVar()

    cmds.xgmCreateSplineDescription (
        createDefaultHair=True,
        name=initSetting.newDescriptionName,
        density=initSetting.density,
        length=initSetting.length,
        widthScale=initSetting.width,
        cvCount=initSetting.cvCount,
        generatorSeed=initSetting.generatorSeed)

    xgui.createIgSplineEditor()



# ===========================================================================
# Copyright 2021 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
