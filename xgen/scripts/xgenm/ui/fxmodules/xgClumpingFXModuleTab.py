from __future__ import division
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
import maya
maya.utils.loadStringResourcesForModule(__name__)


##
# @file xgClumpingFXModuleTab.py
# @brief Contains the Clumping FX Module UI.
#
# <b>CONFIDENTIAL INFORMATION: This software is the confidential and
# proprietary information of Walt Disney Animation Studios ("WDAS").
# This software may not be used, disclosed, reproduced or distributed
# for any purpose without prior written authorization and license
# from WDAS. Reproduction of any section of this software must include
# this legend and all copyright notices.
# Copyright Disney Enterprises, Inc. All rights reserved.</b>
#
# @author Arthur Shek
# @author Thomas V Thompson II
# @author Ying Liu
#
# @version Created 06/26/09
#

import os
import string
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *
import xgenm as xg
import xgenm.xgGlobal as xgg
import xgenm.xgLog as xglog
if xgg.Maya:
    import maya.mel as mel
    import maya.cmds as cmds
from xgenm.ui.widgets import *
from xgenm.ui.fxmodules.xgFXModuleTab import *
from xgenm.ui.util.xgProgressBar import setProgressInfo
from xgenm.ui.dialogs.xgPointsBase import *
from xgenm.ui.util.xgUtil import DpiScale


