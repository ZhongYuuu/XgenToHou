// =======================================================================
// Copyright 2017 Autodesk, Inc. All rights reserved. 
//
// Use of this software is subject to the terms of the Autodesk 
// license agreement provided at the time of installation or download, 
// or which otherwise accompanies this software in either electronic 
// or hard copy form.
// =======================================================================

#include "XgSplineDataToXpdCmd.h"

#include <maya/MArgDatabase.h>
#include <maya/MFnAttribute.h>
#include <maya/MFnPluginData.h>
#include <maya/MPxData.h>
#include <maya/MGlobal.h>
#include <maya/MSelectionList.h>
#include <maya/MPlug.h>

#include <xpd/src/core/Xpd.h>

#include <xgen/src/xgcore/XgUtil.h>
#include <xgen/src/xgsculptcore/api/XgSplineAPI.h>

#include <vector>
#include <set>
#include <string>
#include <sstream>

void* XgSplineDataToXpdCmd::creator()
{
	return new XgSplineDataToXpdCmd();
}

MSyntax XgSplineDataToXpdCmd::newSyntax()
{
	MSyntax syntax;

	syntax.enableEdit(false);
	syntax.enableQuery(false);

	syntax.addFlag("-o", "-output", MSyntax::kString);

	syntax.setMinObjects(1);
	syntax.setMaxObjects(1);
	syntax.setObjectType(MSyntax::kSelectionList);

	return syntax;
}

XgSplineDataToXpdCmd::XgSplineDataToXpdCmd()
{}

XgSplineDataToXpdCmd::~XgSplineDataToXpdCmd()
{}

std::string makeNameUnique(const MString& output, const std::string& meshId)
{
	std::string finalName;

	std::string convertedMeshId(meshId);
	for (size_t i = 0; i < meshId.size(); i++)
	{
		if (meshId[i] == '.' || meshId[i] == '[' || meshId[i] == ']')
			convertedMeshId[i] = '_';
	}

	int dotPos = output.rindex('.');
	int dirSepratorPos = output.rindex('/');
	int dirSepratorPos2 = output.rindex('\\');
	if (dirSepratorPos < dirSepratorPos2) 
		dirSepratorPos = dirSepratorPos2;

	if (dotPos < 0 || dotPos < dirSepratorPos)
	{
		// no file extension, append suffix to last
		finalName = std::string(output.asChar()) + convertedMeshId;
	}
	else
	{
		finalName = std::string(output.substring(0, dotPos - 1).asChar()) + convertedMeshId
			+ std::string(output.substring(dotPos, output.length() - 1).asChar());
	}

	return finalName;
}

