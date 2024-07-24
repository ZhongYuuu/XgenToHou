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
# @file xgEditFXChain.py
# @brief Contains the Edit FX Chain UI.
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
# @version Created 06/22/09
#

import os

from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *
import xgenm as xg
import xgenm.xgGlobal as xgg
from xgenm.ui.util.xgUtil import *
if xgg.Maya:
    import maya.mel as mel

# module name mapped to its localized counterpart
_locNames = {"AnimWires"         :maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kAnimWires'  ],
             "ApplyNetForce"     :maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kApplyNetForce'  ],
             "BakedGroomManager" :maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kGroomBake'  ],
             "BlockAnim"         :maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kBlockAnim'  ],
             "Clumping"          :maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kClumping'  ],
             "Coil"              :maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kCoil'  ],
             "Collision"         :maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kCollision'  ],
             "ControlWires"      :maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kControlwires'  ],
             "Cut"               :maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kCut'  ],
             "Debug"             :maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kDebug'  ],
             "DirectionalForce"  :maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kDirectionalForce'  ],
             "Force"             :maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kForce'  ],
             "MeshCut"           :maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kMeshcut'  ],
             "Noise"             :maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kNoise'  ],
             "Particle"          :maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kParticle'  ],
             "PlaneAnim"         :maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kPlaneAnim'  ],
             "PlaneForce"        :maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kPlaneForce'  ],
             "PolylineForce"     :maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kPolylineForce'  ],
             "PreserveClumps"    :maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kPreserveClumps'  ],
             "Snapshot"          :maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kSnapshot'  ],
             "SphereForce"       :maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kSphereForce'  ],
             "Wind"              :maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kWind'  ]}

class EditFXChainUI(QDialog):
    """A dialog for editing a descriptions FX module chain.

    This provides a list of the available modules, allows the user
    to add/remove modules from the chain, and reorder the modules
    within the chain.
    """
    def __init__(self):
        QDialog.__init__(self)
        self.setWindowTitle(maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kEditModifierStack'  ])
        self.setGeometry(50,50,DpiScale(400),DpiScale(400))
        self.setSizeGripEnabled(True)
        layout = QVBoxLayout()
        self.setLayout(layout)
        # a row for the two lists
        row = QWidget()
        hbox = QHBoxLayout()
        QLayoutItem.setAlignment(hbox, QtCore.Qt.AlignLeft)
        hbox.setSpacing(DpiScale(3))
        hbox.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
        hbox.addWidget( self.mkAvailable() )
        hbox.addWidget( self.mkChain() )
        row.setLayout(hbox)
        layout.addWidget(row)
        layout.addSpacing(DpiScale(10))
        self.addButtons()

    def mkAvailable(self):
        col = QWidget()
        vbox = QVBoxLayout()
        QLayoutItem.setAlignment(vbox, QtCore.Qt.AlignLeft)
        vbox.setSpacing(DpiScale(3))
        vbox.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
        label = QLabel(maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kAvailableModules'  ])
        self.avail = QListWidget()
        for modulename in xgg.FXModuleTypes():
            modulename = modulename.replace("FXModule", "")
            self.avail.addItem(modulename)
        vbox.addWidget(label)
        vbox.addWidget(self.avail)    
        col.setLayout(vbox)
        return col

    def mkChain(self):
        col = QWidget()
        vbox = QVBoxLayout()
        QLayoutItem.setAlignment(vbox, QtCore.Qt.AlignLeft)
        vbox.setSpacing(DpiScale(3))
        vbox.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
        label = QLabel(maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kCurrentModules'  ])
        self.chain = QListWidget()
        self.refreshChain()
        vbox.addWidget(label)
        vbox.addWidget(self.chain)
        col.setLayout(vbox)
        return col

    def refreshChain(self,name=""):
        self.chain.clear()
        de = xgg.DescriptionEditor
        modules = xg.fxModules(de.currentPalette(),de.currentDescription())
        row = 0
        for module in modules:
            self.chain.addItem(module)
            if module == name:
                self.chain.setCurrentRow(row)
            row += 1

    def addButtons(self):
        row = QWidget()
        hbox = QHBoxLayout()
        QLayoutItem.setAlignment(hbox, QtCore.Qt.AlignCenter)
        hbox.setSpacing(DpiScale(3))
        hbox.setContentsMargins(DpiScale(1),DpiScale(1),DpiScale(1),DpiScale(1))
        self.addButton = QToolButton()
        self.addButton.setIcon(CreateIcon("xgFXAdd.png"))
        self.addButton.setFixedSize(DpiScale(42),DpiScale(26))
        self.addButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kAddAnn'  ])
        self.connect(self.addButton, QtCore.SIGNAL("clicked()"),
                     self.addCB)
        hbox.addWidget(self.addButton)
        
        self.removeButton = QToolButton()
        self.removeButton.setIcon(CreateIcon("xgFXRemove.png"))
        self.removeButton.setFixedSize(DpiScale(42),DpiScale(26))
        self.removeButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kRemoveAnn'  ])
        self.connect(self.removeButton, QtCore.SIGNAL("clicked()"),
                     self.removeCB)
        hbox.addWidget(self.removeButton)

        self.upButton = QToolButton()
        self.upButton.setIcon(CreateIcon("xgFXMoveUp.png"))
        self.upButton.setFixedSize(DpiScale(42),DpiScale(26))
        self.upButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kUpAnn'  ])
        self.connect(self.upButton, QtCore.SIGNAL("clicked()"),
                     self.upCB)
        hbox.addWidget(self.upButton)
        
        self.downButton = QToolButton()
        self.downButton.setIcon(CreateIcon("xgFXMoveDown.png"))
        self.downButton.setFixedSize(DpiScale(42),DpiScale(26))
        self.downButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kDownAnn'  ])
        self.connect(self.downButton, QtCore.SIGNAL("clicked()"),
                     self.downCB)
        hbox.addWidget(self.downButton)
        
        filler = QWidget()
        hbox.addWidget(filler)
        hbox.setStretchFactor(filler,100)

        self.doneButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kDone'  ])
        self.doneButton.setFixedWidth(DpiScale(90))
        self.doneButton.setAutoRepeat(False)
        self.doneButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kDoneAnn'  ])
        self.connect(self.doneButton, QtCore.SIGNAL("clicked()"),
                     self.reject)
        hbox.addWidget(self.doneButton)
        row.setLayout(hbox)
        self.layout().addWidget(row)
        
    def addCB(self):
        mo=str(self.avail.currentItem().text()+"FXModule")
        de=xgg.DescriptionEditor
        res=xg.addFXModule(de.currentPalette(),de.currentDescription(),mo)
        if res != "":
            self.refreshChain(res)
            xg.invokeCallbacks("PostFXModuleUserAdd", [res,de.currentPalette(),de.currentDescription(),mo])
        
    def removeCB(self):
        mo=str(self.chain.currentItem().text())
        de=xgg.DescriptionEditor
        res=xg.removeFXModule(de.currentPalette(),de.currentDescription(),mo)
        if res:
            self.refreshChain()
        
    def upCB(self):
        mo=str(self.chain.currentItem().text())
        de=xgg.DescriptionEditor
        res=xg.moveFXModule(de.currentPalette(),de.currentDescription(),mo,-1)
        if res:
            self.refreshChain(mo)
        
    def downCB(self):
        mo=str(self.chain.currentItem().text())
        de=xgg.DescriptionEditor
        res=xg.moveFXModule(de.currentPalette(),de.currentDescription(),mo,1)
        if res:
            self.refreshChain(mo)

def getFxModuleIconPath(moduleName):
    path = xg.iconDir()+"fx_"+moduleName[:1].lower()+moduleName[1:]+".png"
    if not os.path.exists(path):
        return xg.iconDir()+"xgLogo.png"
    else:
        return path

class FXChainLoaderUI(QDialog):
    """A dialog for loading an FX chain module.

    This provides a list of the available modules, allows the user
    to add/remove modules from the chain.
    """
    def __init__(self,x,y):
        QDialog.__init__(self)
        self.setGeometry(x,y,DpiScale(580),DpiScale(330))
        self.setSizeGripEnabled(True)
        self.setWindowTitle(maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kAddModifierWindow'  ])

        self.frame = QFrame(self)

        layout = QVBoxLayout(self.frame)
        self.setLayout(layout)
        layout.setContentsMargins(DpiScale(10),DpiScale(10),DpiScale(10),DpiScale(10))
        layout.setSpacing(DpiScale(0))
        layout.addWidget( self.mkAvailable() )
        self.addButtons()        


    def mkAvailable(self):
        col = QWidget()
        vbox = QVBoxLayout(self.frame)
        QLayoutItem.setAlignment(vbox, QtCore.Qt.AlignLeft)

        # if in localized mode, build tab in horizontal layout to
        # accomodate japanese text better
        isLocalized = mel.eval("about -uiLanguageIsLocalized;")
        self.avail = QListWidget()
        self.avail.setSelectionMode( QAbstractItemView.MultiSelection )
        self.avail.setMovement(QListView.Static)
        self.avail.setResizeMode(QListView.Adjust)
        self.avail.setWordWrap(True)
        if isLocalized == 1:
            self.avail.setViewMode(QListView.ListMode)
            self.avail.setWrapping(True)
            self.avail.setFlow(QListView.LeftToRight)
            self.avail.setIconSize(QSize(DpiScale(50),DpiScale(50)))
        else:
            self.avail.setViewMode(QListView.IconMode)
            self.avail.setGridSize(QSize(DpiScale(64),DpiScale(80)))


        for modulename in xgg.FXModuleTypes():
            modulename = modulename.replace("FXModule", "")
            # If modifier is in global list, take the name from there.
            # Otherwise create the name through makeLabel.
            if ( modulename in _locNames):
                niceName = _locNames[modulename]
            else:
                niceName = makeLabel(modulename) 

            icon = CreateIcon(getFxModuleIconPath(modulename))

            
            item = QListWidgetItem(icon,niceName)
            item.setToolTip(niceName)
            item.setData(QtCore.Qt.UserRole,modulename)
            if isLocalized == 1:
                item.setSizeHint(QSize(DpiScale(110),DpiScale(50)))
                item.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            self.avail.addItem(item)
        
        vbox.addWidget(self.avail)    
        col.setLayout(vbox)
        return col

    def addButtons(self):
        row = QWidget()
        hbox = QHBoxLayout(self.frame)
        QLayoutItem.setAlignment(hbox, QtCore.Qt.AlignCenter)

        self.okButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kOk'  ])
        self.okButton.setFixedWidth(DpiScale(90))
        self.okButton.setAutoRepeat(False)
        self.okButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kOkAnn'  ])
        self.connect(self.okButton, QtCore.SIGNAL("clicked()"), self.okCB)
        self.okButton.setDefault(True)

        self.cancelButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kCancel'  ])
        self.cancelButton.setFixedWidth(DpiScale(90))
        self.cancelButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kCancelAnn'  ])
        self.connect(self.cancelButton, QtCore.SIGNAL("clicked()"), self.reject)
        
        hbox.addWidget(self.okButton)
        hbox.addWidget(self.cancelButton)
        row.setLayout(hbox)
        self.layout().addWidget(row)

    def okCB(self):
        de=xgg.DescriptionEditor
        for m in self.avail.selectedItems():            
            module=str(m.data(QtCore.Qt.UserRole)+"FXModule")
            result=xg.addFXModule(de.currentPalette(),de.currentDescription(),module)
            if result != "":
                xg.invokeCallbacks("PostFXModuleUserAdd", [result,de.currentPalette(),de.currentDescription(),module])
                xgg.DescriptionEditor.fxStackTab.addNewModule( result )
        self.accept()

class FXChainOrderingUI(QDialog):
    """A dialog for ordering modules within an FX module chain.
    """
    def __init__(self,x,y):
        QDialog.__init__(self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setGeometry(x,y,DpiScale(200),DpiScale(300))    
        self.setSizeGripEnabled(True)

        self.frame = QFrame(self)
        self.frame.setGeometry(self.rect())
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Plain)

        layout = QVBoxLayout(self.frame)
        self.setLayout(layout)
        layout.setContentsMargins(DpiScale(0),DpiScale(0),DpiScale(0),DpiScale(0))
        layout.setSpacing(DpiScale(0))
        layout.addWidget( self.mkChain() )
        self.addButtons()        
        
    def addButtons(self):
        row = QWidget()
        hbox = QHBoxLayout(self.frame)
        QLayoutItem.setAlignment(hbox, QtCore.Qt.AlignCenter)
        
        self.okButton = QPushButton(maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kOk2'  ])
        self.okButton.setFixedWidth(DpiScale(70))
        self.okButton.setAutoRepeat(False)
        self.okButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kOkAnn2'  ])
        self.connect(self.okButton, QtCore.SIGNAL("clicked()"), self.accept)
        self.okButton.setDefault(True)
        hbox.addWidget(self.okButton)

        self.upButton = QToolButton()
        self.upButton.setIcon(CreateIcon("xgFXMoveUp.png"))
        self.upButton.setFixedSize(DpiScale(26),DpiScale(26))
        self.upButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kUpAnn2'  ])
        self.connect(self.upButton, QtCore.SIGNAL("clicked()"), self.upCB)
        hbox.addWidget(self.upButton)
        
        self.downButton = QToolButton()
        self.downButton.setIcon(CreateIcon("xgFXMoveDown.png"))
        self.downButton.setFixedSize(DpiScale(26),DpiScale(26))
        self.downButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kDownAnn2'  ])
        self.connect(self.downButton, QtCore.SIGNAL("clicked()"), self.downCB)
        hbox.addWidget(self.downButton)
        
        self.removeButton = QToolButton()
        self.removeButton.setIcon(CreateIcon("xgDelete.png"))
        self.removeButton.setFixedSize(DpiScale(26),DpiScale(26))
        self.removeButton.setToolTip(maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kRemoveAnn2'  ])
        self.connect(self.removeButton, QtCore.SIGNAL("clicked()"), self.removeCB)
        hbox.addWidget(self.removeButton)
        

        row.setLayout(hbox)
        self.layout().addWidget(row)

    def resizeEvent( self, event ):
        r = self.rect()
        s = event.size()
        self.frame.setGeometry( r.x(), r.y(), s.width(), s.height() )
        super(FXChainOrderingUI, self).resizeEvent(event)

    def mkChain(self):
        col = QWidget()
        vbox = QVBoxLayout(self.frame)
        QLayoutItem.setAlignment(vbox, QtCore.Qt.AlignLeft)
        self.chain = QListWidget()
        self.refreshChain()
        vbox.addWidget(self.chain)
        col.setLayout(vbox)
        return col

    def refreshChain(self,name=""):
        self.chain.clear()
        de = xgg.DescriptionEditor
        modules = xg.fxModules(de.currentPalette(),de.currentDescription())
        row = 0
        for module in modules:
            self.chain.addItem(module)
            if module == name:
                self.chain.setCurrentRow(row)
            row += 1
        
    def removeCB(self):
        mo=str(self.chain.currentItem().text())
        de=xgg.DescriptionEditor
        res=xg.removeFXModule(de.currentPalette(),de.currentDescription(),mo)
        if res:
            self.refreshChain()
        
    def upCB(self):
        mo=str(self.chain.currentItem().text())
        de=xgg.DescriptionEditor
        res=xg.moveFXModule(de.currentPalette(),de.currentDescription(),mo,-1)
        if res:
            self.refreshChain(mo)
        
    def downCB(self):
        mo=str(self.chain.currentItem().text())
        de=xgg.DescriptionEditor
        res=xg.moveFXModule(de.currentPalette(),de.currentDescription(),mo,1)
        if res:
            self.refreshChain(mo)
        
def editFXChain():
    """Function to edit an FX module chain using a dialog.

    This provides a simple dialog to list the available fx modules, allow
    adding/removing from the chain, and reording the modules.
    """
    if not xgg.DescriptionEditor:
        print(maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kNoDescriptionEditorOpenSoNoCurrentDescription1'  ])
        return
    dialog = EditFXChainUI()
    dialog.exec_()
    xgg.DescriptionEditor.refresh("Full")
    
def showFXChainLoaderDialog( x, y ):
    """Function to add FX module chains using a dialog.
    """
    if not xgg.DescriptionEditor:
        print(maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kNoDescriptionEditorOpenSoNoCurrentDescription2'  ])
        return
    dialog = FXChainLoaderUI(x,y)
    dialog.exec_()

def showFXChainOrderingDialog( x, y ):
    """Function to order FX module chains using a dialog.
    """
    if not xgg.DescriptionEditor:
        print(maya.stringTable[ u'y_xgenm_ui_dialogs_xgEditFXChain.kNoDescriptionEditorOpenSoNoCurrentDescription3'  ])
        return
    dialog = FXChainOrderingUI(x,y)
    dialog.exec_()
    xgg.DescriptionEditor.refresh("Full")
    
