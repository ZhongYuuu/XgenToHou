import maya
maya.utils.loadStringResourcesForModule(__name__)

from builtins import object
from builtins import range
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *

import xgenm as xg
import xgenm.xgGlobal as xgg
from xgenm.ui.util.xgUtil import *
from xgenm.ui.widgets import *
if xgg.Maya:
    import maya.mel as mel
    import maya
    import maya.utils as utils
    import maya.OpenMaya as om
from xgenm.ui.widgets.xgIgValueSliderUI import *


def getDescriptionToConvert(onlyCurDesc):
    """
    Get selected description nodes. If one node is selected,
    iterate all its children.
    If no description is selected, return current active description.
    """
    descriptions = set()

    if not onlyCurDesc:
        selList = om.MSelectionList()
        om.MGlobal.getActiveSelectionList(selList)

        node = om.MObject()
        for i in range(selList.length()):
            try:
                selList.getDependNode(i, node)
                if node.hasFn(om.MFn.kTransform):
                    nodePath = om.MDagPath()
                    om.MDagPath.getAPathTo(node, nodePath)
                    nodePath.extendToShape()
                    node = nodePath.node()

                depNodeFn = om.MFnDependencyNode(node)
                if depNodeFn.typeName() == "xgmDescription":
                        nodePath = om.MDagPath()
                        om.MDagPath.getAPathTo(node, nodePath)
                        nodePath.pop()
                        descriptions.add(nodePath.fullPathName())
            except Exception as e:
                continue

    if len(descriptions) == 0:
        de = xgg.DescriptionEditor
        if de:
            desc = de.currentDescription()
            if desc:
                descriptions.add(desc)
    print(str(descriptions))

    return descriptions

def composeConvertCmd(setting):
    cmd = 'xgmSplineGeometryConvert'
    cmd += ' -convertSelected '
    cmd += "1" if setting.convertSelected else "0"
    cmd += ' -combineMesh '
    cmd += "1" if setting.combineMesh else "0"
    cmd += ' -useWidthRamp '
    cmd += "1" if setting.useWidthRamp else "0"
    cmd += " -insertWidthSpan "
    cmd += "1" if setting.insertWidthSpan else "0"
    if setting.insertWidthSpan:
        cmd += ' -widthSpanNum '
        cmd += str(setting.widthSpanNum)
        cmd += ' -curvature '
        cmd += str(setting.curvature)
    cmd += ' -uvInTiles '
    cmd += "1" if setting.uvInTiles else "0"
    if setting.uvInTiles:
        cmd += ' -uvLayoutType '
        cmd += str(setting.uvLayoutType)
        cmd += ' -uvTileSeparation '
        cmd += str(setting.uvTileSeparation)
        
    cmd += ' -createStripJoints '
    cmd += "1" if setting.createStripJoints else "0"
    if setting.createStripJoints:
        cmd += ' -stripJointPlacementType '
        cmd += str(setting.stripJointPlacementType)
        cmd += ' -jointNumOnStrip '
        cmd += str(setting.jointNumOnStrip)
        cmd += ' -autoBindSkin '
        cmd += "1" if setting.autoBindSkin else "0"
        if setting.autoBindSkin:
            cmd += ' -maxInfluences '
            cmd += str(setting.maxInfluences)
    #cmd += ' -createGuideJoints '
    #cmd += "1" if setting.createGuideJoints else "0"
    #if setting.createGuideJoints:
    #    cmd += ' -guideJointPlacementType '
    #    cmd += str(setting.guideJointPlacementType)
    #    cmd += ' -jointNumOnGuide '
    #    cmd += str(setting.jointNumOnGuide)
    print(cmd)
    return cmd

