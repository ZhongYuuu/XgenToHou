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


// Calculate the number of affected primitives, sum their lengths and orientations. 
// 
// The values will be added to the global buffer:
// The first item is used to store the primitive count.
// The second item is for the length sum.
// The last three items is for the orientation sum.
__kernel void smooth_attr_sum(
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

    float3 orient;
    if ( !isequal(falloffs[primitiveOffset], -1.0f) ) {
        atomicAdd(&sumBuffer[0], 1.0f);

        float len = getPrimitiveLength( CVs + primitiveOffset * 3, cvNum);
        atomicAdd(&sumBuffer[1], len);

        // tip - root.
        orient = vload3(primitiveOffset + cvNum - 1, CVs) - vload3(primitiveOffset, CVs);
        atomicAdd(&sumBuffer[2], orient.x);
        atomicAdd(&sumBuffer[3], orient.y);
        atomicAdd(&sumBuffer[4], orient.z);
    }
}

static void smooth_curvature_ignore_length(
            __global float* CVs,
            __global float* falloffs,
            __global float* rttFalloffs,
            __global float* frozenSet,
            __global float* tweaks,
            uint begin,
            uint end,
            float curvWeight,
            uint invertFrozen)
{
    if( (end-begin) < 3) return;

    float3 prev = vload3(begin, CVs);
    float3 current = vload3(begin+1, CVs);

    for(uint i=begin+1; i<end-1; ++i) {

        float3 next = vload3(i+1, CVs);
        if(isSelected(falloffs[i])) {
            float frozen = invertFrozen ? 1.0f - frozenSet[i] : frozenSet[i];
            float w = falloffs[i] * rttFalloffs[i] * frozen * curvWeight;
            w = clamp(w, 0.0f, 1.0f);

            float3 p = current * (1.0f - w) + (next + prev) * w * 0.5f;

            float3 t = vload3(i, tweaks) + p - current;
            vstore3(t, i, tweaks);
            vstore3(p, i, CVs);
        }

        prev = current;
        current = next;
    }
}

static void smooth_curvature_keep_length(
            __global float* CVs,
            __global float* falloffs,
            __global float* rttFalloffs,
            __global float* frozenSet,
            __global float* tweaks,
            uint begin,
            uint end,
            float curvWeight,
            uint invertFrozen
            )
{
    if( (end-begin) < 3) return;

    float3 base = vload3(begin, CVs);
    float3 prev = base;

    float3 oldDir = normalize(vload3(end-1, CVs) - base);

    for(uint i=begin+1; i<end; ++i) {
        float3 current = vload3(i, CVs);

        float frozen = invertFrozen ? 1.0f - frozenSet[i] : frozenSet[i];
        float w = falloffs[i] * rttFalloffs[i] * frozen * curvWeight;
        w = clamp(w, 0.0f, 1.0f);

        float3 oldDiff = current - prev;
        float3 newDiff = oldDir * w + oldDiff * (1.0f - w);
        float3 p = current;

        if ( isgreater(length(newDiff), FLT_EPSILON) )
        {
            p = base + newDiff * (length(oldDiff) / length(newDiff));
        }

        float3 t = vload3(i, tweaks) + p - current;
        vstore3(t, i, tweaks);
        vstore3(p, i, CVs);

        prev = current;
        base = p;
    }
}

static void smooth_curvature_local(
            __global float* CVs,
            __global float* falloffs,
            __global float* rttFalloffs,
            __global float* frozenSet,
            __global float* tweaks,
            uint cvNum,
            float curvWeight,
            uint keepLength,
            uint invertFrozen)
{
    if(keepLength) {
        for(uint i=1; i<cvNum;) {

            if(!isSelected(falloffs[i])) {
                ++i;
                continue;
            }

            // find out affected range 
            uint k = i+1;
            while(k<cvNum && isSelected(falloffs[k])) {
                ++k;
            }

            float3 offset = vload3(k-1, CVs);
            smooth_curvature_keep_length(CVs, falloffs, rttFalloffs, frozenSet, tweaks, i-1, k, curvWeight, invertFrozen);
            offset = vload3(k-1, CVs) - offset;

            // For those CVs which is not affected by the smooth algorithm,
            // but have to be moved as length of the smoothed part is kept.
            for(uint j=k; j<cvNum; ++j) {
                vstore3(vload3(j, tweaks) + offset, j, tweaks);
                vstore3(vload3(j, CVs) + offset, j, CVs);
            }

            i = k;
        } 
    } else {
        smooth_curvature_ignore_length(CVs, falloffs, rttFalloffs, frozenSet, tweaks, 0, cvNum, curvWeight, invertFrozen);
    }
}

