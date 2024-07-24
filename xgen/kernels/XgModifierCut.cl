#include <XgSgCurve.cl>
#include <XgUtils.cl>

#define     kFloatEpsilon   1.0e-5f

// Cut modifier
// We cut the primitives by the amount from the tip.
//
__kernel void applyCut(
    __global const  uint*   visIndices,
             const  uint    visCount,
    __global const  uint*   primitiveInfos,
             const  uint    primitiveInfoStride,
             const  uint    primitiveCount,
    __global const  float*  positions,
    __global        float*  positionsOut,
             const  uint    cutAbsolute,
    __global const  float*  maskArray,
             const  uint    maskCount,
    __global const  float*  amountArray,
             const  uint    amountCount,
    __global const  float*  percentArray,
             const  uint    percentCount,
             const  float   minRemainLength,
             const  uint    redistributingCV,
    __global        float*  tempPos)
{
    uint gid = get_global_id(0);
    if (gid >= visCount) return;

    gid = visIndices[gid];
    if (gid >= primitiveCount) return;

    const uint flag = primitiveInfos[gid * primitiveInfoStride + 2];
    if (isPrimCulled(flag))
        return;

    // Primitive at [offset, offset + length)
    const uint offset = primitiveInfos[gid * primitiveInfoStride];
    const uint cvNum  = primitiveInfos[gid * primitiveInfoStride + 1];

    // Mask and Amount are per-primitive
    const float mask  = clamp((maskCount == primitiveCount) ? maskArray[gid] : maskArray[0], 0.0f, 1.0f);
    float amount = (amountCount == primitiveCount) ? amountArray[gid] : amountArray[0];
    float percent = (percentCount == primitiveCount) ? percentArray[gid] : percentArray[0];
    percent = percent / 100.0f;
    float hairLen = cpolyLength(positions, offset, cvNum);
    
    if(cutAbsolute)
    {
        amount = mask * amount;
    }
    else
    {
        amount = mask * hairLen * percent;
    }
    
    if(hairLen - amount < minRemainLength)
    {
        amount = hairLen - minRemainLength;
    }
    
    // Copy over the input positions, the calculation will be applied on the positionsOut data
    passthrough(positions, positionsOut, offset, cvNum);
    cutFromTip(positionsOut, tempPos, offset, cvNum, amount, redistributingCV);
}

