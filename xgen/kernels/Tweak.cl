// =======================================================================
// Copyright 2016 Autodesk, Inc. All rights reserved.
//
// This computer source code and related instructions and comments are the
// unpublished confidential  and proprietary information of Autodesk, Inc.
// and are protected under applicable copyright and trade secret law. They 
// may not be disclosed to, copied  or used by any third party without the 
// prior written consent of Autodesk, Inc.
// =======================================================================

__kernel void applyTweak_kernel(
    __global const float* inPositions,
    __global float* outPositions,
    __global float* tweaks,
    float weight,
    uint n)
{
    uint gid = get_global_id(0);
    if (gid >= n) return;

    float3 p = vload3(gid, inPositions);
    float3 t = vload3(gid, tweaks);
    p = p + t * weight;
    vstore3(p, gid, outPositions);
}

// NVIDIA 365.10 driver is buggy when using clEnqueueCopyBuffer with OpenGL
// shared buffers. The API returns CL_INVALID_VALUE so we have to use a copy
// kernel.
__kernel void copyPositions_kernel(
    __global const float* inPositions,
    __global       float* outPositions,
             const uint   n)
{
    const uint gid = get_global_id(0);
    if (gid >= n) return;
    vstore3(vload3(gid, inPositions), gid, outPositions);
}

