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

static void saveOriginalDirectionPerCV(
    __global uint*  info,
    __global float* directionPerCV,
    __global float* originalDirectionPerCV,
    uint   infoStride,
    uint   index
    )
{
    // Skip if the primitive is already marked as Modified
    if (!isFlagSet(info, infoStride, index, kModified))
    {
        // The primitive is not modified yet. Mark it as modified.
        setFlags(info, infoStride, index, kModified, true);

        // Copy the original vertex Direction data
        const uint offset = info[index * infoStride];
        const uint length = info[index * infoStride + 1];
		for (uint i = 0; i < length; i++)
        {
			vstore3(vload3(offset + i, directionPerCV), offset + i, originalDirectionPerCV);
        }
    }
}

static void AdjustDirectionPerCV(
	__global float* directionPerCV,
	uint   primitiveCount,
    uint   primitiveOffset,
    uint   i,
	uint primitiveLength,
	float frozen,
	uint alignToSurface)
{
	if (alignToSurface == 1 && (frozen > FLT_EPSILON) && i == primitiveLength -1 && i > 0)
	{
		float coeffect = 0.0f;
		for (int cvIndex = 1; cvIndex <= primitiveLength -1; cvIndex++)
		{
			uint float3OffsetPre = primitiveOffset * 3 + cvIndex * 3 - 3;
			float3 directionCVPre =  (float3)(directionPerCV[float3OffsetPre], directionPerCV[float3OffsetPre + 1], directionPerCV[float3OffsetPre + 2]);
			
			uint float3OffsetCurrent = primitiveOffset * 3 + cvIndex * 3;
			float3 directionCV =  (float3)(directionPerCV[float3OffsetCurrent], directionPerCV[float3OffsetCurrent + 1], directionPerCV[float3OffsetCurrent + 2]);
			float sign = dot(directionCVPre, directionCV);
			if (sign < 0)
			{
				directionPerCV[float3OffsetCurrent] = - directionPerCV[float3OffsetCurrent];
				directionPerCV[float3OffsetCurrent + 1] = - directionPerCV[float3OffsetCurrent + 1];
				directionPerCV[float3OffsetCurrent + 2] = - directionPerCV[float3OffsetCurrent + 2];
				coeffect = coeffect - 1.0f;
			}
			else
			{
				coeffect = coeffect + 1.0f;
			}
		}
		
		if (coeffect < 0.0f)
		{
			for (int cvIndex = 0; cvIndex <= primitiveLength -1; cvIndex++)
			{	
				uint float3OffsetCurrent = primitiveOffset * 3 + cvIndex * 3;
				
				directionPerCV[float3OffsetCurrent] = - directionPerCV[float3OffsetCurrent];
				directionPerCV[float3OffsetCurrent + 1] = - directionPerCV[float3OffsetCurrent + 1];
				directionPerCV[float3OffsetCurrent + 2] = - directionPerCV[float3OffsetCurrent + 2];
			}
		}
	}
}

