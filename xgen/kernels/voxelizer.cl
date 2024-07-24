#define     kFloatEpsilon   1.0e-5f

static float calDistance(
    __global float* inSamples,
    __global float* inNormals,
    float4 inThisCenter,
    int toBias
    )
{
    const int toBiasPoint = toBias * 3;
    float4 toP = (float4)(inSamples[toBiasPoint], inSamples[toBiasPoint + 1], inSamples[toBiasPoint + 2], 0.0f);
    float4 normal = (float4)(inNormals[toBiasPoint], inNormals[toBiasPoint + 1], inNormals[toBiasPoint + 2], 0.0f);
    float4 toVec = toP - inThisCenter;
    const float dist = fast_length(toVec);
    return (dot(normal, toVec) > 0.0f) ? -dist : dist;
}

static void checkToUpdateDist(
    __global float* inSamples,
    __global int*   inSampledCount,
    __global float* inNormals,
    float4 inThisCenter,
    int4 dim, int4 coord,
    bool* anyVoxelVisited,
    bool* distanceUpdated,
    float* finalDist, int* finalTriBias
    )
{
    int bias = mul24(mul24(dim.x, dim.y), coord.z) +
        mul24(dim.x, coord.y) + coord.x;

    *anyVoxelVisited = true;
    if (inSampledCount[bias] > 0){
        // If found a triangled voxel
        float newDist = calDistance(inSamples, inNormals, inThisCenter, bias);
        if (fabs(newDist) < *finalDist){
            *finalDist = newDist;
            *finalTriBias = bias;
            *distanceUpdated = true;
        }
    }
}