# Class to hold the UI data
class GeometryRendererSetting(object):
    """A simple class to hold the data setting from UI.
    """
    def __init__(self):
        # default values
        self.loadDefaults()

        # keys for optionVar
        self.kConvertSelected       = 'xgInteractiveGroom_ConvertSelected'
        self.kCombineMesh           = 'xgInteractiveGroom_CombineMesh'
        self.kUseWidthRamp          = 'xgInteractiveGroom_UseWidthRamp'
        self.kInsertWidthSpan       = 'xgInteractiveGroom_InsertWidthSpan'
        self.kWidthSpanNum          = 'xgInteractiveGroom_WidthSpanNum'
        self.kCurvature             = 'xgInteractiveGroom_Curvature'
        self.kUVInTiles             = 'xgInteractiveGroom_UVInTiles'
        self.kUVLayoutType          = 'xgInteractiveGroom_UVLayoutType'
        self.kUVTileSeparation      = 'xgInteractiveGroom_UVTileSeparation'
        self.kCreateStripJoints     = 'xgInteractiveGroom_CreateStripJoints'
        self.kStripJointPlacementType = 'xgInteractiveGroom_StripJointPlacementType'
        self.kJointNumOnStrip       = 'xgInteractiveGroom_JointNumOnStrip'
        self.kAutoBindSkin          = 'xgInteractiveGroom_AutoBindSkin'
        self.kMaxInfluences         = 'xgInteractiveGroom_MaxInfluences'
        #self.kCreateGuideJoints     = 'xgInteractiveGroom_CreateGuideJoints'
        #self.kGuideJointPlacementType = 'xgInteractiveGroom_GuideJointPlacementType'
        #self.kJointNumOnGuide       = 'xgInteractiveGroom_JointNumOnGuide'

    def debug(self):
        # For debug
        print("\n\n")
        print("convertSelected=%d\n" % self.convertSelected)
        print("combineMesh=%d\n" % self.combineMesh)
        print("useWidthRamp=%d\n" % self.useWidthRamp)
        print("insertWidthSpan=%d\n" % self.insertWidthSpan)
        print("widthSpanNum=%d\n" % self.widthSpanNum)
        print("curvature=%f\n" % self.curvature)
        print("uvInTiles=%d\n" % self.uvInTiles)
        print("uvLayoutType=%d\n" % self.uvLayoutType)
        print("uvTileSeparation=%f\n" % self.uvTileSeparation)
        print("createStripJoints=%d\n" % self.createStripJoints)
        print("stripJointPlacementType=%d\n" % self.stripJointPlacementType)
        print("jointNumOnStrip=%d\n" % self.jointNumOnStrip)
        print("autoBindSkin=%d\n" % self.autoBindSkin)
        print("maxInfluences=%d\n" % self.maxInfluences)
        print("createGuideJoints=%d\n" % self.createGuideJoints)
        print("guideJointPlacementType=%d\n" % self.guideJointPlacementType)
        print("jointNumOnGuide=%d\n" % self.jointNumOnGuide)


    def saveToMayaOptionVar(self):
        if cmds :
            cmds.optionVar(intValue   = (self.kConvertSelected, self.convertSelected))
            cmds.optionVar(intValue   = (self.kCombineMesh,     self.combineMesh))
            cmds.optionVar(floatValue = (self.kUseWidthRamp,    self.useWidthRamp))
            cmds.optionVar(floatValue = (self.kInsertWidthSpan, self.insertWidthSpan))
            cmds.optionVar(intValue   = (self.kWidthSpanNum,    self.widthSpanNum))
            cmds.optionVar(floatValue   = (self.kCurvature,       self.curvature))
            cmds.optionVar(intValue   = (self.kUVInTiles,       self.uvInTiles))
            cmds.optionVar(intValue   = (self.kUVLayoutType,    self.uvLayoutType))
            cmds.optionVar(floatValue = (self.kUVTileSeparation, self.uvTileSeparation))
            cmds.optionVar(intValue   = (self.kCreateStripJoints, self.createStripJoints))
            cmds.optionVar(intValue   = (self.kStripJointPlacementType,  self.stripJointPlacementType))
            cmds.optionVar(intValue   = (self.kJointNumOnStrip, self.jointNumOnStrip))
            cmds.optionVar(intValue   = (self.kAutoBindSkin,  self.autoBindSkin))
            cmds.optionVar(intValue   = (self.kMaxInfluences, self.maxInfluences))
            #cmds.optionVar(intValue   = (self.kCreateGuideJoints, self.createGuideJoints))
            #cmds.optionVar(intValue   = (self.kGuideJointPlacementType, self.guideJointPlacementType))
            #cmds.optionVar(intValue   = (self.kJointNumOnGuide, self.jointNumOnGuide))

    def loadFromMayaOptionVar(self):
        if cmds :
            if cmds.optionVar(exists=self.kConvertSelected):
                self.convertSelected = cmds.optionVar(query=self.kConvertSelected)
            if cmds.optionVar(exists=self.kCombineMesh):
                self.combineMesh = cmds.optionVar(query=self.kCombineMesh)
            if cmds.optionVar(exists=self.kUseWidthRamp):
                self.useWidthRamp = cmds.optionVar(query=self.kUseWidthRamp)
            if cmds.optionVar(exists=self.kInsertWidthSpan):
                self.insertWidthSpan = cmds.optionVar(query=self.kInsertWidthSpan)
            if cmds.optionVar(exists=self.kWidthSpanNum):
                self.widthSpanNum = cmds.optionVar(query=self.kWidthSpanNum)
            if cmds.optionVar(exists=self.kCurvature):
                self.curvature = cmds.optionVar(query=self.kCurvature)
            if cmds.optionVar(exists=self.kUVInTiles):
                self.uvInTiles = cmds.optionVar(query=self.kUVInTiles)
            if cmds.optionVar(exists=self.kUVLayoutType):
                self.uvLayoutType = cmds.optionVar(query=self.kUVLayoutType)
            if cmds.optionVar(exists=self.kUVTileSeparation):
                self.uvTileSeparation = cmds.optionVar(query=self.kUVTileSeparation)
            if cmds.optionVar(exists=self.kCreateStripJoints):
                self.createStripJoints = cmds.optionVar(query=self.kCreateStripJoints)
            if cmds.optionVar(exists=self.kStripJointPlacementType):
                self.stripJointPlacementType = cmds.optionVar(query=self.kStripJointPlacementType)
            if cmds.optionVar(exists=self.kJointNumOnStrip):
                self.jointNumOnStrip = cmds.optionVar(query=self.kJointNumOnStrip)
            if cmds.optionVar(exists=self.kAutoBindSkin):
                self.autoBindSkin = cmds.optionVar(query=self.kAutoBindSkin)
            if cmds.optionVar(exists=self.kMaxInfluences):
                self.maxInfluences = cmds.optionVar(query=self.kMaxInfluences)
            #if cmds.optionVar(exists=self.kCreateGuideJoints):
            #    self.createGuideJoints = cmds.optionVar(query=self.kCreateGuideJoints)
            #if cmds.optionVar(exists=self.kGuideJointPlacementType):
            #    self.guideJointPlacementType = cmds.optionVar(query=self.kGuideJointPlacementType)
            #if cmds.optionVar(exists=self.kJointNumOnGuide):
            #    self.jointNumOnGuide = cmds.optionVar(query=self.kJointNumOnGuide)

    def loadDefaults(self):
        # default values
        self.convertSelected     = False
        self.combineMesh         = False
        self.useWidthRamp        = True
        self.insertWidthSpan     = False
        self.widthSpanNum        = 1
        self.curvature           = 0.5
        self.uvInTiles           = True
        self.uvLayoutType        = 0
        self.uvTileSeparation    = 0.0
        self.createStripJoints   = False
        self.stripJointPlacementType = 0
        self.jointNumOnStrip     = 3
        self.autoBindSkin        = False
        self.maxInfluences       = 3
        self.createGuideJoints   = False
        self.guideJointPlacementType = 0
        self.jointNumOnGuide     = 3