static void smooth_apply_collision(
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

__kernel void smooth_noCollision_local_kernel(
                    __global const uint* visIndices,
                             const uint  visCount,
                    __global uint*  info,
                    __global float* positions,
                    __global float* falloffs,
                    __global float* rttFalloffs,
                    __global float* frozenSet,
                    __global float* tweaks,
                    __global float* originalTweaks,
                    uint infoStride,
                    uint primitiveNum,
                    float curvWeight,
                    uint keepCurvLength,
                    uint invertFrozen)
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

    smooth_curvature_local(
            positions + primitiveOffset * 3, 
            falloffs + primitiveOffset, 
            rttFalloffs + primitiveOffset,
            frozenSet + primitiveOffset,
            tweaks + primitiveOffset * 3,
            cvNum,
            curvWeight,
            keepCurvLength,
            invertFrozen);
}

__kernel void smooth_withCollision_local_kernel(
                    __global const uint* visIndices,
                             const uint  visCount,
                    __global uint*  info,
                    __global float* positions,
                    __global float* falloffs,
                    __global float* rttFalloffs,
                    __global float* frozenSet,
                    __global float* tweaks,
                    __global float* originalTweaks,
                    uint infoStride,
                    uint primitiveNum,
                    float curvWeight,
                    uint keepCurvLength,
                    uint invertFrozen,
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

    smooth_curvature_local(
            positions + primitiveOffset * 3, 
            falloffs + primitiveOffset, 
            rttFalloffs + primitiveOffset,
            frozenSet + primitiveOffset,
            tweaks + primitiveOffset * 3,
            cvNum,
            curvWeight,
            keepCurvLength,
            invertFrozen);

    smooth_apply_collision(
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


static void smooth_length_global(
            __global float* CVs,
            __global float* falloffs,
            __global float* rttFalloffs,
            __global float* frozenSet,
            __global float* tweaks,
            uint cvNum,
            float lenWeight,
            float avLength,
            uint invertFrozen)
{

    // In global mode, cvs in the same primitive have the same brush falloff value.
    // Use one of them to calculate the weight.
    float frozen = invertFrozen ? 1.0f - frozenSet[1] : frozenSet[1];
    float lWeight = falloffs[1] * frozen * lenWeight;
    lWeight = clamp(lWeight, 0.0f, 1.0f);

    float currLen = getPrimitiveLength(CVs, cvNum);
    float newLen = currLen * (1.0f - lWeight) + avLength * lWeight;

    float3 prev = vload3(0, CVs);
    float3 base = prev;
    for(uint i=1; i<cvNum; ++i) {
        float3 current = vload3(i, CVs);
        float3 p = current;

        if (currLen != 0)
        {
            p = base + (current - prev) * newLen / currLen;
        }

        float3 t = vload3(i, tweaks) + p - current;
        vstore3(t, i, tweaks);
        vstore3(p, i, CVs);

        base = p;
        prev = current;
    }
}

static void smooth_orientation_global(
            __global float* CVs,
            __global float* falloffs,
            __global float* rttFalloffs,
            __global float* frozenSet,
            __global float* tweaks,
            uint cvNum,
            float orientWeight,
            float3 avOrientation,
            uint invertFrozen)
{
    float3 root = vload3(0, CVs);
    float3 tip = vload3(cvNum-1, CVs);
    float3 currOrient = normalize( tip - root );

    // In global mode, cvs in the same primitive have the same brush falloff value.
    // Use one of them to calculate the weight.
    float frozen = invertFrozen ? 1.0f - frozenSet[1] : frozenSet[1];
    float oWeight = falloffs[1] * frozen * orientWeight; 
    oWeight = clamp(oWeight, 0.0f, 1.0f);

    float3 newOrient = normalize( currOrient * (1.0f - oWeight) + avOrientation * oWeight );

    float3 axis = normalize( cross(currOrient, newOrient) );
    float d = dot(currOrient, newOrient);
    d = clamp( d, -1.0f, 1.0f );
    float angle = acos( d );

    for(uint i=1; i<cvNum; ++i) {

        float3 current = vload3(i, CVs);
        float3 p = current - root;
        p = rotateBy(p, axis, angle * oWeight);
        p = root + p;

        float3 t = vload3(i, tweaks) + p - current;
        vstore3(t, i, tweaks);
        vstore3(p, i, CVs);
    }
}

static void smooth_curvature_global(
            __global float* CVs,
            __global float* falloffs,
            __global float* rttFalloffs,
            __global float* frozenSet,
            __global float* tweaks,
            uint cvNum,
            float curvWeight,
            uint keepLength,
            uint invertFrozen)
{
    if(keepLength)
        smooth_curvature_keep_length(CVs, falloffs, rttFalloffs, frozenSet, tweaks, 0, cvNum, curvWeight, invertFrozen);
    else
        smooth_curvature_ignore_length(CVs, falloffs, rttFalloffs, frozenSet, tweaks, 0, cvNum, curvWeight, invertFrozen);

}

static void smooth_noCollision_global(
            __global float* CVs,
            __global float* falloffs,
            __global float* rttFalloffs,
            __global float* frozenSet,
            __global float* tweaks,
            uint cvNum,
            float lenWeight,
            float orientWeight,
            float curvWeight,
            uint keepLength,
            uint invertFrozen,
            __global float* sumBuffer)
{

    // In global mode, cvs in the same primitive have the same brush falloff value,
    // Use one of them to see if the primitive is selected
    if(!isSelected(falloffs[1])) return; 

    if( isgreater(curvWeight, FLT_EPSILON) )
        smooth_curvature_global(CVs, falloffs, rttFalloffs, frozenSet, tweaks, cvNum, curvWeight, keepLength, invertFrozen);

    if( isgreater(orientWeight, FLT_EPSILON) ) {
        float3 avOrientation = (float3)(sumBuffer[2], sumBuffer[3], sumBuffer[4]);
        avOrientation /= sumBuffer[0];
        smooth_orientation_global(CVs, falloffs, rttFalloffs, frozenSet, tweaks, cvNum, orientWeight, avOrientation, invertFrozen);
    }

    if( isgreater(lenWeight, FLT_EPSILON) )
        smooth_length_global(CVs, falloffs, rttFalloffs, frozenSet, tweaks, cvNum, lenWeight, sumBuffer[1]/sumBuffer[0], invertFrozen);
}

__kernel void smooth_noCollision_global_kernel(
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
                    float lenWeight,
                    float orientWeight,
                    float curvWeight,
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

    smooth_noCollision_global(
        positions + primitiveOffset * 3, 
        falloffs + primitiveOffset, 
        rttFalloffs + primitiveOffset,
        frozenSet + primitiveOffset,
        tweaks + primitiveOffset * 3,
        cvNum,
        lenWeight,
        orientWeight,
        curvWeight,
        keepCurvLength,
        invertFrozen,
        sumBuffer);

}

__kernel void smooth_withCollision_global_kernel(
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
                    float lenWeight,
                    float orientWeight,
                    float curvWeight,
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

    smooth_noCollision_global(
        positions + primitiveOffset * 3, 
        falloffs + primitiveOffset, 
        rttFalloffs + primitiveOffset,
        frozenSet + primitiveOffset,
        tweaks + primitiveOffset * 3,
        cvNum,
        lenWeight,
        orientWeight,
        curvWeight,
        keepCurvLength,
        invertFrozen,
        sumBuffer);

    smooth_apply_collision(
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
