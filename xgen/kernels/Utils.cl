// =======================================================================
// Copyright 2015 Autodesk, Inc. All rights reserved.
//
// This computer source code and related instructions and comments are the
// unpublished confidential  and proprietary information of Autodesk, Inc.
// and are protected under applicable copyright and trade secret law. They 
// may not be disclosed to, copied  or used by any third party without the 
// prior written consent of Autodesk, Inc.
// =======================================================================

#include <XgUtils.cl>

// Primitive Info Flags
//
#define kModified       0x1         // Modified within the stroke

// Returns true if any of the specified flags is set for the primitive
static bool isFlagSet(
    __global const  uint*   primitiveInfos,
                    uint    primitiveInfoStride,
                    uint    index,
                    uint    flag
)
{
    const uint flagOffset = index * primitiveInfoStride + 2;
    return (primitiveInfos[flagOffset] & flag) != 0;
}

// Set the specified flags for the primitive
static void setFlags(
    __global uint*  primitiveInfos,
             uint   primitiveInfoStride,
             uint   index,
             uint   flags,
             bool   set
)
{
    const uint flagOffset = index * primitiveInfoStride + 2;
    if (set)
        primitiveInfos[flagOffset] = (primitiveInfos[flagOffset] | flags);
    else
        primitiveInfos[flagOffset] = (primitiveInfos[flagOffset] & (~flags));
}

static void cacheLength(
                __global float* CVs, 
                uint primitiveLength,
                __global float* segLength)
{
    float4 pnt, newPnt;
    pnt = (float4)(CVs[0], CVs[1], CVs[2], 1.0f);
    for(uint i=1; i<primitiveLength; ++i) {
        newPnt = (float4)(CVs[i*3], CVs[i*3+1], CVs[i*3+2], 1.0f);
        segLength[i] = length(newPnt - pnt);
        pnt = newPnt;
    }
}

static float4 collidedPosition(
            float4 p,
            float8 BB,
            uint4  Dim,
            float minVoxelDist,
            __read_only image3d_t img)
{
    // BB[] = {minX, maxX, minY, maxY, minZ, maxZ};
    if (p.x<=BB.s0 || p.x>=BB.s1) return p;
    if (p.y<=BB.s2 || p.y>=BB.s3) return p;
    if (p.z<=BB.s4 || p.z>=BB.s5) return p;

    const float sX = (p.x - BB.s0) / ((BB.s1-BB.s0) / Dim.x);
    const float sY = (p.y - BB.s2) / ((BB.s3-BB.s2) / Dim.y);
    const float sZ = (p.z - BB.s4) / ((BB.s5-BB.s4) / Dim.z);

    const sampler_t sampler = CLK_FILTER_LINEAR|CLK_ADDRESS_CLAMP;
    const float bias = 1.0f;
    float4 pixel = read_imagef(img, sampler, (float4)(sX, sY, sZ, 1.0f));
    pixel += read_imagef(img, sampler, (float4)(sX-bias, sY, sZ, 1.0f));
    pixel += read_imagef(img, sampler, (float4)(sX+bias, sY, sZ, 1.0f));
    pixel += read_imagef(img, sampler, (float4)(sX, sY-bias, sZ, 1.0f));
    pixel += read_imagef(img, sampler, (float4)(sX, sY+bias, sZ, 1.0f));
    pixel += read_imagef(img, sampler, (float4)(sX, sY, sZ-bias, 1.0f));
    pixel += read_imagef(img, sampler, (float4)(sX, sY, sZ+bias, 1.0f));
    pixel /= 7.0f;

    if (pixel.w >= minVoxelDist){
        return p;
    }
    else{
        return p + pixel*(minVoxelDist - pixel.w);
    }
}

