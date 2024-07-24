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

static void saveOriginalWidthPerCV(
    __global uint*  info,
    __global float* widthPerCV,
    __global float* originalWidthPerCV,
    uint   infoStride,
    uint   index
    )
{
    // Skip if the primitive is already marked as Modified
    if (!isFlagSet(info, infoStride, index, kModified))
    {
        // The primitive is not modified yet. Mark it as modified.
        setFlags(info, infoStride, index, kModified, true);

        // Copy the original vertex width data
        const uint offset = info[index * infoStride];
        const uint length = info[index * infoStride + 1];
        for (uint i = offset; i < offset + length; i++)
        {
            originalWidthPerCV[i] = widthPerCV[i];
        }
    }
}

// Falloff ----> width per cv value
__kernel void paintWidth(
    __global const uint* visIndices,
             const uint  visCount,
    __global uint*  info,
    __global const float* falloffs,
    __global const float* rttFalloffs,
    __global const float* frozenSet,
    __global       float* widthPerCV,
    __global       float* originalWidthPerCV,
    uint infoStride,
    uint n,
    uint invertFrozen,
    float minWidth,
    float maxWidth,
    float incWidth)
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

    // Skip the whole spline if not affected
    if (isequal(falloffs[primitiveOffset], -1.0f))
        return;

    // Save original width before changing it
    saveOriginalWidthPerCV(info, widthPerCV, originalWidthPerCV, infoStride, gid);

    // Loop each cv on the spline [1, primitiveLength)
    for (uint i = 1; i < primitiveLength;++i) {
        if (isSelected(falloffs[primitiveOffset + i])) {
            float frozen = invertFrozen ? 1.0f - frozenSet[primitiveOffset + i] : frozenSet[primitiveOffset + i];
            widthPerCV[primitiveOffset + i] =
                clamp(widthPerCV[primitiveOffset + i] +
                    incWidth*falloffs[primitiveOffset + i] * rttFalloffs[primitiveOffset + i] * frozen,
                    minWidth, maxWidth);
        }
    }

    // Special process [0].
    // Since falloffs[0] has no meaningful falloff, reuse from falloffs[1]
    if (isSelected(falloffs[primitiveOffset + 1])) {
        float frozen = invertFrozen ? 1.0f - frozenSet[primitiveOffset] : frozenSet[primitiveOffset];
        widthPerCV[primitiveOffset] =
            clamp(widthPerCV[primitiveOffset] +
                incWidth*falloffs[primitiveOffset + 1] * rttFalloffs[primitiveOffset + 1] * frozen,
                minWidth, maxWidth);
    }
}


// Apply width scale
__kernel void applyWidthScale(
    __global const uint*  info,
    __global const float* widthPerCV_base, // Width with no scales
    __global       float* widthPerCV,      // Width with scales
    uint infoStride,
    uint n,
    __global const float* rampScales,
    float scale,
    float taper,
    float taperStart
    )
{
    uint gid = get_global_id(0);
    if (gid >= n) return;

    const uint primitiveFlag = info[gid * infoStride + 2];
    if (isPrimCulled(primitiveFlag))
        return;

    const uint primitiveOffset = info[gid * infoStride];
    const uint primitiveLength = info[gid * infoStride + 1];

    const float segUVSpan = 1.0f / (primitiveLength - 1);

    for (uint i = 0; i < primitiveLength;++i) {
        // non-taper scale
        float scale1 = scale * rampScales[i];

        // taper scale
        float v = i*segUVSpan;
        float scale2 = (v > taperStart) ? (1.0f - taper*((v - taperStart) / (1.0f - taperStart))) : 1.0f;

        widthPerCV[primitiveOffset + i] = widthPerCV_base[primitiveOffset + i] * scale1 * scale2;
    }
}
