// =======================================================================
// Copyright 2017 Autodesk, Inc. All rights reserved. 
//
// Use of this software is subject to the terms of the Autodesk 
// license agreement provided at the time of installation or download, 
// or which otherwise accompanies this software in either electronic 
// or hard copy form.
// =======================================================================


//
//
// Description:
//  Sample plug-in demonstrating how to use interactive XGEN API to access spline data.
//  This sample is also write the spline data to xpd file, which can be read back by
//  the legacy XGen.
//
//
// Example usages:
// xgSplineDataToXpd -output "g:/pSphere1.xpd" description1_Shape.outSplineData;

//
//
#include <maya/MPxCommand.h>
#include <maya/MSyntax.h>
#include <maya/MArgList.h>
#include <maya/MArgDatabase.h>
#include <maya/MGlobal.h>
#include <maya/MFnPlugin.h>

#include "XgSplineDataToXpdCmd.h"

#define kCmdName "xgSplineDataToXpd"
#define CLASSNAME XgSplineDataToXpdCmd
//////////////////////////////////////////////////////////////////////////
//
// Plugin registration
//
//////////////////////////////////////////////////////////////////////////

MStatus initializePlugin(MObject obj)
{
	MFnPlugin plugin(obj);
	MStatus stat = plugin.registerCommand(kCmdName, CLASSNAME::creator, CLASSNAME::newSyntax);
	return stat;
}

MStatus uninitializePlugin(MObject obj)
{
	MFnPlugin plugin(obj);
	return plugin.deregisterCommand(kCmdName);
}