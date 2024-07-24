// =======================================================================
// Copyright 2017 Autodesk, Inc. All rights reserved. 
//
// Use of this software is subject to the terms of the Autodesk 
// license agreement provided at the time of installation or download, 
// or which otherwise accompanies this software in either electronic 
// or hard copy form.
// =======================================================================

#ifndef __XGSPLINEDATATOXPDCMD_H__
#define __XGSPLINEDATATOXPDCMD_H__

#include <maya/MPxCommand.h>
#include <maya/MSyntax.h>


// Export the specified spline data plug to a disk file in our internal
// binary format. The file can be loaded by the APIs in XgSplineAPI.h
//
class XgSplineDataToXpdCmd : public MPxCommand
{
public:
	XgSplineDataToXpdCmd();
	virtual ~XgSplineDataToXpdCmd() override;

	virtual MStatus doIt(const MArgList& args) override;

	virtual bool isUndoable() const override { return false; }
	virtual bool hasSyntax()  const override { return true; }

public:
	static void* creator();
	static MSyntax newSyntax();
};

#endif // __XGSPLINEDATATOXPDCMD_H__
