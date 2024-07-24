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

static void length_core(
			__global float* CVs,
            __global float* falloffs,
            __global float* rttFalloffs,
            __global float* frozenSet,
            __global float* tweaks,
            uint primitiveLength,
            uint invertFrozen,
			float oldScale,
			float newScale
			)
{
	if(!isSelected(falloffs[1])) return;
	const float3 root = vload3(0, CVs);
	const float primfalloff = falloffs[1];
	for(uint i=1; i<primitiveLength; ++i) {
		float3 current = vload3(i, CVs);
        float frozen = invertFrozen ? 1.0f - frozenSet[i] : frozenSet[i];
		const float cvfalloff = primfalloff * rttFalloffs[i] * frozen;
		float oldMultiplier = (oldScale - 1.0f) * cvfalloff + 1.0f;
		float newMultiplier = (newScale - 1.0f) * cvfalloff + 1.0f;
		float3 pt = (current - root) * (newMultiplier / oldMultiplier) + root;
		float3 offset = pt - current;
		
		tweaks[i*3] += offset.x;
		tweaks[i*3+1] += offset.y;
		tweaks[i*3+2] += offset.z;
    }
}

static void length_floating(
            __global float* CVs,
            __global float* falloffs,
            __global float* rttFalloffs,
            __global float* frozenSet,
            __global float* tweaks,
            uint primitiveLength,
            uint invertFrozen,
			float minLength,
			float maxLength,
			float incLength
            )
{
	if(!isSelected(falloffs[1])) return;
	const float3 root = vload3(0, CVs);
	float3 prev = root;
	float hairLength = 0.0f;
	// compute current length
    for(uint i=1; i<primitiveLength; ++i) {
		float3 current = vload3(i, CVs);
		hairLength += fast_distance(prev, current);
		prev = current;
    }
	float targetHairLength = clamp(hairLength + incLength, minLength, maxLength);
	length_core(CVs, falloffs, rttFalloffs, frozenSet, tweaks, primitiveLength, invertFrozen, 1.0f, targetHairLength/hairLength);
}

// Track the unmodified tweaks within the stroke
// NOTE: This function doesn't work in Utils.cl when compiled by NVIDIA driver..
static void saveOriginalTweaks(
    __global uint*  primitiveInfos,
    __global float* tweaks,
    __global float* originalTweaks,
             uint   primitiveInfoStride,
             uint   index
)
{
    // Skip if the primitive is already marked as Modified
    if (!isFlagSet(primitiveInfos, primitiveInfoStride, index, kModified))
    {
        // The primitive is not modified yet. Mark it as modified.
        setFlags(primitiveInfos, primitiveInfoStride, index, kModified, true);

        // Copy the original vertex data
        const uint offset = primitiveInfos[index * primitiveInfoStride];
        const uint length = primitiveInfos[index * primitiveInfoStride + 1];
        for (uint i = 0; i < length; i++)
        {
            vstore3(vload3(offset + i, tweaks), offset + i, originalTweaks);
        }
    }
}

__kernel void length_floating_kernel(
                    __global const uint* visIndices,
                             const uint  visCount,
                    __global uint* info,
                    __global float* positions,
                    __global float* falloffs,
                    __global float* rttFalloffs,
                    __global float* frozenSet,
                    __global float* tweaks,
                    __global float* originalTweaks,
                    uint infoStride,
                    uint n,
                    uint invertFrozen,
					float minLength,
					float maxLength,
					float incLength)
{
    uint gid = get_global_id(0);
    if (gid >= visCount) return;

    gid = visIndices[gid];
    if (gid >= n) return;

	const uint primitiveFlag = info[gid * infoStride + 2];
    if (isPrimCulled(primitiveFlag))
        return;

    const uint primitiveOffset = info[gid * infoStride];

    if (falloffs[primitiveOffset] < 0 ) return;
	
	saveOriginalTweaks(info, tweaks, originalTweaks, infoStride, gid);

    const uint primitiveLength = info[gid * infoStride + 1];

    length_floating(
        positions + primitiveOffset * 3, 
        falloffs + primitiveOffset, 
        rttFalloffs + primitiveOffset,
        frozenSet + primitiveOffset,
        tweaks + primitiveOffset * 3,
        primitiveLength,
        invertFrozen,
		minLength,
		maxLength,
		incLength
		);
}

__kernel void length_locked_kernel(
                    __global const uint* visIndices,
                             const uint  visCount,
                    __global uint* info,
                    __global float* positions,
                    __global float* falloffs,
                    __global float* rttFalloffs,
                    __global float* frozenSet,
                    __global float* tweaks,
                    __global float* originalTweaks,
                    uint infoStride,
                    uint n,
                    uint invertFrozen,
					float minLength,
					float maxLength,
					float oldScaleFactor,
					float newScaleFactor
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

    if (falloffs[primitiveOffset] < 0 ) return;
	
	saveOriginalTweaks(info, tweaks, originalTweaks, infoStride, gid);

    const uint primitiveLength = info[gid * infoStride + 1];

    length_core(
        positions + primitiveOffset * 3, 
        falloffs + primitiveOffset, 
        rttFalloffs + primitiveOffset,
        frozenSet + primitiveOffset,
        tweaks + primitiveOffset * 3,
        primitiveLength,
        invertFrozen,
		oldScaleFactor,
		newScaleFactor
		);
}