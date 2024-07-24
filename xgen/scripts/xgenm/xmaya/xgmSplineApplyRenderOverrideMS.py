import argparse
import os
import sys

import maya.cmds as cmds
import maya.OpenMaya as om
import maya.standalone as ms


'''
    Apply the Render Overrides to the spline description shape node.
'''
def main(args):
    try:
        # Initialize Maya standalone
        ms.initialize(name=r'python')

        # Default module script paths
        for module in cmds.moduleInfo(listModules=True):
            scriptDir = os.path.join(cmds.moduleInfo(moduleName=module, path=True), r'scripts')
            sys.path.append(scriptDir)
            for root, dirs, files in os.walk(scriptDir):
                for dir in dirs:
                    sys.path.append(os.path.join(root, dir))

        # Load xgen
        cmds.loadPlugin(r'xgenToolkit')

        # Check the existence of the scene file
        if not os.path.exists(args.sceneFile):
            print(r'The specified Maya scene does not exist: %s' % args.sceneFile)
            return 1

        # Load the scene file
        cmds.file(args.sceneFile, force=True, open=True)

        # Check the existence of the spline description shape
        if not cmds.objExists(args.dagPath):
            print(r'The specified description path does not exist: %s' % args.dagPath)
            return 1

        # Check the type of the dag path
        if not cmds.objectType(args.dagPath, isAType=r'xgmSplineDescription'):
            print(r'The specified dag path is not a spline description: %s' % args.dagPath)
            return 1

        # Rely on some ui scripts to find the spline base node.. listHistory
        # does not work here because we only want to trace inSplineData/outSplineData
        # connections.
        from xgenm.ui.util.xgIgSplineUtil import findUpstreamSplinePlug, isSplineBaseNode
        dagPath  = om.MDagPath()
        baseNode = r''
        try:
            sl = om.MSelectionList()
            sl.add(args.dagPath)
            sl.getDagPath(0, dagPath)
        except:
            pass
        plug = om.MFnDagNode(dagPath).findPlug(r'outSplineData')
        while not plug.isNull():
            # Go upstream
            destinationPlug = findUpstreamSplinePlug(plug)
            sourcePlug = destinationPlug.source()
            plug = sourcePlug
            # Found the connection (src,dst)
            if not destinationPlug.isNull() and not sourcePlug.isNull():
                if isSplineBaseNode(sourcePlug.node()):
                    baseNode = om.MFnDependencyNode(sourcePlug.node()).name()
                    break

        # Not found ?
        if not baseNode:
            print(r'The spline base node is not found..')
            return 1

        # Get the Render Density Multiplier from the spline description node
        plug = r'%s.renderDensityMultiplier' % args.dagPath
        renderDensityMultiplier = cmds.getAttr(plug)

        # Get the Density Multiplier from the spline base node
        plug = r'%s.densityMultiplier' % baseNode
        baseDensityMultiplier = cmds.getAttr(plug)

        # Override the Density Multiplier on the spline base node
        finalDensityMultiplier = baseDensityMultiplier * renderDensityMultiplier
        cmds.xgmSplineBaseDensityScaleChangeCmd(baseNode, value=finalDensityMultiplier)

        # Write the render splines to external storage
        plug = r'%s.outRenderData' % args.dagPath
        cmds.xgmExportSplineDataInternal(plug, output=args.output)

    finally:
        # Clean up
        ms.uninitialize()

    return 0

'''
    This is an standalone script running in mayapy.
'''
if __name__ == r'__main__':
    # Parse the arguments and go
    parser = argparse.ArgumentParser(
        description = r'Apply render overrides to xgen spline descriptions.')
    parser.add_argument(r'-sceneFile', required=True,
        help = r'Maya scene file to process')
    parser.add_argument(r'-dagPath', required=True,
        help = r'Path to the spline description in the scene file')
    parser.add_argument(r'-output', required=True,
        help = r'Output binary file of the render splines')
    args = parser.parse_args()
    ret = main(args)
    os._exit(ret)
# ===========================================================================
# Copyright 2021 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
