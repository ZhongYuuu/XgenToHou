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


#
# @file xgBrushTab.py
# @brief Contains the UI for Brush tab
# 
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *
import xgenm as xg
import xgenm as xgen
import xgenm.xgGlobal as xgg
from xgenm.ui.widgets import *
from xgenm.ui.brushes import xgBrush as xgb
from xgenm.ui.xgConsts import *
from xgenm.ui.util.xgUtil import CreateIcon
from xgenm.ui.util.xgUtil import DpiScale
from xgenm.ui.util.xgUtil import labelWidth
from xgenm.ui.util.xgUtil import ToolButtonSizeHint
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om
import traceback

UI_NO_GROOMABLE_SPLINE_ID = 0 
UI_GROOMING_ID = 1

def _igFileBrowserCB( title, fieldName, full ):
    mel.eval('igFileBrowser \"%s\" \"%s\" %d' % (title,fieldName,full))

def _igRefreshDensityCB( var ):
    mel.eval('igRefreshDensity("%s")'%var)

def _igRefreshXUVCB( var ):
    mel.eval('igRefreshXUV("%s")'%var)

def _igToggleVisibilityCB( ):
    mel.eval( 'XgGroomingVis();' )

def _onSetLengthCB():
    # trigger a preview update
    xgg.DescriptionEditor.playblast()

def _onSetWidthCB():
    # trigger a preview update
    xgg.DescriptionEditor.playblast()

def _onDisplayTypeCB():
    # trigger a preview update
    xgg.DescriptionEditor.playblast()

def _updateAutoExportTpuCB( ):
    val = cmds.floatSliderGrp( 'IG_AUTOEXPORT_TPU', q=True, v=True )
    igDesc = xg.igCurrentDescription( )
    if len(igDesc):
        # set the new value
        xg.setAttrValue( igDesc, ('igAutoExportTpu',val,'float') )
        # force the description to export
        xg.igForceExport( igDesc )

def _autoExportCB( ):
    val = cmds.textFieldButtonGrp( 'IG_AUTOEXPORT_DIR', q=True, tx=True )
    xg.setOptionVarString( 'igAutoExportFolder', val )
    # trigger a preview update
    xgg.DescriptionEditor.playblast()

def _onDensityChangeCB( ):
    """ Emit density change if the sync option is set. """    
    sync = cmds.checkBoxGrp("IG_SYNC_DENSITY", q=1, v1=1)
    if sync:
        val = cmds.floatSliderGrp( 'IG_DENSITY', q=True, v=True )
        xgg.DescriptionEditor.brushTab.densityChanged.emit( val )

def _igResetPrims():
    cmds.undoInfo( ock=True, cn="igResetPrims" )
    desc = xg.igCurrentDescription( )
    if len(desc):
        try:
            cmds.waitCursor( state=True )
            density = '%s.density' % desc
            interpStyle = '%s.interpStyle' % desc
            tickle = '%s.tickle' % desc
            val = cmds.getAttr( density )
            tempVal = val - 0.001
            cmds.setAttr( density, tempVal )
            style = cmds.getAttr(interpStyle)
            cmds.setAttr(interpStyle, 0 )
            cmds.setAttr(tickle,True )
            cmds.setAttr(density, val )
            cmds.setAttr(interpStyle, style )
        finally:
            cmds.undoInfo( cck=True )
            cmds.waitCursor( state=False )
            # trigger a preview update
            xgg.DescriptionEditor.playblast()


def _igUpdateSettingUI( ):
    """ update the UI connection for the igroom setting """
    igDesc = xg.igCurrentDescription( )
    try:    
        if len(igDesc) > 0:
            density = '%s.density' % igDesc
            interpStyle = '%s.interpStyle' % igDesc
            mask = '%s.mask' % igDesc
            xuvDir = '%s.xuvDir' % igDesc
            displayType = '%s.displayType' % igDesc
            tipColor = '%s.tipColor' % igDesc
            baseColor = '%s.baseColor' % igDesc
            length = '%s.length' % igDesc
            width = '%s.width' % igDesc

            cmds.connectControl( 'IG_DENSITY', density, index=2 )
            cmds.connectControl( 'IG_DENSITY', density, index=3 )
            cmds.connectControl( 'IG_METHOD', interpStyle )
            cmds.connectControl( 'IG_MASK', mask, index=2 )
            cmds.connectControl( 'IG_XUVDIR', xuvDir, index=2 )
            cmds.attrColorSliderGrp( 'IG_TIPCOLOR', edit=True, at=tipColor )
            cmds.attrColorSliderGrp( 'IG_BASECOLOR', edit=True, at=baseColor )
            cmds.connectControl( 'IG_DISPLAYTYPE', displayType )
            cmds.connectControl( 'IG_LENGTH', length, index=2 )
            cmds.connectControl( 'IG_LENGTH', length, index=3 )
            cmds.connectControl( 'IG_WIDTH', width, index=2 )
            cmds.connectControl( 'IG_WIDTH', width, index=3 )

    except:
        print(traceback.print_exc())

