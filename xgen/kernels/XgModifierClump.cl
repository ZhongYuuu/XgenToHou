#include <XgSgCurve.cl>
#include <XgModifierNoise.cl>

#define PI 3.1415926535897931f


inline static void atomicAddFloat(__global volatile float* address, const float operand)
{
    union { uint uintVal; float floatVal; } newVal;
    union { uint uintVal; float floatVal; } localVal;
    do
    {
        localVal.floatVal = *address;
        newVal.floatVal = localVal.floatVal + operand;
    } while (atomic_cmpxchg((__global volatile uint*)address, localVal.uintVal, newVal.uintVal) != localVal.uintVal);
}

__kernel void clumpModifierComputeCutGuide(
    __global const  uint*   guidePrimInfos,
             const  uint    guidePrimStride,
             const  uint    guidePrimNum,
    __global        float*  guidePos,
    __global        float*  guideTempPos,
    __global const  float*  guidePolyLen,
    __global        float*  guideLeftLen,
    __global const  float*  cutArray,
             const  uint    cutNum)
{
    const uint gid = get_global_id(0);
    if (gid >= guidePrimNum) return;

    const uint flag = guidePrimInfos[gid * guidePrimStride + 2];
    if (isPrimCulled(flag))
        return;

    const uint guideOffset = guidePrimInfos[gid * guidePrimStride];
    const uint guideCvNum = guidePrimInfos[gid * guidePrimStride + 1];

    float cut = (cutNum == guidePrimNum) ? cutArray[gid] : cutArray[0];
    cut /= 100.0f;

    float polyLen = guidePolyLen[gid];

    // Check whether there is any cut applied to clump guides
    // The cut is the amount to cut from the tip on clump guides
    float cutAmount = cut * polyLen;
    if (cutAmount < FLT_EPSILON || cutAmount > polyLen) {
        guideLeftLen[gid] = polyLen;
        return;
    }

    cutFromTip(guidePos, guideTempPos, guideOffset, guideCvNum, cutAmount, true);

    guideLeftLen[gid] = polyLen - cutAmount;

}


__kernel void clumpModifierComputeCutSpline(
    __global const  uint*   visIndices,
             const  uint    visCount,
    __global const  uint*   primitiveInfos,
             const  uint    primitiveInfoStride,
             const  uint    primNum,
    __global const  float*  positions,
    __global        float*  positionsOut,
    __global const  uint*   guideInfos,
             const  uint    guideInfoStride,
             const  uint    currentItemId,
    __global const  uint*   guidePrimInfos,
             const  uint    guidePrimStride,
    __global        float*  splineTempPos,
    __global const  float*  guideLeftLen,
    __global const  float*  maskArray,
             const  uint    maskNum)
{
    uint gid = get_global_id(0);
    if (gid >= visCount) return;

    gid = visIndices[gid];
    if (gid >= primNum) return;

    const uint flag = primitiveInfos[gid * primitiveInfoStride + 2];
    if (isPrimCulled(flag))
        return;

    const uint itemId = guideInfos[gid * guideInfoStride];
    if (itemId != currentItemId)
        return;

    const uint guideIdx = guideInfos[gid * guideInfoStride + 1];
    const uint guideOffset = guidePrimInfos[guideIdx * guidePrimStride];
    const uint guideCvNum = guidePrimInfos[guideIdx * guidePrimStride + 1];

    const uint offset = primitiveInfos[gid * primitiveInfoStride];
    const uint cvNum = primitiveInfos[gid * primitiveInfoStride + 1];

    if (guideCvNum != cvNum)
        return;

    // Copy over the input positions, the calculation will be applied on the positionsOut data
    passthrough(positions, positionsOut, offset, cvNum);

    // per-primitive parameters
    float mask = clamp((maskNum == primNum) ? maskArray[gid] : maskArray[0], 0.0f, 1.0f);

    // Escape out if mask says do nothing
    if (mask < FLT_EPSILON) {
        return;
    }

    // Any primitive that is longer than it's clump guide needs to be
    // scaled to the clump guides length. This prevents any "bubbles" at
    // the tips of the hairs as they clump backward.
    cutToLength(positionsOut, splineTempPos, offset, cvNum, guideLeftLen[guideIdx], true);
}

