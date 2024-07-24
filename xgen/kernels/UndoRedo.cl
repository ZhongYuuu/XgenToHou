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

#define REDUCE_LOCAL_SIZE 16

// Count the number of modified primitives and points
__kernel void countModified(
    __global            uint*   primitiveInfos,
                        uint    primitiveInfoStride,
                        uint    primitiveCount,
    __global volatile   uint*   counts,
                        uint    countPrimitiveOffset,
                        uint    countPointOffset,
                        uint    countIndex
)
{
    // Primitive Id
    const uint gid = get_global_id(0);
    const uint tid = get_local_id(0);

    // Reduce lock contention by using local memory
    __local volatile uint localPrimitiveCount[REDUCE_LOCAL_SIZE];
    __local volatile uint localPointCount    [REDUCE_LOCAL_SIZE];

    // Thread 0 to initialize local memory
    //? if (tid < REDUCE_LOCAL_SIZE) localPrimitiveCount[gid] = 0;
    //? if (tid < REDUCE_LOCAL_SIZE) localPointCount[gid] = 0;
    if (tid == 0)
    {
        for (uint i = 0; i < REDUCE_LOCAL_SIZE; i++)
        {
            localPrimitiveCount[i] = 0;
            localPointCount[i]     = 0;
        }
    }
    barrier(CLK_LOCAL_MEM_FENCE);

    if (gid >= primitiveCount) return;

    // Count the number of modified primitives and points into local memory
    if (isFlagSet(primitiveInfos, primitiveInfoStride, gid, kModified))
    {
        // Found one modified primitive
        const uint one = 1;
        atomic_add(&localPrimitiveCount[gid % REDUCE_LOCAL_SIZE], one);

        // Add the number of points
        const uint length = primitiveInfos[gid * primitiveInfoStride + 1];
        atomic_add(&localPointCount[gid % REDUCE_LOCAL_SIZE], length);
    }
    barrier(CLK_LOCAL_MEM_FENCE);

    // Parallel reduce local memory to global memory
    if (tid == 0)
    {
        // Sum up the local counts
        uint localPrimitiveTotal = 0;
        uint localPointTotal     = 0;
        for (uint i = 0; i < REDUCE_LOCAL_SIZE; i++)
        {
            localPrimitiveTotal += localPrimitiveCount[i];
            localPointTotal     += localPointCount[i];
        }

        // Reduce to global memory
        atomic_add(counts + countPrimitiveOffset + countIndex, localPrimitiveTotal);
        atomic_add(counts + countPointOffset     + countIndex, localPointTotal    );
    }
}

// Build the mappings from original primitives to packed primitives
__kernel void buildVaryingMappings3f(
    __global            uint*   primitiveInfos,
                        uint    primitiveInfoStride,
                        uint    primitiveCount,
    __global            uint*   mappings,
                        uint    mappingStride,
    __global const      float*  varying,
    __global const      float*  originalVarying,
    __global            float*  packedModifiedVarying,
    __global            float*  packedOriginalVarying,
    __global volatile   uint*   counts,
                        uint    countPrimitiveOffset,
                        uint    countPointOffset,
                        uint    countPrimitiveTailOffset,
                        uint    countPointTailOffset,
                        uint    countIndex
)
{
    // Primitive Id
    const uint gid = get_global_id(0);

    if (gid >= primitiveCount) return;
    if (!isFlagSet(primitiveInfos, primitiveInfoStride, gid, kModified)) return;

    // Clear the modified flag
    setFlags(primitiveInfos, primitiveInfoStride, gid, kModified, false);

    // Offset in varying and originalVarying
    const uint offset = primitiveInfos[gid * primitiveInfoStride];
    const uint length = primitiveInfos[gid * primitiveInfoStride + 1];

    // Offset in mappings
    const uint mappingId = atomic_add(counts + countPrimitiveTailOffset + countIndex, 1u);

    // Offset in packedModifiedVarying and packedOriginalVarying
    const uint packedOffset = atomic_add(counts + countPointTailOffset + countIndex, length);

    // Set the mappings
    mappings[mappingId * mappingStride]     = offset;
    mappings[mappingId * mappingStride + 1] = packedOffset;
    mappings[mappingId * mappingStride + 2] = length;

    // Copy the points
    for (uint i = 0; i < length; i++)
    {
        vstore3(vload3(offset + i, varying),         packedOffset + i, packedModifiedVarying);
        vstore3(vload3(offset + i, originalVarying), packedOffset + i, packedOriginalVarying);
    }
}