class ClumpingFXModuleTabUI(FXModuleTabUI):
    def __init__(self,name):
        FXModuleTabUI.__init__(self,name,maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kClumpingModifier'  ])
        # Widgets
        self.baseTopUI()
        
        # Clump Effect
        self.clumpEffect = ExpandUI(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kClumpEffect'  ])
        self.layout().addWidget(self.clumpEffect)

        self.clump = ExpressionUI("clump",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kClumpAnn'  ],
             self.name,
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kClump'  ])
        self.clumpEffect.addWidget(self.clump)

        self.clumpScale = RampUI("clumpScale",
                           maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kClumpScaleAnn'  ],
                           self.name,
                           maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kClumpScale'  ])
        self.clumpEffect.addWidget(self.clumpScale)
        
        self.clumpVolumize = CheckBoxUI(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kClumpVolumize'  ], "clumpVolumize",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kClumpVolumizeAnn'  ],
             self.name)
        self.clumpEffect.addWidget(self.clumpVolumize)

        self.clumpVariance = ExpressionUI("clumpVariance",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kClumpVarianceAnn'  ],
             self.name,
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kClumpVariance'  ])
        self.clumpEffect.addWidget(self.clumpVariance)

        # Copy Effect
        self.copyEffect = ExpandUI(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kCopyEffect'  ], False)
        self.layout().addWidget(self.copyEffect)

        self.copy = ExpressionUI("copy",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kCopyAnn'  ],
             self.name,
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kCopy'  ])
        self.copyEffect.addWidget(self.copy)

        self.copyScale = RampUI("copyScale",
                           maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kCopyScaleAnn'  ],
                           self.name,
                           maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kCopyScale'  ])
        self.copyEffect.addWidget(self.copyScale)
        
        self.copyVariance = ExpressionUI("copyVariance",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kCopyVarianceAnn'  ],
             self.name,
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kCopyVariance'  ])
        self.copyEffect.addWidget(self.copyVariance)

        # Cut Effect
        self.cutEffect = ExpandUI(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kCutEffect'  ], False)
        self.layout().addWidget(self.cutEffect)

        self.cut = ExpressionUI("cut",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kCutAnn'  ],
             self.name,
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kCut'  ])
        self.cutEffect.addWidget(self.cut)

        # Noise Effect
        self.noiseEffect = ExpandUI(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kNoiseEffect'  ], False)
        self.layout().addWidget(self.noiseEffect)

        self.noise = ExpressionUI("noise",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kNoiseAnn'  ],
             self.name,
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kNoise'  ])
        self.noiseEffect.addWidget(self.noise)

        self.noiseScale = RampUI("noiseScale",
                           maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kNoiseScaleAnn'  ],
                           self.name,
                           maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kNoiseScale'  ])
        self.noiseEffect.addWidget(self.noiseScale)
        
        self.noiseFrequency = ExpressionUI("noiseFrequency",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kNoiseFrequencyAnn'  ],
             self.name,
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kNoiseFrequency'  ])
        self.noiseEffect.addWidget(self.noiseFrequency)

        self.noiseCorrelation = ExpressionUI("noiseCorrelation",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kNoiseCorrelationAnn'  ],
             self.name,
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kNoiseCorrelation'  ])
        self.noiseEffect.addWidget(self.noiseCorrelation)

        # Frame Offset
        self.frameOffset = ExpandUI(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kFrameOffset'  ], False)
        self.layout().addWidget(self.frameOffset)

        self.frame = ExpressionUI("frame",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kFrameAnn'  ],
             self.name,
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kFrame'  ])
        self.frameOffset.addWidget(self.frame)

        # Flatness Effect
        self.flatnessEffect = ExpandUI(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kFlatnessEffect'  ], False)
        self.layout().addWidget(self.flatnessEffect)

        self.flatness = ExpressionUI("flatness",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kFlatnessAnn'  ],
             self.name,
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kFlatness'  ])
        self.flatnessEffect.addWidget(self.flatness)

        self.flatnessScale = RampUI("flatnessScale",
                           maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kFlatnessScaleAnn'  ],
                           self.name,
                           maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kFlatnessScale'  ])
        self.flatnessEffect.addWidget(self.flatnessScale)
        
        # Offset Effect
        self.offsetEffect = ExpandUI(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kOffsetEffect'  ], False)
        self.layout().addWidget(self.offsetEffect)

        self.offset = ExpressionUI("offset",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kOffsetAnn'  ],
             self.name,
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kOffset'  ])
        self.offsetEffect.addWidget(self.offset)

        self.offsetScale = RampUI("offsetScale",
                           maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kOffsetScaleAnn'  ],
                           self.name,
                           maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kOffsetScale'  ])
        self.offsetEffect.addWidget(self.offsetScale)
        
        # Curl Effect
        self.curlEffect = ExpandUI(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kCurlEffect'  ], False)
        self.layout().addWidget(self.curlEffect)

        self.curl = ExpressionUI("curl",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kCurlAnn'  ],
             self.name,
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kCurl'  ])
        self.curlEffect.addWidget(self.curl)

        self.curlScale = RampUI("curlScale",
                           maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kCurlScaleAnn'  ],
                           self.name,
                           maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kCurlScale'  ])
        self.curlEffect.addWidget(self.curlScale)
        
        self.options = CheckBoxUI(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kOptions'  ], ["colorPreview","cvAttr"],
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kOptionsAnn'  ],
             self.name,0,0,
             [maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kColorPreview'  ],
              maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kCvAttr'  ]])
        self.layout().addWidget(self.options)

        if ( xgg.Maya ):
            self.layout().addSpacing(DpiScale(10))
            buttonBox = QWidget()
            buttonLayout = QHBoxLayout()
            QLayoutItem.setAlignment(buttonLayout, QtCore.Qt.AlignRight)
            buttonLayout.setSpacing(DpiScale(3))
            buttonLayout.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
            buttonBox.setLayout(buttonLayout)
            setupMapButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kSetupMaps'  ])
            buttonLayout.addWidget(setupMapButton)
            self.layout().addWidget(buttonBox)
            
            self.layout().addSpacing(DpiScale(10))
            buttonBox = QWidget()
            buttonLayout = QHBoxLayout()
            QLayoutItem.setAlignment(buttonLayout, QtCore.Qt.AlignRight)
            buttonLayout.setSpacing(DpiScale(3))
            buttonLayout.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
            buttonBox.setLayout(buttonLayout)
            previewGuidesButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kPreviewGuides'  ])
            buttonLayout.addWidget(previewGuidesButton)
            exportGuidesButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kExportGuides'  ])
            buttonLayout.addWidget(exportGuidesButton)
            self.layout().addWidget(buttonBox)
            
            self.connect(setupMapButton, QtCore.SIGNAL("clicked()"),
                         self.setupMapSlot)
            self.connect(previewGuidesButton, QtCore.SIGNAL("clicked()"),
                         self.previewGuidesSlot)
            self.connect(exportGuidesButton, QtCore.SIGNAL("clicked()"),
                         self.exportGuidesSlot)
            
        # Fix for the expanding ramp ui
        filler = QWidget()
        self.layout().addWidget(filler)
        self.layout().setStretchFactor(filler,100)

    def setupMapSlot(self):
        dialog = GenerateClumpingMapsUI(self.name)
        dialog.show() # Using show() to get a non modal dialog to allow the edit point context tool to interact with the viewport.

    def previewGuidesSlot(self):
        de = xgg.DescriptionEditor
        pal = de.currentPalette()
        desc = de.currentDescription()
        # Grab current generator type and switch to Point
        c_grtr = xg.getActive(pal,desc,"Generator")
        c_disp = de.getAttr(c_grtr,"displacement")
        c_vecd = de.getAttr(c_grtr,"vectorDisplacement")
        c_bump = de.getAttr(c_grtr,"bump")
        c_ofst = de.getAttr(c_grtr,"offset")
        percent = de.getAttr("GLRenderer","percent")
        xg.setActive(pal,desc,"PointGenerator")
        # Grab its attributes and replace them
        p_pdir = de.getAttr("PointGenerator","pointDir")
        p_cull = de.getAttr("PointGenerator","cullFlag")
        p_disp = de.getAttr("PointGenerator","displacement")
        p_vecd = de.getAttr("PointGenerator","vectorDisplacement")
        p_bump = de.getAttr("PointGenerator","bump")
        p_ofst = de.getAttr("PointGenerator","offset")
        val = de.getAttr(self.name,"pointDir").replace("${FXMODULE}",self.name)
        de.setAttr("PointGenerator","pointDir",val)
        de.setAttr("PointGenerator","cullFlag","False")
        de.setAttr("PointGenerator","displacement",c_disp)
        de.setAttr("PointGenerator","vectorDisplacement",c_vecd)
        de.setAttr("PointGenerator","bump",c_bump)
        de.setAttr("PointGenerator","offset",c_ofst)
        de.setAttr("GLRenderer","percent","100.0")
        # Render out the clump guides
        setProgressInfo(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kPreviewingProgress' ] % self.name)
        cmd = 'xgmPreview -pb {"'+desc+'"}'
        mel.eval(cmd)
        # Restore everything
        de.setAttr("PointGenerator","pointDir",p_pdir)
        de.setAttr("PointGenerator","cullFlag",p_cull)
        de.setAttr("PointGenerator","displacement",p_disp)
        de.setAttr("PointGenerator","vectorDisplacement",p_vecd)
        de.setAttr("PointGenerator","bump",p_bump)
        de.setAttr("PointGenerator","offset",p_ofst)
        de.setAttr("GLRenderer","percent",percent)
        xg.setActive(pal,desc,c_grtr)

    def exportGuidesSlot(self):
        de = xgg.DescriptionEditor
        value = de.getAttr(self.name,"exportDir")
        (res,ok) = QInputDialog.getText(self,maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kExportClumpGuides'  ],
                    maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kExportClumpGuidesAnn'  ],
                    QLineEdit.Normal,value)
        if ok:
            de.setAttr(self.name,"exportDir",str(res))
            de.setAttr(self.name,"exportCurves","true")
            #
            # Need to fill in the export faces to correct value
            #
            de.setAttr(self.name,"exportFaces","")
            setProgressInfo(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kExportingClumpingGuidesProgress'  ])
            cmd = 'xgmNullRender -percent 0 "'+de.currentDescription()+'"'
            mel.eval(cmd)
            de.setAttr(self.name,"exportCurves","false")
            de.setAttr(self.name,"exportFaces","")

    def refresh(self):
        FXModuleTabUI.refresh(self)
        self.clump.refresh()
        self.clumpScale.refresh()
        self.clumpVolumize.refresh()
        self.clumpVariance.refresh()
        self.copy.refresh()
        self.copyScale.refresh()
        self.copyVariance.refresh()
        self.cut.refresh()
        self.noise.refresh()
        self.noiseScale.refresh()
        self.noiseFrequency.refresh()
        self.noiseCorrelation.refresh()
        self.frame.refresh()
        self.flatness.refresh()
        self.flatnessScale.refresh()
        self.offset.refresh()
        self.offsetScale.refresh()
        self.curl.refresh()
        self.curlScale.refresh()
        self.options.refresh()


class GenerateClumpingMapsUI(PointsBaseUI):
    """A dialog to specify the options for generating clumping maps.

    This provides fields for editing radius, texel resolution, and
    control maps, and also provides buttons for generate and cancel.
    """
    def __init__(self,name):
        PointsBaseUI.__init__(self,maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kGenerateClumpingMaps'  ])
        self.name = name

        de = xgg.DescriptionEditor
        mapInitialized = xg.stringToBool(de.getAttr(self.name,"mapInitialized"))
        if mapInitialized:
            useControlMap = xg.stringToBool(de.getAttr(self.name,"useControlMaps"))
            controlMask = de.getAttr(self.name,"controlMask")
            controlMap = de.getAttr(self.name,"controlMapDir")
        else:
            # gather control map information
            useControlMap = False
            modules = xg.fxModules(de.currentPalette(),de.currentDescription())
            clumpMod = ""
            for mod in modules:
                if mod == self.name:
                    break
                type = xg.fxModuleType(de.currentPalette(),
                                       de.currentDescription(),mod)
                if type == "ClumpingFXModule":
                    clumpMod = mod
            if clumpMod == "":
                # No prior clumping module so (possibly) use region map
                prim = de.activePrimitive()
                controlMask = de.getAttr(prim,"regionMask")
                controlMap = de.getAttr(prim,"regionMap")
                if controlMask != "0.0" and controlMask != "0":
                    useControlMap = True
            else:
                useControlMap = True
                controlMask = de.getAttr(clumpMod,"mask")
                controlMap = de.getAttr(clumpMod,"mapDir")
                controlMap = controlMap.replace("${FXMODULE}",clumpMod)
        
        # build the point definition section
        group = QGroupBox(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kPoints'  ])
        group.setAlignment(QtCore.Qt.AlignLeft)
        groupFont = group.font()
        groupFont.setBold(True)
        group.setFont(groupFont)
        layout = QVBoxLayout()

        self.pointDirUI(layout,
                        "pointDir",
                        maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kPointDirAnn'  ],
                        self.name,
                        maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kPointDir'  ])

        self.ptDensity = FloatUI("Density",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kDensityAnn'  ],
             "",0.0,10000.0,0.01,100.0,
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kDensity'  ])
        value = de.getAttr(self.name,"ptDensity")
        self.ptDensity.setValue(value)
        layout.addWidget(self.ptDensity)

        self.ptMask = ExpressionUI("Mask",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kMaskAnn'  ],
             "",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kMask'  ])
        self.ptMask.setMinimumWidth(DpiScale(50))
        value = de.getAttr(self.name,"ptMask")        
        self.ptMask.setValue(value)
        self.ptMask.refresh()
        layout.addWidget(self.ptMask)

        self.ptLengthUI(layout,
                        self.name)

        layout.addSpacing(DpiScale(5))
        ptButtonBox = QWidget()
        ptButtonLayout = QHBoxLayout()
        QLayoutItem.setAlignment(ptButtonLayout, QtCore.Qt.AlignRight)
        ptButtonLayout.setSpacing(DpiScale(3))
        ptButtonLayout.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
        ptButtonBox.setLayout(ptButtonLayout)
        ptLoadButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kLoad'  ])
        ptLoadButton.setAutoDefault(False)
        ptLoadButton.setDefault(False)
        ptButtonLayout.addWidget(ptLoadButton)
        ptGenButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kGenerate'  ])
        ptGenButton.setAutoDefault(False)
        ptGenButton.setDefault(False)
        ptButtonLayout.addWidget(ptGenButton)
        ptGuideButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kGuide'  ])
        ptGuideButton.setAutoDefault(False)
        ptGuideButton.setDefault(False)
        ptButtonLayout.addWidget(ptGuideButton)
        ptClrButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kClear'  ])
        ptClrButton.setAutoDefault(False)
        ptClrButton.setDefault(False)
        ptButtonLayout.addWidget(ptClrButton)
        layout.addWidget(ptButtonBox)
        self.connect(ptLoadButton, QtCore.SIGNAL("clicked()"),
                     lambda: self.loadPoints(self.name))
        self.connect(ptGenButton, QtCore.SIGNAL("clicked()"),
                     lambda: self.generatePoints(self.ptDensity.value(),
                                                 self.ptMask.value(),
                                                 self.name))
        self.connect(ptGuideButton, QtCore.SIGNAL("clicked()"),
                     self.guidePoints)
        self.connect(ptClrButton, QtCore.SIGNAL("clicked()"),
                     self.clearPoints)
        group.setLayout(layout)
        self.layout().addWidget(group)
        self.layout().addSpacing(DpiScale(5))

        # build the map definition section
        group = QGroupBox(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kMaps'  ])
        group.setAlignment(QtCore.Qt.AlignLeft)
        groupFont = group.font()
        groupFont.setBold(True)
        group.setFont(groupFont)
        layout = QVBoxLayout()
        self.mapDir = BrowseUI("mapDir",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kMapDirAnn'  ],
             self.name,"","in",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kMapDir'  ])
        self.mapDir.refresh()
        layout.addWidget(self.mapDir)
        
        self.radius = ExpressionUI("radiusVariance",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kRadiusVarianceAnn'  ],
             self.name,
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kRadiusVariance'  ])
        self.radius.setMinimumWidth(DpiScale(50))
        self.radius.refresh()
        layout.addWidget(self.radius)

        self.useCM = CheckBoxUI(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kUseControlMaps'  ],"useControlMaps",
                                maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kUseControlMapsAnn'  ], self.name)
        self.connect(self.useCM.boxValue[0], QtCore.SIGNAL("clicked(bool)"),
                     lambda x: self.cmUpdate())
        self.useCM.setValue(useControlMap)
        layout.addWidget(self.useCM)
        self.controlMask = ExpressionUI("controlMask", 
                   maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kControlMaskAnn'  ],
                   self.name, 
                   maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kControlMask'  ])
        self.controlMask.setValue(controlMask)
        layout.addWidget(self.controlMask)
        self.controlMap = BrowseUI("controlMapDir",
                   maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kControlMapAnn'  ],
                   self.name,"","in",
                   maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kControlMap'  ])
        self.controlMap.setValue(controlMap)
        layout.addWidget(self.controlMap)

        self.tpu = FloatUI("texelsPerUnit",
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kTexelsPerUnitAnn'  ],
             self.name,0.0,10000,1.0,50.0,
             maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kTexelsPerUnit'  ])
        self.connect(self.tpu.floatValue,QtCore.SIGNAL("editingFinished()"),
                     self.tpuUpdate)
        self.tpu.refresh()
        layout.addWidget(self.tpu)
        self.mem = QLabel(" 0 MB")
        self.mem.setToolTip(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kMemorySizeInMb'  ])
        self.tpu.layout().insertWidget(3,self.mem,100)
        group.setLayout(layout)
        self.layout().addWidget(group)
        self.layout().addSpacing(DpiScale(10))

        mapButtonBox = QWidget()
        mapButtonLayout = QHBoxLayout()
        QLayoutItem.setAlignment(mapButtonLayout, QtCore.Qt.AlignRight)
        mapButtonLayout.setSpacing(DpiScale(3))
        mapButtonLayout.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
        mapButtonBox.setLayout(mapButtonLayout)
        mapSaveButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kSave'  ])
        mapSaveButton.setAutoDefault(False)
        mapSaveButton.setDefault(False)
        mapButtonLayout.addWidget(mapSaveButton)
        mapCancelButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kCancel'  ])
        mapCancelButton.setAutoDefault(False)
        mapCancelButton.setDefault(False)
        mapButtonLayout.addWidget(mapCancelButton)
        self.layout().addWidget(mapButtonBox)
        self.connect(mapSaveButton, QtCore.SIGNAL("clicked()"),
                     self.generateMaps)
        self.connect(mapCancelButton, QtCore.SIGNAL("clicked()"),
                     self.close)

        self.cmUpdate()
        self.tpuUpdate()
        self.initDialog(self.name)

    def tpuUpdate(self):
        de = xgg.DescriptionEditor
        tpu = self.tpu.value()
        cmd = 'xgmClumpMap -computeMemory -texelsPerUnit '+tpu
        cmd += ' -d "'+de.currentDescription()+'"'
        memUsed = mel.eval(cmd)
        if memUsed > 1024.0:
            memUsed = memUsed/1024.0
            if memUsed > 1024.0:
                memUsed = memUsed/1024.0
                self.mem.setText('{0:0.3f} TB'.format(memUsed))
            else:
                self.mem.setText('{0:0.3f} GB'.format(memUsed))
        else:
            self.mem.setText('{0:0.3f} MB'.format(memUsed))

    def cmUpdate(self):
        value = self.useCM.value()
        if value:
            self.controlMask.setEnabled(True)
            self.controlMap.setEnabled(True)
            self.tpu.setEnabled(False)
        else:
            self.controlMask.setEnabled(False)
            self.controlMap.setEnabled(False)
            self.tpu.setEnabled(True)
            
    def generateMaps(self):
        de = xgg.DescriptionEditor
        de.setAttr(self.name,"mapInitialized","True")
        # set the attribute explictly. For non-first clumping, their value
        # is set from previous clumping, need to set back to C-side
        if self.useCM.value():
            de.setAttr(self.name,"useControlMaps", "1")
        else :
            de.setAttr(self.name,"useControlMaps", "0")
        de.setAttr(self.name,"controlMask", self.controlMask.value())
        de.setAttr(self.name,"controlMapDir", self.controlMap.value())

        # Save out the current points and what was use to define them. 
        self.savePoints(self.name)

        # Check if the point were generated and saved
        dirPath = de.getAttr(self.name,"pointDir").replace("${FXMODULE}",self.name)
        dirPath = xg.expandFilepath( dirPath, de.currentDescription() )
        if not os.path.exists(dirPath):
            xglog.XGWarning(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kNoPointFileFound'  ] % dirPath )
            return

        de.setAttr(self.name,"ptDensity",str(self.ptDensity.value()))
        de.setAttr(self.name,"ptMask",str(self.ptMask.value()))
        # Generate the clumping maps using the new points.
        setProgressInfo(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kClumpingProgress'  ])
        cmd = 'xgmClumpMap -pb'
        cmd += ' -fxmodule "' + self.name + '"'
        cmd += ' -mapDir "' + de.getAttr(self.name,"mapDir") + '"'
        cmd += ' -pointDir "' + de.getAttr(self.name,"pointDir") + '"'
        cmd += ' -texelsPerUnit ' + de.getAttr(self.name,"texelsPerUnit")
        cmd += ' -radiusVariance "' + \
            de.getAttr(self.name,"radiusVariance") + '"'
        useCM = self.useCM.value()
        if useCM:
            cmask = self.controlMask.value()
            cmask = cmds.encodeString(cmask)
            cmd += ' -controlMask "' + cmask + '"'
            cmd += ' -controlMap "' + self.controlMap.value() + '"'
        cmd += ' -d "' + de.currentDescription() + '"'
        maps = mel.eval(cmd)
        print(maya.stringTable[ u'y_xgenm_ui_fxmodules_xgClumpingFXModuleTab.kBakeInfo'  ] % maps)
        self.close()