__kernel void clumpModifierComputeCopy(
    __global const  uint*   visIndices,
             const  uint    visCount,
    __global const  uint*   primitiveInfos,
             const  uint    primitiveInfoStride,
             const  uint    primNum,
    __global const  float*  positions,
    __global        float*  positionsOut,
    __global const  uint*   guideInfos,
             const  uint    guideInfoStride,
             const  uint    currentItemId,
    __global const  uint*   guidePrimInfos,
             const  uint    guidePrimStride,
             const  uint    guidePrimNum,
    __global        float*  guidePos,
    __global const  float*  maskArray,
             const  uint    maskNum,
    __global const  float*  copyArray,
             const  uint    copyNum,
    __global const  float*  copyVarianceArray,
             const  uint    copyVarianceNum,
    __global const  float*  copyScale)
{
    uint gid = get_global_id(0);
    if (gid >= visCount) return;

    gid = visIndices[gid];
    if (gid >= primNum) return;

    const uint flag = primitiveInfos[gid * primitiveInfoStride + 2];
    if (isPrimCulled(flag))
        return;

    const uint itemId = guideInfos[gid * guideInfoStride];
    if (itemId != currentItemId)
        return;

    const uint guideIdx = guideInfos[gid * guideInfoStride + 1];
    const uint guideOffset = guidePrimInfos[guideIdx * guidePrimStride];
    const uint guideCvNum = guidePrimInfos[guideIdx * guidePrimStride + 1];

    const uint offset = primitiveInfos[gid * primitiveInfoStride];
    const uint cvNum = primitiveInfos[gid * primitiveInfoStride + 1];

    if (guideCvNum != cvNum)
        return;

    // per-primitive parameters
    float mask = clamp((maskNum == primNum) ? maskArray[gid] : maskArray[0], 0.0f, 1.0f);

    // Escape out if mask says do nothing
    if (mask < FLT_EPSILON) {
        return;
    }

    float copy = (copyNum == guidePrimNum) ? copyArray[guideIdx] : copyArray[0];
    copy /= 100.0f;

    float copyVariance = (copyVarianceNum == primNum) ? copyVarianceArray[gid] : copyVarianceArray[0];
    copyVariance = 1.0f - clamp(-copyVariance, -1.0f, 1.0f);

    float3 p0 = vload3(offset, positionsOut);
    float3 g0 = vload3(guideOffset, guidePos);
    for (uint i = 1; i < cvNum; i++) {
        float fullCopy = copy * copyScale[i] * copyVariance * mask;
        fullCopy = clamp(fullCopy, 0.0f, 1.0f);

        // Change the primitive
        float3 pi = vload3(offset + i, positionsOut);
        float3 gi = vload3(guideOffset + i, guidePos);

        float3 copyPt = p0 + (gi - g0);
        pi = fullCopy * copyPt + (1.0f - fullCopy) * pi;
        vstore3(pi, offset + i, positionsOut);
    }
}

