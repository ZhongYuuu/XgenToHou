// =======================================================================
// Copyright 2015 Autodesk, Inc. All rights reserved.
//
// This computer source code and related instructions and comments are the
// unpublished confidential  and proprietary information of Autodesk, Inc.
// and are protected under applicable copyright and trade secret law. They 
// may not be disclosed to, copied  or used by any third party without the 
// prior written consent of Autodesk, Inc.
// =======================================================================


static void calBitangents(__global const float* CVs,
                __global float* bitangents,
                uint primitiveLength)
{
    float3 pnt, newPnt, diff;
    float3 lastValid = (float3)(1.0f, 0.0f, 0.0f);
    
    // Note: No way to calculate a valid bitangent for overlapped CVs, 
    // use the last valid bitangent in this case.
    for(uint i = 0; i < primitiveLength-1; i++ ) {
        pnt = vload3(i, CVs);
        newPnt = vload3((i+1), CVs);
        diff = newPnt - pnt;
        if(length(diff) > 0.00001f){
            lastValid = diff;
        }
        vstore3(lastValid, i, bitangents);
    }
    vstore3(lastValid, (primitiveLength - 1), bitangents);
}

__kernel void calBitangent_kernel(
                    __global const uint* visIndices,
                             const uint  visCount,
                    __global const uint*  info,
                    __global const float* positions,
                    __global float* bitangents,
                    uint infoStride,
                    uint n)
{
    // Out of range
    uint gid = get_global_id(0);
    if (gid >= visCount) return;

    gid = visIndices[gid];
    if (gid >= n) return;

    // Compute the bitangents
    const uint primitiveOffset = info[gid * infoStride];
    const uint primitiveLength = info[gid * infoStride + 1];

    if(primitiveLength > 0)
        calBitangents(positions + primitiveOffset * 3, bitangents + primitiveOffset * 3, primitiveLength);
}
