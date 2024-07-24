import maya
maya.utils.loadStringResourcesForModule(__name__)

from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *

from xgenm.ui.util.xgUtil import DpiScale


'''
    A modal dialog to confirm the deletion of a shared modifier.
'''
class IgSplineDeleteSharedModifierUI(QDialog):
    
    # 'disconnect' : Disconnect the modifier from the modifier chain
    # 'delete'     : Delete the modifier node
    # 'cancel'     : Cancel the operation
    operation   = r'cancel'

    # Modifier dg node name
    modifier    = r''
    
    def __init__(self, modifier, x, y):
        ''' Create a dialog at (x,y) '''
        QDialog.__init__(self)

        self.operation = r'cancel'
        self.modifier = modifier
        
        # Dialog properties
        self.setGeometry(x, y, DpiScale(420), DpiScale(100))
        self.setSizeGripEnabled(True)
        self.setWindowTitle(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgSplineDeleteSharedModifier.kDeleteModifier'] % modifier)
        
        # Warning label
        msgLabelUI = QLabel(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgSplineDeleteSharedModifier.kWarnSharedModifier'] % modifier)
        
        # Disconnect button
        disconnectButton = QPushButton(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgSplineDeleteSharedModifier.kDeleteInCurrent'])
        disconnectButton.setAutoRepeat(False)
        disconnectButton.setDefault(True)
        
        # Delete button
        deleteButton = QPushButton(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgSplineDeleteSharedModifier.kDeleteInAll'])
        
        # Cancel button
        cancelButton = QPushButton(maya.stringTable[u'y_xgenm_ui_dialogs_xgIgSplineDeleteSharedModifier.kCancel'])
        
        # Label layout
        labelLayout = QHBoxLayout()
        QLayoutItem.setAlignment(labelLayout, QtCore.Qt.AlignLeft)
        labelLayout.addSpacing(DpiScale(20))
        labelLayout.addWidget(msgLabelUI)
        
        # Buttons Layout
        buttonsLayout = QHBoxLayout()
        QLayoutItem.setAlignment(buttonsLayout, QtCore.Qt.AlignCenter)
        buttonsLayout.addWidget(disconnectButton)
        buttonsLayout.addStretch(DpiScale(5))
        buttonsLayout.addWidget(deleteButton)
        buttonsLayout.addStretch(DpiScale(5))
        buttonsLayout.addWidget(cancelButton)
        
        # Main Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(DpiScale(10), DpiScale(5), DpiScale(10), DpiScale(5))
        layout.setSpacing(DpiScale(0))
        layout.addLayout(labelLayout)
        layout.addLayout(buttonsLayout)
        self.setLayout(layout)
        
        # Connect Signals
        disconnectButton.clicked.connect(self.__onDisconnectButtonClicked)
        deleteButton.clicked.connect(self.__onDeleteButtonClicked)
        cancelButton.clicked.connect(self.reject)
        
    def __onDisconnectButtonClicked(self):
        ''' Invoked when the disconnect button is clicked '''
        self.operation = r'disconnect'
        self.accept()
        
    def __onDeleteButtonClicked(self):
        ''' Invoked when the delete button is clicked '''
        self.operation = r'delete'
        self.accept()
        
    def getOperation(self):
        ''' Return the operation chosen by the user '''
        return self.operation

# ===========================================================================
# Copyright 2021 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