__kernel void clumpModifierComputeNoise(
    __global const  uint*   visIndices,
             const  uint    visCount,
    __global const  uint*   primitiveInfos,
             const  uint    primitiveInfoStride,
             const  uint    primNum,
    __global const  float*  positions,
    __global        float*  positionsOut,
    __global const  uint*   guideInfos,
             const  uint    guideInfoStride,
             const  uint    currentItemId,
    __global const  uint*   guidePrimInfos,
             const  uint    guidePrimStride,
             const  uint    guidePrimNum,
    __global const  float*  guidePrefPts,
    __global        float*  guidePos,
    __global const  float*  guideMeshN,
    __global const  float*  guideMeshU,
    __global const  float*  guideMeshV,
    __global const  float*  guidePolyLen,
    __global const  float*  guideSegLen,
    __global const  float*  maskArray,
             const  uint    maskNum,
    __global const  float*  noiseArray,
             const  uint    noiseNum,
    __global const  float*  noiseFreq,
             const  uint    noiseFreqNum,
    __global const  float*  noiseCorrel,
             const  uint    noiseCorrelNum,
    __global const  float*  noiseScale,
    __global        float*  noiseTable)
{
    uint gid = get_global_id(0);
    if (gid >= visCount) return;

    gid = visIndices[gid];
    if (gid >= primNum) return;

    const uint flag = primitiveInfos[gid * primitiveInfoStride + 2];
    if (isPrimCulled(flag))
        return;

    const uint itemId = guideInfos[gid * guideInfoStride];
    if (itemId != currentItemId)
        return;

    const uint guideIdx = guideInfos[gid * guideInfoStride + 1];
    const uint guideOffset = guidePrimInfos[guideIdx * guidePrimStride];
    const uint guideCvNum = guidePrimInfos[guideIdx * guidePrimStride + 1];

    const uint offset = primitiveInfos[gid * primitiveInfoStride];
    const uint cvNum = primitiveInfos[gid * primitiveInfoStride + 1];

    if (guideCvNum != cvNum)
        return;

    // per-primitive parameters
    float mask = clamp((maskNum == primNum) ? maskArray[gid] : maskArray[0], 0.0f, 1.0f);

    // Escape out if mask says do nothing
    if (mask < FLT_EPSILON) {
        return;
    }

    float noise = max(0.0f, (noiseNum == guidePrimNum) ? noiseArray[guideIdx] : noiseArray[0]);
    if (noise < FLT_EPSILON) {
        return;
    }

    float noiseFrequency = max(0.0f, (noiseFreqNum == guidePrimNum) ? noiseFreq[guideIdx] : noiseFreq[0]);
    float noiseCorrelation = max(0.0f, (noiseCorrelNum == guidePrimNum) ? noiseCorrel[guideIdx] : noiseCorrel[0]);

    // Correlation was given as a percentage, so convert it into a
    // usable form. This is basically a quadratic mapping from 0.0
    // to 100.0.
    noiseCorrelation = 1.0f - clamp(noiseCorrelation / 100.0f, 0.0f, 1.0f);
    noiseCorrelation = (noiseCorrelation * noiseCorrelation) * 100.0f;

    // Get the base point on pref for noise computations and offset it by
    // a small odd value to prevent hitting noise nodes at ingeger values
    float3 tan0, tan1, tan2, axis, axis0, axis1;

    float3 nVec = vload3(guideIdx, guideMeshN);
    float3 uVec = vload3(guideIdx, guideMeshU);
    float3 vVec = vload3(guideIdx, guideMeshV);

    const float3 g0 = vload3(guideOffset, guidePos);
    const float3 g1 = vload3(guideOffset + 1, guidePos);
    tan0 = fast_normalize(g1 - g0);

    float3 P = vload3(gid, guidePrefPts);

    // rotate the patch normal to align with the first guide tangent
    float dotVal = dot(nVec, tan0);
    if (isless(dotVal, 1.0f)) { // tan0 and nVec are not parallel
        axis0 = cross(nVec, tan0);
        axis0 = fast_normalize(axis0);
        float angle = acos(dotVal);
        uVec = rotateBy(uVec, axis0, angle);
        vVec = rotateBy(vVec, axis0, angle);
    }

    // Noise hits a node at the origin and at integral intervals. Add a
    // little something ~odd~ to our origin to avoid this case.
    P += (float3)(0.419276f, 0.184247f, 0.805721f);

    // Get a base offset for the noise and original segment length
    P *= noiseCorrelation;

    // Clamp frequency to a value that results in at least a half turn
    float polyLen = guidePolyLen[guideIdx];
    if (polyLen > FLT_EPSILON) {
        noiseFrequency = max(0.5f / polyLen, noiseFrequency);
    }

    float angle0 = 0.0f;
    float angle1 = 0.0f;
    float len = 0.0f;

    for (uint i = 1; i < cvNum; i++) {
        float3 gCurrent = vload3(guideOffset + i, guidePos);

        len += guideSegLen[guideOffset + i];
        float fullNoise = noise * noiseScale[i];

        // Walk our coordinate frame down the clump guide
        if (i < cvNum - 1) {
            // all points except the last (and the first)
            float3 gNext = vload3(guideOffset + i + 1, guidePos);
            tan1 = fast_normalize(gNext - gCurrent);
        }
        else {
            // last point
            tan1 = tan0;
        }

        // Finish last step
        if (fabs(angle0) > 0.0f) {
            uVec = rotateBy(uVec, axis0, angle0);
            vVec = rotateBy(vVec, axis0, angle0);
            angle0 = 0.0f;
        }
        // Take the step
        dotVal = dot(tan0, tan1);
        if (isless(fabs(dotVal), 1.0f)) { // tan0 and tan1 are not parallel
                                          // rotate the normal to align with the guide tangent
            axis1 = cross(tan0, tan1);
            axis1 = fast_normalize(axis1);
            angle1 = 0.5f * acos(dotVal);

            uVec = rotateBy(uVec, axis1, angle1);
            vVec = rotateBy(vVec, axis1, angle1);

            angle0 = angle1;
            axis0 = axis1;
        }
        uVec = fast_normalize(uVec);
        vVec = fast_normalize(vVec);

        float dist = len * noiseFrequency;

        float ndu = noiseFn((float3)(P.x + dist, P.y, P.z), noiseTable);
        float ndv = noiseFn((float3)(P.x, P.y, P.z + dist), noiseTable);

        float3 du = uVec * (fullNoise * (ndu - 0.5f));
        float3 dv = vVec * (fullNoise * (ndv - 0.5f));

        float3 delta = mask * (du + dv);
        gCurrent = gCurrent + delta;
        tan0 = tan1;

        float3 pt = vload3(offset + i, positionsOut);
        vstore3(pt + delta, offset + i, positionsOut);
    }
}

