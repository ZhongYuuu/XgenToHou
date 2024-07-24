from __future__ import division
import maya
maya.utils.loadStringResourcesForModule(__name__)

from builtins import range
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from shiboken2 import wrapInstance

import xgenm as xg
import xgenm.xgGlobal as xgg
if xgg.Maya:
    import maya.cmds as cmds
    import maya.mel as mel
from xgenm.ui.util.xgUtil import *
from xgenm.ui.util.xgComboBox import _ComboBoxUI
from xgenm.ui.widgets import *
from xgenm.ui.xgSetMapAttr import setMapAttr
from xgenm.ui.widgets.xgFileBrowserUI import *
from xgenm.ui.dialogs.xgExportFile import fixFileName
from maya import OpenMaya as om
from maya import OpenMayaUI as omui
from maya import OpenMayaRender as omr

import os
import shutil

from xgenm.xmaya import xgmSplinePreset
import sys

long_type = int if sys.version_info[0] >= 3 else long


presetExtension = r"xgip"
importPresetDialogTitle = maya.stringTable[u'y_xgenm_ui_xgmSplinePresetUI.kImportDialogTitle' ]
exportPresetDialogTitle = maya.stringTable[u'y_xgenm_ui_xgmSplinePresetUI.kExportDialogTitle' ]
importPresetDialog = None
exportPresetDialog = None

mayaMainWindowPtr = None
mayaMainWindow = None
if om.MGlobal.mayaState() == om.MGlobal.kInteractive:
    mayaMainWindowPtr = omui.MQtUtil.mainWindow()
    mayaMainWindow = wrapInstance(long_type(mayaMainWindowPtr), QWidget)


def xgmSplinePresetUIImport():
    __xgmSplinePresetUIImport()


def xgmSplinePresetUIImportWithPath(filePath):
    __xgmSplinePresetUIImport(filePath)


def __xgmSplinePresetUIImport(filePath=None):
    global importPresetDialog
    if not importPresetDialog:
        importPresetDialog = xgmSplinePresetImportDialog()
    else:
        importPresetDialog.refresh()

    if filePath:
        importPresetDialog.setFilePath(filePath)

    importPresetDialog.show()


def xgmSplinePresetUIExport():
    global exportPresetDialog

    # Save the scene before export.
    # When export a description with initial unsaved scene,
    # textures of xgen's map may not be saved. As we support
    # to export map, their texture should be saved before export.
    sceneName = saveScene()
    if len(sceneName) == 0:
        return

    if not exportPresetDialog:
        exportPresetDialog = xgmSplinePresetExportDialog()
    else:
        exportPresetDialog.refresh(True)

    exportPresetDialog.show()


class xgmSplinePresetDialog(QWidget):

    def __init__(self, parent):
        super(xgmSplinePresetDialog, self).__init__(parent)

    @staticmethod
    def _createRowLayout(parent):
        row = QWidget()
        hbox = QHBoxLayout()
        hbox.setContentsMargins(DpiScale(0), DpiScale(0), DpiScale(0), DpiScale(0))
        row.setLayout(hbox)
        parent.addWidget(row)
        return hbox

    @staticmethod
    def _createVerticalGroupLayout(parentRowLayout):
        w = QWidget()
        vbox = QVBoxLayout()
        vbox.setContentsMargins(DpiScale(0), DpiScale(0), DpiScale(0), DpiScale(0))
        w.setLayout(vbox)
        parentRowLayout.addWidget(w)
        return vbox

    @staticmethod
    def __normPath(path):
        return os.path.normpath(path).replace('''\\''', '''/''')

    @classmethod
    def _getDefaultFilePath(cls):
        # Aligned with XGen Library, see xgenLibrary.mel
        presetPath = cls.__normPath(os.path.join(
            xg.rootDir(),
            r'presets/library/default.%s' % presetExtension
        ))
        return presetPath

    @classmethod
    def _getFixedFileName(cls, path):
        return cls.__normPath(fixFileName(path, r'.%s' % presetExtension))
        return fixFileName(self.presetFile.value(), r'.%s' % presetExtension)


