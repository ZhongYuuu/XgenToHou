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

#define     kFloatEpsilon   1.0e-5f

__kernel void cacheSegLength_kernel(
                    __global const uint* visIndices,
                             const uint  visCount,
                    __global const uint* info,
                    __global float* positions,
                    uint infoStride,
                    uint n,
                    __global float* segLength)
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

    cacheLength(positions + primitiveOffset * 3, primitiveLength, segLength + primitiveOffset);
}

static void grab_noCollision(
            __global float* CVs,
            __global float* falloffs,
            __global float* rttFalloffs,
            __global float* frozenSet,
            __global float* tweaks,
            uint primitiveLength,
            float distance,
            uint invertFrozen,
            int isOrtho,
            float4 cameraPos,
            float4 sculptDir,
            float tweakWeight
            )
{
    for(uint i=1; i<primitiveLength; ++i) {
        float4 offset;
        float4 p = (float4)(CVs[i*3], CVs[i*3+1], CVs[i*3+2], 1.0f);
        if(isgreater(falloffs[i], 0.0f) && islessequal(falloffs[i], 1.0f)) {
            float frozen = invertFrozen ? 1.0f - frozenSet[i] : frozenSet[i];

            if (!isOrtho) {
                float dist = length(cameraPos-p);
                float mag = dist / distance;
                
                offset = mag * falloffs[i] * rttFalloffs[i] * frozen * sculptDir;
            }
            else {
                offset = falloffs[i] * rttFalloffs[i] * frozen * sculptDir;
            }

            tweaks[i*3] = tweaks[i*3] + offset.x;
            tweaks[i*3+1] = tweaks[i*3+1] +  offset.y;
            tweaks[i*3+2] = tweaks[i*3+2] +  offset.z;

            CVs[i*3] = CVs[i*3] + offset.x * tweakWeight;
            CVs[i*3+1] = CVs[i*3+1] + offset.y * tweakWeight;
            CVs[i*3+2] = CVs[i*3+2] + offset.z * tweakWeight;
        }
    }
}

