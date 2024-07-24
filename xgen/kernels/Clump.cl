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


// Calculate the number of affected primitives
// Sum the i'th CV for every affected primitive, and put the result to sumBuffer[i]
// 
// The values will be added to the global buffer:
// The first item is used to store the primitive count.
// The remaining items are for the position sum.
__kernel void clump_attr_sum(
                            __global float* CVs,
                            __global const uint* visIndices,
                                     const uint  visCount,
                            __global const uint* primitiveInfos,
                            __global float* falloffs,
                            uint primitiveInfoStride,
                            uint primitiveNum,
                            __global volatile float* sumBuffer)
{
    uint gid = get_global_id(0);
    if (gid >= visCount) return;

    gid = visIndices[gid];
    if (gid >= primitiveNum) return;

    const uint primitiveFlag = primitiveInfos[gid * primitiveInfoStride + 2];
    if (isPrimCulled(primitiveFlag))
        return;

    const uint primitiveOffset = primitiveInfos[gid * primitiveInfoStride];
    const uint cvNum = primitiveInfos[gid * primitiveInfoStride + 1];

    float3 currentCV;
    if ( !isequal(falloffs[primitiveOffset], -1.0f) ) {
        atomicAdd(&sumBuffer[0], 1.0f);

        for(uint i=0; i<cvNum; ++i) {
            currentCV = vload3(primitiveOffset+i, CVs);
            atomicAdd(&sumBuffer[1+3*i], currentCV.x);
            atomicAdd(&sumBuffer[2+3*i], currentCV.y);
            atomicAdd(&sumBuffer[3+3*i], currentCV.z);
        }
    }
}

static void clump_ignore_length(
            __global float* CVs,
            __global float* falloffs,
            __global float* rttFalloffs,
            __global float* frozenSet,
            __global float* tweaks,
            uint begin,
            uint end,
            float clumpWeight,
            uint invertFrozen,
            __global float* sumBuffer
            )
{
    if( (end-begin) < 3) return;

    float3 center;
    float3 current;
    for(uint i=begin; i<end; ++i) {
        if(isSelected(falloffs[i])) {
            current = vload3(i, CVs);
            center.x = sumBuffer[1+3*i]/sumBuffer[0];
            center.y = sumBuffer[2+3*i]/sumBuffer[0];
            center.z = sumBuffer[3+3*i]/sumBuffer[0];
            float ifloat = convert_float_rte( i );
            //float cvWeight = ifloat/(end - begin);
            float frozen = invertFrozen ? 1.0f - frozenSet[i] : frozenSet[i];
            float w = falloffs[i] * (1.0f-rttFalloffs[i]) * frozen * clumpWeight;
            w = clamp(w, 0.0f, 1.0f);
            float3 delta = (center - current)*w;
            float3 p = current + delta;
            float3 t = vload3(i, tweaks) + delta;
            vstore3(t, i, tweaks);
            vstore3(p, i, CVs);
        }
    }

}


//  oldT here is the target point when ignore length
//  oldT = current + (center - current)*w;
//  p is the real target of lockLength
//  alpha = length(current-prevO)/length(oldT-prev)
//  realDelta = p-current 
//            = (p-prev) - (current-prev)
//            = alpha*(oldT-prev) - (current-prev)
//            = alpha*(current+delta-prev)- (current-prev)
//            = alpha*delta + (alpha-1)*(current-prev)
//
//   o oldT
//    \           o current
//     \          |
//      o p       |
//       \        |
//        \       | 
//         \      o prevO (original)
//          \ 
//           o prev

static void clump_keep_length(
            __global float* CVs,
            __global float* falloffs,
            __global float* rttFalloffs,
            __global float* frozenSet,
            __global float* tweaks,
            uint begin,
            uint end,
            float clumpWeight,
            uint invertFrozen,
            __global float* sumBuffer)
{
    if( (end-begin) < 3) return;

    float3 base = vload3(begin, CVs);
    //prev: previous CV that has been modified
    //prev0: previous CV that has not yet 
    float3 prev = base;
    float3 prevO = base;
    float3 center;
    float3 current;
    //skip root point (i=begin), we won't move root position anyway.
    for(uint i=begin + 1; i<end; ++i) {
        if(isSelected(falloffs[i])) {
            current = vload3(i, CVs);
            prev = vload3(i-1, CVs);
            center.x = sumBuffer[1+3*i]/sumBuffer[0];
            center.y = sumBuffer[2+3*i]/sumBuffer[0];
            center.z = sumBuffer[3+3*i]/sumBuffer[0];
            float ifloat = convert_float_rte( i );
            //float cvWeight = ifloat/(end - begin);
            float frozen = invertFrozen ? 1.0f - frozenSet[i] : frozenSet[i];
            float w = falloffs[i] * (1.0f-rttFalloffs[i]) * frozen * clumpWeight;
            w = clamp(w, 0.0f, 1.0f);
            float3 delta = (center - current)*w;

            //handle lock length here
            float3 oldVector = current - prevO;
            float3 newVector = current + delta - prev;
            float3 p = current;

            if ( isgreater(length(newVector), FLT_EPSILON) )
            {
                p = newVector * length(oldVector) / length(newVector) + prev;
            }
            
            prevO = current;
            float3 t = vload3(i, tweaks) + p - current;
            vstore3(t, i, tweaks);
            vstore3(p, i, CVs);
        }
    }

}


