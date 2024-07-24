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

static void part_global(
                         __global float* CVs,
                         __global float* falloffs,
                         __global float* rttFalloffs,
                         __global float* frozenSet,
                         __global float* tweaks,
						 float3 norm,
						 float3 center,
						 float3 dir,
						 float weight,
                         uint cvNum,
                         uint alongStroke,
                         uint invertFrozen)
{
	float3 bp = vload3(0, CVs);
	float3 vec = bp - center;
	float3 axis;
	float3 tmp = normalize(cross(norm, vec)); 
	if(alongStroke)
	{
		axis = dir;
		if(dot(tmp, axis) < 0)
			axis = -axis;
	}
	else
	{
		axis = tmp;
	}
	
	for(uint i=1; i<cvNum; ++i) {
		if(length(normalize(vec)) > 0.0001 )
		{
			float3 p = vload3(i, CVs);
			vec = p - bp;
            float frozen = invertFrozen ? 1.0f - frozenSet[i] : frozenSet[i];
			float angle = 0.0174532 * weight * falloffs[i] * rttFalloffs[i] * frozen;
			vec = rotateBy(vec, axis, angle);
			
			float3 np = bp + vec;
			float3 t = vload3(i, tweaks) + np - p;
			vstore3(t, i, tweaks);
			vstore3(p, i, CVs);
		}
	}
}

static void part_noCollision_global(
                                     __global float* CVs,
                                     __global float* falloffs,
                                     __global float* rttFalloffs,
                                     __global float* frozenSet,
                                     __global float* tweaks,
									 float3 norm,
									 float3 center,
									 float3 dir,
									 float weight,
                                     uint cvNum,
                                     uint alongStroke,
                                     uint invertFrozen)
{
    // In global mode, cvs in the same primitive have the same brush falloff value,
    // Use one of them to see if the primitive is selected
    if(!isSelected(falloffs[1])) return;
    
    part_global(CVs, falloffs, rttFalloffs, frozenSet, tweaks, norm, center, dir, weight, cvNum, alongStroke, invertFrozen);
}

__kernel void part_noCollision_global_kernel(
                                              __global const uint* visIndices,
                                                       const uint  visCount,
                                              __global uint* info,
                                              __global float* positions,
                                              __global float* falloffs,
                                              __global float* rttFalloffs,
                                              __global float* frozenSet,
                                              __global float* tweaks,
                                              __global float* originalTweaks,
											  __global float* normals,
											  float4 center,
											  float3 direction,
											  float weight,
                                              uint infoStride,
                                              uint primitiveNum,
											  uint alongStroke,
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
    const float3 norm = (float3)(normals[gid*3], normals[gid*3+1], normals[gid*3+2]);
	const float3 cp = (float3)(center.xyz);
	const float3 dir = (float3)(direction.xyz);
    if (falloffs[primitiveOffset] < 0 ) return;
    if (rttFalloffs[primitiveOffset] < 0 ) return;
    
    saveOriginalTweaks(info, tweaks, originalTweaks, infoStride, gid);
    
    const uint cvNum = info[gid * infoStride + 1];
    
    part_noCollision_global(
                             positions + primitiveOffset * 3,
                             falloffs + primitiveOffset,
                             rttFalloffs + primitiveOffset,
                             frozenSet + primitiveOffset,
                             tweaks + primitiveOffset * 3,
							 norm,
							 cp,
							 dir,
							 weight,
                             cvNum,
							 alongStroke,
                             invertFrozen);
}

static void part_apply_collision(
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


__kernel void part_withCollision_global_kernel(
                                                __global const uint* visIndices,
                                                         const uint  visCount,
                                                __global uint* info,
                                                __global float* positions,
                                                __global float* falloffs,
                                                __global float* rttFalloffs,
                                                __global float* frozenSet,
                                                __global float* tweaks,
                                                __global float* originalTweaks,
												__global float* normals,
												float4 center,
												float4 direction,
												float weight,
                                                uint infoStride,
                                                uint primitiveNum,
												uint alongStroke,
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
    const float3 norm = (float3)(normals[gid*3], normals[gid*3+1], normals[gid*3+2]);
	const float3 cp = (float3)(center.xyz);
	const float3 dir = (float3)(direction.xyz);
    if (falloffs[primitiveOffset] < 0 ) return;
    if (rttFalloffs[primitiveOffset] < 0 ) return;
    
    saveOriginalTweaks(info, tweaks, originalTweaks, infoStride, gid);
    
    const uint cvNum = info[gid * infoStride + 1];
    
    part_noCollision_global(
                             positions + primitiveOffset * 3, 
                             falloffs + primitiveOffset, 
                             rttFalloffs + primitiveOffset,
                             frozenSet + primitiveOffset,
                             tweaks + primitiveOffset * 3,
							 norm,
							 cp,		
							 dir,
							 weight,
                             cvNum,
							 alongStroke,
                             invertFrozen);
    
    part_apply_collision(
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