static float computeCurl(
    const  float  curlScale,
    const  float  polyLen,
    const  float  segLen,
           float  rotation)
{
    float rotScale = 0.0f;
    if(polyLen > FLT_EPSILON) {
        rotScale = 100.0f * 2.0f * PI / polyLen;
    }

    if (curlScale > 0.5f) {
        rotation -= (curlScale - 0.5f) * segLen * rotScale;
    }
    else {
        rotation += (0.5f - curlScale) * segLen * rotScale;
    }

    return rotation;
}

__kernel void applyClump(
    __global const  uint*   visIndices,
             const  uint    visCount,
    __global const  uint*   primitiveInfos,
             const  uint    primitiveInfoStride,
             const  uint    primNum,
    __global const  float*  positions,
    __global        float*  positionsOut,
    __global const  uint*   guideInfos,
             const  uint    guideInfoStride,
             const  uint    currentItemId,
    __global const  uint*   guidePrimInfos,
             const  uint    guidePrimStride,
             const  uint    guidePrimNum,
    __global        float*  guidePos,
    __global const  float*  guideMeshN,
    __global const  float*  guideMeshU,
    __global const  float*  guideMeshV,
    __global const  float*  guidePolyLen,
    __global const  float*  guideSegLen,
    __global const  float*  maskArray,
             const  uint    maskNum,
    __global const  float*  clumpArray,
             const  uint    clumpNum,
    __global const  float*  clumpScale,
             const  uint    clumpVolumize,
    __global const  float*  clumpVarianceArray,
             const  uint    clumpVarianceNum,
    __global const  float*  preserveLengthArray,
             const  uint    preserveLengthNum,
    __global const  float*  flatnessArray,
             const  uint    flatnessNum,
    __global const  float*  flatnessScale,
    __global const  float*  offsetArray,
             const  uint    offsetNum,
    __global const  float*  offsetScale,
    __global const  float*  curlArray,
             const  uint    curlNum,
    __global const  float*  curlScale,
    __global const  float*  orientArray,
             const  uint    orientNum)
{
    uint gid = get_global_id(0);
    if (gid >= visCount) return;

    gid = visIndices[gid];
    if (gid >= primNum) return;

    const uint flag = primitiveInfos[gid * primitiveInfoStride + 2];
    if (isPrimCulled(flag))
        return;

    const uint itemId = guideInfos[gid * guideInfoStride];
    if (itemId != currentItemId)
        return;

    const uint guideIdx = guideInfos[gid * guideInfoStride + 1];
    const uint guideOffset = guidePrimInfos[guideIdx * guidePrimStride];
    const uint guideCvNum = guidePrimInfos[guideIdx * guidePrimStride + 1];

    const uint offset = primitiveInfos[gid * primitiveInfoStride];
    const uint cvNum = primitiveInfos[gid * primitiveInfoStride + 1];

    if (guideCvNum != cvNum)
        return;

    // per-primitive parameters
    float mask  = clamp((maskNum == primNum) ? maskArray[gid] : maskArray[0], 0.0f, 1.0f);

    // Escape out if mask says do nothing
    if ( mask < FLT_EPSILON) {
        passthrough(positions, positionsOut, offset, cvNum);
        return;
    }

    float clump = (clumpNum == guidePrimNum) ? clumpArray[guideIdx] : clumpArray[0];
    float clumpVariance = (clumpVarianceNum == primNum) ? clumpVarianceArray[gid] : clumpVarianceArray[0];
    clumpVariance = 1.0f - clamp(-clumpVariance, -1.0f, 1.0f);

    float preserveLength = clamp((preserveLengthNum == primNum) ? preserveLengthArray[gid] : preserveLengthArray[0], 0.0f, 100.0f);
    preserveLength = preserveLength / 100.0f;

    float flatness = (flatnessNum == guidePrimNum) ? flatnessArray[guideIdx] : flatnessArray[0];
    float off = (offsetNum == guidePrimNum) ? offsetArray[guideIdx] : offsetArray[0];
    float curl = (curlNum == guidePrimNum) ? curlArray[guideIdx] : curlArray[0];
    curl = 0.025f * curl;

    // Guide frame values
    float3 tan0, tan1, axis, axis0, axis1;

    float3 nVec = vload3(guideIdx, guideMeshN);
    float3 uVec = vload3(guideIdx, guideMeshU);
    float3 vVec = vload3(guideIdx, guideMeshV);

    // guide tangent
    const float3 g0 = vload3(guideOffset, guidePos);
    const float3 g1 = vload3(guideOffset + 1, guidePos);
    tan0 = fast_normalize(g1 - g0);

    // rotate the patch normal to align with the first guide tangent
    float dotVal = dot(nVec, tan0);
    if (isless(dotVal, 1.0f)) { // tan0 and nVec are not parallel
        axis0 = cross(nVec, tan0);
        axis0 = fast_normalize(axis0);
        float angle = acos(dotVal);

        nVec = rotateBy(nVec, axis0, angle);
        uVec = rotateBy(uVec, axis0, angle);
        vVec = rotateBy(vVec, axis0, angle);
    }

    float orAngle = (orientNum == guidePrimNum) ? orientArray[guideIdx] : orientArray[0];
    uVec = rotateBy(uVec, nVec, orAngle);
    vVec = rotateBy(vVec, nVec, orAngle);

    float angle0 = 0.0f;
    float angle1 = 0.0f;

    float3 gPrev = g0;
    const float3 pIn0 = vload3(offset, positionsOut);
    const float3 pOut0 = pIn0;
    float curlRotation = 0.0f;
    for ( uint i=1; i<cvNum; ++i ) {

        float3 gCurrent = vload3(guideOffset + i, guidePos);

        // Calculate how far the current CV should move
        float fullClump = clump * clumpScale[i] * clumpVariance * mask;
        curlRotation = computeCurl(curlScale[i],
                            guidePolyLen[guideIdx],
                            guideSegLen[guideOffset + i],
                            curlRotation);
        float fullCurl = curl * curlRotation * mask;
        float fullOffset = off * offsetScale[i] * mask;
        float fullFlatness = clamp(flatness * flatnessScale[i] * mask, 0.0f, 1.0f);

        // Walk our coordinate frame down the clump guide
        if (i < cvNum-1) {
            // all points except the last (and the first)
            float3 gNext = vload3(guideOffset + i + 1, guidePos);
            tan1 = fast_normalize(gNext - gCurrent);
        } else {
            // last point
            tan1 = tan0;
        }

        const float3 pCurrent = vload3(offset + i, positionsOut);
        float3 vec = pCurrent - gCurrent;
        if ( clumpVolumize ) {
            // Blend between space curve version and groomed point. This
            // pushes the clump towards round as it is clumped.
            float amount = fabs(fullClump);
            float volumize = mix(0.0f, 1.0f, pow(amount, 0.7f));
            float vlen = length(vec);
            float3 spc = cross(gCurrent, vec);
            spc = cross(spc, gCurrent);
            spc = fast_normalize(spc);
            spc = spc * vlen;
            vec = (1.0f - volumize) * vec + volumize * spc;
        }
        vec = vec * (1.0f - fullClump);

        // Finish last step
        if (fabs(angle0) > 0.0f) {
            nVec = rotateBy(nVec, axis0, angle0);
            uVec = rotateBy(uVec, axis0, angle0);
            vVec = rotateBy(vVec, axis0, angle0);
            angle0 = 0.0f;
        }

        // Take this step
        dotVal = dot(tan0, tan1);
        if (isless(fabs(dotVal), 1.0f)) { // tan0 and tan1 are not parallel
            // rotate the normal to align with the guide tangent
            axis1 = cross(tan0, tan1);
            axis1 = fast_normalize(axis1);
            angle1 = 0.5f * acos(dotVal);

            nVec = rotateBy(nVec, axis1, angle1);
            uVec = rotateBy(uVec, axis1, angle1);
            vVec = rotateBy(vVec, axis1, angle1);

            angle0 = angle1;
            axis0 = axis1;
        }

        nVec = fast_normalize(nVec);
        uVec = fast_normalize(uVec);
        vVec = fast_normalize(vVec);

        // project the vector along the rotated u, v, n frame. since u, v, and
        // n are all orthonormal this is a simple matter of dot products.
        float a = dot(vec, uVec);
        float b = dot(vec, vVec);
        float c = dot(vec, nVec);

        // Once the vector is broken into its components
        // we can handle flatness and offset
        float3 A = a * uVec;
        float3 B = ((1.0f - fullFlatness) * b * vVec);
        float3 C = c * nVec;

        // The flattened and offset point as a vector from the clump guide
        float3 vecOffset = A + B + C;

        // Modified clump axis resulting from offset
        float3 vecAxis = fullOffset * vVec;

        // Handle curling
        if ( isnotequal(fullCurl, 0.0f) ) {
            vecOffset = rotateBy(vecOffset, nVec, fullCurl);
            vecAxis = rotateBy(vecAxis, nVec, fullCurl);
        }

        // Compute thre next point on the axis curve.
        gCurrent = gCurrent + vecAxis;
        float3 pt = gCurrent + vecOffset;

        // Tilt the profile to be along the modified axis
        float3 tiltVec = fast_normalize(gCurrent - gPrev);
        dotVal = dot(tiltVec, tan0);
        if (isless(fabs(dotVal), 1.0f)) { // tiltVec and tan0 are not parallel
            // transform about new axis center
            axis = cross(tan0, tiltVec);
            axis = fast_normalize(axis); 
            float angle = acos(dotVal);
            float3 tmp = pt - gCurrent;
            tmp = rotateBy(tmp, axis, angle);
            pt = gCurrent + tmp;
        }
        tan0 = tan1;

        if (preserveLength > 0.0f) {
            const float3 pIni = vload3(offset + i, positionsOut);
            const float3 pOuti = pt;

            const float3 vecIn = pIni - pIn0;
            const float3 vecOut = pOuti - pOut0;

            float scale = 1.0f;
            if (isgreater(length(vecOut), FLT_EPSILON)) {
                const float f = length(vecIn) / length(vecOut);
                scale = f + (1.0f - f) * (1.0f - preserveLength);
            }

            // Scale the vector from the root vertex to the current vertex
            pt = pOut0 + (pOuti - pOut0) * scale;
        }

        vstore3(pt, offset + i, positionsOut);

        gPrev = gCurrent;
    }

    // Set the final root vertex
    vstore3(vload3(offset, positions), offset, positionsOut);
}

