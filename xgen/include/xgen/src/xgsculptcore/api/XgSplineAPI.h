// =======================================================================
// Copyright 2015 Autodesk, Inc. All rights reserved.
//
// This computer source code and related instructions and comments are the
// unpublished confidential  and proprietary information of Autodesk, Inc.
// and are protected under applicable copyright and trade secret law. They 
// may not be disclosed to, copied  or used by any third party without the 
// prior written consent of Autodesk, Inc.
// =======================================================================

#ifndef __XGSPLINEAPI_H__
#define __XGSPLINEAPI_H__

#include "porting/XgWinExport.h"
#include <xgen/src/sggeom/SgBox3T.h>
#include <xgen/src/sggeom/SgVec3T.h>
#include <xgen/src/sggeom/SgVec2T.h>
#include <istream>

#define XGEN_SPLINE_API_VERSION 201740

// APIs in this file load and interpret the BLOB data, which is written by
// calling MPxData::writeBinary(). The data is type of xgmSplineData in Maya.
// 
namespace XGenSplineAPI
{

// ============================================================================

// XgItSpline iterates the spline data from Maya.
class XGEN_EXPORT XgItSpline
{
public:
    XgItSpline();
    XgItSpline(const XgItSpline& other);
    XgItSpline(const XgItSpline& begin, const XgItSpline& end);
    ~XgItSpline();

    // Iterator methods
    void reset();
    bool isDone() const;
    void next();

    // Stride of the primitive info array
    //  [0]: Offset
    //  [1]: Length
    // Offset and length determines the varying attribute location
    // of each vertex in the varying array.
    unsigned int  primitiveInfoStride() const;

    // Return the number of primitives
    unsigned int  primitiveCount() const;

    // Return the number of vertices
    unsigned int  vertexCount() const;

    // Return the bounding box
    SgBox3f       boundingBox(int motion = 0) const;

    // Return the bounding box of motion vectors
    SgBox3f       motionBoundingBox() const;

	std::string boundMeshId() const;

    // Primitive info. See primitiveInfoStride()
    const unsigned int* primitiveInfos() const;

	const unsigned int* faceId() const;

	const SgVec2f* faceUV() const;

    // Varying (per-vertex) Attributes
    //

    // Vertex positions
    const SgVec3f*      positions(int motion = 0) const;

    // Texcoords from root to tip
    // U is 0.0
    // V ranges from 0.0 (root vertex) to 1.0 (tip vertex)
    const SgVec2f*      texcoords(int motion = 0) const;

    // Texcoords of the root vertex on the patch
    const SgVec2f*      patchUVs(int motion = 0) const;

    // Width
    const float*        width(int motion = 0) const;

	// Width direction
	const SgVec3f*      widthDirection(int motion = 0) const;

private:
    friend class XgFnSpline;
    XgItSpline& operator=(const XgItSpline&);
    char _rep[64];
};

// ============================================================================

// XgFnSpline loads the data from xgmSplineDescription.outRenderData plug in
// Maya. Translators use Maya's MPxData::writeBinary() method to serialize the
// plug data into a BLOB. XgFnSpline can interpret the data without Maya.
class XGEN_EXPORT XgFnSpline
{
public:
    XgFnSpline();
    XgFnSpline(const XgFnSpline& other);
    ~XgFnSpline();

    // Set FPS (frame-per-second) for spline generation
    void setFps(float fps);

    // Load the data from the specified stream and size
    bool load(std::istream& strm, size_t size, float frame);

    // Iterate the spline data loaded before
    XgItSpline iterator() const;

    // Get the number of motion samples
    unsigned int sampleCount() const;

    // Execute the render-time script
    // We export the raw splines with a render-time script such as density
    // multiplier and density mask. This method execute the script to modify
    // the raw splines. Call this method after all load methods complete.
    bool executeScript();

private:
    XgFnSpline& operator=(const XgFnSpline&);
    char _rep[64];
};

// ============================================================================

} // namespace XGenSplineAPI

#endif // __XGSPLINEAPI_H__