// Copy the packed primitives to current primitives
__kernel void copyMappedVarying3f(
    __global const      uint*   mappings,
                        uint    mappingStride,
                        uint    primitiveCount,
    __global const      float*  packedVarying,
    __global            float*  varying
)
{
    // Primitive Id
    const uint gid = get_global_id(0);
    if (gid >= primitiveCount) return;

    // Mappings from packed to current
    const uint offset       = mappings[gid * mappingStride];
    const uint packedOffset = mappings[gid * mappingStride + 1];
    const uint length       = mappings[gid * mappingStride + 2];

    // Copy the points
    for (uint i = 0; i < length; i++)
    {
        vstore3(vload3(packedOffset + i, packedVarying), offset + i, varying);
    }
}


// Build the mappings from original primitives to packed primitives
__kernel void buildVaryingMappingsf(
    __global            uint*   primitiveInfos,
                        uint    primitiveInfoStride,
                        uint    primitiveCount,
    __global            uint*   mappings,
                        uint    mappingStride,
    __global const      float*  varying,
    __global const      float*  originalVarying,
    __global            float*  packedModifiedVarying,
    __global            float*  packedOriginalVarying,
    __global volatile   uint*   counts,
                        uint    countPrimitiveOffset,
                        uint    countPointOffset,
                        uint    countPrimitiveTailOffset,
                        uint    countPointTailOffset,
                        uint    countIndex
)
{
    // Primitive Id
    const uint gid = get_global_id(0);

    if (gid >= primitiveCount) return;
    if (!isFlagSet(primitiveInfos, primitiveInfoStride, gid, kModified)) return;

    // Clear the modified flag
    setFlags(primitiveInfos, primitiveInfoStride, gid, kModified, false);

    // Offset in varying and originalVarying
    const uint offset = primitiveInfos[gid * primitiveInfoStride];
    const uint length = primitiveInfos[gid * primitiveInfoStride + 1];

    // Offset in mappings
    const uint mappingId = atomic_add(counts + countPrimitiveTailOffset + countIndex, 1u);

    // Offset in packedModifiedVarying and packedOriginalVarying
    const uint packedOffset = atomic_add(counts + countPointTailOffset + countIndex, length);

    // Set the mappings
    mappings[mappingId * mappingStride]     = offset;
    mappings[mappingId * mappingStride + 1] = packedOffset;
    mappings[mappingId * mappingStride + 2] = length;

    // Copy the points
    for (uint i = 0; i < length; i++)
    {
        packedModifiedVarying[packedOffset + i] = varying[offset + i];
        packedOriginalVarying[packedOffset + i] = originalVarying[offset + i];
    }
}

__kernel void copyMappedVaryingf(
    __global const      uint*   mappings,
                        uint    mappingStride,
                        uint    primitiveCount,
    __global const      float*  packedVarying,
    __global            float*  varying
)
{
    // Primitive Id
    const uint gid = get_global_id(0);
    if (gid >= primitiveCount) return;

    // Mappings from packed to current
    const uint offset       = mappings[gid * mappingStride];
    const uint packedOffset = mappings[gid * mappingStride + 1];
    const uint length       = mappings[gid * mappingStride + 2];

    // Copy the points
    for (uint i = 0; i < length; i++)
    {
        varying[offset + i] = packedVarying[packedOffset + i];
    }

}
