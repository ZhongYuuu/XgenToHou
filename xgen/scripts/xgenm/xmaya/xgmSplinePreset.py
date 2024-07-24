from builtins import object
import re
import os
import contextlib

import maya.mel as mel
import maya.cmds as cmds


@contextlib.contextmanager
def transferModeGuard(transferModeNodes, mappingType, alignToNormal, rootNodes, bbInfo):
    transferModeAttrName = r'transferMode'
    bbInfoAttrName = r'transferModeBBInfo'
    mappingTypeAttrName = r'transferModeMappingType'
    alignToNormalAttrName = r'transferModeAlignToNormal'

    mappingTypeDict = {
    r'position': 0,
    r'uv': 1,
    }

    for node in transferModeNodes:
        cmds.setAttr(r'%s.%s' % (node, transferModeAttrName), True)
        cmds.setAttr(r'%s.%s' % (node, alignToNormalAttrName), alignToNormal)
        cmds.setAttr(r'%s.%s' % (node, mappingTypeAttrName), mappingTypeDict[mappingType])
    for node in rootNodes:
        cmds.setAttr(r'%s.%s' % (node, bbInfoAttrName), bbInfo, type=r'string')

    yield

    for node in transferModeNodes:
        cmds.setAttr(r'%s.%s' % (node, transferModeAttrName), False)
    for node in rootNodes:
        cmds.setAttr(r'%s.%s' % (node, bbInfoAttrName), '', type=r'string')


class ForwardCompatibilityError(RuntimeError):
    pass


