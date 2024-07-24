// =======================================================================
// Copyright 2016 Autodesk, Inc. All rights reserved.
//
// This computer source code and related instructions and comments are the
// unpublished confidential  and proprietary information of Autodesk, Inc.
// and are protected under applicable copyright and trade secret law. They 
// may not be disclosed to, copied  or used by any third party without the 
// prior written consent of Autodesk, Inc.
// =======================================================================

// Culled flag
#define XG_SPLINE_CULLED_FLAG (0x1 << 1) // refer to XgSplineData.h
#define XG_SPLINE_SUPPRESSED_FLAG (0x1 << 2) // refer to XgSplineData.h

inline static bool isPrimCulled(unsigned int primFlag)
{
    return primFlag & (XG_SPLINE_CULLED_FLAG | XG_SPLINE_SUPPRESSED_FLAG);
}
