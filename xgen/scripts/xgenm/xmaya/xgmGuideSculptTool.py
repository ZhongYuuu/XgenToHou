import maya.cmds as cmds

'''
    When the Guide Sculpt Tool is on, the tool will register this method to
    CurrentDescriptionSet callback. This is the bridge between the current
    palette/description in the Description Editor and the tool. Whenever the
    current palette/description changes, the tool should find the guides
    again.
'''
def notifyCurrentDescriptionChanged(desc):
    # This callback is only active when the Guide Sculpt Tool is on. So the
    # current tool is expected to be the guide sculpt tool.
    currentCtx = cmds.currentCtx()
    if cmds.xgmGuideSculptContext(currentCtx, q=True, exists=True):
        # Reset the affected guides. The tool will find the guides again
        # in the next event. i.e. hovering, dragging, clicking...
        cmds.xgmGuideSculptContext(currentCtx, e=True, resetAffected=True)
# ===========================================================================
# Copyright 2021 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