MStatus XgSplineDataToXpdCmd::doIt(const MArgList& args)
{
	MArgDatabase argData(syntax(), args);

	// Get the list of positional arguments
	MSelectionList positionalArgs;
	argData.getObjects(positionalArgs);

	// Check the number of parameters
	if (positionalArgs.length() != 1)
	{
		XGError("Wrong number of arguments.");
		return MS::kFailure;
	}

	// Get the plug from positional arguments
	MPlug splinePlug;
	positionalArgs.getPlug(0, splinePlug);

	// Get the output file path
	MString output;
	argData.getFlagArgument("-output", 0, output);

	// Check the output file path
	if (output.length() == 0)
	{
		XGError("-output flag is not specified properly.");
		return MS::kFailure;
	}

	MStatus status;
	
	// Open the output file for writing
	std::stringstream opaqueStrm;

	// Get the spline data from the output plug
	MObject splineData = splinePlug.asMObject();

	// Get the Maya interface for streaming
	MPxData* userData = MFnPluginData(splineData).data();

	// Stream out the spline data
	if (!userData || !userData->writeBinary(opaqueStrm))
	{
		return MS::kFailure;
	}

	opaqueStrm.flush();
	opaqueStrm.seekp(0, std::ios_base::end);

	XGenSplineAPI::XgFnSpline  _splines;
	size_t dataSize = opaqueStrm.tellp();

	opaqueStrm.seekp(0);

	// get current frame
	double frame;
	MString cmd("currentTime -query");
	status = MGlobal::executeCommand(cmd, frame);
	if (!status)
	{
		return MS::kFailure;
	}

	if (!_splines.load(opaqueStrm, dataSize, (float)frame))
	{
		XGError("Failed to load data from plug: " + std::string(splinePlug.name().asChar()));
		return MS::kFailure;
	}

	// Execute script to remove culled primitives from primitiveInfos array
	_splines.executeScript();

	std::set<std::string> meshIds;
	for (XGenSplineAPI::XgItSpline splineIt = _splines.iterator(); !splineIt.isDone(); splineIt.next())
	{
		const std::string meshId = splineIt.boundMeshId();

		meshIds.insert(meshId);
	}

	size_t meshNum = meshIds.size();
	if (meshNum == 0)
	{
		XGError("No spline data found from plug: " + std::string(splinePlug.name().asChar()));
		return MS::kFailure;
	}
	for (const std::string meshId : meshIds)
	{
		std::string xpdFilename;
		if (meshNum > 1)
		{
			// append suffix to the output file name
			xpdFilename = makeNameUnique(output, meshId);
		}
		else
		{
			xpdFilename = output.asChar();
		}

		std::map<unsigned int, std::vector<std::vector<unsigned int>>> faceToDataMap;

		unsigned int maxFaceId = 0;
		std::vector<const SgVec2f*> uvArray;
		std::vector<const SgVec3f*> posArray;
		std::vector<const float*> widthArray;
		std::vector<const SgVec3f*> widthDirArray;
		unsigned int primCount = 0;
		unsigned int cvCountPerPrim = 5;

		unsigned int curItemNum = 1;
		for (XGenSplineAPI::XgItSpline splineIt = _splines.iterator(); !splineIt.isDone(); splineIt.next())
		{
			if (splineIt.boundMeshId() != meshId )
				continue;

			for (auto it : faceToDataMap)
			{
				std::vector<unsigned int> emptyArr;
				it.second.push_back(emptyArr);
			}

			const unsigned int  stride = splineIt.primitiveInfoStride();
			primCount += splineIt.primitiveCount();
			const unsigned int* primitiveInfos = splineIt.primitiveInfos();
			cvCountPerPrim = primitiveInfos[1];	// each prim has same cv count

			const unsigned int* faceId = splineIt.faceId();

			for (unsigned int p = 0; p < splineIt.primitiveCount(); p++)
			{
				const unsigned int offset = primitiveInfos[p * stride] / cvCountPerPrim;
				auto it = faceToDataMap.find(faceId[offset]);
				if (faceId[offset] > maxFaceId)
					maxFaceId = faceId[offset];

				if (it == faceToDataMap.end())
				{
					std::vector<std::vector<unsigned int>> dataIndex;
					dataIndex.resize(curItemNum);
					dataIndex.back().push_back(offset);
					faceToDataMap.insert(std::make_pair(faceId[offset], dataIndex));
				}
				else
				{
					std::vector<std::vector<unsigned int>>& data = it->second;
					if (data.size() < curItemNum)
					{
						data.resize(curItemNum);
					}
					(it->second).back().push_back(offset);
				}
			}

			uvArray.push_back(splineIt.faceUV());
			posArray.push_back(splineIt.positions());
			widthArray.push_back(splineIt.width());
			widthDirArray.push_back(splineIt.widthDirection());

			curItemNum++;
		}

		// write xpd file
		//
		safevector<std::string> keys;
		safevector<std::string> blocks;
		blocks.push_back("BakedGroom");

#define PRIM_ATTR_VERSION 3
		XpdWriter *xFile = XpdWriter::open(xpdFilename, maxFaceId+1,
			Xpd::Spline, PRIM_ATTR_VERSION,
			Xpd::Object, blocks,
			(float)frame,
			cvCountPerPrim, &keys);

        if (!xFile)
        {
            XGError("Failed to create XPD file: " + xpdFilename + ". Please check if file path is valid.");
            return MS::kFailure;
        }

		// iterate each face
		for (unsigned int faceId = 0; faceId <= maxFaceId; faceId++)
		{
			auto it = faceToDataMap.find(faceId);
			unsigned int id = 0;

			// for face without primitive, still start a face
			if (!xFile->startFace(faceId)) {
				XGError("Failed to start a new face in XPD file: " + xpdFilename);
			}
			else if (!xFile->startBlock()) {
				XGError("Failed to start block in XPD file: " + xpdFilename);
			}

			// fill primitives data
			if (it != faceToDataMap.end())
			{
				auto& data = it->second;
				for (size_t i = 0; i < data.size(); i++)
				{
					std::vector<unsigned int >& prims = data[i];
					for (unsigned int index : prims)
					{
						safevector<float> primData;
						primData.push_back((float)id++);
						primData.push_back(uvArray[i][index][0]);
						primData.push_back(uvArray[i][index][1]);

						unsigned int posOffset = index * cvCountPerPrim;
						for (unsigned int j = 0; j < cvCountPerPrim; j++) {
							primData.push_back((float)posArray[i][posOffset][0]);
							primData.push_back((float)posArray[i][posOffset][1]);
							primData.push_back((float)posArray[i][posOffset][2]);
							posOffset++;
						}

						// cv attr
						primData.push_back(1.0); // length
						primData.push_back(widthArray[i][index * cvCountPerPrim]); // width
						primData.push_back(0.0); // taper
						primData.push_back(0.0); // taper start
						primData.push_back(widthDirArray[i][index * cvCountPerPrim][0]); // width vector .x
						primData.push_back(widthDirArray[i][index * cvCountPerPrim][1]); // width vector .y
						primData.push_back(widthDirArray[i][index * cvCountPerPrim][2]); // width vector .z

						xFile->writePrim(primData);
					}
				}
			}
		}

		xFile->close();
	}

	return MS::kSuccess;
}