static void rotateDirectionPerCV(
	__global uint*  info,
    __global float* positions,
	__global float* directionPerCV,
	__global const float* falloffs,
	__global const float* rttFalloffs,
	__global 	   float* meshN,
	uint   gid,
	uint   infoStride,
	uint   primitiveCount,
    uint   primitiveOffset,
    uint   i,
	uint primitiveLength,
	float frozen,
	float incDirection,
	uint alignToSurface,
	uint localSelection,
	uint hitSurface,
	float3 hitNormal
    )
{
    uint float3Offset = primitiveOffset * 3 + i * 3;
	
	float3 directionCV =  (float3)(directionPerCV[float3Offset], directionPerCV[float3Offset + 1], directionPerCV[float3Offset + 2]);
	float3 splineDirection;
	if (i == primitiveLength -1 && i > 0)
	{
		uint float3OffsetPre = primitiveOffset * 3 + i * 3 - 3;
		float3 positionCV = (float3)(positions[float3Offset], positions[float3Offset + 1], positions[float3Offset + 2]);
		float3 positionCVPre = (float3)(positions[float3OffsetPre], positions[float3OffsetPre + 1], positions[float3OffsetPre + 2]);
		splineDirection = positionCV - positionCVPre;
	}
	else
	{
		uint float3OffsetNext = primitiveOffset * 3 + i * 3 + 3;
		float3 positionCV = (float3)(positions[float3Offset], positions[float3Offset + 1], positions[float3Offset + 2]);
		float3 positionCVNext = (float3)(positions[float3OffsetNext], positions[float3OffsetNext + 1], positions[float3OffsetNext + 2]);
		splineDirection = positionCVNext - positionCV;
	}
	
	float angle = incDirection*falloffs[primitiveOffset + i] * rttFalloffs[primitiveOffset + i] * frozen;
	if (i == 0)
	{
		angle = incDirection*falloffs[primitiveOffset + 1] * rttFalloffs[primitiveOffset + 1] * frozen;
	}
	
	splineDirection = normalize(splineDirection);
	directionCV = normalize(directionCV);
	float3 newdirectionCV = directionCV;
	if (alignToSurface == 1 && (frozen > FLT_EPSILON))
	{
		float3 rootNormal =  (float3)(meshN[gid*3], meshN[gid*3+1], meshN[gid*3+2]);
		if (localSelection == 1)
		{
			if (hitSurface == 0)
			{
				return;
			}
			rootNormal = hitNormal;
		}
		else if (i > 0)
		{
			float3 positionCV = (float3)(positions[float3Offset], positions[float3Offset + 1], positions[float3Offset + 2]);
			float3 currentRootPositionCV = (float3)(positions[primitiveOffset * 3], positions[primitiveOffset * 3 + 1], positions[primitiveOffset * 3 + 2]);
			float minDistance = length(currentRootPositionCV - positionCV);
			uint sampleNumberMax = 64 ;
			if (primitiveCount > sampleNumberMax)
			{
				uint sampleStep = primitiveCount / sampleNumberMax;
				for (uint primitiveIndex = 0; primitiveIndex < sampleNumberMax;++primitiveIndex) 
				{
					uint sampleIndex = primitiveIndex * sampleStep;
					const uint aRootPrimitiveOffset = info[sampleIndex * infoStride];
					uint aRootFloat3Offset = aRootPrimitiveOffset * 3;
					float3 aRootPositionCV = (float3)(positions[aRootFloat3Offset], positions[aRootFloat3Offset + 1], positions[aRootFloat3Offset + 2]);
					float distance = length(aRootPositionCV - positionCV);
					if (minDistance > distance)
					{
						minDistance = distance;
						rootNormal = (float3)(meshN[sampleIndex*3], meshN[sampleIndex*3+1], meshN[sampleIndex*3+2]);
					}
				}
			}
			else
			{
				for (uint primitiveIndex = 0; primitiveIndex < primitiveCount;++primitiveIndex) 
				{
					const uint aRootPrimitiveOffset = info[primitiveIndex * infoStride];
					uint aRootFloat3Offset = aRootPrimitiveOffset * 3;
					float3 aRootPositionCV = (float3)(positions[aRootFloat3Offset], positions[aRootFloat3Offset + 1], positions[aRootFloat3Offset + 2]);
					float distance = length(aRootPositionCV - positionCV);
					if (minDistance > distance)
					{
						minDistance = distance;
						rootNormal = (float3)(meshN[primitiveIndex*3], meshN[primitiveIndex*3+1], meshN[primitiveIndex*3+2]);
					}
				}
			}
		}
		
		newdirectionCV = cross(splineDirection, rootNormal);
		if (i > 0)
		{
			uint float3OffsetPre = primitiveOffset * 3 + i * 3 - 3;
			float3 directionCVPre =  (float3)(directionPerCV[float3OffsetPre], directionPerCV[float3OffsetPre + 1], directionPerCV[float3OffsetPre + 2]);
			
			// if normal and spline have same direction, use previous direction directly.
			if (length(newdirectionCV) < 0.1f)
			{
				newdirectionCV = directionCVPre;
			}
		}
	}
	else	
	{
		newdirectionCV = rotateBy(directionCV, splineDirection, angle);
	}
	
	if (length(newdirectionCV) < 0.1f)
	{
		return;
	}
	newdirectionCV = normalize(newdirectionCV);
	if (length(newdirectionCV) < 0.1f)
	{
		return;
	}
	directionPerCV[float3Offset] = newdirectionCV.x;
	directionPerCV[float3Offset + 1] = newdirectionCV.y;
	directionPerCV[float3Offset + 2] = newdirectionCV.z;
	
	AdjustDirectionPerCV(directionPerCV, primitiveCount, primitiveOffset, i, primitiveLength, frozen, alignToSurface);
}