static void calLength_noCollision(
                __global float* CVs,
                __global float* frozenSet,
                uint primitiveLength,
                __global float* segLength,
                __global float* tweaks,
                float tweakWeight,
                uint invertFrozen
                )
{
    for(uint i = primitiveLength-2 ; i > 0; i-- ) {
        float frozen = invertFrozen ? 1.0f - frozenSet[i] : frozenSet[i];
        if (isequal(frozen, 0.0f))
            continue;

        const float4 prevPnt = (float4)(CVs[(i+1) * 3], CVs[(i+1) * 3 + 1], CVs[(i+1) * 3 + 2], 1.0f);
        const float4 curPnt  = (float4)(CVs[i*3], CVs[i*3+1], CVs[i*3+2], 1.0f);
        float4 diff = curPnt - prevPnt;
        float len = length(diff);
        float4 pnt = curPnt;
        if (len > FLT_EPSILON)
        {
            pnt = prevPnt + diff * (segLength[i + 1] / len);
        }

        tweaks[i*3] = tweaks[i*3] + (pnt.x-CVs[i*3]) / tweakWeight;
        tweaks[i*3+1] = tweaks[i*3+1] +  (pnt.y-CVs[i*3+1]) / tweakWeight;
        tweaks[i*3+2] = tweaks[i*3+2] +  (pnt.z-CVs[i*3+2]) / tweakWeight;

        CVs[i*3]   = pnt.x;
        CVs[i*3+1] = pnt.y;
        CVs[i*3+2] = pnt.z;
    }

    for(uint i = 1; i < primitiveLength; i++ ) {
        float frozen = invertFrozen ? 1.0f - frozenSet[i] : frozenSet[i];
        if (isequal(frozen, 0.0f))
            continue;

        const float4 prevPnt = (float4)(CVs[(i - 1) * 3], CVs[(i - 1) * 3 + 1], CVs[(i - 1) * 3 + 2], 1.0f);
        const float4 curPnt = (float4)(CVs[i * 3], CVs[i * 3 + 1], CVs[i * 3 + 2], 1.0f);
        float4 diff = curPnt - prevPnt;
        float len = length(diff);
        float4 pnt = curPnt;
        if (len > FLT_EPSILON)
        {
            pnt = prevPnt + diff * (segLength[i] / len);
        }

        tweaks[i*3] = tweaks[i*3] + (pnt.x-CVs[i*3]) / tweakWeight;
        tweaks[i*3+1] = tweaks[i*3+1] + (pnt.y-CVs[i*3+1]) / tweakWeight;
        tweaks[i*3+2] = tweaks[i*3+2] + (pnt.z-CVs[i*3+2]) / tweakWeight;

        CVs[i*3] = pnt.x;
        CVs[i*3+1] = pnt.y;
        CVs[i*3+2] = pnt.z;
    }
}

static void calLength_withCollision(
                __global float* CVs,
                __global float* frozenSet,
                uint primitiveLength,
                __global float* segLength,
                __global float* tweaks,
                float tweakWeight,
                uint invertFrozen,
                float minVoxelDist,
                float8 collisionImageWorldBB,
                uint4  collisionImageDim,
                __read_only image3d_t collisionImage
                )
{
    for(uint i = primitiveLength-2 ; i > 0; i-- ) {

        float frozen = invertFrozen ? 1.0f - frozenSet[i] : frozenSet[i];
        if (isequal(frozen, 0.0f))
            continue;

        const float4 prevPnt = (float4)(CVs[(i+1) * 3], CVs[(i+1) * 3 + 1], CVs[(i+1) * 3 + 2], 1.0f);
        const float4 curPnt  = (float4)(CVs[i*3], CVs[i*3+1], CVs[i*3+2], 1.0f);
        float4 diff = curPnt - prevPnt;
        float len = length(diff);
        float4 pnt = curPnt;
        if (len > FLT_EPSILON)
        {
            pnt = prevPnt + diff * (segLength[i + 1] / len);
        }

        // Collision
        pnt = collidedPosition(pnt, collisionImageWorldBB, collisionImageDim, minVoxelDist, collisionImage);
        diff = pnt - prevPnt;
        len = length(diff);
        if (len > FLT_EPSILON)
        {
            pnt = prevPnt + diff * (segLength[i + 1] / len);
        }

        tweaks[i*3] = tweaks[i*3] + (pnt.x-CVs[i*3]) / tweakWeight;
        tweaks[i*3+1] = tweaks[i*3+1] + (pnt.y-CVs[i*3+1]) / tweakWeight;
        tweaks[i*3+2] = tweaks[i*3+2] + (pnt.z-CVs[i*3+2]) / tweakWeight;

        CVs[i*3]   = pnt.x;
        CVs[i*3+1] = pnt.y;
        CVs[i*3+2] = pnt.z;
    }

    for(uint i = 1; i < primitiveLength; i++ ) {

        float frozen = invertFrozen ? 1.0f - frozenSet[i] : frozenSet[i];
        if (isequal(frozen, 0.0f))
            continue;

        const float4 prevPnt = (float4)(CVs[(i - 1) * 3], CVs[(i - 1) * 3 + 1], CVs[(i - 1) * 3 + 2], 1.0f);
        const float4 curPnt = (float4)(CVs[i * 3], CVs[i * 3 + 1], CVs[i * 3 + 2], 1.0f);
        float4 diff = curPnt - prevPnt;
        float len = length(diff);
        float4 pnt = curPnt;
        if (len > FLT_EPSILON)
        {
            pnt = prevPnt + diff * (segLength[i] / len);
        }

        // Collision
        pnt = collidedPosition(pnt, collisionImageWorldBB, collisionImageDim, minVoxelDist, collisionImage);
        diff = pnt - prevPnt;
        len = length(diff);
        if (len > FLT_EPSILON)
        {
            pnt = prevPnt + diff * (segLength[i] / len);
        }

        tweaks[i*3] = tweaks[i*3] + (pnt.x-CVs[i*3]) / tweakWeight;
        tweaks[i*3+1] = tweaks[i*3+1] + (pnt.y-CVs[i*3+1]) / tweakWeight;
        tweaks[i*3+2] = tweaks[i*3+2] + (pnt.z-CVs[i*3+2]) / tweakWeight;

        CVs[i*3] = pnt.x;
        CVs[i*3+1] = pnt.y;
        CVs[i*3+2] = pnt.z;
    }
}