class xgmSplinePresetImportDialog(xgmSplinePresetDialog):

    def __init__(self, parent=mayaMainWindow):
        super(xgmSplinePresetImportDialog, self).__init__(parent)

        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.setWindowTitle(importPresetDialogTitle)

        layout = QVBoxLayout()
        QLayoutItem.setAlignment(layout, QtCore.Qt.AlignTop)
        self.setLayout(layout)

        self.__setupDescriptionUI(layout)
        self.__setupButtons(layout)

        self.setMinimumWidth(DpiScale(600))
        self.setFixedHeight(self.sizeHint().height())

        self.refresh()

    def refresh(self):
        self.posBasedTransfer.setChecked(True)
        self.rotateOrientationToNewNormal.setChecked(True)

    def setFilePath(self, filePath):
        self.presetFile.textValue.setText(filePath)

    def keyPressEvent(self, e):
        pass

    def closeEvent(self, e):
        pass

    def __setupDescriptionUI(self, layout):
        self.presetFile = FileBrowserUI(maya.stringTable[u'y_xgenm_ui_xgmSplinePresetUI.kFileNameForPresetImport' ], r"", r"*.%s" % presetExtension, r"in")
        self.connect(self.presetFile.textValue, QtCore.SIGNAL(r"editingFinished()"), self.__onFileSelectedCallback)
        self.presetFile.textValue.setText(self._getDefaultFilePath())
        layout.addWidget(self.presetFile)

        # Seperator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        # Transfer method
        transferLayout = self._createRowLayout(layout)
        tranferLabel = QLabel(maya.stringTable[u'y_xgenm_ui_xgmSplinePresetUI.kTransferMethod' ])
        tranferLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
        tranferLabel.setFixedWidth(DpiScale(150))
        transferLayout.addWidget(tranferLabel)
        self.transferRadioButtonGroup = self._createVerticalGroupLayout(transferLayout)
        self.posBasedTransfer = QRadioButton(maya.stringTable[ u'y_xgenm_ui_xgmSplinePresetUI.kPosBasedTransfer' ])
        self.transferRadioButtonGroup.addWidget(self.posBasedTransfer)
        self.uvBasedTransfer = QRadioButton(maya.stringTable[u'y_xgenm_ui_xgmSplinePresetUI.kUVBasedTransfer' ])
        self.transferRadioButtonGroup.addWidget(self.uvBasedTransfer)

        # Orientation
        orientationLayout = self._createRowLayout(layout)
        orientationLabel = QLabel(maya.stringTable[u'y_xgenm_ui_xgmSplinePresetUI.kOrientation'  ])
        orientationLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
        orientationLabel.setFixedWidth(DpiScale(150))
        orientationLayout.addWidget(orientationLabel)
        self.orientationRadioButtonGroup = self._createVerticalGroupLayout(orientationLayout)
        self.rotateOrientationToNewNormal = QRadioButton(maya.stringTable[u'y_xgenm_ui_xgmSplinePresetUI.kRotateOrientationToNewNormal' ])
        self.orientationRadioButtonGroup.addWidget(self.rotateOrientationToNewNormal)
        self.keepOrientation = QRadioButton(maya.stringTable[u'y_xgenm_ui_xgmSplinePresetUI.kKeepOrientation' ])
        self.orientationRadioButtonGroup.addWidget(self.keepOrientation)

    def __setupButtons(self, layout):
        row = QWidget()
        hbox = QHBoxLayout()
        QLayoutItem.setAlignment(hbox, QtCore.Qt.AlignRight)
        hbox.setSpacing(DpiScale(15))
        hbox.setContentsMargins(DpiScale(1), DpiScale(1), DpiScale(1), DpiScale(1))
        self.importButton = QPushButton(maya.stringTable[u'y_xgenm_ui_xgmSplinePresetUI.kImportPreset' ])
        self.importButton.setFixedWidth(DpiScale(100))
        self.importButton.setAutoRepeat(False)
        self.connect(self.importButton, QtCore.SIGNAL(r"clicked()"), self.__importPresetCallback)
        hbox.addWidget(self.importButton)
        self.cancelButton = QPushButton(maya.stringTable[u'y_xgenm_ui_xgmSplinePresetUI.kCancelImportPreset' ])
        self.cancelButton.setFixedWidth(DpiScale(100))
        self.cancelButton.setAutoRepeat(False)
        self.connect(self.cancelButton, QtCore.SIGNAL(r"clicked()"), self.close)
        hbox.addWidget(self.cancelButton)
        row.setLayout(hbox)
        layout.addWidget(row)

    def __onFileSelectedCallback(self):
        presetFilePath = self._getFixedFileName(self.presetFile.value())
        if len(presetFilePath):
            self.presetFile.setValue(presetFilePath)

    def __importPresetCallback(self):
        # Validate user's input
        presetFilePath = self._getFixedFileName(self.presetFile.value())
        if not os.path.exists(presetFilePath):
            text = maya.stringTable[u'y_xgenm_ui_xgmSplinePresetUI.kNotAValidPathImport' ]
            QMessageBox.warning(self, importPresetDialogTitle, text)
            return

        selectedShapes = xgmSplinePreset.PresetUtil.getSelectedShapes()
        if not selectedShapes or len(selectedShapes) != 1:
            text = maya.stringTable[u'y_xgenm_ui_xgmSplinePresetUI.kPleaseSelectOneMesh' ]
            QMessageBox.warning(self, importPresetDialogTitle, text)
            return

        alignToNormal = self.rotateOrientationToNewNormal.isChecked()
        mappingType = r'position' if self.posBasedTransfer.isChecked() else r'uv'

        cmds.xgmSplinePreset(presetFilePath, i=True, mappingType=mappingType, alignToNormal=alignToNormal)

        # Close dialog
        self.close()