__kernel void clumpModifierInterpolateGuideSum(
    __global const  uint*   primitiveInfos,
             const  uint    primitiveInfoStride,
             const  uint    primNum,
    __global const  float*  positions,
    __global const  float*  meshN,
    __global const  uint*   guideInfos,
             const  uint    guideInfoStride,
             const  uint    currentItemId,
    __global const  uint*   guidePrimInfos,
             const  uint    guidePrimStride,
             const  uint    guidePrimNum,
    __global const  float*  guidePos,
    __global const  float*  guideMeshN,
             const  float   maxRadius,
    __global volatile float*  guideTempPos,
    __global volatile float*  guideTempWeight)
{
    const uint gid = get_global_id(0);
    if (gid >= primNum) return;

    const uint itemId = guideInfos[gid * guideInfoStride];
    if (itemId != currentItemId)
        return;

    const uint guideIdx = guideInfos[gid * guideInfoStride + 1];
    const uint guideOffset = guidePrimInfos[guideIdx * guidePrimStride];
    const uint guideCvNum = guidePrimInfos[guideIdx * guidePrimStride + 1];

    const uint offset = primitiveInfos[gid * primitiveInfoStride];
    const uint cvNum = primitiveInfos[gid * primitiveInfoStride + 1];

    if (guideCvNum != cvNum)
        return;

    float3 sRoot = vload3(offset, positions);
    float3 gRoot = vload3(guideOffset, guidePos);

    float3 sN = vload3(gid, meshN);
    float3 gN = vload3(guideIdx, guideMeshN);
    float dotVal = dot(sN, gN);
    if (dotVal > 0.15f && maxRadius > 0.0f) {
        float dist = length(sRoot - gRoot);
        float w = dist / maxRadius;
        w = pow(2.0f, -2.0f * 2.0f * w * 2.0f * w);
        w *= (dotVal - 0.15f) / 0.85f;

        atomicAddFloat(&guideTempWeight[guideIdx], w);

        for (uint j = 1; j < cvNum; j++) {
            float3 sPt = vload3(offset + j, positions);
            float3 gPt = (sPt - sRoot) * w;

            uint tempOffset = (guideOffset + j) * 3;
            atomicAddFloat(&guideTempPos[tempOffset], gPt.x);
            atomicAddFloat(&guideTempPos[tempOffset + 1], gPt.y);
            atomicAddFloat(&guideTempPos[tempOffset + 2], gPt.z);
        }
    }
}

__kernel void clumpModifierInterpolateGuide(
    __global const  uint*   guidePrimInfos,
             const  uint    guidePrimStride,
             const  uint    guidePrimNum,
    __global        float*  guidePos,
    __global        float*  guideTempPos,
    __global        float*  guideTempWeight)
{
    const uint gid = get_global_id(0);
    if (gid >= guidePrimNum) return;

    const uint flag = guidePrimInfos[gid * guidePrimStride + 2];
    if (isPrimCulled(flag))
        return;

    const uint guideOffset = guidePrimInfos[gid * guidePrimStride];
    const uint guideCvNum = guidePrimInfos[gid * guidePrimStride + 1];

    float w = guideTempWeight[gid];
    if (w > 0.0f) {
        float3 P = vload3(guideOffset, guidePos);
        for (uint j = 1; j < guideCvNum; j++) {
            float3 pt = vload3(guideOffset + j, guideTempPos);
            pt = pt / w + P;
            vstore3(pt, guideOffset + j, guidePos);
        }
    }
}
