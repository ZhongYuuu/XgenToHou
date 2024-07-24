#include <XgUtils.cl>

// Scale modifier
// We scale the primitive by scaling the vector from root to each vertex.
//
__kernel void applyScale(
    __global const  uint*   visIndices,
             const  uint    visCount,
    __global const  uint*   primitiveInfos,
             const  uint    primitiveInfoStride,
             const  uint    primitiveCount,
    __global const  float*  positions,
    __global        float*  positionsOut,
    __global const  float*  maskArray,
             const  uint    maskCount,
    __global const  float*  scaleArray,
             const  uint    scaleCount)
{
    uint gid = get_global_id(0);
    if (gid >= visCount) return;

    gid = visIndices[gid];
    if (gid >= primitiveCount) return;

    const uint flag = primitiveInfos[gid * primitiveInfoStride + 2];
    if (isPrimCulled(flag))
        return;

    // Mask and Scale are per-primitive
    const float mask  = clamp((maskCount == primitiveCount) ? maskArray[gid] : maskArray[0], 0.0f, 1.0f);
    const float scale = (scaleCount == primitiveCount) ? scaleArray[gid] : scaleArray[0];

    // Primitive at [offset, offset + length)
    const uint offset = primitiveInfos[gid * primitiveInfoStride];
    const uint length = primitiveInfos[gid * primitiveInfoStride + 1];

    // Get the positions of the root vertex
    const float3 P0 = vload3(offset, positions);

    // Scale the primitive by changing the position of each vertex
    for (uint i = 1; i < length; i++)
    {
        // Get the positions of the i-th vertex
        const float3 Pi = vload3(offset + i, positions);

        // Scale the vector from the root vertex to the current vertex
        const float3 Pout = P0 + (Pi - P0) * mask * scale;

        // Set the final vertex to output
        vstore3(Pout, offset + i, positionsOut);
    }

    // Set the final root vertex
    vstore3(P0, offset, positionsOut);
}