def _createWidget( func, name, **kwargs ):
    ctrl = func( name, **kwargs )
    w = xg.toQtWidget(ctrl)
    return w

def _createWidget2( func, **kwargs ):
    ctrl = func( **kwargs )
    w = xg.toQtWidget(ctrl)
    return w

def _addWidgetAndShow( addTo, widget):
    addTo.addWidget(widget)
    widget.show()

def _updateWidgets( ):
    """ Update various widgets in the tab """
    # All Setting widgets
    _igUpdateSettingUI( )
    
    # visibility checkbox
    vis = xg.igGetDescriptionVisibility()
    cmds.checkBoxGrp( 'IG_VISIBILITY', e=True, v1=vis )

    # tpu control    
    tpu = xg.igDescriptionTpu( xg.igCurrentDescription( ) )
    cmds.floatSliderGrp( 'IG_AUTOEXPORT_TPU', e=True, v=tpu )

def _onPostToolChanged( brushUI ):
    """ Abort current grooming tool on new context tools """
    if not cmds.currentCtx() == 'igBrushContextInstance':
        brushUI._abortActiveBrush()

class BrushTabUI(QWidget):
    densityChanged = QtCore.Signal( float )

    def __init__(self, parent):
        QWidget.__init__(self,parent)

        self._currentDesc = None
        xgg.DescriptionEditor.xgCurrentDescriptionChanged.connect(self.onXgDescriptionChanged)
        self.clearUI()

        # tablayout will be the actual layout for the whole tab
        self.tabLayout = QVBoxLayout(self)
        QLayoutItem.setAlignment(self.tabLayout, QtCore.Qt.AlignTop)
        self.tabLayout.setSpacing(DpiScale(0))
        self.tabLayout.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))
        self.setLayout(self.tabLayout)

        # build the ui stack which holds the UI containers. 
        self.uiStack = StackUI()

        # empty container 
        emptyContainer = QLabel(maya.stringTable[u'y_xgenm_ui_tabs_xgBrushTab.kGroomingNotAvailable' ])
        emptyContainer.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignHCenter)
        emptyContainer.setWordWrap(True)
        emptyContainer.setContentsMargins(DpiScale(16),DpiScale(16),DpiScale(16),DpiScale(16))
        self.uiStack.addWidget( emptyContainer )

        self.tabLayout.addWidget(self.uiStack)
        
        # width controls for the ui spacings. 
        self.mainColumnWidth = int(labelWidth() / DpiScale(1.0))
        self.columnWidth = [1,self.mainColumnWidth]
        self.mainSideWidth=65
        self.sideWidth = [1,self.mainSideWidth]
        self.spacing="   "

    def buildUI( self ):

        # put all the ui in a widget so we can quickly hide the content of the editor
        editorContainer = QWidget()
        mainLayout = QVBoxLayout(self)
        QLayoutItem.setAlignment(mainLayout, QtCore.Qt.AlignTop)
        mainLayout.setSpacing(DpiScale(0))
        mainLayout.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))
        editorContainer.setLayout(mainLayout)
        # add to the ui stack
        self.uiStack.addWidget( editorContainer )

        # holds the layout for the brush buttons and brush UI
        topWidget = ExpandUI( maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kBrush'  ] )

        # holds the layout for the igroom settings
        bottomWidget = QWidget()
        bottomLayout = QVBoxLayout()
        QLayoutItem.setAlignment(bottomLayout, QtCore.Qt.AlignTop)
        bottomLayout.setSpacing(DpiScale(0))
        bottomLayout.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))
        bottomWidget.setLayout(bottomLayout)

        # build brush buttons and UI layout
        brushBtnWidget = QWidget()
        brushBtnLayout = QGridLayout(brushBtnWidget)
        brushBtnLayout.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))        
        brushBtnLayout.setSpacing(DpiScale(1))
        brushBtnLayout.setSizeConstraint( QLayout.SetFixedSize )
        brushBtnWidget.setLayout(brushBtnLayout)

        self.brushUIWidget = StackUI()        
        self.brushUI(brushBtnLayout)
        topWidget.addWidget(brushBtnWidget)
        topWidget.addWidget(self.brushUIWidget)    
        mainLayout.addWidget( topWidget )

        # build the edit layout
        self.editUI( bottomLayout )

        # build brush settings UI layout
        self.settingsUI( bottomLayout )

        mainLayout.addWidget( bottomWidget )

    def brushUI( self, theLayout ):
        def button(brush):
            """ create 'compound' brush button """
            (text,icon) = brush.uiInfo()
            b = QToolButton()
            b.setText(text)
            b.setToolButtonStyle( QtCore.Qt.ToolButtonTextUnderIcon )
            b.setIcon(CreateIcon(icon))
            b.setIconSize(QSize(DpiScale(32),DpiScale(32)))
            b.setMinimumSize( ToolButtonSizeHint(b, GroomBrushButtonSize, bottomText=text) )
            b.setToolTip( maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kBrushAnn'  ] % text )
            b.setAutoRaise(True)
            b.setCheckable(True)
            b.setStyleSheet( 'QToolButton:checked { background-color:rgb(88,88,88); border:1px solid rgb(32,32,32); border-radius:3px; }' )
            b.setProperty( 'brush', brush )
            b.clicked.connect( self.invokeBrush )
            self.brushBtnMap[text] = b
            return b

        # get all brush classes     
        brushes = xgb.brushList()
        k = 0
        for i,row in enumerate(brushes):
            for j,brush in enumerate(row):
                br = brush()
                self.brushUIWidget.addWidget( br )
                self.brushesToInit.add( br.objectName() )
                self.brushIndexMap[ br.objectName() ] = k
                k += 1 
                b = button( br )            
                theLayout.addWidget( b, i, j )
        
        # add a blank UI for the initial UI state
        blankBrushWidget = QWidget()
        blankBrushLayout = QVBoxLayout(blankBrushWidget)
        blankBrushLayout.setContentsMargins(DpiScale(32),DpiScale(32),DpiScale(32),DpiScale(32))
        QLayoutItem.setAlignment(blankBrushLayout, QtCore.Qt.AlignVCenter|QtCore.Qt.AlignHCenter)
        label = QLabel(maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kNoBrushSelected'  ])
        blankBrushLayout.addWidget( label )
        self.brushUIWidget.addWidget( blankBrushWidget )

    def settingsUI( self, theLayout ):
        settingWidget = ExpandUI( maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kSettings'  ] )

        vis = bool(xg.igGetDescriptionVisibility())
        _addWidgetAndShow(settingWidget, _createWidget(  cmds.checkBoxGrp, "IG_VISIBILITY", l=maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kVisibility'  ]+self.spacing, cw=self.columnWidth, ncb=1, l1='', v1=vis,
                                                             ann=maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kVisibilityAnn'  ],
                                                             cc='xgen.ui.tabs.xgBrushTab._igToggleVisibilityCB()' ))

        densityWidget = QWidget()
        densityLayout = QHBoxLayout(densityWidget)
        densityLayout.setSpacing(DpiScale(0))
        densityLayout.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))        
        QLayoutItem.setAlignment(densityLayout, QtCore.Qt.AlignLeft)
        densityWidget.setLayout(densityLayout)

        _addWidgetAndShow(densityLayout, _createWidget( cmds.floatSliderGrp, 'IG_DENSITY', l=maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kDensity'  ]+self.spacing, pre=4, f=True, 
                                                            min=0.001, max=500.0, fmx=25000.0, step=0.02, v=1.0, cw=self.columnWidth, 
                                                            ann=maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kDensityAnn'  ],
                                                            cc='xgen.ui.tabs.xgBrushTab._onDensityChangeCB()' ))

        vis = True
        _addWidgetAndShow(densityLayout, _createWidget(  cmds.checkBoxGrp, "IG_SYNC_DENSITY", l=maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kSyncGen'  ]+self.spacing, cw=self.sideWidth, ncb=1, l1='', 
                                                             v1=vis,
                                                             ann=maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kSyncGenAnn'  ] ))
        settingWidget.addWidget(densityWidget)

        _addWidgetAndShow(settingWidget, _createWidget( cmds.radioButtonGrp, 'IG_METHOD', l=maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kSampling'  ]+self.spacing, nrb=3, cw=self.columnWidth, sl=0,
                                                            ann=maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kMethodAnn'  ],
                                                            la3=[maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kLinear'  ],maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kNearest'  ],maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kInterp'  ]],
                                                            data1=0, data2=1, data3=2 ))
        
        maskWidget = QWidget()
        maskLayout = QHBoxLayout(maskWidget)
        maskLayout.setSpacing(DpiScale(0))
        QLayoutItem.setAlignment(maskLayout, QtCore.Qt.AlignLeft)
        maskLayout.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))        
        maskWidget.setLayout(maskLayout)

        _addWidgetAndShow(maskLayout, _createWidget( cmds.textFieldGrp, 'IG_MASK', l=maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kMask'  ]+self.spacing, cw=self.columnWidth, 
                                                         ann=maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kMaskAnn'  ] ))

        _addWidgetAndShow(maskLayout, _createWidget2( cmds.iconTextButton, style="iconOnly", width=22, height=22,
                                                          ann=maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kRefreshAnn'  ],
                                                          c='xgen.ui.tabs.xgBrushTab._igRefreshDensityCB("IG_MASK")',
                                                          image=xg.iconDir()+'igRefresh.png' ))
        settingWidget.addWidget(maskWidget)

        xuvWidget = QWidget()
        xuvLayout = QHBoxLayout(xuvWidget)
        xuvLayout.setSpacing(DpiScale(0))
        QLayoutItem.setAlignment(xuvLayout, QtCore.Qt.AlignLeft)
        xuvLayout.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))        
        xuvWidget.setLayout(xuvLayout)

        cmd = 'xgen.ui.tabs.xgBrushTab._igFileBrowserCB( "'+maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kXuvFolder'  ]+'", "IG_XUVDIR", 0 )'
        _addWidgetAndShow(xuvLayout, _createWidget( cmds.textFieldButtonGrp, 'IG_XUVDIR', l=maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kXuv'  ]+self.spacing, cw=self.columnWidth,
                                                        bl=maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kBrowse'  ], bc=cmd, cal=[1,'right'], 
                                                        ann=( maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kBrowseAnn'  ]) ))

        _addWidgetAndShow(xuvLayout, _createWidget2( cmds.iconTextButton, style="iconOnly", width=22, height=22,
                                                         ann=maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kRefreshTheXuvPointsFromDisk'  ],
                                                         c='xgen.ui.tabs.xgBrushTab._igRefreshXUVCB("IG_XUVDIR")',
                                                         image=xg.iconDir()+"igRefresh.png" ))
        settingWidget.addWidget(xuvWidget)

        _addWidgetAndShow(settingWidget,_createWidget( cmds.attrColorSliderGrp, 'IG_TIPCOLOR', l=maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kTipColor'  ]+self.spacing, cw=self.columnWidth, sb=False,
                                                           ann=maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kTipColorAnn'  ] ))

        _addWidgetAndShow(settingWidget, _createWidget( cmds.attrColorSliderGrp, 'IG_BASECOLOR', l=maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kBaseColor'  ]+self.spacing, cw=self.columnWidth, sb=False,
                                                            ann=maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kBaseColorAnn'  ] ))

        _addWidgetAndShow(settingWidget, _createWidget( cmds.radioButtonGrp, 'IG_DISPLAYTYPE', l=maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kDisplay'  ]+self.spacing, nrb=2, cw=self.columnWidth,
                                                            ann=maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kDisplayAnn'  ],
                                                            la2=[maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kLines'  ],
                                                                 maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kCards'  ]],
                                                            data1=0, data2=1,
                                                            onc='xgen.ui.tabs.xgBrushTab._onDisplayTypeCB()'))

        _addWidgetAndShow(settingWidget, _createWidget( cmds.floatSliderGrp, 'IG_LENGTH', l=maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kLength'  ]+self.spacing, pre=4, f=True, 
                                                            min=0.001, max=3.0, fmx=5000.0, step=0.02, v=0.5, cw=self.columnWidth, 
                                                            ann=maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kLengthAnn'  ],
                                                            cc='xgen.ui.tabs.xgBrushTab._onSetLengthCB()' ))
        
        _addWidgetAndShow(settingWidget, _createWidget( cmds.floatSliderGrp, 'IG_WIDTH', l=maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kWidth'  ]+self.spacing, pre=4, f=True, 
                                                            min=0.001, max=3.0, fmx=1000.0, step=0.02, v=0.1, cw=self.columnWidth, 
                                                            ann=maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kWidthAnn'  ],
                                                            cc='xgen.ui.tabs.xgBrushTab._onSetWidthCB()' ))
        
        # auto map export defaults        
        tpu = xg.igDescriptionTpu( xg.igCurrentDescription( ) )
        _addWidgetAndShow(settingWidget, _createWidget( cmds.floatSliderGrp, "IG_AUTOEXPORT_TPU", l=maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kTexelsPerUnit'  ]+self.spacing, f=True, cw=self.columnWidth,
                                                            min=0.001, max=100.0, fmx=10000.0, pre=3, step=0.001, v=tpu,
                                                            ann=( maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kTexelsPerUnitAnn'  ]),
                                                            cc='xgen.ui.tabs.xgBrushTab._updateAutoExportTpuCB()' ))

        axDir = xg.getOptionVarString( 'igAutoExportFolder', '${DESC}/groom'  )
        bccb = 'xgen.ui.tabs.xgBrushTab._igFileBrowserCB( "'+maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kAutoExportDirectory'  ]+'", "IG_AUTOEXPORT_DIR", 1 )'
        cccb = 'xgen.ui.tabs.xgBrushTab._autoExportCB( )'
        _addWidgetAndShow(settingWidget, _createWidget( cmds.textFieldButtonGrp, "IG_AUTOEXPORT_DIR", l=maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kExportFolder'  ]+self.spacing, cw=self.columnWidth,
                                                            bl=maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kBrowse2'  ], bc=bccb, cc=cccb, cal=[1,'right'], text=axDir,
                                                            ann=maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kExportAnn'  ] ))

        theLayout.addWidget(settingWidget)

    def editUI( self, theLayout ):
        def button( text, tooltip, func, icon):
            """ create function button """
            b = QToolButton()
            b.setText(text)
            b.setIcon(CreateIcon(icon))
            b.setIconSize(QSize(DpiScale(32),DpiScale(32)))
            b.setMinimumSize( ToolButtonSizeHint(b, GroomEditButtonSize, bottomText=text) )
            b.setToolTip(tooltip)
            b.setAutoRaise(True)
            b.setToolButtonStyle( QtCore.Qt.ToolButtonTextUnderIcon )
            b.clicked.connect( self.igFuncCB )
            b.setProperty( 'func', func )
            return b

        editWidget = ExpandUI( maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kEdit'  ] )

        tbarWidget = QWidget()
        hLayout = QHBoxLayout(tbarWidget)
        hLayout.setSpacing(DpiScale(0))
        hLayout.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))        
        QLayoutItem.setAlignment(hLayout, QtCore.Qt.AlignLeft)
        tbarWidget.setLayout(hLayout)

        w = button( maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kFlipToRight'  ], maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kFlipLeftToRight'  ], ('mel','igFlip 1'), 'iGroom_flipR.png' )
        hLayout.addWidget( w )
        w = button( maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kFlipToLeft'  ], maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kFlipRightToLeft'  ], ('mel','igFlip 0'), 'iGroom_flipL.png' )
        hLayout.addWidget( w )
        w = button( maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kAutoTwist'  ], maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kAutoTwist2'  ], ('mel','igAutoTwist'), 'iGroom_autoTwist.png' )
        hLayout.addWidget( w )
        w = button( maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kReset'  ], maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kResetPrimitives'  ], ('py','_igResetPrims()'), 'iGroom_reset.png' )
        hLayout.addWidget( w )
        w = button( maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kClear'  ], maya.stringTable[ u'y_xgenm_ui_tabs_xgBrushTab.kClearCurrentMask'  ], ('mel','string $igDesc = igCurrentDescription();iGroom -cm -d $igDesc ;'), 'iGroom_unmask.png' )
        hLayout.addWidget( w )
        editWidget.addWidget( tbarWidget )

        theLayout.addWidget( editWidget )

    def igFuncCB( self ):
        evaluator = { 'mel':mel.eval, 'py':eval }
        (lang,func) = self.sender().property('func')
        try:
            cmds.waitCursor( state=True )
            evaluator[lang](func)
        finally:
            # trigger a preview update
            xgg.DescriptionEditor.playblast()
            cmds.waitCursor( state=False )

        _updateWidgets( )

    def showEvent( self, event ):
        xg.igActivateDescription( xgg.DescriptionEditor.currentDescription() )
        self.updateUI()

    def onXgDescriptionChanged( self, xgPal, xgDescr ):
        """ activate ig description related to the current xgen description/palette and update the UI """
        if self._currentDesc and not self._currentDesc == xgDescr:
            # abort the last active tool if any
            self._abortActiveBrush()
        self._currentDesc = xgDescr
        xg.igActivateDescription( xgDescr )
        self.updateUI()

    def clearUI(self):
        self.activeBrush = None
        self.brushBtnMap = {}
        self.brushIndexMap = {}
        self.brushesToInit = set()
        self.initUI = False
        self._toolChangedID = None

    def updateUI( self ):
        """ Show the UI only if we have a valid ig description for the current xgen description """        
        # process ui only if the tab is visible
        if not self.isVisible():
            return

        # make content visible if we have a valid igroom description and an active spline primitive
        xdesc = xgg.DescriptionEditor.currentDescription()
        xpal = xgg.DescriptionEditor.currentPalette()
        prim = xg.getActive(xpal,xdesc,"Primitive")
        igDesc = xg.igCurrentDescription()

        if not len(igDesc) or not prim == 'SplinePrimitive':
            # show empty UI
            self.uiStack.setCurrent( UI_NO_GROOMABLE_SPLINE_ID )
            self._abortActiveBrush()
            return

        if not self.initUI:
            # build tab UI if not already done
            # note: the UI must be built only when we have an active grooming description
            self.buildUI()

            # set the brush UI to blank
            self.brushUIWidget.setCurrent( len(self.brushUIWidget.stack)-1 )
            self.initUI = True

        # show full UI
        self.uiStack.setCurrent( UI_GROOMING_ID )

        _updateWidgets( )

    def _abortActiveBrush(self):
        if self.activeBrush:
            self._uninstallToolChangedCB()
            info = self.activeBrush.uiInfo()
            currentBtn = self.brushBtnMap[ info[0] ]
            currentBtn.setChecked(False)
            self.activeBrush.abort()
            # set the brush UI to blank
            self.brushUIWidget.setCurrent( len(self.brushUIWidget.stack)-1 )
            
    def updateBrushButton( self, newBr ):
        """ 
        Update tool button and activate the new brush tool.
        Note: This method also builds the brush UI. This needs to be done when 
        the brush tab is shown, so calling this method in other scenarios 
        will get you invalid UI controls.
        """
        if newBr == self.activeBrush:
            # check button again if user clicked on the same tool
            info = newBr.uiInfo()
            currentBtn = self.brushBtnMap[ info[0] ]
            currentBtn.setChecked(True)
        elif not self.activeBrush is None:
            # deactivate old brush
            info = self.activeBrush.uiInfo()
            activeBtn = self.brushBtnMap[ info[0] ]
            activeBtn.setChecked(False)

        # new active brush
        self.activeBrush = newBr
        info = self.activeBrush.uiInfo()
        activeBtn = self.brushBtnMap[ info[0] ]

        # build UI if not done yet
        if self.activeBrush.objectName() in self.brushesToInit:            
            self.activeBrush.buildUI()
            self.brushesToInit.remove( self.activeBrush.objectName() )

        self.activeBrush.refresh()
        
    def invokeBrush( self ):
        """ update the brush UI and activate the new brush tool """

        self._installToolChangedCB()
        br = self.sender().property('brush')
        self.updateBrushButton( br )

        # show brush UI 
        index = self.brushIndexMap[ br.objectName() ]    
        self.brushUIWidget.setCurrent( index )

        # invoke brush tool
        br.invoke()

    def _installToolChangedCB(self):
        """ register callback to listen to post tool changed """
        if self._toolChangedID == None:
            self._toolChangedID = om.MEventMessage.addEventCallback( "PostToolChanged", _onPostToolChanged, self )              

    def _uninstallToolChangedCB(self):
        """ remove tool changed callback """
        if not self._toolChangedID == None:
            om.MEventMessage.removeCallback( self._toolChangedID )
            self._toolChangedID = None
