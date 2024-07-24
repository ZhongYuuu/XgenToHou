// =======================================================================
// Copyright 2015 Autodesk, Inc. All rights reserved.
//
// This computer source code and related instructions and comments are the
// unpublished confidential  and proprietary information of Autodesk, Inc.
// and are protected under applicable copyright and trade secret law. They 
// may not be disclosed to, copied  or used by any third party without the 
// prior written consent of Autodesk, Inc.
// =======================================================================


// Same as that in "XgModifierNoise.cl"
static void blendLength(
            global float* CVs,
            uint    numCVs,
            float   newLen
            )
{
    // Calculate total length
    float curLen = 0.0f;
    for (uint i = 1; i < numCVs; ++i) {
        curLen += fast_length((float3)(
            CVs[i * 3] - CVs[i * 3 - 3],
            CVs[i * 3 + 1] - CVs[i * 3 - 2],
            CVs[i * 3 + 2] - CVs[i * 3 - 1]));
    }

    if (islessequal(curLen, 0.0f))
        return;

    // If there is basically no change just return.
    if (isless(fabs(curLen - newLen), 0.0001f))
        return;

    // Now correct it by scaling all control poly segments
    const float ratio = newLen / curLen;

    //scalePoly(CVs, cvCount, ratio);
    float3 oldSeg, newSeg, vec;
    for (uint j = 0; j < numCVs - 1; j++)
    {
        oldSeg = (float3)(
            CVs[j * 3 + 3] - CVs[j * 3],
            CVs[j * 3 + 4] - CVs[j * 3 + 1],
            CVs[j * 3 + 5] - CVs[j * 3 + 2]
            );
        newSeg = oldSeg * ratio;
        vec = newSeg - oldSeg;
        for (uint k = j + 1; k < numCVs; k++)
        {
            CVs[k * 3]     += vec.x;
            CVs[k * 3 + 1] += vec.y;
            CVs[k * 3 + 2] += vec.z;
        }
    }
}

__kernel void setLength(
            __global uint*  info,
            __global float* CVs,
            uint            infoStride,
            uint            totalSplineCnt,
            float           newLen
        )
{
    uint gid = get_global_id(0);
    if (gid >= totalSplineCnt) return;

    const uint primitiveOffset = info[gid * infoStride];
    const uint primitiveLength = info[gid * infoStride + 1];

    blendLength(CVs+3*primitiveOffset, primitiveLength, newLen);
}