class xgmSplinePresetExportDialog(xgmSplinePresetDialog):

    def __init__(self, parent=mayaMainWindow):
        super(xgmSplinePresetExportDialog, self).__init__(parent)

        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.setWindowTitle(exportPresetDialogTitle)

        layout = QVBoxLayout()
        QLayoutItem.setAlignment(layout, QtCore.Qt.AlignTop)
        self.setLayout(layout)

        self.__setupDescriptionUI(layout)

        # Seperator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        self.__setupThumbnailUI(layout)

        self.__setupButtons(layout)

        self.setMinimumWidth(DpiScale(600))
        self.setFixedHeight(self.sizeHint().height())

        self.currentCtx = None

        self.refresh(True)

    def createSnapshot(self, startX, startY, scale):
        view = omui.M3dView().active3dView()
        portWidth = view.portWidth()
        portHeight = view.portHeight()
        srcImage = om.MImage()
        srcImage.create(portWidth, portHeight)
        if not view.readColorBuffer(srcImage, True):
            rangeX = scale
            rangeY = scale
            if startX < 0:
                rangeX = scale + startX
                startX = 0

            if startY < 0:
                rangeY = scale + startY
                startY = 0

            if (startX + scale) > portWidth:
                rangeX = portWidth - 1 - startX

            if (startY + scale) > portHeight:
                rangeY = portHeight - 1 - startY

            srcBuffer = srcImage.pixels()
            self.destImage = QImage(rangeX, rangeY, QImage.Format_RGB32)

            for x in range(rangeX):
                for y in range(rangeY):
                    w = startX + x
                    h = startY + rangeY - y
                    srcIndex = h * portWidth * 4 + w * 4

                    r = om.MScriptUtil.getUcharArrayItem(srcBuffer, srcIndex + 0)
                    g = om.MScriptUtil.getUcharArrayItem(srcBuffer, srcIndex + 1)
                    b = om.MScriptUtil.getUcharArrayItem(srcBuffer, srcIndex + 2)

                    self.destImage.setPixel(x, y, qRgb(r, g, b))

            self.pixmap = QPixmap.fromImage(self.destImage)
            self.thumbnailIcon.setPixmap(self.pixmap)

        self.__restoreContext()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.__restoreContext()

    def closeEvent(self, e):
        self.__restoreContext()

    def __setupDescriptionUI(self, layout):
        self.presetFile = FileBrowserUI(maya.stringTable[u'y_xgenm_ui_xgmSplinePresetUI.kFileNameForPresetExport' ], r"", r"*.%s" % presetExtension, r"out")
        self.connect(self.presetFile.textValue, QtCore.SIGNAL(r"editingFinished()"), self.__onFileSelectedCallback)

        self.presetFile.textValue.setText(self._getDefaultFilePath())

        layout.addWidget(self.presetFile)

    def __setupThumbnailUI(self, layout):
        thumbnailPart = QWidget()
        hbox = QHBoxLayout()
        hbox.setSpacing(DpiScale(10))
        hbox.setContentsMargins(DpiScale(1), DpiScale(1), DpiScale(1), DpiScale(20))

        label = QLabel(maya.stringTable[u'y_xgenm_ui_xgmSplinePresetUI.kXGenPresetThumbnail' ])
        label.setFixedWidth(labelWidth())
        label.setAlignment(QtCore.Qt.AlignRight)
        hbox.addWidget(label)

        defaultImage = os.path.normpath(os.path.join(os.environ[r'MAYA_LOCATION'], r"icons/mayaico.png"))
        self.thumbnailIcon = QLabel()
        self.thumbnailIcon.setPixmap(defaultImage)
        self.thumbnailIcon.setFixedWidth(DpiScale(128))
        self.thumbnailIcon.setFixedHeight(DpiScale(128))
        self.thumbnailIcon.setAlignment(QtCore.Qt.AlignLeft)
        self.thumbnailIcon.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.thumbnailIcon.setScaledContents(True)
        hbox.addWidget(self.thumbnailIcon)

        buttonWidget = QWidget()
        buttonVbox = QVBoxLayout()
        QLayoutItem.setAlignment(buttonVbox, QtCore.Qt.AlignTop)
        buttonVbox.setContentsMargins(DpiScale(1), DpiScale(1), DpiScale(1), DpiScale(1))
        snapshotButton = QPushButton(maya.stringTable[u'y_xgenm_ui_xgmSplinePresetUI.kSnapshotButtonForPresetThumbnail' ])
        snapshotButton.setFixedWidth(DpiScale(120))
        snapshotButton.setAutoRepeat(False)
        self.connect(snapshotButton, QtCore.SIGNAL(r"clicked()"), self.__snapshotContext)
        buttonVbox.addWidget(snapshotButton)
        browseButton = QPushButton(maya.stringTable[u'y_xgenm_ui_xgmSplinePresetUI.kBrowseButtonForPresetThumbnail' ])
        browseButton.setFixedWidth(DpiScale(120))
        browseButton.setAutoRepeat(False)
        self.connect(browseButton, QtCore.SIGNAL(r"clicked()"), self.__fileBrowser)
        buttonVbox.addWidget(browseButton)
        buttonWidget.setLayout(buttonVbox)
        hbox.addWidget(buttonWidget)

        thumbnailPart.setLayout(hbox)
        layout.addWidget(thumbnailPart)

    def __setupButtons(self, layout):
        row = QWidget()
        hbox = QHBoxLayout()
        QLayoutItem.setAlignment(hbox, QtCore.Qt.AlignRight)
        hbox.setSpacing(DpiScale(15))
        hbox.setContentsMargins(DpiScale(1), DpiScale(1), DpiScale(1), DpiScale(1))
        self.exportButton = QPushButton(maya.stringTable[u'y_xgenm_ui_xgmSplinePresetUI.kExportPreset' ])
        self.exportButton.setFixedWidth(DpiScale(100))
        self.exportButton.setAutoRepeat(False)
        self.connect(self.exportButton, QtCore.SIGNAL(r"clicked()"), self.__exportPresetCallback)
        hbox.addWidget(self.exportButton)
        self.cancelButton = QPushButton(maya.stringTable[u'y_xgenm_ui_xgmSplinePresetUI.kCancelExportPreset' ])
        self.cancelButton.setFixedWidth(DpiScale(100))
        self.cancelButton.setAutoRepeat(False)
        self.connect(self.cancelButton, QtCore.SIGNAL(r"clicked()"), self.close)
        hbox.addWidget(self.cancelButton)
        row.setLayout(hbox)
        layout.addWidget(row)

    def __snapshotContext(self):
        currentCtx = cmds.currentCtx()
        if currentCtx != r"xgmSplinePresetSnapshotInstance":

            cmd = r"xgmPresetSnapshotContext -q -ex xgmSplinePresetSnapshotInstance"
            if not mel.eval(cmd):
                cmd = r'xgmPresetSnapshotContext -callback "xgmSplinePresetUI.grabSnapshotInExportPresetDialogCallback" xgmSplinePresetSnapshotInstance'
                mel.eval(cmd)

            cmds.setToolTo(r"xgmSplinePresetSnapshotInstance")

            self.currentCtx = currentCtx

    def __defaultSnapshot(self):
        view = omui.M3dView().active3dView()
        portWidth = view.portWidth()
        portHeight = view.portHeight()
        scale = min(portWidth, portHeight) // 2
        startX = (portWidth - scale) // 2
        startY = (portHeight - scale) // 2

        self.createSnapshot(startX, startY, scale)

    def __restoreContext(self):
        if self.currentCtx:
            cmds.setToolTo(self.currentCtx)
        else:
            cmds.setToolTo(r"selectSuperContext")

        self.currentCtx = None

    def __fileBrowser(self):
        self.thumbnailToCopy = fileBrowserDlg(self, xg.userRepo(), r"*.png *.jpg", r"in")
        if len(self.thumbnailToCopy) > 0:
            self.thumbnailIcon.setPixmap(self.thumbnailToCopy)

    def refresh(self, defaultSnapshot=False):
        if defaultSnapshot:
            self.__defaultSnapshot()

    def __onFileSelectedCallback(self):
        presetFilePath = self._getFixedFileName(self.presetFile.value())
        if len(presetFilePath):
            self.presetFile.setValue(presetFilePath)

    def __exportPresetCallback(self):
        # Validate user's input
        presetFilePath = self._getFixedFileName(self.presetFile.value())
        if not os.path.exists(os.path.dirname(presetFilePath)):
            text = maya.stringTable[ u'y_xgenm_ui_xgmSplinePresetUI.kNotAValidPathExport'  ]
            QMessageBox.warning(self, exportPresetDialogTitle, text)
            return

        selectedDescs = xgmSplinePreset.PresetUtil.getSelectedDescriptions()
        if not selectedDescs or len(selectedDescs) != 1:
            text = maya.stringTable[u'y_xgenm_ui_xgmSplinePresetUI.kPleaseSelectOneDescription' ]
            QMessageBox.warning(self, exportPresetDialogTitle, text)
            return

        if os.path.isfile(presetFilePath):
            text = """'%s' %s""" % (presetFilePath, maya.stringTable[u'y_xgenm_ui_xgmSplinePresetUI.kReplaceFile' ])
            selection = QMessageBox.warning(self, exportPresetDialogTitle, text, QMessageBox.Ok | QMessageBox.Cancel)
            if selection == QMessageBox.Cancel:
                return

        self.__exportSplines(presetFilePath)
        self.__exportThumbnail(presetFilePath)

        # Close dialog
        self.close()

    def __exportSplines(self, presetFilePath):
        cmds.xgmSplinePreset(presetFilePath, e=True)

    def __exportThumbnail(self, presetFilePath):
        try:
            filename = os.path.splitext(presetFilePath)[0] + r".png"
            pixmap = self.thumbnailIcon.pixmap()
            pixmap.save(filename, r"png")
        except:
            return False
        else:
            return True


def grabSnapshotInExportPresetDialogCallback(x, y, scale):
    global exportPresetDialog
    if exportPresetDialog:
        exportPresetDialog.createSnapshot(x, y, scale)
# ===========================================================================
# Copyright 2021 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