__kernel void realizeVoxels(
        __global float* inCenters,
        __global float* inSamples,
        __global int*   inSampledCount,
        __global float* inNormals,
        __global float* outDistances,
        __global float* outVoxelVecs,
        float4 BBMin,
        float4 BBMax,
        int4 dim, int4 cDim,
        __global int* inCoarseRadius
    )
{
    // Get location of this voxel
    const int x = get_global_id(0);
    const int y = get_global_id(1);
    const int z = get_global_id(2);
    const int thisBias = mul24(mul24(dim.x, dim.y),z)+mul24(dim.x, y)+x;

    // If this is a triangled voxel, just simple set distance and vec
    if (inSampledCount[thisBias] > 0){
        outDistances[thisBias] = 0.0f;
        outVoxelVecs[thisBias * 3]   = inNormals[thisBias * 3];
        outVoxelVecs[thisBias * 3+1] = inNormals[thisBias * 3+1];
        outVoxelVecs[thisBias * 3+2] = inNormals[thisBias * 3+2];
        return;
    }

    int expandRadius = 1;
    // If using coarse radius, we can start at a bigger radius
    if (cDim.x > 0){
        const int multiX = (int)(dim.x / cDim.x);
        const int multiY = (int)(dim.y / cDim.y);
        const int multiZ = (int)(dim.z / cDim.z);
        const int multiMin = min(min(multiX, multiY), multiZ);

        int cX = (int)(x / multiX);
        int cY = (int)(y / multiY);
        int cZ = (int)(z / multiZ);

        int coarseR = inCoarseRadius[cDim.x*cDim.y*cZ + cDim.x*cY + cX];
        if (coarseR >= 2){
            expandRadius = (coarseR - 1)*multiMin;
        }
    }

    // Center of current voxel
    const float4 thisCenter = (float4)(
        inCenters[thisBias * 3], inCenters[thisBias * 3 + 1], inCenters[thisBias * 3 + 2],
        0.0f);


    // Now, it is a empty voxel, we need to find the nearest triangle voxel

    float finalDist = FLT_MAX;
    int finalTriBias = 0;

    bool distanceUpdated = false;
    bool anyVoxelVisited = true;
    const int dimMax = max(max(dim.x, dim.y), dim.z);

    // Search the nearest voxel and calculate finalDist
    while (anyVoxelVisited && !distanceUpdated && (expandRadius<(int)dimMax)){
        anyVoxelVisited = false;

        // boundary
        const int2 boundZ = clamp((int2)(z - expandRadius, z + expandRadius), 0, dim.z - 1);
        const int2 boundX = clamp((int2)(x - expandRadius, x + expandRadius), 0, dim.x - 1);
        const int2 boundY_1 = clamp((int2)(y - expandRadius + 1, y + expandRadius - 1), 0, dim.y - 1);
        const int2 boundZ_1 = clamp((int2)(z - expandRadius + 1, z + expandRadius - 1), 0, dim.z - 1);

        // top
        const int topY = y + expandRadius;
        if (topY < (int)dim.y){
            for (int zIt = boundZ.x; zIt <= boundZ.y; ++zIt){
                for (int xIt = boundX.x; xIt <= boundX.y; ++xIt){
                    checkToUpdateDist(inSamples, inSampledCount, inNormals,
                        thisCenter, dim, (int4)(xIt, topY, zIt, 1),
                        &anyVoxelVisited, &distanceUpdated, &finalDist, &finalTriBias);
                }
            }
        }

        // surrounding
        // along y
        for (int yIt = boundY_1.x; yIt <= boundY_1.y; ++yIt){

            // along x
            if (z - expandRadius >= 0){
                for (int xIt = boundX.x; xIt <= boundX.y; ++xIt){
                    checkToUpdateDist(inSamples, inSampledCount, inNormals,
                        thisCenter, dim, (int4)(xIt, yIt, z - expandRadius, 1),
                        &anyVoxelVisited, &distanceUpdated, &finalDist, &finalTriBias);
                }
            }

            if (z + expandRadius < dim.z){
                for (int xIt = boundX.x; xIt <= boundX.y; ++xIt){
                    checkToUpdateDist(inSamples, inSampledCount, inNormals,
                        thisCenter, dim, (int4)(xIt, yIt, z + expandRadius, 1),
                        &anyVoxelVisited, &distanceUpdated, &finalDist, &finalTriBias);
                }
            }

            // along z
            if (x - expandRadius > 0){
                for (int zIt = boundZ_1.x; zIt <= boundZ_1.y; ++zIt){
                    checkToUpdateDist(inSamples, inSampledCount, inNormals,
                        thisCenter, dim, (int4)(x - expandRadius, yIt, zIt, 1),
                        &anyVoxelVisited, &distanceUpdated, &finalDist, &finalTriBias);
                }
            }

            if (x + expandRadius < dim.x){
                for (int zIt = boundZ_1.x; zIt <= boundZ_1.y; ++zIt){
                    checkToUpdateDist(inSamples, inSampledCount, inNormals,
                        thisCenter, dim, (int4)(x + expandRadius, yIt, zIt, 1),
                        &anyVoxelVisited, &distanceUpdated, &finalDist, &finalTriBias);
                }
            }
        }

        // bottom
        const int bottomY = y - expandRadius;
        if (bottomY >= 0){
            for (int zIt = boundZ.x; zIt <= boundZ.y; ++zIt){
                for (int xIt = boundX.x; xIt <= boundX.y; ++xIt){
                    checkToUpdateDist(inSamples, inSampledCount, inNormals,
                        thisCenter, dim, (int4)(xIt, bottomY, zIt, 1),
                        &anyVoxelVisited, &distanceUpdated, &finalDist, &finalTriBias);
                }
            }
        }

        expandRadius += 1;
    }

    // update finalDist
    if (finalDist < 0.0f){
        float4 clampedC = clamp(thisCenter, BBMin, BBMax);
        if (fast_distance(clampedC, thisCenter) > kFloatEpsilon){
            finalDist = fabs(finalDist);
        }
    }
    outDistances[thisBias] = finalDist;

    // Only update toVec for internal voxels
    float4 toVec =
        fast_normalize((float4)(
        inSamples[3 * finalTriBias] - thisCenter.x,
        inSamples[3 * finalTriBias + 1] - thisCenter.y,
        inSamples[3 * finalTriBias + 2] - thisCenter.z,
        0.0f));

    if (finalDist>0.0f){
        toVec *= -1.0f;
    }

    outVoxelVecs[thisBias * 3] = toVec.x;
    outVoxelVecs[thisBias * 3 + 1] = toVec.y;
    outVoxelVecs[thisBias * 3 + 2] = toVec.z;
}