// Falloff ----> Direction per cv value
__kernel void paintDirection(
    __global const uint* visIndices,
             const uint  visCount,
    __global uint*  info,
	__global float* positions,
    __global const float* falloffs,
    __global const float* rttFalloffs,
	__global const float* selectionSet,
	__global 	   float* meshN,
    __global const float* frozenSet,
    __global       float* directionPerCV,
    __global       float* originalDirectionPerCV,
    uint infoStride,
    uint n,
    uint invertFrozen,
	uint alignToSurface,
	uint selectionOnly,
	uint localSelection,
	uint hitSurface,
	float minDirection,
    float maxDirection,
    float incDirection,
	float hitNormalX,
	float hitNormalY,
	float hitNormalZ)
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
		
	if (incDirection < minDirection)
	{
		incDirection = minDirection;
	}
	
	if (incDirection > maxDirection)
	{
		incDirection = maxDirection;
	}
	
	float3 hitNormal = (float3)(hitNormalX, hitNormalY, hitNormalZ);

    // Save original Direction before changing it
    saveOriginalDirectionPerCV(info, directionPerCV, originalDirectionPerCV, infoStride, gid);
	
	// Special process [0].
    // Since falloffs[0] has no meaningful falloff, reuse from falloffs[1]
    if (isSelected(falloffs[primitiveOffset + 1])) {
		if (!selectionOnly || (selectionOnly && getSelectFlag(selectionSet[primitiveOffset + 1], SELECT_MASK_SELECTED)))
		{
			float frozen = invertFrozen ? 1.0f - frozenSet[primitiveOffset] : frozenSet[primitiveOffset];
			rotateDirectionPerCV(info, positions, directionPerCV, falloffs, rttFalloffs, meshN, gid, infoStride, n, primitiveOffset, 0, primitiveLength, frozen, incDirection, alignToSurface, localSelection, hitSurface, hitNormal);
		}
    }
	
    // Loop each cv on the spline [1, primitiveLength)
    for (uint i = 1; i < primitiveLength;++i) {
        if (isSelected(falloffs[primitiveOffset + i])) 
		{
			if (!selectionOnly || (selectionOnly && getSelectFlag(selectionSet[primitiveOffset + i], SELECT_MASK_SELECTED)))
			{
				float frozen = invertFrozen ? 1.0f - frozenSet[primitiveOffset + i] : frozenSet[primitiveOffset + i];
				rotateDirectionPerCV(info, positions, directionPerCV, falloffs, rttFalloffs, meshN, gid, infoStride, n, primitiveOffset, i, primitiveLength, frozen, incDirection, alignToSurface, localSelection, hitSurface, hitNormal);	
			}
        }
    }
}


// Apply Direction scale
__kernel void applyDirectionScale(
    __global const uint* visIndices,
             const uint  visCount,
    __global const uint*  info,
    __global const float* directionPerCV_base, // Direction with no scales
    __global       float* directionPerCV,      // Direction with scales
    uint infoStride,
    uint n,
    __global const float* rampScales,
    float scale,
    float taper,
    float taperStart
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

    const float segUVSpan = 1.0f / (primitiveLength - 1);

    for (uint i = 0; i < primitiveLength;++i) {
        // non-taper scale
        float scale1 = scale * rampScales[i];

        // taper scale
        float v = i*segUVSpan;
        float scale2 = (v > taperStart) ? (1.0f - taper*((v - taperStart) / (1.0f - taperStart))) : 1.0f;

        directionPerCV[primitiveOffset + i] = directionPerCV_base[primitiveOffset + i] * scale1 * scale2;
    }
}