gXGenConvertPrimToPolyWin = None

def showConvertWindow(mayaMainWindow):
    global gXGenConvertPrimToPolyWin

    if not gXGenConvertPrimToPolyWin:
        gXGenConvertPrimToPolyWin = ConvertPrimitiveToPolygonWindow(mayaMainWindow)
        gXGenConvertPrimToPolyWin.run()
    else:
        gXGenConvertPrimToPolyWin.showNormal()
        gXGenConvertPrimToPolyWin.activateWindow()

# UI
class ConvertPrimitiveToPolygonWindow(QMainWindow):
    """A window for configuring interactive spline description creating.
    """

    def __init__(self, parent):
        QMainWindow.__init__(self, parent)

        # Set modal
        self.hide()
        self.setWindowModality(QtCore.Qt.NonModal)

        # Window title
        self.setWindowTitle( maya.stringTable[u'y_xgenm_ui_dialogs_xgSplineToGeometryConvertUI.kConvertPrimToPolyWinTitle' ])

        self.initSetting = GeometryRendererSetting()
        self.initSetting.loadFromMayaOptionVar()

        # Create menus
        self.__createMenus()

        # Set Central widget with grid layout
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)

        vLayout = QVBoxLayout()
        vLayout.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))
        vLayout.setSpacing(DpiScale(0))
        centralWidget.setLayout(vLayout)

        frameWidget = QFrame()
        frameWidget.setFrameShape(QFrame.StyledPanel)
        frameWidget.setFrameShadow (QFrame.Sunken )
        frameWidget.setMinimumSize(DpiScale(500), DpiScale(500))

        scrollArea = QScrollArea()
        #scrollArea.setBackgroundRole(QPalette.Dark)
        scrollArea.setWidget(frameWidget)
        scrollArea.setWidgetResizable(True)
        scrollArea.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))

        vLayout.addWidget(scrollArea)

        gridLayout = QGridLayout()
        frameWidget.setLayout(gridLayout)
        
        # width for "label"+"edit"+"slider"
        textUIWidth   = 130
        editUIWidth   = 70
        sliderUIWidth = 0

        gridLine = 0

        # 'Convert Selected' check box
        self.convertSelectedChkBoxUI = QCheckBox(maya.stringTable[u'y_xgenm_ui_dialogs_xgSplineToGeometryConvertUI.kConvertSelected' ])
        self.connect(self.convertSelectedChkBoxUI, QtCore.SIGNAL("clicked()"), self.__onClickConvertSelected)
        gridLayout.addWidget(self.convertSelectedChkBoxUI, gridLine, 1, 1, 2)
        gridLine += 1

        # 'Combine Mesh' check box
        self.combineMeshChkBoxUI = QCheckBox(maya.stringTable[u'y_xgenm_ui_dialogs_xgSplineToGeometryConvertUI.kCombineMesh' ])
        gridLayout.addWidget(self.combineMeshChkBoxUI, gridLine, 1, 1, 2)
        gridLine += 1

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        gridLayout.addWidget(separator, gridLine, 0, 1, 3)
        gridLine += 1

        # 'Use Width Ramp' check box
        self.useWidthRampChkBoxUI = QCheckBox(maya.stringTable[u'y_xgenm_ui_dialogs_xgSplineToGeometryConvertUI.kUseWidthRamp' ])
        gridLayout.addWidget(self.useWidthRampChkBoxUI, gridLine, 1, 1, 2)
        gridLine += 1

        # 'Insert Spans Along Width' check box
        self.insertSpansChkBoxUI = QCheckBox(maya.stringTable[u'y_xgenm_ui_dialogs_xgSplineToGeometryConvertUI.kInsertSpans' ])
        self.connect(self.insertSpansChkBoxUI, QtCore.SIGNAL("clicked()"), self.__onClickInsertSpans)
        gridLayout.addWidget(self.insertSpansChkBoxUI, gridLine, 1, 1, 2)
        gridLine += 1

        # Number of Spans - int
        self.spanNumIntUI = IgIntSliderUI(
                maya.stringTable[u'y_xgenm_ui_dialogs_xgSplineToGeometryConvertUI.kSpanNum' ],
                maya.stringTable[u'y_xgenm_ui_dialogs_xgSplineToGeometryConvertUI.kkSpanNumAnno' ],
                True,
                0, 100, 0, 10,
                gridLayout, gridLine,
                textUIWidth, editUIWidth, sliderUIWidth)
        gridLine += 1

        self.curvatureFloatUI = IgFloatSliderUI(
                maya.stringTable[u'y_xgenm_ui_dialogs_xgSplineToGeometryConvertUI.kCurvature' ],
                maya.stringTable[u'y_xgenm_ui_dialogs_xgSplineToGeometryConvertUI.kCurvatureAnno' ],
                True,
                -1.0, 1.0, -1.0, 1.0,
                gridLayout, gridLine,
                textUIWidth, editUIWidth, sliderUIWidth)
        gridLine += 1

        # 'Place UV in Tiles' check box
        self.placeUVChkBoxUI = QCheckBox(maya.stringTable[u'y_xgenm_ui_dialogs_xgSplineToGeometryConvertUI.kPlaceUV' ])
        self.connect(self.placeUVChkBoxUI, QtCore.SIGNAL("clicked()"), self.__onClickPlaceUV)
        gridLayout.addWidget(self.placeUVChkBoxUI, gridLine, 1, 1, 2)
        gridLine += 1

        # UV Layout Type
        self.uvLayoutTypeLabelUI = QLabel(maya.stringTable[ u'y_xgenm_ui_dialogs_xgSplineToGeometryConvertUI.kUVLayoutType'  ])
        self.uvLayoutTypeLabelUI.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        gridLayout.addWidget(self.uvLayoutTypeLabelUI, gridLine, 0)

        self.uvLayoutTypeComboUI = QComboBox()
        self.uvLayoutTypeComboUI.addItem("2x2")
        self.uvLayoutTypeComboUI.addItem("3x3")
        self.uvLayoutTypeComboUI.addItem("4x4")
        gridLayout.addWidget(self.uvLayoutTypeComboUI, gridLine, 1, 1, 1)
        gridLine += 1

        # Tile Separation - float
        self.tileSeparationFloatUI = IgFloatSliderUI(
                maya.stringTable[u'y_xgenm_ui_dialogs_xgSplineToGeometryConvertUI.kTileSeparation' ],
                maya.stringTable[u'y_xgenm_ui_dialogs_xgSplineToGeometryConvertUI.kTileSeparationAnno' ],
                True,
                0.0, 1.0, 0.0, 1.0,
                gridLayout, gridLine,
                textUIWidth, editUIWidth, sliderUIWidth)
        gridLine += 1

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        gridLayout.addWidget(separator, gridLine, 0, 1, 3)
        gridLine += 1

        # Create Joints on Strips
        self.createStripJointsChkBoxUI = QCheckBox(maya.stringTable[u'y_xgenm_ui_dialogs_xgSplineToGeometryConvertUI.kCreateStripJoints' ])
        self.connect(self.createStripJointsChkBoxUI, QtCore.SIGNAL("clicked()"), self.__onClickCreateStripJoints)
        gridLayout.addWidget(self.createStripJointsChkBoxUI, gridLine, 1, 1, 2)
        gridLine += 1

        jointPlacementStr = maya.stringTable[ u'y_xgenm_ui_dialogs_xgSplineToGeometryConvertUI.kJointPlacement'  ]
        jointPerSpanStr = maya.stringTable[ u'y_xgenm_ui_dialogs_xgSplineToGeometryConvertUI.kJointPerSpan'  ]
        jointPerCVStr = maya.stringTable[ u'y_xgenm_ui_dialogs_xgSplineToGeometryConvertUI.kJointPerCV'  ]
        specifyJointNumStr = maya.stringTable[ u'y_xgenm_ui_dialogs_xgSplineToGeometryConvertUI.kSpecifyJointNum'  ]

        # Joint Placement
        self.stripJointPlacementLabelUI = QLabel(jointPlacementStr)
        self.stripJointPlacementLabelUI.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        gridLayout.addWidget(self.stripJointPlacementLabelUI, gridLine, 0)

        self.stripJointPlacementRadioGrpUI = QWidget()
        self.stripJointPlacementRadioGrpUI.setFixedSize(DpiScale(300), DpiScale(20))
        hLayout = QHBoxLayout()
        hLayout.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))
        hLayout.setSpacing(DpiScale(0))
        self.stripJointPlacementRadioGrpUI.setLayout(hLayout)

        self.radioBtnStripPerCV = QRadioButton(jointPerSpanStr)
        self.radioBtnStripPerCV.setFixedSize(DpiScale(150), DpiScale(20))
        self.connect(self.radioBtnStripPerCV, QtCore.SIGNAL("clicked()"), self.__onClickStripJointPlacement)
        hLayout.addWidget(self.radioBtnStripPerCV)

        self.radioBtnStripSpecifyNum = QRadioButton(specifyJointNumStr)
        self.radioBtnStripSpecifyNum.setFixedSize(DpiScale(150), DpiScale(20))
        self.connect(self.radioBtnStripSpecifyNum, QtCore.SIGNAL("clicked()"), self.__onClickStripJointPlacement)
        hLayout.addWidget(self.radioBtnStripSpecifyNum)
        gridLayout.addWidget(self.stripJointPlacementRadioGrpUI, gridLine, 1, 1, 2)
        gridLine += 1

        # Number of Joints on Each Strip - int
        self.stripJointNumIntUI = IgIntSliderUI(
                maya.stringTable[u'y_xgenm_ui_dialogs_xgSplineToGeometryConvertUI.kStripJointNum' ],
                maya.stringTable[u'y_xgenm_ui_dialogs_xgSplineToGeometryConvertUI.kStripJointNumAnno' ],
                True,
                3, 100, 3, 10,
                gridLayout, gridLine,
                textUIWidth, editUIWidth, sliderUIWidth)
        gridLine += 1

        # Auto Bind Skin
        self.autoBindSkinChkBoxUI = QCheckBox(maya.stringTable[u'y_xgenm_ui_dialogs_xgSplineToGeometryConvertUI.kAutoBindSkin' ])
        self.connect(self.autoBindSkinChkBoxUI, QtCore.SIGNAL("clicked()"), self.__onClickAutoBindSkin)
        gridLayout.addWidget(self.autoBindSkinChkBoxUI, gridLine, 1, 1, 2)
        gridLine += 1

        # Max Influences - int
        self.maxInfluencesIntUI = IgIntSliderUI(
                maya.stringTable[u'y_xgenm_ui_dialogs_xgSplineToGeometryConvertUI.kMaxInfluences' ],
                maya.stringTable[u'y_xgenm_ui_dialogs_xgSplineToGeometryConvertUI.kMaxInfluencesAnno' ],
                True,
                3, 100, 3, 10,
                gridLayout, gridLine,
                textUIWidth, editUIWidth, sliderUIWidth)
        gridLine += 1

        #separator = QFrame()
        #separator.setFrameShape(QFrame.HLine)
        #gridLayout.addWidget(separator, gridLine, 0, 1, 3)
        #gridLine += 1

        # Create Joints on Guide
        #self.createGuideJointsChkBoxUI = QCheckBox(_L10N(kCreateGuideJoint, "Create Joints on Guides"))
        #self.connect(self.createGuideJointsChkBoxUI, QtCore.SIGNAL("clicked()"), self.__onClickCreateGuideJoints)
        #gridLayout.addWidget(self.createGuideJointsChkBoxUI, gridLine, 1, 1, 2)
        #gridLine += 1

        # Joint Placement
        #self.guideJointPlacementLabelUI = QLabel(jointPlacementStr)
        #self.guideJointPlacementLabelUI.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        #gridLayout.addWidget(self.guideJointPlacementLabelUI, gridLine, 0)

        #self.guideJointPlacementRadioGrpUI = QWidget()
        #self.guideJointPlacementRadioGrpUI.setFixedSize(DpiScale(300), DpiScale(20))
        #hLayout = QHBoxLayout()
        #hLayout.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))
        #hLayout.setSpacing(DpiScale(0))
        #self.guideJointPlacementRadioGrpUI.setLayout(hLayout)

        #self.radioBtnGuidePerCV = QRadioButton(jointPerCVStr)
        #self.radioBtnGuidePerCV.setFixedSize(DpiScale(150), DpiScale(20))
        #self.connect(self.radioBtnGuidePerCV, QtCore.SIGNAL("clicked()"), self.__onClickGuideJointPlacement)
        #hLayout.addWidget(self.radioBtnGuidePerCV)

        #self.radioBtnGuideSpecifyNum = QRadioButton(specifyJointNumStr)
        #self.radioBtnGuideSpecifyNum.setFixedSize(DpiScale(150), DpiScale(20))
        #self.connect(self.radioBtnGuideSpecifyNum, QtCore.SIGNAL("clicked()"), self.__onClickGuideJointPlacement)
        #hLayout.addWidget(self.radioBtnGuideSpecifyNum)
        #gridLayout.addWidget(self.guideJointPlacementRadioGrpUI, gridLine, 1, 1, 2)
        #gridLine += 1

        # Number of Joints on Each Strip - int
        #self.guideJointNumIntUI = IgIntSliderUI(
        #        _L10N(kGuideJointNum, "Joints per Guide:"),
        #        _L10N(kGuideJointNumAnno, "Number of joints on each guide."),
        #        True,
        #        3, 100, 3, 10,
        #        gridLayout, gridLine,
        #        textUIWidth, editUIWidth, sliderUIWidth)
        #gridLine += 1

        #emptyLabelUI = QLabel("")
        #gridLayout.addWidget(emptyLabelUI, gridLine, 0)

        # Buttons
        buttonHeight = DpiScale(26)
        buttonRowWidget = QWidget()
        buttonRowHLayout = QHBoxLayout()
        buttonRowHLayout.setContentsMargins(DpiScale(3),DpiScale(3),DpiScale(3),DpiScale(3))
        buttonRowHLayout.setSpacing(DpiScale(3))
        buttonRowWidget.setLayout(buttonRowHLayout)

        self.convertButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_dialogs_xgSplineToGeometryConvertUI.kConvert'  ])
        self.convertButton.setFixedHeight(buttonHeight)
        self.connect(self.convertButton, QtCore.SIGNAL("clicked()"), self.__onClickConvertButton)
        buttonRowHLayout.addWidget(self.convertButton)

        self.applyButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_dialogs_xgSplineToGeometryConvertUI.kApply'  ])
        self.applyButton.setFixedHeight(buttonHeight)
        self.connect(self.applyButton, QtCore.SIGNAL("clicked()"), self.__onClickApplyButton)
        buttonRowHLayout.addWidget(self.applyButton)

        self.cancelButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_dialogs_xgSplineToGeometryConvertUI.kCancel'  ])
        self.cancelButton.setFixedHeight(buttonHeight)
        self.connect(self.cancelButton, QtCore.SIGNAL("clicked()"), self.__onClickCancelButton)
        buttonRowHLayout.addWidget(self.cancelButton)

        vLayout.addWidget(buttonRowWidget)

        self.__updateUIFromSettings()

        self.resize(DpiScale(550), DpiScale(570))

    def __createMenus(self):

        # Edit menu
        editMenu = self.menuBar().addMenu(maya.stringTable[u'y_xgenm_ui_dialogs_xgSplineToGeometryConvertUI.kEdit' ])
        editMenu.addAction(maya.stringTable[u'y_xgenm_ui_dialogs_xgSplineToGeometryConvertUI.kResetSettings' ], self.__onMenuResetSettings)
        editMenu.addAction(maya.stringTable[u'y_xgenm_ui_dialogs_xgSplineToGeometryConvertUI.kSaveSettings' ], self.__onMenuSaveSettings)

        # Help menu
        helpMenu = self.menuBar().addMenu(maya.stringTable[u'y_xgenm_ui_dialogs_xgSplineToGeometryConvertUI.kHelp' ])
        helpMenu.addAction(maya.stringTable[u'y_xgenm_ui_dialogs_xgSplineToGeometryConvertUI.kHelpMenu' ], self.__onMenuHelp)

    def __onMenuResetSettings(self):
        # Default Data ---> UI
        self.initSetting.loadDefaults()
        self.__updateUIFromSettings()

    def __updateUIFromSettings(self):
        if self.initSetting.convertSelected:
            self.convertSelectedChkBoxUI.setCheckState(QtCore.Qt.Checked)
        else:
            self.convertSelectedChkBoxUI.setCheckState(QtCore.Qt.Unchecked)
        if self.initSetting.combineMesh:
            self.combineMeshChkBoxUI.setCheckState(QtCore.Qt.Checked)
        else:
            self.combineMeshChkBoxUI.setCheckState(QtCore.Qt.Unchecked)
        if self.initSetting.useWidthRamp:
            self.useWidthRampChkBoxUI.setCheckState(QtCore.Qt.Checked)
        else:
            self.useWidthRampChkBoxUI.setCheckState(QtCore.Qt.Unchecked)
        if self.initSetting.insertWidthSpan:
            self.insertSpansChkBoxUI.setCheckState(QtCore.Qt.Checked)
        else:
            self.insertSpansChkBoxUI.setCheckState(QtCore.Qt.Unchecked)
        self.spanNumIntUI.setValue(self.initSetting.widthSpanNum)
        self.curvatureFloatUI.setValue(self.initSetting.curvature)
        if self.initSetting.uvInTiles:
            self.placeUVChkBoxUI.setCheckState(QtCore.Qt.Checked)
        else:
            self.placeUVChkBoxUI.setCheckState(QtCore.Qt.Unchecked)
        self.uvLayoutTypeComboUI.setCurrentIndex(self.initSetting.uvLayoutType)
        self.tileSeparationFloatUI.setValue(self.initSetting.uvTileSeparation)

        if self.initSetting.createStripJoints:
            self.createStripJointsChkBoxUI.setCheckState(QtCore.Qt.Checked)
        else:
            self.createStripJointsChkBoxUI.setCheckState(QtCore.Qt.Unchecked)
        if self.initSetting.stripJointPlacementType == 0:
            self.radioBtnStripPerCV.setChecked(True)
        else:
            self.radioBtnStripSpecifyNum.setChecked(True)
        self.stripJointNumIntUI.setValue(self.initSetting.jointNumOnStrip)
        if self.initSetting.autoBindSkin:
            self.autoBindSkinChkBoxUI.setCheckState(QtCore.Qt.Checked)
        else:
            self.autoBindSkinChkBoxUI.setCheckState(QtCore.Qt.Unchecked)
        self.maxInfluencesIntUI.setValue(self.initSetting.maxInfluences)

        #if self.initSetting.createGuideJoints:
        #    self.createGuideJointsChkBoxUI.setCheckState(QtCore.Qt.Checked)
		#else:
        #    self.createGuideJointsChkBoxUI.setCheckState(QtCore.Qt.Unchecked)
        #if self.initSetting.guideJointPlacementType == 0:
        #    self.radioBtnGuidePerCV.setChecked(True)
        #else:
        #    self.radioBtnGuideSpecifyNum.setChecked(True)
        #self.guideJointNumIntUI.setValue(self.initSetting.jointNumOnGuide)

        self.__onClickConvertSelected()
        self.__onClickInsertSpans()
        self.__onClickPlaceUV()
        self.__onClickCreateStripJoints()
        #self.__onClickCreateGuideJoints()

    def __onMenuSaveSettings(self):
        self.initSetting.convertSelected = self.convertSelectedChkBoxUI.isChecked()
        self.initSetting.combineMesh = self.combineMeshChkBoxUI.isChecked()
        self.initSetting.useWidthRamp = self.useWidthRampChkBoxUI.isChecked()
        self.initSetting.insertWidthSpan = self.insertSpansChkBoxUI.isChecked()
        self.initSetting.widthSpanNum = int(self.spanNumIntUI.value())
        self.initSetting.curvature = float(self.curvatureFloatUI.value())
        self.initSetting.uvInTiles = self.placeUVChkBoxUI.isChecked()
        self.initSetting.uvLayoutType = self.uvLayoutTypeComboUI.currentIndex()
        self.initSetting.uvTileSeparation = float(self.tileSeparationFloatUI.value())
        self.initSetting.createStripJoints = self.createStripJointsChkBoxUI.isChecked()
        self.initSetting.stripJointPlacementType = 0 if self.radioBtnStripPerCV.isChecked() else 1
        self.initSetting.jointNumOnStrip = int(self.stripJointNumIntUI.value())
        self.initSetting.autoBindSkin = self.autoBindSkinChkBoxUI.isChecked()
        self.initSetting.maxInfluences = int(self.maxInfluencesIntUI.value())
        #self.initSetting.createGuideJoints = self.createGuideJointsChkBoxUI.isChecked()
        #self.initSetting.guideJointPlacementType = 0 if self.radioBtnGuidePerCV.isChecked() else 1
        #self.initSetting.jointNumOnGuide = int(self.guideJointNumIntUI.value())

        self.initSetting.saveToMayaOptionVar()

    def __onMenuHelp(self):
        mel.eval("showHelp PrimToPoly")

    def __onClickConvertSelected(self):
        if self.convertSelectedChkBoxUI.isChecked():
            self.useWidthRampChkBoxUI.setChecked(True)
        self.useWidthRampChkBoxUI.setEnabled(not self.convertSelectedChkBoxUI.isChecked())

    def __onClickInsertSpans(self):
        self.spanNumIntUI.setEnabled(self.insertSpansChkBoxUI.isChecked())
        self.curvatureFloatUI.setEnabled(self.insertSpansChkBoxUI.isChecked())

    def __onClickPlaceUV(self):
        self.uvLayoutTypeLabelUI.setEnabled(self.placeUVChkBoxUI.isChecked())
        self.uvLayoutTypeComboUI.setEnabled(self.placeUVChkBoxUI.isChecked())
        self.tileSeparationFloatUI.setEnabled(self.placeUVChkBoxUI.isChecked())
        
    def __onClickCreateStripJoints(self):
        self.stripJointPlacementLabelUI.setEnabled(self.createStripJointsChkBoxUI.isChecked())
        self.stripJointPlacementRadioGrpUI.setEnabled(self.createStripJointsChkBoxUI.isChecked())
        self.stripJointNumIntUI.setEnabled(self.createStripJointsChkBoxUI.isChecked() and
                                            self.radioBtnStripSpecifyNum.isChecked())
        self.autoBindSkinChkBoxUI.setEnabled(self.createStripJointsChkBoxUI.isChecked())
        self.maxInfluencesIntUI.setEnabled(self.createStripJointsChkBoxUI.isChecked() and 
                                                self.autoBindSkinChkBoxUI.isChecked())

    def __onClickAutoBindSkin(self):
        self.maxInfluencesIntUI.setEnabled(self.autoBindSkinChkBoxUI.isChecked())
    

    def __onClickCreateGuideJoints(self):
        self.guideJointPlacementLabelUI.setEnabled(self.createGuideJointsChkBoxUI.isChecked())
        self.guideJointPlacementRadioGrpUI.setEnabled(self.createGuideJointsChkBoxUI.isChecked())
        self.guideJointNumIntUI.setEnabled(self.createGuideJointsChkBoxUI.isChecked() and
                                            self.radioBtnGuideSpecifyNum.isChecked())

    def __onClickStripJointPlacement(self):
        self.stripJointNumIntUI.setEnabled(self.radioBtnStripSpecifyNum.isChecked())

    def __onClickGuideJointPlacement(self):
        self.guideJointNumIntUI.setEnabled(self.radioBtnGuideSpecifyNum.isChecked())

    def __onClickConvertButton(self):
        self.__onMenuSaveSettings()
        self.__geomExport()
        self.close()

    def __onClickApplyButton(self):
        self.__onMenuSaveSettings()
        self.__geomExport()

    def __onClickCancelButton(self):
        self.close()

    def __geomExport(self):
        cmd = composeConvertCmd(self.initSetting)
        if len(cmd) > 0:
            results = mel.eval(cmd)

    def run(self):
        self.show()
        
    def closeEvent(self, event):
        global gXGenConvertPrimToPolyWin

        event.accept()
        gXGenConvertPrimToPolyWin = None
# ===========================================================================
# Copyright 2021 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
