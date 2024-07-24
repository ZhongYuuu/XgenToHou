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

static void cut_noRebuild(
            __global float* CVs,
            __global float* falloffs,
            __global float* frozenSet,
            __global float* tweaks,
            uint primitiveLength,
            uint invertFrozen,
			float minLength
            )
{
	float3 prev = vload3(0, CVs);
	float hairLength = 0.0f;
    for(uint i=1; i<primitiveLength; ++i) {
    	float frozen = invertFrozen ? 1.0f - frozenSet[i] : frozenSet[i];
        if(isequal(frozen, 0.0f))
            continue;

		float3 current = vload3(i, CVs);
		// find the cut position
		float w = falloffs[i];
        if(isSelected(w)) {
			// this is going to be the new tip
			float3 pt = prev + (current - prev) * w;
			
			for (; i<primitiveLength; ++i)
			{
				current = vload3(i, CVs);
				if (hairLength + fast_distance(prev, pt) < minLength)
				{
					if (hairLength + fast_distance(prev, current) >= minLength)
					{
						// offset the tip, but still cut this segment
						pt = prev + normalize(current - prev) * (minLength - hairLength);
					}else
					{
						hairLength += fast_distance(prev, current);
						prev = current;
						pt = prev;
						continue;
					}
				}
				
				// compress the primitive by joining the other CVs
				for (uint j=i; j<primitiveLength; j++)
				{
					current = vload3(j, CVs);
					float3 offset = pt - current;
					tweaks[j*3] += offset.x;
					tweaks[j*3+1] += offset.y;
					tweaks[j*3+2] += offset.z;
				}
				break;
			}
			break;
        }
		hairLength += fast_distance(prev, current);
		prev = current;
    }
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

__kernel void cut_noRebuild_kernel(
                    __global const uint* visIndices,
                             const uint  visCount,
                    __global uint* info,
                    __global float* positions,
                    __global float* falloffs,
                    __global float* frozenSet,
                    __global float* tweaks,
                    __global float* originalTweaks,
                    uint infoStride,
                    uint n,
                    uint invertFrozen,
					float minLength)
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

    cut_noRebuild(
        positions + primitiveOffset * 3, 
        falloffs + primitiveOffset, 
        frozenSet + primitiveOffset,
        tweaks + primitiveOffset * 3,
        primitiveLength,
        invertFrozen,
		minLength
		);
}