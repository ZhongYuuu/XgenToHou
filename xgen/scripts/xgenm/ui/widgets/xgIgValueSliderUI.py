from __future__ import division
import string
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *

from xgenm.ui.util.xgUtil import DpiScale

from maya.internal.common.qt.doubleValidator import MayaQclocaleDoubleValidator


class IgSlider(QSlider):
    def __init__(self,direction):
        QSlider.__init__(self,direction)
        
        self.setAccessibleName(r'XgIgSlider')

    def wheelEvent( self, e ):
        e.ignore()

_sliderNumSteps = 200
_sliderSingleSteps = 1
_sliderPageSteps = 10

class IgValueSliderUI(QWidget):
    """A wrapper consisting of 1 label, 1 value entry box, 1 slider
    """
    def __init__(self, label, annotation, hasSlider, dMin, dMax, uiMin, uiMax, gridLayout, gridRow, w1, w2, w3):
        QWidget.__init__(self)
        # Min, Max
        self.dMin = dMin
        self.dMax = dMax
        self.uiMinDefault = self.uiMin = max( uiMin, self.dMin )
        self.uiMaxDefault = self.uiMax = min( uiMax, self.dMax )

        self.hasSlider = hasSlider
        
        self.setAccessibleName(r'XgIgValueSliderUI')

        # Label
        self.labelUI = QLabel(label)
        self.labelUI.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        self.labelUI.setToolTip(annotation)
        self.labelUI.setFixedWidth(DpiScale(w1))
        gridLayout.addWidget(self.labelUI, gridRow, 0)

        # Value editor
        self.valueUI = QLineEdit()
        self.valueUI.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.valueUI.setFixedWidth(DpiScale(w2))
        self.valueUI.setValidator( MayaQclocaleDoubleValidator(self.valueUI) )
        gridLayout.addWidget(self.valueUI, gridRow, 1)

        # Slider
        if self.hasSlider:
            self.sliderUI = IgSlider(QtCore.Qt.Horizontal)
            self.sliderUI.setFixedHeight(DpiScale(18))
            if w3 != 0:
                self.sliderUI.setFixedWidth(DpiScale(w3))
            self.sliderUI.setMinimum(int(self.uiMin*_sliderNumSteps))
            self.sliderUI.setMaximum(int(self.uiMax*_sliderNumSteps))
            self.sliderUI.setPageStep(_sliderPageSteps)
            self.sliderUI.setSingleStep(_sliderSingleSteps)
            gridLayout.addWidget(self.sliderUI, gridRow, 2)

    def value(self):
        return str(self.valueUI.text())

    def setEnabled(self, e):
        self.labelUI.setEnabled(e)
        self.valueUI.setEnabled(e)
        if self.hasSlider:
            self.sliderUI.setEnabled(e)

    def updateSliderLimits(self):
        v = float( self.value() )
        if v > self.uiMax:
            self.uiMax = v
            self.sliderUI.setMaximum(int(self.uiMax*_sliderNumSteps))
        elif v < self.uiMin:
            self.uiMin = v
            self.sliderUI.setMinimum(int(self.uiMin*_sliderNumSteps))


class IgFloatSliderUI(IgValueSliderUI):
    """
    """

    # Value changed signal
    valueChangedSignal = QtCore.Signal()

    def __init__(self, label, annotation, hasSlider, dMin, dMax, uiMin, uiMax, gridLayout, gridRow, w1, w2, w3):
        IgValueSliderUI.__init__(self, label, annotation, hasSlider, dMin, dMax, uiMin, uiMax, gridLayout, gridRow, w1, w2, w3)

        # Set validator
        validator = MayaQclocaleDoubleValidator(self.dMin, self.dMax, 6, self.valueUI)
        validator.fixup = self.myFixup
        self.valueUI.setValidator(validator)
        self.setAccessibleName(r'XgIgFloatSliderUI')

        # Connect
        self.valueUI.connect(self.valueUI, QtCore.SIGNAL("editingFinished()"), self.editChanged )
        if self.hasSlider:
            self.sliderUI.connect(self.sliderUI, QtCore.SIGNAL("valueChanged(int)"), self.sliderChanged )

    def setValue(self,value):
        self.valueUI.setText(str(value))
        self.editChanged()
        self.valueChangedSignal.emit()


    def myFixup(self, value):
        if float(value)<=self.dMin:
            self.setValue(self.dMin)
        elif float(value)>=self.dMax:
            self.setValue(self.dMax)
        self.valueUI.emit(QtCore.SIGNAL("editingFinished()"))

    def editChanged(self):
        if self.hasSlider:
            self.updateSliderLimits()
            self.sliderUI.setValue( int( (float( self.value() )) * float(_sliderNumSteps) ) )

    def sliderChanged(self,v):
        self.setValue( v/float(_sliderNumSteps) )

class IgIntSliderUI(IgValueSliderUI):
    """
    """

    # Value changed signal
    valueChangedSignal = QtCore.Signal()

    def __init__(self, label, annotation, hasSlider, dMin, dMax, uiMin, uiMax, gridLayout, gridRow, w1, w2, w3):
        IgValueSliderUI.__init__(self, label, annotation, hasSlider, dMin, dMax, uiMin, uiMax, gridLayout, gridRow, w1, w2, w3)

        # Set validator
        validator = QIntValidator(self.dMin, self.dMax, self.valueUI)
        validator.fixup = self.myFixup
        self.valueUI.setValidator(validator)
        self.setAccessibleName(r'XgIgIntSliderUI')

        # Connect
        self.valueUI.connect(self.valueUI, QtCore.SIGNAL("editingFinished()"), self.editChanged )
        if self.hasSlider:
            self.sliderUI.connect(self.sliderUI, QtCore.SIGNAL("valueChanged(int)"), self.sliderChanged )

    def setValue(self,value):
        self.valueUI.setText(str(value))
        self.editChanged()
        self.valueChangedSignal.emit()

    def myFixup(self, value):
        if int(value)<=self.dMin:
            self.setValue(self.dMin)
        elif int(value)>=self.dMax:
            self.setValue(self.dMax)
        self.valueUI.emit(QtCore.SIGNAL("editingFinished()"))

    def editChanged(self):
        if self.hasSlider:
            self.updateSliderLimits()
            self.sliderUI.setValue( int( (int( self.value() )) * float(_sliderNumSteps) ) )

    def sliderChanged(self,v):
        self.setValue( int(v/_sliderNumSteps) )
# ===========================================================================
# Copyright 2021 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
