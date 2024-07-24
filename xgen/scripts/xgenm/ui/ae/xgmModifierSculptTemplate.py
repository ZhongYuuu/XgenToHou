import maya
maya.utils.loadStringResourcesForModule(__name__)

import maya.cmds as cmds
import maya.mel as mel

'''
    Attribute Editor for xgmModifierSculpt node

    We construct the Attribute Editor template by calling standard Maya
    commands.
'''

def determineNames(node, index):
    name         = r'tweaks{}'.format(index)
    plug         = r'{}.tweaks[{}]'.format(node, index)
    strengthAttr = r'{}.strength'.format(plug)
    uiName       = cmds.getAttr(r'{}.uiName'.format(plug))
    if len(uiName) == 0:
        uiName = r'{} {}'.format(maya.stringTable[u'y_xgenm_ui_ae_xgmModifierSculptTemplate.kSculptLayerHeader'], index+1)
    assert(len(uiName))
    return name, uiName, strengthAttr

def createSlider(name, uiName, strengthAttr):
    cmds.attrFieldSliderGrp(name,
        label=uiName,
        attribute=strengthAttr,
        visible=True,
        sliderMinValue=0.0, sliderMaxValue=1.0,
        fieldMinValue= -10.0, fieldMaxValue= 10.0,
        step = 0.1)

def AExgmModifierSculptTemplate(nodeName):
    ''' Construct the AE template for xgmModifierSculpt node '''
    # Begin xgmModifierSculpt Attribute Editor template
    cmds.editorTemplate(beginScrollLayout=True)

    # Common Attributes
    mel.eval(r'AExgmModifierBaseTemplate {}'.format(nodeName))

    # Sculpt Modifier Attributes
    cmds.editorTemplate(beginLayout=maya.stringTable[u'y_xgenm_ui_ae_xgmModifierSculptTemplate.kSculptModifier'], collapse=False)
    cmdstr = r'xgmCreateAEUiForFloatAttr "mask" "{}" "xgmModifierGuide"'.format(maya.stringTable[u'y_xgenm_ui_ae_xgmModifierSculptTemplate.kMask' ])
    mel.eval(cmdstr)
    cmds.editorTemplate(endLayout=True)

    # Layer Attributes
    cmds.editorTemplate(beginLayout=maya.stringTable[u'y_xgenm_ui_ae_xgmModifierSculptTemplate.kSculptLayers'], collapse=False)
    cmds.editorTemplate(r'tweaks', 
        callCustom=[AExgmModifierSculptLayerAttributesNew,AExgmModifierSculptLayerAttributesReplace])
    cmds.editorTemplate(endLayout=True)
    
    # Add derived attributes
    mel.eval(r'AEdependNodeTemplate {}'.format(nodeName))
    
    # Add dynamic attributes
    cmds.editorTemplate(addExtraControls=True)

    # End xgmModifierSculpt Attribute Editor template
    cmds.editorTemplate(endScrollLayout=True)

    # Suppress attributes
    suppress = [r'activeTweak', r'groups', r'tweaks', r'tweakGroups']
    for s in suppress:
        cmds.editorTemplate(suppress=s)

def AExgmModifierSculptLayerAttributesNew(nodeAttr):
    ''' Create the UI template for Layer Attributes '''

    cmds.setUITemplate(r'attributeEditorTemplate', pushTemplate=True)
    # Column Layout 
    cmds.columnLayout(r'sculptLayerColumn', adj=True)
    # Get the node name of the sculpt modifier
    node = nodeAttr[:nodeAttr.find(r'.')]

    # Get a list of logical indices of sculpt layers
    indices = cmds.getAttr(r'{}.tweaks'.format(node), multiIndices=True)    

    # Iterate over the multi-indices of the tweaks plug
    for index in list(indices):
        # Get sculpt layer attributes
        name, uiName, strengthAttr = determineNames(node, index)
        cmds.setUITemplate(r'attributeEditorTemplate', pushTemplate=True)
        createSlider(name, uiName, strengthAttr)
        cmds.setUITemplate( popTemplate=True )

    # End Column Layout
    cmds.setParent(r'..')
    cmds.setUITemplate( popTemplate=True )
    
    # Update UI and wire controls
    AExgmModifierSculptLayerAttributesReplace(nodeAttr)

def AExgmModifierSculptLayerAttributesReplace(nodeAttr):
    ''' Update the UI template for Layer Attributes '''
    cmds.setUITemplate(r'attributeEditorTemplate', pushTemplate=True)
    cmds.setParent (r'sculptLayerColumn')

    # Get a list of all the current sliders
    layout = cmds.setParent(query=True)
    prevSliders = cmds.columnLayout(layout, query=True, childArray=True)

    # Get the node name of the sculpt modifier
    node = nodeAttr[:nodeAttr.find(r'.')]
  
    # Get a list of logical indices of sculpt layers
    indices = cmds.getAttr(r'{}.tweaks'.format(node), multiIndices=True)

    # Iterate over the multi-indices of the tweaks plug
    for index in list(indices):
        sliderName, uiName, strengthAttr = determineNames(node, index)
        if cmds.attrFieldSliderGrp(sliderName, exists=True):
            cmds.attrFieldSliderGrp(sliderName, label=uiName, attribute=strengthAttr, edit=True)
        else:
            cmds.setUITemplate(r'attributeEditorTemplate', pushTemplate=True)
            createSlider(sliderName, uiName, strengthAttr)
            cmds.setUITemplate( popTemplate=True )

    # Remove any sliders that are no longer needed
    currentSliders = [ r'tweaks{}'.format(i) for i in list(indices)]
    for prevSlider in prevSliders :
        if prevSlider not in currentSliders and cmds.attrFieldSliderGrp(prevSlider, exists=True) :
            cmds.deleteUI(prevSlider)

    # End Column Layout
    cmds.setParent(r'..')
    cmds.setUITemplate(popTemplate=True)
# ===========================================================================
# Copyright 2021 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