static void clump_apply_collision(
            __global float* CVs,
            __global float* tweaks,
            __global float* frozenSet,
            uint cvNum,
            float minVoxelDist,
            float8 collisionImageWorldBB,
            uint4  collisionImageDim,
            __read_only image3d_t collisionImage,
            uint invertFrozen)
{
    float3 prev = vload3(0, CVs);
    for(uint i=1; i<cvNum; ++i) {
        float3 current = vload3(i, CVs);
        float frozen = invertFrozen ? 1.0f - frozenSet[i] : frozenSet[i];
        if(isnotequal(frozen, 0.0f)) {
            float3 oldDiff = current - prev;
            float4 p = (float4)(current.xyz, 1.0f);
            p = collidedPosition(p, collisionImageWorldBB, collisionImageDim, minVoxelDist, collisionImage);
            float3 newDiff = p.xyz - prev;

            if ( isgreater(length(newDiff), FLT_EPSILON) )
            {
                p.xyz = prev + newDiff * (length(oldDiff) / length(newDiff));
            }
            else
            {
                p.xyz = current;
            }

            float3 t = vload3(i, tweaks) + p.xyz - current;
            vstore3(t, i, tweaks);
            vstore3(p.xyz, i, CVs);
        }
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

static void clump_global(
            __global float* CVs,
            __global float* falloffs,
            __global float* rttFalloffs,
            __global float* frozenSet,
            __global float* tweaks,
            uint cvNum,
            float clumpWeight,
            uint keepLength,
            uint invertFrozen,
            __global float* sumBuffer)
{

    if(keepLength)
        clump_keep_length(CVs, falloffs, rttFalloffs, frozenSet, tweaks, 0, cvNum, clumpWeight, invertFrozen, sumBuffer);
    else
        clump_ignore_length(CVs, falloffs, rttFalloffs, frozenSet, tweaks, 0, cvNum, clumpWeight, invertFrozen, sumBuffer);

}

static void clump_noCollision_global(
            __global float* CVs,
            __global float* falloffs,
            __global float* rttFalloffs,
            __global float* frozenSet,
            __global float* tweaks,
            uint cvNum,
            float clumpWeight,
            uint keepLength,
            uint invertFrozen,
            __global float* sumBuffer)
{

    // In global mode, cvs in the same primitive have the same brush falloff value,
    // Use one of them to see if the primitive is selected
    if(!isSelected(falloffs[1])) return; 

    if( isgreater(clumpWeight, FLT_EPSILON) )
        clump_global(CVs, falloffs, rttFalloffs, frozenSet, tweaks, cvNum, clumpWeight, keepLength, invertFrozen, sumBuffer);

}

__kernel void clump_noCollision_global_kernel(
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
                    uint primitiveNum,
                    float clumpWeight,
                    uint keepCurvLength,
                    uint invertFrozen,
                    __global float* sumBuffer)
{
    uint gid = get_global_id(0);
    if (gid >= visCount) return;

    gid = visIndices[gid];
    if (gid >= primitiveNum) return;

	const uint primitiveFlag = info[gid * infoStride + 2];
    if (isPrimCulled(primitiveFlag))
        return;

    const uint primitiveOffset = info[gid * infoStride];

    if (falloffs[primitiveOffset] < 0 ) return;
    if (rttFalloffs[primitiveOffset] < 0 ) return;

    saveOriginalTweaks(info, tweaks, originalTweaks, infoStride, gid);

    const uint cvNum = info[gid * infoStride + 1];

    clump_noCollision_global(
        positions + primitiveOffset * 3, 
        falloffs + primitiveOffset, 
        rttFalloffs + primitiveOffset,
        frozenSet + primitiveOffset,
        tweaks + primitiveOffset * 3,
        cvNum,
        clumpWeight,
        keepCurvLength,
        invertFrozen,
        sumBuffer);

}

__kernel void clump_withCollision_global_kernel(
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
                    uint primitiveNum,
                    float clumpWeight,
                    uint keepCurvLength,
                    uint invertFrozen,
                    __global float* sumBuffer,
                    float minVoxelDist,
                    float8 collisionImageWorldBB,
                    uint4  collisionImageDim,
                    __read_only image3d_t collisionImage)
{
    uint gid = get_global_id(0);
    if (gid >= visCount) return;

    gid = visIndices[gid];
    if (gid >= primitiveNum) return;

	const uint primitiveFlag = info[gid * infoStride + 2];
    if (isPrimCulled(primitiveFlag))
        return;

    const uint primitiveOffset = info[gid * infoStride];

    if (falloffs[primitiveOffset] < 0 ) return;
    if (rttFalloffs[primitiveOffset] < 0 ) return;

    saveOriginalTweaks(info, tweaks, originalTweaks, infoStride, gid);

    const uint cvNum = info[gid * infoStride + 1];

    clump_noCollision_global(
        positions + primitiveOffset * 3, 
        falloffs + primitiveOffset, 
        rttFalloffs + primitiveOffset,
        frozenSet + primitiveOffset,
        tweaks + primitiveOffset * 3,
        cvNum,
        clumpWeight,
        keepCurvLength,
        invertFrozen,
        sumBuffer);

    clump_apply_collision(
            positions + primitiveOffset * 3,
            tweaks + primitiveOffset * 3,
            frozenSet + primitiveOffset,
            cvNum,
            minVoxelDist,
            collisionImageWorldBB,
            collisionImageDim,
            collisionImage,
            invertFrozen);
}
