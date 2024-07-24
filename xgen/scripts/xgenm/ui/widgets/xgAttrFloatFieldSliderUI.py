from __future__ import division
import maya
maya.utils.loadStringResourcesForModule(__name__)

from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *

import maya.cmds as cmds

from xgenm.ui.widgets.xgPlugWatcher import PlugWatcher
from xgenm.ui.util.xgUtil import DpiScale

from maya.internal.common.qt.doubleValidator import MayaQclocaleDoubleValidator


'''
    A widget to imitate Maya's attrFieldSliderGrp control.
    
    We don't have access to Maya internal classes and there is no valid UI
    path name in QTreeWidget. So we can't use the attrFieldSliderGrp command 
    as well.
    What we can do is to make something that looks similar...
    Note that the control does not receive drop event from Maya because
    Maya's drop data is an internal C++ object..
'''
class AttrFloatFieldSliderUI(QWidget):
    
    # Watch the Maya plug
    plug        = None
    watcher     = None
    
    # UI elements
    field       = None
    validator   = None
    slider      = None
    
    # Default Soft Min/Max
    softMin     = None
    softMax     = None
    
    # Flags
    isUpdating  = False
    
    # Constants
    FIELD_COLOR_LOCKED  = QColor( 92, 104, 116)
    FIELD_COLOR_EXPR    = QColor(203, 165, 241)
    FIELD_COLOR_KEYED   = QColor(221, 114, 122)
    FIELD_COLOR_DRV_KEY = QColor( 80, 153, 218)
    FIELD_COLOR_ON_KEY1 = QColor(205,  39,  41)
    FIELD_COLOR_ON_KEY2 = QColor(253, 203, 196)
    FIELD_COLOR_IS_DEST = QColor(241, 241, 165)
    FIELD_COLOR_DISABLE = QColor( 64,  64,  64)
    SLIDER_NUM_STEPS    = 200
    SLIDER_SINGLE_STEP  = 1
    SLIDER_PAGE_STEP    = 10
    
    def __init__(self, parent=None):
        ''' Constructor to create a UI with a field and a slider'''
        QWidget.__init__(self, parent)
        
        # Set accessible name
        self.setAccessibleName(r'XgAttrFloatFieldSliderUI')
        
        # Create the watcher to observe and manipulate plug
        self.watcher = PlugWatcher()
        
        # Create the field control and its validator
        self.field = QLineEdit()
        self.field.setFixedWidth(DpiScale(62))
        self.field.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        
        self.validator = CustomDoubleValidator(self.field)
        self.field.setValidator(self.validator)
        
        # Create the slider control
        self.slider = CustomSlider(QtCore.Qt.Horizontal)
        self.slider.setSingleStep(self.SLIDER_SINGLE_STEP)
        self.slider.setPageStep(self.SLIDER_PAGE_STEP)
        
        layout = QHBoxLayout()
        QLayoutItem.setAlignment(layout, QtCore.Qt.AlignLeft)
        layout.setContentsMargins(DpiScale(1), DpiScale(1), DpiScale(1), DpiScale(1))
        layout.addWidget(self.field)
        layout.addWidget(self.slider)
        self.setLayout(layout)
        
        # Connect signals
        self.field.editingFinished.connect(self.__onFieldChanged)
        self.field.customContextMenuRequested.connect(self.__onFieldContextMenu)
        self.field.returnPressed.connect(self.setFocus)
        self.validator.fixedUp.connect(self.__onValidatorFixedUp)
        self.slider.valueChanged.connect(self.__onSliderChanged)
        self.slider.sliderPressed.connect(self.__onSliderPressed)
        self.slider.sliderReleased.connect(self.__onSliderReleased)
        
    def setFieldMinMax(self, fieldMin, fieldMax):
        ''' Set the range of the input field '''
        self.validator.setBottom(fieldMin)
        self.validator.setTop(fieldMax)
        
    def setFieldColor(self, background=None, foreground=None):
        ''' Set the color of the field control '''
        palette = QPalette()
        
        # Background color
        if background is not None:
            palette.setColor(QPalette.Active, QPalette.Base, background)
            palette.setColor(QPalette.Inactive, QPalette.Base, background)
        palette.setColor(QPalette.Disabled, QPalette.Base, self.FIELD_COLOR_DISABLE)
            
        # Foreground color
        if foreground is not None:
            palette.setColor(QPalette.Active, QPalette.Text, foreground)
            palette.setColor(QPalette.Inactive, QPalette.Text, foreground)
            
        # Set the color palette to the QLineEdit control
        self.field.setPalette(palette)
        
    def setSliderColor(self, groove=None):
        ''' Set the color of the slider control '''
        palette = QPalette()

        # Groove color
        if groove is not None:
            palette.setColor(QPalette.Active, QPalette.Base, groove)
            palette.setColor(QPalette.Inactive, QPalette.Base, groove)

        # Set the color palette to the QSlider control
        self.slider.setPalette(palette)
        
    def setSliderSoftMinMax(self, softMin, softMax):
        ''' Set the range of the slider '''
        self.softMin = softMin
        self.softMax = softMax
        self.slider.setMinimum(int(softMin * self.SLIDER_NUM_STEPS))
        self.slider.setMaximum(int(softMax * self.SLIDER_NUM_STEPS))
        
    def refresh(self):
        ''' Refresh the controls from the plug '''

        # Reject if the node no longer exists
        if not self.watcher.isValidPlug():
            return
        
        # Get the state of the plug
        plugValue   = self.watcher.plugAsFloat()
        plugLocked  = self.watcher.isPlugLocked()
        plugIsDest  = self.watcher.isPlugConnected()
        plugHasExpr = self.watcher.isPlugHasExpression() if plugIsDest else False
        plugKeyed   = self.watcher.isPlugKeyed() if plugIsDest else False
        plugDrvKey  = self.watcher.isPlugDrivenKeyed() if plugKeyed else False
        plugOnKey, keyValue = self.watcher.isPlugOnKey() if plugKeyed else (False, None)
        
        # Begin updating UI controls
        self.isUpdating = True

        # Update the field
        self.field.setText(r'%.3f' % plugValue)
        if plugLocked:
            self.setFieldColor(background=self.FIELD_COLOR_LOCKED, foreground=QtCore.Qt.black)
        elif plugHasExpr:
            self.setFieldColor(background=self.FIELD_COLOR_EXPR, foreground=QtCore.Qt.black)
        elif plugDrvKey:
            self.setFieldColor(background=self.FIELD_COLOR_DRV_KEY, foreground=QtCore.Qt.black)
        elif plugOnKey:
            if plugValue == keyValue:
                self.setFieldColor(background=self.FIELD_COLOR_ON_KEY1, foreground=None)
            else:
                self.setFieldColor(background=self.FIELD_COLOR_ON_KEY2, foreground=QtCore.Qt.black)
        elif plugKeyed:
            self.setFieldColor(background=self.FIELD_COLOR_KEYED, foreground=QtCore.Qt.black)
        elif plugIsDest:
            self.setFieldColor(background=self.FIELD_COLOR_IS_DEST, foreground=QtCore.Qt.black)
        else:
            self.setFieldColor(background=None, foreground=None)
        
        # Update the slider control
        self.__updateSliderSoftMinMax(plugValue)
        self.slider.setValue(int(plugValue * self.SLIDER_NUM_STEPS))
        
        # End updating UI controls
        self.isUpdating = False
        
    def connectPlug(self, plug):
        ''' Connect the control to a Maya plug '''
        if self.plug != plug:
            self.isUpdating = True
            self.plug = plug
            self.slider.setMinimum(int(self.softMin * self.SLIDER_NUM_STEPS))
            self.slider.setMaximum(int(self.softMax * self.SLIDER_NUM_STEPS))
            self.isUpdating = False
        self.watcher.connectPlug(plug)
        self.watcher.watchAttributeSet(self.cbAttributeChanged)
        self.watcher.watchAttributeLock(self.cbAttributeChanged)
        self.watcher.watchAttributeConnection(self.cbAttributeChanged)
        self.watcher.watchTimeChange(self.cbTimeChange)
        self.watcher.watchKeyframeEdited(self.cbKeyframeEdited)
        self.refresh()

    def disconnectPlug(self):
        ''' Disconnect the Maya plug from the widget '''
        self.plug = None
        self.watcher = PlugWatcher()
        
    def __updateSliderSoftMinMax(self, plugValue):
        ''' Update the range of the slider when the plug changes '''
        
        # Get the current value for the slider
        sliderValue = int(plugValue * self.SLIDER_NUM_STEPS) 
        
        # Lesser than minimum ?
        if sliderValue < self.slider.minimum():
            self.slider.setMinimum(sliderValue)
        
        # Larger than maximum ?
        if sliderValue > self.slider.maximum():
            self.slider.setMaximum(sliderValue)
            
    def __onFieldChanged(self):
        ''' Invoked when the field control is changed '''
        
        # Updating ?
        if self.isUpdating:
            return
        
        # Get the new value from the field control
        newValue = float(self.field.text())
        self.__setPlugValue(newValue)
        
    def __onFieldContextMenu(self, pos):
        ''' Invoked when a context menu is requested for the field control '''
        
        # Create the context menu for the field control
        ctxMenu = QMenu()
        
        if not self.watcher.isPlugLocked():
            plugIsDest  = self.watcher.isPlugConnected()
            
            if self.watcher.isPlugHasExpression():
                # Attribute with Expression
                ctxMenu.addAction(maya.stringTable[u'y_xgenm_ui_widgets_xgAttrFloatFieldSliderUI.kEditExpression'], self.watcher.plugSetExpression)
                ctxMenu.addAction(maya.stringTable[u'y_xgenm_ui_widgets_xgAttrFloatFieldSliderUI.kDeleteExpression'], self.watcher.plugDeleteExpression)
            else:
                # Open source node Attribute Editor when there is a connection
                if plugIsDest:
                    ctxMenu.addAction(self.watcher.plugSourceName() + r'...', self.watcher.plugOpenSourceAE)
                
                # Create Expression when there is no connection
                if not plugIsDest:
                    ctxMenu.addAction(maya.stringTable[u'y_xgenm_ui_widgets_xgAttrFloatFieldSliderUI.kCreateNewExpression'], self.watcher.plugSetExpression)
                    
                # Set Key when there is no key or already keyed
                if not plugIsDest or self.watcher.isPlugKeyed():
                    ctxMenu.addAction(maya.stringTable[u'y_xgenm_ui_widgets_xgAttrFloatFieldSliderUI.kSetKey'], self.watcher.plugSetKey)

                # Set Driven Key when there is a connection
                # BUG: Maya's setDrivenKeyWindow *doesn't* work with multi child plug !
                #ctxMenu.addAction(_L10N(kSetDrivenKey,'Set Driven Key...'), self.watcher.plugSetDrivenKey)
                    
                # Create New Texture when there is no connection
                if not plugIsDest:
                    ctxMenu.addAction(maya.stringTable[u'y_xgenm_ui_widgets_xgAttrFloatFieldSliderUI.kCreateNewTexture'], self.watcher.plugCreateTexture)
                    
                # Break Connection when there is a connection
                if plugIsDest:
                    ctxMenu.addAction(maya.stringTable[u'y_xgenm_ui_widgets_xgAttrFloatFieldSliderUI.kBreakConnection'], self.watcher.breakPlugConnection)
                    
            ctxMenu.addAction(maya.stringTable[u'y_xgenm_ui_widgets_xgAttrFloatFieldSliderUI.kLockAttribute'], self.watcher.lockPlug)

            # Ignore when rendering when there is a connection
            if plugIsDest and not self.watcher.isPlugHasExpression():
                if self.watcher.isPlugIgnoreWhenRendering():
                    ctxMenu.addAction(maya.stringTable[u'y_xgenm_ui_widgets_xgAttrFloatFieldSliderUI.kDontIgnoreWhenRendering'], self.watcher.plugToggleIgnoreWhenRendering)
                else:
                    ctxMenu.addAction(maya.stringTable[u'y_xgenm_ui_widgets_xgAttrFloatFieldSliderUI.kIgnoreWhenRendering'], self.watcher.plugToggleIgnoreWhenRendering)
        else:
            # Locked Attribute
            ctxMenu.addAction(maya.stringTable[u'y_xgenm_ui_widgets_xgAttrFloatFieldSliderUI.kUnlockAttribute'], self.watcher.unlockPlug)
        
        # Popup the menu
        ctxMenu.exec_(self.field.mapToGlobal(pos))
        
    def __onValidatorFixedUp(self, input):
        ''' Invoked when the validator fixed an input string '''

        # Updating ?
        if self.isUpdating:
            return
        
        self.field.setText(input)
        self.field.editingFinished.emit()
        
    def __onSliderChanged(self, sliderValue):
        ''' Invoked when the slider control is changed '''

        # Updating ?
        if self.isUpdating:
            return

        # Get the new value from the slider control
        newValue = float(sliderValue) / float(self.SLIDER_NUM_STEPS)
        self.__setPlugValue(newValue)
        
    def __onSliderPressed(self):
        ''' Invoked when the mouse is pressed on the slider control '''
        cmds.undoInfo(openChunk=True, chunkName=self.plug)
        
    def __onSliderReleased(self):
        ''' Invoked when the mouse is released on the slider control '''
        cmds.undoInfo(closeChunk=True)
        
    def __setPlugValue(self, newValue):
        ''' Internal method to set the new plug value '''

        # No change (exactly equal) ?
        if newValue == self.watcher.plugAsFloat():
            return
        
        # Locked ?
        if self.watcher.isPlugLocked():
            self.refresh()
            return
        
        # Connected ?
        if self.watcher.isPlugConnected() and not self.watcher.isPlugKeyed():
            self.refresh()
            return
        
        # Set the plug value
        self.watcher.plugSetFloat(newValue)
        
    def cbAttributeChanged(self, plug):
        ''' Invoked when the connected attribute has been changed '''
        QTimer.singleShot(0, lambda: self.refresh())
        
    def cbTimeChange(self, time):
        ''' Invoked when Maya time changes '''
        QTimer.singleShot(0, lambda: self.refresh())

    def cbKeyframeEdited(self, objects):
        ''' Invoked when Maya keyframe is edited '''
        QTimer.singleShot(0, lambda: self.refresh())
        