static void grab_withCollision(
            __global float* CVs,
            __global float* falloffs,
            __global float* rttFalloffs,
            __global float* frozenSet,
            __global float* tweaks,
            uint invertFrozen,
            uint primitiveLength,
            float distance,
            int isOrtho,
            float4 cameraPos,
            float4 sculptDir,
            float tweakWeight,
            float minVoxelDist,
            float8 collisionImageWorldBB,
            uint4  collisionImageDim,
            __read_only image3d_t collisionImage)
{
    for(uint i=1; i<primitiveLength; ++i) {
        float4 offset;
        float4 p = (float4)(CVs[i*3], CVs[i*3+1], CVs[i*3+2], 1.0f);
        if(isgreater(falloffs[i], 0.0f) && islessequal(falloffs[i], 1.0f)) {
            float frozen = invertFrozen ? 1.0f - frozenSet[i] : frozenSet[i];

            if (!isOrtho) {
                float dist = length(cameraPos-p);
                float mag = dist / distance;
                offset = mag * falloffs[i] * rttFalloffs[i] * frozen * sculptDir;
            }
            else {
                offset = falloffs[i] * rttFalloffs[i] * frozen * sculptDir;
            }

            p = p + offset * tweakWeight;
            
            float4 newP = p;
            if(isnotequal(frozen, 0.0f)) {
                newP = collidedPosition(p, collisionImageWorldBB, collisionImageDim, minVoxelDist, collisionImage);
                if (isnotequal(newP.x, p.x) || isnotequal(newP.y, p.y) || isnotequal(newP.z, p.z)) {
                    offset.x = newP.x - CVs[i*3];
                    offset.y = newP.y - CVs[i*3+1];
                    offset.z = newP.z - CVs[i*3+2];
                }
            }
            tweaks[i*3] = tweaks[i*3] + offset.x;
            tweaks[i*3+1] = tweaks[i*3+1] +  offset.y;
            tweaks[i*3+2] = tweaks[i*3+2] +  offset.z;

            CVs[i*3] = newP.x;
            CVs[i*3+1] = newP.y;
            CVs[i*3+2] = newP.z;
        }
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

__kernel void grab_noCollision_kernel(
                    __global const uint* visIndices,
                             const uint  visCount,
                    __global uint*  info,
                    __global float* positions,
                    __global float* falloffs,
                    __global float* rttFalloffs,
                    __global float* frozenSet,
                    __global float* tweaks,
                    __global float* originalTweaks,
                    __global float* masks,
                    __global float* segLength,
                    uint infoStride,
                    uint n,
                    float distance,
                    int isOrtho,
                    float4 cameraPos,
                    float4 sculptDir,
                    uint invertFrozen,
                    uint lockLength,
                    float tweakWeight,
                    int isMaskConst
                    )
{
    uint gid = get_global_id(0);
    if (gid >= visCount) return;

    gid = visIndices[gid];
    if (gid >= n) return;

    const uint primitiveFlag = info[gid * infoStride + 2];
    if (isPrimCulled(primitiveFlag))
        return;

    float mask = isMaskConst ? masks[0] : masks[gid];
    tweakWeight *= mask;

    if ( fabs(tweakWeight) < kFloatEpsilon)
        return;

    const uint primitiveOffset = info[gid * infoStride];

    if (falloffs[primitiveOffset] < 0 ) return;
    if (rttFalloffs[primitiveOffset] < 0 ) return;

    saveOriginalTweaks(info, tweaks, originalTweaks, infoStride, gid);

    const uint primitiveLength = info[gid * infoStride + 1];

    grab_noCollision(
        positions + primitiveOffset * 3, falloffs + primitiveOffset, rttFalloffs + primitiveOffset, frozenSet + primitiveOffset, tweaks + primitiveOffset * 3,
        primitiveLength, distance, invertFrozen, isOrtho, cameraPos, sculptDir, tweakWeight);

    if (lockLength){
        calLength_noCollision(
            positions + primitiveOffset * 3, frozenSet + primitiveOffset, primitiveLength, segLength + primitiveOffset, tweaks + primitiveOffset * 3, tweakWeight, invertFrozen);
    }
}


__kernel void grab_withCollision_kernel(
                    __global const uint* visIndices,
                             const uint  visCount,
                    __global uint*  info,
                    __global float* positions,
                    __global float* falloffs,
                    __global float* rttFalloffs,
                    __global float* frozenSet,
                    __global float* tweaks,
                    __global float* originalTweaks,
                    __global float* masks,
                    __global float* segLength,
                    uint infoStride,
                    uint n,
                    float distance,
                    int isOrtho,
                    float4 cameraPos,
                    float4 sculptDir,
                    uint invertFrozen,
                    uint lockLength,
                    float tweakWeight,
                    int isMaskConst,
                    float minVoxelDist,
                    float8 collisionImageWorldBB,
                    uint4  collisionImageDim,
                    __read_only image3d_t collisionImage
                    )
{
    uint gid = get_global_id(0);
    if (gid >= visCount) return;

    gid = visIndices[gid];
    if (gid >= n) return;

    const uint primitiveFlag = info[gid * infoStride + 2];
    if (isPrimCulled(primitiveFlag))
        return;

    float mask = isMaskConst ? masks[0] : masks[gid];
    tweakWeight *= mask;

    if ( fabs(tweakWeight) < kFloatEpsilon)
        return;

    const uint primitiveOffset = info[gid * infoStride];

    if (falloffs[primitiveOffset] < 0 ) return;
    if (rttFalloffs[primitiveOffset] < 0 ) return;

    saveOriginalTweaks(info, tweaks, originalTweaks, infoStride, gid);

    const uint primitiveLength = info[gid * infoStride + 1];

    grab_withCollision(
        positions + primitiveOffset * 3, falloffs + primitiveOffset, rttFalloffs + primitiveOffset, frozenSet + primitiveOffset, tweaks + primitiveOffset * 3,
        invertFrozen, primitiveLength, distance, isOrtho, cameraPos, sculptDir, tweakWeight,
        minVoxelDist, collisionImageWorldBB, collisionImageDim, collisionImage);

    if (lockLength){
        calLength_withCollision(
            positions + primitiveOffset * 3, frozenSet + primitiveOffset, primitiveLength, segLength + primitiveOffset, tweaks + primitiveOffset * 3, tweakWeight, invertFrozen,
            minVoxelDist, collisionImageWorldBB, collisionImageDim, collisionImage);
    }
}