// Downsample "SampledCount" data from size dim*dim*dim to cDim*cDim*cDim
// "dim" should be multiple of "cDim"
__kernel void downsamplingToTriRadius(
    __global int* inSampledCount,
    __global int* outSampledCount,
    int4 dim,
    int4 cDim
    )
{
    const int x = get_global_id(0);
    const int y = get_global_id(1);
    const int z = get_global_id(2);
    const int bias = mul24(mul24(cDim.x, cDim.y),z) + mul24(cDim.x, y) + x;
    outSampledCount[bias] = 0;

    const int multiX = (int)(dim.x / cDim.x);
    const int multiY = (int)(dim.y / cDim.y);
    const int multiZ = (int)(dim.z / cDim.z);
    const int oX = multiX*x;
    const int oY = multiY*y;
    const int oZ = multiZ*z;

    for (int zIt = oZ; zIt < oZ + multiZ;++zIt)
        for (int yIt = oY; yIt < oY + multiY; ++yIt)
            for (int xIt = oX; xIt < oX + multiX; ++xIt){
                if (inSampledCount[dim.x*dim.y*zIt + dim.x*yIt + xIt] > 0){
                    outSampledCount[bias] = 1;
                    return;
                }
            }
}

// Returns true if this voxel is a triangled voxel
// Returns false else
static bool thisIsATriangleVoxel(
    __global int* inSampledCount,
    int4 dim, int x, int y, int z,
    bool* validVoxel
    )
{
    if (x < 0 || x >= dim.x)
        return false;
    if (y < 0 || y >= dim.y)
        return false;
    if (z < 0 || z >= dim.z)
        return false;

    *validVoxel = true;

    int bias = mul24(mul24(dim.x, dim.y), z) +
        mul24(dim.x, y) + x;

    return inSampledCount[bias] > 0;
}

// Evaludate radius for each empty voxel to nearest triangled voxel
__kernel void evaluateRadius(
    __global int* inSampledCount,
    __global int* outRadius,
    int4 dim
    )
{
    const int x = get_global_id(0);
    const int y = get_global_id(1);
    const int z = get_global_id(2);
    const int bias = mul24(mul24(dim.x, dim.y), z) + mul24(dim.x, y) + x;

    outRadius[bias] = 0;
    if (inSampledCount[bias] > 0){
        return;
    }

    int expandRadius = 1;
    bool anyVoxelVisited = true;

    const int dimMax = max(max(dim.x, dim.y), dim.z);

    // Search the nearest triangled voxel
    while (anyVoxelVisited && (expandRadius<dimMax)){
        anyVoxelVisited = false;

        // top
        const int topY = y + expandRadius;
        if (topY < dim.y){
            for (int zIt = z - expandRadius; zIt <= z + expandRadius; ++zIt){
                for (int xIt = x - expandRadius; xIt <= x + expandRadius; ++xIt){
                    if (thisIsATriangleVoxel(inSampledCount, dim, xIt, topY, zIt, &anyVoxelVisited)){
                        outRadius[bias] = expandRadius;
                        return;
                    }
                }
            }
        }

        // surrounding
        // along y
        for (int yIt = y - expandRadius + 1; yIt <= y + expandRadius - 1; ++yIt){
            if (yIt<0 || yIt>dim.y - 1) continue;

            // along x
            for (int xIt = x - expandRadius; xIt <= x + expandRadius; ++xIt){
                if (thisIsATriangleVoxel(inSampledCount, dim, xIt, yIt, z + expandRadius, &anyVoxelVisited)){
                    outRadius[bias] = expandRadius;
                    return;
                }
                if (thisIsATriangleVoxel(inSampledCount, dim, xIt, yIt, z - expandRadius, &anyVoxelVisited)){
                    outRadius[bias] = expandRadius;
                    return;
                }
            }

            // along z
            for (int zIt = z - expandRadius + 1; zIt <= z + expandRadius - 1; ++zIt){
                if (thisIsATriangleVoxel(inSampledCount, dim, x - expandRadius, yIt, zIt, &anyVoxelVisited)){
                    outRadius[bias] = expandRadius;
                    return;
                }
                if (thisIsATriangleVoxel(inSampledCount, dim, x + expandRadius, yIt, zIt, &anyVoxelVisited)){
                    outRadius[bias] = expandRadius;
                    return;
                }
            }
        }

        // bottom
        const int bottomY = y - expandRadius;
        if (bottomY >= 0){
            for (int zIt = z - expandRadius; zIt <= z + expandRadius; ++zIt){
                for (int xIt = x - expandRadius; xIt <= x + expandRadius; ++xIt){
                    if (thisIsATriangleVoxel(inSampledCount, dim, xIt, bottomY, zIt, &anyVoxelVisited)){
                        outRadius[bias] = expandRadius;
                        return;
                    }
                }
            }
        }

        expandRadius += 1;
    }
}