'''
    The field validator (double)
'''
class CustomDoubleValidator(MayaQclocaleDoubleValidator):
    
    # Signals
    fixedUp = QtCore.Signal(str)
    
    def __init__(self, parent=None):
        ''' Constructor '''
        MayaQclocaleDoubleValidator.__init__(self, parent)
        
    def fixup(self, input):
        ''' Override QValidator.fixup(input) '''
        fieldValue = float(input)
        fieldMin   = self.bottom()
        fieldMax   = self.top()
        fixedInput = str(max(fieldMin, min(fieldValue, fieldMax)))
        self.fixedUp.emit(fixedInput)
        
'''
    The slider control
'''
class CustomSlider(QSlider): 
    
    def __init__(self, orientation, parent=None):
        ''' Constructor '''
        QSlider.__init__(self, orientation, parent)
        
        self.setAccessibleName(r'XgCustomSlider')
        
    def mousePressEvent(self, event):
        ''' Invoked when mouse is pressed '''
        # Qt emits a valueChanged signal before sliderPressed signal
        # The valueChanged signal is actually part of slider tracking..
        self.setSliderDown(True)
        QSlider.mousePressEvent(self, event)
        
    def mouseReleaseEvent(self, event):
        ''' Invoked when mouse is released '''
        # Restore the sliderDown state that was done in mousePressEvent()
        QSlider.mouseReleaseEvent(self, event)
        if self.isSliderDown() and event.buttons() == QtCore.Qt.NoButton:
            self.setSliderDown(False)
        
    def wheelEvent(self, event):
        ''' Invoked on mouse wheel '''
        event.ignore()


# ===========================================================================
# Copyright 2021 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
