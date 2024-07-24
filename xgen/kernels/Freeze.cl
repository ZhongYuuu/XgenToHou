// =======================================================================
// Copyright 2015 Autodesk, Inc. All rights reserved.
//
// This computer source code and related instructions and comments are the
// unpublished confidential  and proprietary information of Autodesk, Inc.
// and are protected under applicable copyright and trade secret law. They 
// may not be disclosed to, copied  or used by any third party without the 
// prior written consent of Autodesk, Inc.
// =======================================================================

#include <Utils.cl>

__kernel void markFrozen(
                    __global const uint* visIndices,
                             const uint  visCount,
                    __global uint*  info,
                    __global float* falloffs,
                    __global float* frozenSet,
                    __global float* originalFrozenSet,
                    uint infoStride,
                    uint n,
                    uint invert,
                    float strength
                    )
{
    uint gid = get_global_id(0);
    if (gid >= visCount) return;

    gid = visIndices[gid];
    if (gid >= n) return;

    const uint primitiveFlag = info[gid * infoStride + 2];
    if (isPrimCulled(primitiveFlag))
        return;

    saveOriginalFrozenSet(info, frozenSet, originalFrozenSet, infoStride, gid);

    const uint primitiveOffset = info[gid * infoStride];
    const uint primitiveLength = info[gid * infoStride + 1];

    for(uint i=primitiveOffset+1; i<primitiveOffset+primitiveLength; ++i) {
        if(isSelected(falloffs[i])) {
            if(invert) {
                frozenSet[i] += falloffs[i] * strength;
            } else {
                frozenSet[i] -= falloffs[i] * strength;
            }
            frozenSet[i] = clamp(frozenSet[i], 0.0f, 1.0f);
        }
    }
    frozenSet[primitiveOffset] = frozenSet[primitiveOffset+1];
}

__kernel void sumFrozen(
                    __global const uint* visIndices,
                             const uint  visCount,
                    __global uint*  info,
                    __global float* falloffs,
                    __global float* frozenSet,
                    __global volatile float* sumBuffer,
                    uint infoStride,
                    uint n
                    )
{
    uint gid = get_global_id(0);
    if (gid >= visCount) return;

    gid = visIndices[gid];
    if (gid >= n) return;

    const uint primitiveFlag = info[gid * infoStride + 2];
    if (isPrimCulled(primitiveFlag))
        return;

    const uint primitiveOffset = info[gid * infoStride];
    const uint primitiveLength = info[gid * infoStride + 1];

    if (isequal(falloffs[primitiveOffset], -1.0f)) return;

    for(uint i=primitiveOffset+1; i<primitiveOffset+primitiveLength; ++i) {
        if(isSelected(falloffs[i])) {
            atomicAdd(&sumBuffer[0], 1.0f);
            atomicAdd(&sumBuffer[1], frozenSet[i]);
        }
    }
}

__kernel void smoothFrozen(
                    __global const uint* visIndices,
                             const uint  visCount,
                    __global uint*  info,
                    __global float* falloffs,
                    __global float* frozenSet,
                    __global float* originalFrozenSet,
                    __global volatile float* sumBuffer,
                    uint infoStride,
                    uint n,
                    float strength
                    )
{
    uint gid = get_global_id(0);
    if (gid >= visCount) return;

    gid = visIndices[gid];
    if (gid >= n) return;

    const uint primitiveFlag = info[gid * infoStride + 2];
    if (isPrimCulled(primitiveFlag))
        return;

    const uint primitiveOffset = info[gid * infoStride];
    const uint primitiveLength = info[gid * infoStride + 1];

    if (isequal(falloffs[primitiveOffset], -1.0f)) return;
    if (isequal(sumBuffer[0], 0.0f)) return;

    saveOriginalFrozenSet(info, frozenSet, originalFrozenSet, infoStride, gid);

    float aveFalloff = sumBuffer[1]/sumBuffer[0];
    for(uint i=primitiveOffset+1; i<primitiveOffset+primitiveLength; ++i) {
        if(isSelected(falloffs[i])) {
            float w = falloffs[i] * strength;
            w = clamp(w, 0.0f, 1.0f);
            frozenSet[i] = frozenSet[i] * (1.0f - w) + aveFalloff * w;
        }
    }
    frozenSet[primitiveOffset] = frozenSet[primitiveOffset+1];
}

__kernel void unfreezeAll(
                    __global const uint* visIndices,
                             const uint  visCount,
                    __global uint*  info,
                    __global float* frozenSet,
                    __global float* originalFrozenSet,
                    uint infoStride,
                    uint n
                    )
{
    uint gid = get_global_id(0);
    if (gid >= visCount) return;

    gid = visIndices[gid];
    if (gid >= n) return;

    const uint primitiveFlag = info[gid * infoStride + 2];
    if (isPrimCulled(primitiveFlag))
        return;

    saveOriginalFrozenSet(info, frozenSet, originalFrozenSet, infoStride, gid);

    const uint primitiveOffset = info[gid * infoStride];
    const uint primitiveLength = info[gid * infoStride + 1];

    for(uint i=primitiveOffset; i<primitiveOffset+primitiveLength; ++i) {
        frozenSet[i] = 1.0f;
    }
}
__kernel void invertFrozen(
                    __global const uint* visIndices,
                             const uint  visCount,
                    __global uint*  info,
                    __global float* frozenSet,
                    __global float* originalFrozenSet,
                    uint infoStride,
                    uint n
                    )
{
    uint gid = get_global_id(0);
    if (gid >= visCount) return;

    gid = visIndices[gid];
    if (gid >= n) return;

    const uint primitiveFlag = info[gid * infoStride + 2];
    if (isPrimCulled(primitiveFlag))
        return;

    saveOriginalFrozenSet(info, frozenSet, originalFrozenSet, infoStride, gid);

    const uint primitiveOffset = info[gid * infoStride];
    const uint primitiveLength = info[gid * infoStride + 1];

    for(uint i=primitiveOffset; i<primitiveOffset+primitiveLength; ++i) {
        frozenSet[i] = 1.0f - frozenSet[i];
    }
}

