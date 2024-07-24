# =======================================================================
# Copyright 2015 Autodesk, Inc. All rights reserved.
#
# This computer source code and related instructions and comments are the
# unpublished confidential  and proprietary information of Autodesk, Inc.
# and are protected under applicable copyright and trade secret law. They 
# may not be disclosed to, copied  or used by any third party without the 
# prior written consent of Autodesk, Inc.
# =======================================================================
import maya
maya.utils.loadStringResourcesForModule(__name__)



##
# @file xgGeometryRendererTab.py
# @brief Contains the UI for Geometry Renderer tab

import string
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *
import xgenm as xg
import xgenm.xgGlobal as xgg
if xgg.Maya:
    import maya.mel as mel
from xgenm.ui.widgets import *
from xgenm.ui.tabs.xgRendererTab import *
from xgenm.ui.util.xgProgressBar import setProgressInfo
from xgenm.ui.dialogs.xgConvertPrimitiveToPolygonUI import GeometryRendererSetting
from xgenm.ui.util.xgUtil import DpiScale

class GeometryRendererTabUI(RendererTabUI):
    def __init__(self):
        RendererTabUI.__init__(self,'Geometry')
        # Widgets
        self.baseTopUI(False)
        
        self.convertSelected = CheckBoxUI( maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.kConvertSelected'  ], "",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.kConvertSelectedAnn'  ],
             "")
        self.layout().addWidget(self.convertSelected)
        self.connect(self.convertSelected.boxValue[0], QtCore.SIGNAL("clicked()"), self.__onClickConvertSelected)

        self.combineMesh = CheckBoxUI( maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.kCombineMesh'  ],"combineMesh",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.kCombineMeshAnn'  ],
             "GeometryRenderer")
        self.layout().addWidget(self.combineMesh)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        self.layout().addWidget(separator)

        self.useWidthRamp = CheckBoxUI( maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.kUseWidthRamp'  ],"useWidthRamp",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.kUseWidthRampAnn'  ],
             "GeometryRenderer")
        self.layout().addWidget(self.useWidthRamp)

        self.insertWidthSpan = CheckBoxUI( maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.kInsertWidthSpan'  ], "insertWidthSpan",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.kInsertWidthSpanAnn'  ],
             "GeometryRenderer")
        self.layout().addWidget(self.insertWidthSpan)
        self.connect(self.insertWidthSpan.boxValue[0], QtCore.SIGNAL("clicked()"), self.__onClickInsertSpans)

        self.widthSpanNum = IntegerUI("widthSpanNum",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.kSpanNumAnn'  ],
             "GeometryRenderer",0,10,maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.kSpanNum'  ])
        self.layout().addWidget(self.widthSpanNum)

        self.curvature = FloatUI("curvature",
             maya.stringTable[u'y_xgenm_ui_tabs_xgGeometryRendererTab.kCurvatureAnno' ],
             "GeometryRenderer",-1.0,1.0,-1.0,1.0,maya.stringTable[u'y_xgenm_ui_tabs_xgGeometryRendererTab.kCurvature' ])
        self.layout().addWidget(self.curvature)

        self.uvInTiles = CheckBoxUI( maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.kUVInTiles'  ], "uvInTiles",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.kUVInTilesAnn'  ],
             "GeometryRenderer")
        self.layout().addWidget(self.uvInTiles)
        self.connect(self.uvInTiles.boxValue[0], QtCore.SIGNAL("clicked()"), self.__onClickPlaceUV)

        self.uvLayoutType = EnumUI("uvLayoutType", [ maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.k2x2'  ], maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.k3x3'  ], maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.k4x4'  ] ],
            maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.kUVLayoutTypeAnn'  ],
            "GeometryRenderer",
            maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.kUVLayoutType' ])
        self.layout().addWidget(self.uvLayoutType)

        self.uvTileSeparation = FloatUI("uvTileSeparation",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.kTileSeparationAnn'  ],
             "GeometryRenderer",0.0,1.0,0.0,1.0,maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.kTileSeparation'  ])
        self.layout().addWidget(self.uvTileSeparation)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        self.layout().addWidget(separator)


        self.createStripJoints = CheckBoxUI( maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.kCreateStripJoints'  ],"createStripJoints",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.kCreateStripJointsAnn'  ],
             "GeometryRenderer")
        self.layout().addWidget(self.createStripJoints)
        self.connect(self.createStripJoints.boxValue[0], QtCore.SIGNAL("clicked()"), self.__onClickCreateStripJoints)

        jointPlacementStr = maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.kJointPlacement'  ]
        jointPerSpanStr = maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.kJointPerSpan'  ]
        jointPerCVStr = maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.kJointPerCV'  ]
        specifyJointNumStr = maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.kSpecifyJointNum'  ]
        self.stripJointPlacementType = RadioUI("stripJointPlacementType",
             [jointPerSpanStr, specifyJointNumStr],
             maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.kStripJointPlacementAnn'  ],
             "GeometryRenderer",
             jointPlacementStr)
        self.layout().addWidget(self.stripJointPlacementType)
        self.connect(self.stripJointPlacementType.buttons[0],QtCore.SIGNAL("toggled(bool)"), self.__onClickStripJointPlacement)
        self.connect(self.stripJointPlacementType.buttons[1],QtCore.SIGNAL("toggled(bool)"), self.__onClickStripJointPlacement)

        self.jointNumOnStrip = IntegerUI("jointNumOnStrip",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.kStripJointNumAnn'  ],
             "GeometryRenderer",3,100,maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.kStripJointNum'  ])
        self.layout().addWidget(self.jointNumOnStrip)

        self.autoBindSkin = CheckBoxUI( maya.stringTable[u'y_xgenm_ui_tabs_xgGeometryRendererTab.kAutoBindSkin' ],"",
             maya.stringTable[u'y_xgenm_ui_tabs_xgGeometryRendererTab.kAutoBindSkinAnn' ],
             "")
        self.layout().addWidget(self.autoBindSkin)
        self.connect(self.autoBindSkin.boxValue[0], QtCore.SIGNAL("clicked()"), self.__onClickAutoBindSkin)

        self.maxInfluences = IntegerUI("",
             maya.stringTable[u'y_xgenm_ui_tabs_xgGeometryRendererTab.kMaxInfluencesAnn' ],
             "",0,10,maya.stringTable[u'y_xgenm_ui_tabs_xgGeometryRendererTab.kMaxInfluences' ])
        self.layout().addWidget(self.maxInfluences)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        self.layout().addWidget(separator)

        self.createGuideJoints = CheckBoxUI( maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.kCreateGuideJoints'  ],"createGuideJoints",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.kCreateGuideJointsAnn'  ],
             "GeometryRenderer")
        self.layout().addWidget(self.createGuideJoints) 
        self.connect(self.createGuideJoints.boxValue[0], QtCore.SIGNAL("clicked()"), self.__onClickCreateGuideJoints)

        self.guideJointPlacementType = RadioUI("guideJointPlacementType",
             [jointPerCVStr, specifyJointNumStr],
             maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.kGuideJointPlacementAnn'  ],
             "GeometryRenderer",
             jointPlacementStr)
        self.layout().addWidget(self.guideJointPlacementType)
        self.connect(self.guideJointPlacementType.buttons[0],QtCore.SIGNAL("toggled(bool)"), self.__onClickGuideJointPlacement)
        self.connect(self.guideJointPlacementType.buttons[1],QtCore.SIGNAL("toggled(bool)"), self.__onClickGuideJointPlacement)

        self.jointNumOnGuide = IntegerUI("jointNumOnGuide",
             maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.kGuideJointNumAnn'  ],
             "GeometryRenderer",3,100,maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.kGuideJointNum'  ])
        self.layout().addWidget(self.jointNumOnGuide)

        if ( xgg.Maya ):
            self.layout().addSpacing(DpiScale(10))
            row = QWidget()
            hbox = QHBoxLayout()
            QLayoutItem.setAlignment(hbox, QtCore.Qt.AlignLeft)
            hbox.setSpacing(DpiScale(3))
            hbox.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))
            hbox.addSpacing(labelWidth()+DpiScale(3))
            self.p3dButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.kCreateGeo'  ])
            self.p3dButton.setFixedWidth(DpiScale(160))
            self.p3dButton.setAutoRepeat(False)
            self.p3dButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.kCreateGeoAnn'  ])
            self.connect(self.p3dButton, QtCore.SIGNAL("clicked()"), self.geomRender)
            hbox.addWidget(self.p3dButton)
            row.setLayout(hbox)
            self.layout().addWidget(row)

    def __onClickConvertSelected(self):
        if self.convertSelected.boxValue[0].isChecked():
            self.useWidthRamp.boxValue[0].setChecked(True)
        self.useWidthRamp.boxValue[0].setEnabled(not self.convertSelected.boxValue[0].isChecked())

    def __onClickInsertSpans(self):
        self.widthSpanNum.label.setEnabled(self.insertWidthSpan.boxValue[0].isChecked())
        self.widthSpanNum.intValue.setEnabled(self.insertWidthSpan.boxValue[0].isChecked())
        self.curvature.label.setEnabled(self.insertWidthSpan.boxValue[0].isChecked())
        self.curvature.floatValue.setEnabled(self.insertWidthSpan.boxValue[0].isChecked())

    def __onClickPlaceUV(self):
        self.uvLayoutType.label.setEnabled(self.uvInTiles.boxValue[0].isChecked())
        self.uvLayoutType.enumValue.setEnabled(self.uvInTiles.boxValue[0].isChecked())
        self.uvTileSeparation.label.setEnabled(self.uvInTiles.boxValue[0].isChecked())
        self.uvTileSeparation.floatValue.setEnabled(self.uvInTiles.boxValue[0].isChecked())

    def __onClickCreateStripJoints(self):
        self.stripJointPlacementType.label.setEnabled(self.createStripJoints.boxValue[0].isChecked())
        self.stripJointPlacementType.buttons[0].setEnabled(self.createStripJoints.boxValue[0].isChecked())
        self.stripJointPlacementType.buttons[1].setEnabled(self.createStripJoints.boxValue[0].isChecked())
        self.jointNumOnStrip.label.setEnabled(self.createStripJoints.boxValue[0].isChecked() and
                                            self.stripJointPlacementType.buttons[1].isChecked())
        self.jointNumOnStrip.intValue.setEnabled(self.createStripJoints.boxValue[0].isChecked() and
                                            self.stripJointPlacementType.buttons[1].isChecked())
        self.autoBindSkin.boxValue[0].setEnabled(self.createStripJoints.boxValue[0].isChecked())
        self.maxInfluences.label.setEnabled(self.createStripJoints.boxValue[0].isChecked() and 
                                                self.autoBindSkin.boxValue[0].isChecked())
        self.maxInfluences.intValue.setEnabled(self.createStripJoints.boxValue[0].isChecked() and 
                                                self.autoBindSkin.boxValue[0].isChecked())

    def __onClickAutoBindSkin(self):
        self.maxInfluences.label.setEnabled(self.createStripJoints.boxValue[0].isChecked())
        self.maxInfluences.intValue.setEnabled(self.createStripJoints.boxValue[0].isChecked())
    

    def __onClickCreateGuideJoints(self):
        self.guideJointPlacementType.label.setEnabled(self.createGuideJoints.boxValue[0].isChecked())
        self.guideJointPlacementType.buttons[0].setEnabled(self.createGuideJoints.boxValue[0].isChecked())
        self.guideJointPlacementType.buttons[1].setEnabled(self.createGuideJoints.boxValue[0].isChecked())
        self.jointNumOnGuide.label.setEnabled(self.createGuideJoints.boxValue[0].isChecked() and
                                            self.guideJointPlacementType.buttons[1].isChecked())
        self.jointNumOnGuide.intValue.setEnabled(self.createGuideJoints.boxValue[0].isChecked() and
                                            self.guideJointPlacementType.buttons[1].isChecked())

    def __onClickStripJointPlacement(self):
        self.jointNumOnStrip.label.setEnabled(self.stripJointPlacementType.buttons[1].isChecked())
        self.jointNumOnStrip.intValue.setEnabled(self.stripJointPlacementType.buttons[1].isChecked())

    def __onClickGuideJointPlacement(self):
        self.jointNumOnGuide.label.setEnabled(self.guideJointPlacementType.buttons[1].isChecked())
        self.jointNumOnGuide.intValue.setEnabled(self.guideJointPlacementType.buttons[1].isChecked())

    def geomRender(self):
        de = xgg.DescriptionEditor
        desc = de.currentDescription()
        setProgressInfo(maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.kGeoProgressInfo'  ])
        cmd = 'xgmGeoRender -pb '
        cmd += ' -convertSelected '
        cmd += "1" if self.convertSelected.value() else "0"
        cmd += ' -combineMesh '
        cmd += "1" if self.combineMesh.value() else "0"
        cmd += ' -useWidthRamp '
        cmd += "1" if self.useWidthRamp.value() else "0"
        cmd += " -insertWidthSpan "
        cmd += "1" if self.insertWidthSpan.value() else "0"
        if self.insertWidthSpan.value():
            cmd += ' -widthSpanNum '
            cmd += str(self.widthSpanNum.value())
            cmd += ' -curvature '
            cmd += str(self.curvature.value())
        cmd += ' -uvInTiles '
        cmd += "1" if self.uvInTiles.value() else "0"
        if self.uvInTiles.value():
            cmd += ' -uvLayoutType '
            cmd += str(self.uvLayoutType.value())
            cmd += ' -uvTileSeparation '
            cmd += str(self.uvTileSeparation.value())

        cmd += ' -createStripJoints '
        cmd += "1" if self.createStripJoints.value() else "0"
        if self.createStripJoints.value():
            cmd += ' -stripJointPlacementType '
            cmd += str(self.stripJointPlacementType.value())
            cmd += ' -jointNumOnStrip '
            cmd += str(self.jointNumOnStrip.value())
            cmd += ' -autoBindSkin '
            cmd += "1" if self.autoBindSkin.value() else "0"
            if self.autoBindSkin:
                cmd += ' -maxInfluences '
                cmd += str(self.maxInfluences.value())

        cmd += ' -createGuideJoints '
        cmd += "1" if self.createGuideJoints.value() else "0"
        if self.createGuideJoints.value():
            cmd += ' -guideJointPlacementType '
            cmd += str(self.guideJointPlacementType.value())
            cmd += ' -jointNumOnGuide '
            cmd += str(self.jointNumOnGuide.value())

        cmd += " \"" + desc + "\" "

        results = mel.eval(cmd)

    def rangeExport(self):
        print(maya.stringTable[ u'y_xgenm_ui_tabs_xgGeometryRendererTab.kFrameRangeRenderNotYetSupported'  ])
        pass

    def refresh(self):
        RendererTabUI.refresh(self)
        self.convertSelected.refresh()
        self.combineMesh.refresh()
        self.useWidthRamp.refresh()
        self.insertWidthSpan.refresh()
        self.widthSpanNum.refresh()
        self.curvature.refresh()
        self.uvInTiles.refresh()
        self.uvLayoutType.refresh()
        self.uvTileSeparation.refresh()
        self.createStripJoints.refresh()
        self.stripJointPlacementType.refresh()
        self.jointNumOnStrip.refresh()
        self.autoBindSkin.refresh()
        self.maxInfluences.refresh()
        self.createGuideJoints.refresh()
        self.guideJointPlacementType.refresh()
        self.jointNumOnGuide.refresh()

        initSetting = GeometryRendererSetting()
        initSetting.loadFromMayaOptionVar()
        self.convertSelected.setValue(initSetting.convertSelected)
        self.autoBindSkin.setValue(initSetting.autoBindSkin)
        self.maxInfluences.setValue(initSetting.maxInfluences)

        self.__onClickConvertSelected()
        self.__onClickInsertSpans()
        self.__onClickPlaceUV()
        self.__onClickCreateStripJoints()
        self.__onClickCreateGuideJoints()