static int isSelected(float falloff)
{
    return isgreaterequal(falloff, 0.0f) && islessequal(falloff, 1.0f);
}

static float3 rotateBy( float3 vec, float3 axis, float angle ) 
{
    float ca = cos(angle);
    float sa = sin(angle);
    float ca1 = (1.0f - ca);
    float a01 = axis.x * axis.y;
    float a02 = axis.x * axis.z;
    float a12 = axis.y * axis.z;
    float a00 = axis.x * axis.x;
    float a11 = axis.y * axis.y;
    float a22 = axis.z * axis.z;
    return (float3)( vec.x * (a00 * ca1 + ca) +
        vec.y * (a01 * ca1 - axis.z * sa) +
        vec.z * (a02 * ca1 + axis.y * sa),

        vec.x * (a01 * ca1 + axis.z * sa) +
        vec.y * (a11 * ca1 + ca) +
        vec.z * (a12 *ca1 - axis.x * sa),

        vec.x * (a02 * ca1 - axis.y * sa) +
        vec.y * (a12 * ca1 + axis.x * sa) +
        vec.z * (a22 * ca1 + ca) );
}

static float getPrimitiveLength(__global const float* CVs, const uint primCount)
{
    float len = 0.0f;
    for(uint i=1; i<primCount; ++i) {
        len += length( vload3(i, CVs) - vload3(i-1, CVs) );
    }
    return len;
}

inline static void atomicAdd(__global volatile float* address, const float operand)
{
    union { uint uintVal; float floatVal; } newVal;
    union { uint uintVal; float floatVal; } localVal;
    do
    {
        localVal.floatVal = *address;
        newVal.floatVal = localVal.floatVal + operand;
    } while (atomic_cmpxchg((__global volatile uint*)address, localVal.uintVal, newVal.uintVal) != localVal.uintVal);
}

inline static void atomicMin(__global volatile float* address, const float operand)
{
    union { uint uintVal; float floatVal; } newVal;
    union { uint uintVal; float floatVal; } localVal;
    do
    {
        localVal.floatVal = *address;
        newVal.floatVal = min(localVal.floatVal, operand);
    } while (atomic_cmpxchg((__global volatile uint*)address, localVal.uintVal, newVal.uintVal) != localVal.uintVal);
}


// SelectionSet buffer handling

// Selection bit mask enums, up to 8 bit currently
#define SELECT_MASK_SELECTED 0 // Selected bit
#define SELECT_MASK_HIDDEN 1   // Hidden bit

// Compress float [0, 1.0] to bitset [0x00, 0xFF]
inline static unsigned char compressToBitset(const float val)
{
    return (unsigned char)(val * 255.0f + 0.5f);
}

// Uncompress float [0, 1.0] from bitset [0x00, 0xFF]
inline static float uncompressFromBitset(const unsigned char val)
{
    return (float)val / 255.0f;
}

// Return whether specific flag is set
static bool getSelectFlag(const float val, int mask)
{
    unsigned char ival = compressToBitset(val);
    return ival & (0x1u << mask);
}

// Set flag specified by mask
static void setSelectFlag(__global float *pval, int mask, bool onOff)
{
    unsigned char ival = compressToBitset(*pval);
    bool originalOnOff = ival & (0x1u << mask);
    if (!originalOnOff && onOff) {
        *pval = uncompressFromBitset(ival | (0x1u << mask));
    }
    else if (originalOnOff && !onOff) {
        *pval = uncompressFromBitset(ival & ~(0x1u << mask));
    }
}

static void saveOriginalSelectionSet(
    __global uint*  info,
    __global float* selectionSet,
    __global float* originalSelectionSet,
             uint   infoStride,
             uint   index
             )
{
    // Skip if the primitive is already marked as Modified
    if (!isFlagSet(info, infoStride, index, kModified))
    {
        // The primitive is not modified yet. Mark it as modified.
        setFlags(info, infoStride, index, kModified, true);

        // Copy the original vertex data
        const uint offset = info[index * infoStride];
        const uint length = info[index * infoStride + 1];
        for (uint i = offset; i < offset+length; i++)
        {
            originalSelectionSet[i] = selectionSet[i];
        }
    }
}

static void saveOriginalFrozenSet(
    __global uint*  info,
    __global float* frozenSet,
    __global float* originalFrozenSet,
             uint   infoStride,
             uint   index
)
{
    // Skip if the primitive is already marked as Modified
    if (!isFlagSet(info, infoStride, index, kModified))
    {
        // The primitive is not modified yet. Mark it as modified.
        setFlags(info, infoStride, index, kModified, true);

        // Copy the original vertex data
        const uint offset = info[index * infoStride];
        const uint length = info[index * infoStride + 1];
        for (uint i = offset; i < offset+length; i++)
        {
            originalFrozenSet[i] = frozenSet[i];
        }
    }
}