class PresetUtil(object):

    buildVersion = 1

    presetNodeClassifications = {
        r'xgen/spline',
        r'animation',
        r'texture',
        r'utility/general/placement',
    }

    extraNodeTypes = {
        r'transform',
        r'shadingEngine',
    }

    transferModeNodeTypes = {
        r'xgmSplineBase',
        r'xgmModifierSculpt',
        r'xgmModifierLinearWire',
    }

    transformNodeType = r'transform'
    rootNodeType = r'xgmSplineBase'
    descNodeType = r'xgmSplineDescription'
    shadingEngineNodeType = r'shadingEngine'

    requiresPattern = re.compile(r'''^requires maya.*''')
    commentPattern = re.compile(r'''^//.*''')
    bbInfoPattern = re.compile(r'''^//XGIP:BBINFO: (.*)''')
    versionPattern = re.compile(r'''^//XGIP:VERSION: (\d+)''')
    createNodePattern = re.compile(r'''^createNode\s(\w+).*\s\-n\s"([\w:]+)"''')
    createNodeWithParentPattern = re.compile(r'''^createNode\s(\w+).*\s\-n\s"([\w:]+)".*\s\-p\s"([\w:]+)"''')
    renamePattern = re.compile(r'''^\s+rename\s([\-\w:]+)\s''')
    setAttrPattern = re.compile(r'''^\s+setAttr\s''')
    addAttrPattern = re.compile(r'''^\s+addAttr\s''')
    connectAttrPattern = re.compile(r'''^connectAttr\s+"([\w\.\[\]:]+)"\s"([\w\.\[\]:]+)"''')

    @classmethod
    def convertMAToPreset(cls, inFile, outFile, boundingBoxInfo, removeOriginal=True):
        '''Convert MA to Preset file'''
        cls.__convertMAToPreset(inFile, outFile, boundingBoxInfo)
        if removeOriginal:
            cls.__removeFile(inFile)

    @classmethod
    def applyPreset(cls, filePath, mappingType, alignToNormal):
        '''Apply Preset file to selected node'''

        # Keep a record of currently selected node
        selectedShapes = cls.getSelectedShapes()
        selectedShape = selectedShapes[0] if selectedShapes else ''

        # Import and collect grooming nodes
        transferModeNodes, rootNodes, descNodes, bbInfo = cls.__importPreset(filePath)

        # Bind selected node to grooming nodes, while in Transfer Mode
        with transferModeGuard(transferModeNodes, mappingType, alignToNormal, rootNodes, bbInfo):
            cls.__bindSelected(selectedShape, rootNodes, descNodes)

    @staticmethod
    def getSelectedShapes():
        objectsSelectedInScene = cmds.ls(selection=True, objectsOnly=True)
        shapesSelectedInScene = cmds.listRelatives(
            *objectsSelectedInScene,
            shapes=True,
            noIntermediate=True,
            type=r'mesh',
            path=True
        )
        return shapesSelectedInScene

    @staticmethod
    def getSelectedDescriptions():
        objectsSelectedInScene = cmds.ls(selection=True, objectsOnly=True)
        descsSelectedInScene = cmds.listRelatives(
            *objectsSelectedInScene,
            noIntermediate=True,
            type=r'xgmSplineDescription',
            path=True
        )
        return descsSelectedInScene

    @classmethod
    def __importPreset(cls, filePath):
        '''Import file, return collected nodes'''
        transformModeNodeNames = []
        rootNodeNames = []
        descNodeNames = []
        bbInfo = ''
        fileVersion = None

        if os.path.isfile(filePath):
            with open(filePath, r'r') as f:
                for line in f:
                    line = line.rstrip()

                    matchBBInfoPattern = cls.bbInfoPattern.search(line)
                    if matchBBInfoPattern:
                        # bbInfo appears only once
                        bbInfo = matchBBInfoPattern.group(1)

                    matchVersionPattern = cls.versionPattern.search(line)
                    if matchVersionPattern:
                        # version appears only once
                        fileVersion = int(matchVersionPattern.group(1))

                    if bbInfo and fileVersion is not None:
                        break

            if fileVersion and fileVersion > cls.buildVersion:
                # TODO: L10N
                raise ForwardCompatibilityError(
                    '''Current Preset build version: %s. Cannot import Preset of a higher verison: %s.''' % (cls.buildVersion, fileVersion)
                )

            nodesBeforeImport = set(cmds.ls())

            try:
                newNodes = cmds.file(
                    filePath,
                    i=True,
                    type=r"mayaAscii",
                    ignoreVersion=True,
                    renameAll=True,
                    mergeNamespacesOnClash=True,
                    preserveReferences=True,
                    returnNewNodes=True
                )
            except Exception as e:
                import traceback
                traceback.print_exc()

                # If exception occurs during importing, try to recover newNodes
                # by comparing scene nodes snapshots
                nodesAfterImport = set(cmds.ls())
                newNodes = list(nodesAfterImport - nodesBeforeImport)

            for nodeName in newNodes:
                nodeType = cmds.nodeType(nodeName)
                if nodeType == cls.rootNodeType:
                    rootNodeNames.append(nodeName)
                elif nodeType == cls.descNodeType:
                    descNodeNames.append(nodeName)
                if nodeType in cls.transferModeNodeTypes:
                    transformModeNodeNames.append(nodeName)

        return transformModeNodeNames, rootNodeNames, descNodeNames, bbInfo

    @staticmethod
    def __bindSelected(shape, rootNodes, descNodes):
        for rootNode in rootNodes:
            fromAttr = r'%s.worldMesh' % shape
            toAttr = r'%s.boundMesh[0]' % rootNode
            cmds.connectAttr(fromAttr, toAttr)

        for descNode in descNodes:
            # Force grooming DG eval
            # This must be done once before Transfer Mode turned off
            descAttr = r'%s.outSplineData' % descNode
            cmds.dgeval(descAttr)

    @classmethod
    def __convertMAToPreset(cls, inFile, outFile, boundingBoxInfo):

        with open(inFile, r'r') as f:
            maBuff = f.read()

        melBuff = cls.__convertMAToPresetBuffer(maBuff, boundingBoxInfo)

        with open(outFile, r'w') as f:
            f.write(melBuff)

    @classmethod
    def __getExtendedExtraNodeTypes(cls, fileBuff):
        # Make a copy so that we can dynamically modify it
        extraNodeTypes = set(cls.extraNodeTypes)

        # shadingEngine node names
        shadingEngineNodeNames = set()

        # map node name to its type
        nodeTypeMapping = dict()

        # map plugTo to plugFrom, used for locating Surface Shader
        connectMapping = dict()

        # Preparation pass, used for extend extraNodeTypes to include shading related nodes
        cmdLineList = cls.__getCmdLineList(fileBuff)
        for line in cmdLineList:
            lineStr = ' '.join(line)

            # Record createNode
            matchCreateNode = cls.createNodePattern.search(lineStr)
            if matchCreateNode:
                nodeType = matchCreateNode.group(1)
                nodeName = matchCreateNode.group(2)
                nodeTypeMapping[nodeName] = nodeType
                if nodeType == cls.shadingEngineNodeType:
                    shadingEngineNodeNames.add(nodeName)

                continue

            # Record connectAttr
            matchConnectAttr = cls.connectAttrPattern.search(lineStr)
            if matchConnectAttr:
                plugFrom = matchConnectAttr.group(1)
                plugTo = matchConnectAttr.group(2)
                connectMapping[plugTo] = plugFrom

                continue

        # Entend extraNodeTypes
        for nodeName in shadingEngineNodeNames:
            candidatePlug = r'%s.ss' % nodeName
            correspondingPlug = connectMapping.get(candidatePlug)
            if correspondingPlug:
                correspondingNode = correspondingPlug.split(r'.')[0]
                nodeType = nodeTypeMapping.get(correspondingNode)
                if nodeType:
                    extraNodeTypes.add(nodeType)

        return extraNodeTypes

    @classmethod
    def __getCmdLineList(cls, fileBuff):
        cmdLine = []
        cmdLineList = []
        for line in fileBuff.split('\n'):
            line = line.rstrip()

            # Comment line found
            if cls.commentPattern.search(line):
                continue

            # Cache incomplete lines
            cmdLine.append(line)
            if not line.endswith(r';'):
                continue

            cmdLineList.append(cmdLine)
            cmdLine = []

        return cmdLineList

    @classmethod
    def __convertMAToPresetBuffer(cls, fileBuff, boundingBoxInfo):
        extraNodeTypes = cls.__getExtendedExtraNodeTypes(fileBuff)
        content = cls.__getMAToPresetBuffer(fileBuff, extraNodeTypes)
        content = cls.__filterUnusedTransform(content)
        content = cls.__addMetaData(content, boundingBoxInfo)
        content = cls.__addHeader(content)

        return content

    @classmethod
    def __shouldKeepNodeType(cls, nodeType, extraNodeTypes):
        if nodeType in extraNodeTypes:
            return True
        for classification in cls.presetNodeClassifications:
            if cmds.getClassification(nodeType, satisfies=classification):
                return True

        return False

    @classmethod
    def __getMAToPresetBuffer(cls, fileBuff, extraNodeTypes):

        def processRequires():
            content.extend(line)

            lineIdx[0] += 1

        def processCreateNode():
            nodeType = matchCreateNode.group(1)
            keepCurrentNode = cls.__shouldKeepNodeType(nodeType, extraNodeTypes)

            if keepCurrentNode:
                content.extend(line)
                nodeName = matchCreateNode.group(2)
                collectedNodeNames.add(nodeName)

            lineIdx[0] += 1

            # in createNode's inner scope
            while lineIdx[0] < len(cmdLineList):
                innerLine = cmdLineList[lineIdx[0]]
                innerLineStr = ' '.join(innerLine)

                matchRename = cls.renamePattern.search(innerLineStr)
                matchSetAttr = cls.setAttrPattern.search(innerLineStr)
                matchAddAttr = cls.addAttrPattern.search(innerLineStr)
                if matchRename or matchSetAttr or matchAddAttr:
                    if keepCurrentNode:
                        if matchRename and matchRename.group(1) == r'-uid':
                            # Ignore uid changes
                            pass
                        else:
                            content.extend(innerLine)

                    lineIdx[0] += 1
                    continue
                else:
                    # Out of inner scope already
                    break

        def processConnectAttr():
            plugFrom, plugTo = matchConnectAttr.group(1), matchConnectAttr.group(2)
            nodeFrom = plugFrom.split(r'.')[0]
            nodeTo = plugTo.split(r'.')[0]
            if (nodeFrom in collectedNodeNames or nodeFrom.startswith(r':')) and \
                    (nodeTo in collectedNodeNames or nodeTo.startswith(r':')):
                content.extend(line)

            lineIdx[0] += 1

        # Main pass, used for composing Preset content
        content = []
        collectedNodeNames = set()
        cmdLineList = cls.__getCmdLineList(fileBuff)

        # A single element list, used to workaround the limitation that closure
        # cannot write to a parent scope immutable variable
        lineIdx = [0]

        while lineIdx[0] < len(cmdLineList):
            line = cmdLineList[lineIdx[0]]
            lineStr = ' '.join(line)

            # requires found
            matchRequires = cls.requiresPattern.search(lineStr)
            if matchRequires:
                processRequires()
                continue

            # createNode found
            matchCreateNode = cls.createNodePattern.search(lineStr)
            if matchCreateNode:
                processCreateNode()
                continue

            matchConnectAttr = cls.connectAttrPattern.search(lineStr)
            if matchConnectAttr:
                processConnectAttr()
                continue

            lineIdx[0] += 1
            continue

        return '\n'.join(content)

    @classmethod
    def __filterUnusedTransform(cls, fileBuff):

        def processCreateNode():
            nodeType = matchCreateNode.group(1)
            nodeName = matchCreateNode.group(2)

            keepCurrentNode = nodeType != cls.transformNodeType or \
                nodeName in referencedTransformNodes

            if keepCurrentNode:
                content.extend(line)
                collectedNodeNames.add(nodeName)

            lineIdx[0] += 1

            # in createNode's inner scope
            while lineIdx[0] < len(cmdLineList):
                innerLine = cmdLineList[lineIdx[0]]
                innerLineStr = ' '.join(innerLine)

                matchRename = cls.renamePattern.search(innerLineStr)
                matchSetAttr = cls.setAttrPattern.search(innerLineStr)
                matchAddAttr = cls.addAttrPattern.search(innerLineStr)
                if matchRename or matchSetAttr or matchAddAttr:
                    if keepCurrentNode:
                        content.extend(innerLine)

                    lineIdx[0] += 1
                    continue
                else:
                    # Out of inner scope already
                    break

        def processConnectAttr():
            plugFrom, plugTo = matchConnectAttr.group(1), matchConnectAttr.group(2)
            nodeFrom = plugFrom.split(r'.')[0]
            nodeTo = plugTo.split(r'.')[0]
            if (nodeFrom in collectedNodeNames or nodeFrom.startswith(r':')) and \
                    (nodeTo in collectedNodeNames or nodeTo.startswith(r':')):
                content.extend(line)

            lineIdx[0] += 1

        cmdLineList = cls.__getCmdLineList(fileBuff)

        # Build nodes parenting relationship
        nodeParenting = dict()
        for line in cmdLineList:
            lineStr = ' '.join(line)

            matchCreateNodeWithParent = cls.createNodeWithParentPattern.search(lineStr)
            if matchCreateNodeWithParent:
                nodeType = matchCreateNodeWithParent.group(1)
                nodeName = matchCreateNodeWithParent.group(2)
                nodeParent = matchCreateNodeWithParent.group(3)
                nodeParenting[nodeName] = (nodeType, nodeParent)
                continue

        # Collect referenced transform nodes
        referencedTransformNodes = set()
        for k in nodeParenting:
            nodeType, nodeParent = nodeParenting[k]
            if nodeType != cls.transformNodeType:
                candidate = nodeParent
                # Recursively add parents up thru the chain
                while True:
                    referencedTransformNodes.add(candidate)
                    parent = nodeParenting.get(candidate, None)
                    if not parent:
                        break
                    parentType, candidate = parent

        content = []
        lineIdx = [0]
        collectedNodeNames = set()

        while lineIdx[0] < len(cmdLineList):
            line = cmdLineList[lineIdx[0]]
            lineStr = ' '.join(line)

            matchCreateNode = cls.createNodePattern.search(lineStr)
            if matchCreateNode:
                processCreateNode()
                continue

            matchConnectAttr = cls.connectAttrPattern.search(lineStr)
            if matchConnectAttr:
                processConnectAttr()
                continue

            # For other content, just copy as is
            content.extend(line)

            lineIdx[0] += 1

        return '\n'.join(content)

    @staticmethod
    def __addMetaData(content, boundingBoxInfo):
        contentList = []
        bbBuff = r"//XGIP:BBINFO: %s" % boundingBoxInfo
        contentList.append(bbBuff)
        contentList.append(content)

        return '\n'.join(contentList)

    @classmethod
    def __addHeader(cls, content):
        contentList = [
        r"// XGen Interactive Grooming Preset",
        r"//",
        r"// Author:       %s" % mel.eval(r'getenv("USER")'),
        r"// Date:         %s" % cmds.date(),
        r"//",
        r"//XGIP:VERSION: %s" % cls.buildVersion,
        ]
        contentList.append(content)

        return '\n'.join(contentList)

    @staticmethod
    def __removeFile(filePath):
        try:
            os.remove(filePath)
        except Exception as e:
            # TODO: Why am I here?
            pass
# ===========================================================================
# Copyright 2021 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
