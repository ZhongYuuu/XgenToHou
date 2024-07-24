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

// For the selected primitives, we used to assign MAXFLOAT to the falloff of its root cv.
// As the root cv is not going to be moved, the MAXFLOAT value can be used to distinguish its falloff from other cv's falloff(normally >0 && <=1).
// But now we also have new algorithm to evalutate falloff by affected cv count.
// To resue the falloff buffer, the affected cv count now is stored into the falloff buffer of the root cv for later calculation.
// The macro COUNTING_INDEX defines a counting index bigger than 1, so that the falloff of the root cv can still be different from the normal falloff value. 
#define COUNTING_INDEX 2.0f


static float4 worldToWindow(float4 p, float4 vp, float16 mvp)
{
    float4 clipPt;

    // mvp * p
    clipPt.x = mvp.s0 * p.x + mvp.s4 * p.y + mvp.s8 * p.z + mvp.sc * p.w;
    clipPt.y = mvp.s1 * p.x + mvp.s5 * p.y + mvp.s9 * p.z + mvp.sd * p.w;
    clipPt.z = mvp.s2 * p.x + mvp.s6 * p.y + mvp.sa * p.z + mvp.se * p.w;
    clipPt.w = mvp.s3 * p.x + mvp.s7 * p.y + mvp.sb * p.z + mvp.sf * p.w;

    if ( isnotequal(clipPt.w, 0.0f) ) {  // w != 0
        clipPt.x /= clipPt.w;
        clipPt.y /= clipPt.w;
        clipPt.z /= clipPt.w;
    } else {
        clipPt.x = MAXFLOAT;
        clipPt.y = MAXFLOAT;
        clipPt.z = MAXFLOAT;
    }

    //  If depth buffer enabled scale Z to range 0..1
    //
    //  Scale the port space to normalized space.
    //
    float w_over_two = vp.z * 0.5f;
    float h_over_two = vp.w * 0.5f;
    clipPt.x = w_over_two * clipPt.x + w_over_two + vp.x;
    clipPt.y = h_over_two * clipPt.y + h_over_two + vp.y;
    clipPt.z = 0.5f * (clipPt.z + 1.0f);
    clipPt.w = 1.0f;
    return (float4)(clipPt.x, clipPt.y, clipPt.z, clipPt.w);
}

static float calBackfaceFactor(bool enable, float4 faceNormal, float4 viewDir, float startAngle, float endAngle)
{
    if (!enable) {
        return 1.0f;
    }

    viewDir = -viewDir;

    float angle = acos(dot(faceNormal, viewDir));
    if (angle <= startAngle)
        return 1.0f;
    if (angle >= endAngle)
        return 0.0f;

    float v = clamp((angle - startAngle) / (endAngle - startAngle) * M_PI_F, 0.0f, M_PI_F);
    return (cos(v) + 1.0f) / 2.0f;

}

static float calDepth(float4 viewDir, float4 nearPt, float4 pt)
{
    float4 v = pt - nearPt;
    return dot(v, viewDir) / length(viewDir);
}

__kernel void nearestcv_to_brush_center(
                            __global float* CVs,
                            __global const uint* visIndices,
                                     const uint  visCount,
                            __global const uint* primitiveInfos,
                            float4 viewDir,
                            __global float* meshN,
                            uint filterBackface,
                            float filterBackfaceStartAngle,
                            float filterBackfaceEndAngle,
                            uint primitiveInfoStride,
                            uint primitiveCount,
                            short cursorX,
                            short cursorY,
                            float searchRadius,
                            float4 nearPt,
                            float4 viewport,
                            float16 mvpmatrix,
                            __global volatile float* nearestCV
                            )
{
    uint gid = get_global_id(0);
    if (gid >= visCount) return;

    gid = visIndices[gid];
    if (gid >= primitiveCount) return;

    const uint primitiveFlag = primitiveInfos[gid * primitiveInfoStride + 2];
    if (isPrimCulled(primitiveFlag))
        return;

    const float4 meshNormal = (float4)(vload3(gid, meshN), 0.0f);

    const float backFaceFactor =
        calBackfaceFactor(filterBackface, meshNormal, viewDir, filterBackfaceStartAngle, filterBackfaceEndAngle);

    const uint primitiveOffset = primitiveInfos[gid * primitiveInfoStride];
    const uint primitiveLength = primitiveInfos[gid * primitiveInfoStride + 1];

    float minDepth = MAXFLOAT;
    float4 nearest = (float4)(MAXFLOAT, MAXFLOAT, MAXFLOAT, MAXFLOAT);

    if (isgreater(backFaceFactor, 0.0f)) {
        for(uint i=primitiveOffset+1; i<primitiveOffset+primitiveLength; ++i) {
            float4 p = (float4)(vload3(i, CVs), 1.0f);
            float4 viewPt = (float4)worldToWindow( p, viewport, mvpmatrix );
            float dist = fast_distance((float2)(viewPt.x, viewPt.y), (float2)(cursorX, cursorY));
            if(isgreater(dist, searchRadius))
                continue;

            float dep = calDepth(viewDir, nearPt, p);
            if( isless(dep, minDepth) ) {
                nearest = p;
                minDepth = dep;
            }
        }
    }

    atomicMin(nearestCV, minDepth);

    barrier(CLK_GLOBAL_MEM_FENCE);

    if(nearestCV[0] == minDepth) {
        atomic_xchg(nearestCV+1, (float)gid);
    }

    barrier(CLK_GLOBAL_MEM_FENCE);

    if(nearestCV[0] == minDepth && nearestCV[1] == gid) {
        nearestCV[2] = nearest.x;
        nearestCV[3] = nearest.y;
        nearestCV[4] = nearest.z;
    }
}

__kernel void nearestcv_to_brush_center_lockSel(
                            __global float* CVs,
                            __global float* falloffs,
                            __global const uint* visIndices,
                                     const uint  visCount,
                            __global const uint* primitiveInfos,
                            float4 viewDir,
                            uint primitiveInfoStride,
                            uint primitiveCount,
                            short cursorX,
                            short cursorY,
                            float searchRadius,
                            float4 nearPt,
                            float4 viewport,
                            float16 mvpmatrix,
                            __global volatile float* nearestCV)
{
    uint gid = get_global_id(0);
    if (gid >= visCount) return;

    gid = visIndices[gid];
    if (gid >= primitiveCount) return;

    const uint primitiveFlag = primitiveInfos[gid * primitiveInfoStride + 2];
    if (isPrimCulled(primitiveFlag))
        return;

    const uint primitiveOffset = primitiveInfos[gid * primitiveInfoStride];
    const uint primitiveLength = primitiveInfos[gid * primitiveInfoStride + 1];

    float minDepth = MAXFLOAT;
    float4 nearest = (float4)(MAXFLOAT, MAXFLOAT, MAXFLOAT, MAXFLOAT);

    // Skip primitive which is completed unselected
    if ( isnotequal(falloffs[primitiveOffset], -1.0f) ) {

        for(uint i=primitiveOffset+1; i<primitiveOffset+primitiveLength; ++i) {
            float4 p = (float4)(vload3(i, CVs) , 1.0f);
            float4 viewPt = (float4)worldToWindow( p, viewport, mvpmatrix );
            float dist = fast_distance((float2)(viewPt.x, viewPt.y), (float2)(cursorX, cursorY));
            if(isgreater(dist, searchRadius))
                continue;

            float dep = calDepth(viewDir, nearPt, p);
            if( isless(dep, minDepth) ) {
                nearest = p;
                minDepth = dep;
            }
        }
    }

    atomicMin(nearestCV, minDepth);

    barrier(CLK_GLOBAL_MEM_FENCE);

    if(nearestCV[0] == minDepth) {
        atomic_xchg(nearestCV+1, (float)gid);
    }

    barrier(CLK_GLOBAL_MEM_FENCE);

    if(nearestCV[0] == minDepth && nearestCV[1] == gid) {
        nearestCV[2] = nearest.x;
        nearestCV[3] = nearest.y;
        nearestCV[4] = nearest.z;
    }
}

__kernel void select_kernel_flood(
                            __global float* CVs,
                            __global float* texcoords,
                            __global float* selectionSet,
                            __global float* falloffs,
                            __global float* rttFalloffs,
                            __global const uint* visIndices,
                                     const uint  visCount,
                            __global const uint* primitiveInfos,
                            uint primitiveInfoStride,
                            uint primitiveCount,
                            __read_only image2d_t rootToTipFCImage,
                            uint clear)
{
    uint gid = get_global_id(0);
    if (gid >= visCount) return;

    gid = visIndices[gid];
    if (gid >= primitiveCount) return;

    const uint primitiveFlag = primitiveInfos[gid * primitiveInfoStride + 2];
    if (isPrimCulled(primitiveFlag))
        return;

    const uint primitiveOffset = primitiveInfos[gid * primitiveInfoStride];
    const uint primitiveLength = primitiveInfos[gid * primitiveInfoStride + 1];

    falloffs[primitiveOffset] = COUNTING_INDEX + primitiveLength - 1.0f; // Count affected CV number
    rttFalloffs[primitiveOffset] = MAXFLOAT;

    const sampler_t sampler = CLK_NORMALIZED_COORDS_TRUE | CLK_ADDRESS_CLAMP_TO_EDGE | CLK_FILTER_LINEAR;

    for(uint i = primitiveOffset + 1; i < primitiveOffset+primitiveLength; ++i) {
        if (clear || getSelectFlag(selectionSet[primitiveOffset], SELECT_MASK_HIDDEN)) {
            falloffs[i] = -1.0f;
            rttFalloffs[i] = -1.0f;
        }
        else {
            falloffs[i] = 1.0f;
            float4 pixel = read_imagef(rootToTipFCImage, sampler, (float2)(texcoords[i * 2 + 1], 0.0f));
            rttFalloffs[i] = pixel.x;
        }
    }
}

__kernel void select_kernel_2d(
                            uint brushType,
                            __global float* CVs,
                            __global float* texcoords,
                            __global float* selectionSet,
                            __global float* falloffs,
                            __global float* rttFalloffs,
                            __global const uint* visIndices,
                                     const uint  visCount,
                            __global const uint* primitiveInfos,
                            __global float* meshN,
                            float4 viewDir,
                            uint filterBackface,
                            float filterBackfaceStartAngle,
                            float filterBackfaceEndAngle,
                            uint primitiveInfoStride,
                            uint primitiveCount,
                            short cursorX,
                            short cursorY,
                            float radius,
                            float4 viewport,
                            float16 mvpmatrix,
                            __read_only image2d_t brushFCImage,
                            __read_only image2d_t rootToTipFCImage)
{
    uint gid = get_global_id(0);
    if (gid >= visCount) return;

    gid = visIndices[gid];
    if (gid >= primitiveCount) return;

    const uint primitiveFlag = primitiveInfos[gid * primitiveInfoStride + 2];
    if (isPrimCulled(primitiveFlag))
        return;

    const float4 meshNormal = (float4)(meshN[gid*3], meshN[gid*3+1], meshN[gid*3+2], 0.0f);
    const float backFaceFactor =
        calBackfaceFactor(filterBackface, meshNormal, viewDir, filterBackfaceStartAngle, filterBackfaceEndAngle);

    const uint primitiveOffset = primitiveInfos[gid * primitiveInfoStride];
    const uint primitiveLength = primitiveInfos[gid * primitiveInfoStride + 1];

    falloffs[primitiveOffset] = COUNTING_INDEX;
    rttFalloffs[primitiveOffset] = MAXFLOAT;
    if (!getSelectFlag(selectionSet[primitiveOffset], SELECT_MASK_HIDDEN) && isgreater(backFaceFactor, 0.0f)) {
        const sampler_t sampler = CLK_NORMALIZED_COORDS_TRUE | CLK_ADDRESS_CLAMP_TO_EDGE | CLK_FILTER_LINEAR;

        for(uint i=primitiveOffset+1; i<primitiveOffset+primitiveLength; ++i) {
            float4 p = (float4)(CVs[i*3], CVs[i*3+1], CVs[i*3+2], 1.0f);
            float4 viewPt = (float4)worldToWindow( p, viewport, mvpmatrix );

            float distanceToCursor = fast_distance((float2)(viewPt.x, viewPt.y), (float2)(cursorX, cursorY));
            if( isless(distanceToCursor, radius) ) {
                float4 pixel = read_imagef(brushFCImage, sampler, (float2)(distanceToCursor / radius, 0.0f));
                falloffs[i] = pixel.x * backFaceFactor;

                pixel = read_imagef(rootToTipFCImage, sampler, (float2)(texcoords[i*2+1], 0.0f));
                rttFalloffs[i] = pixel.x;

                falloffs[primitiveOffset] += 1.0f; // count the affected CV number
            } else {
                falloffs[i] = MAXFLOAT;
                rttFalloffs[i] = MAXFLOAT;
            }
        }
    }

    // Make falloffs all to -1 if completed unselected
    if ( getSelectFlag(selectionSet[primitiveOffset], SELECT_MASK_HIDDEN) || isequal(falloffs[primitiveOffset], COUNTING_INDEX) ) {
        for (uint i = primitiveOffset; i < primitiveOffset+primitiveLength; i++) {
            falloffs[i] = -1.0f;
            rttFalloffs[i] = -1.0f;
        }
    } 

}

__kernel void select_kernel_2d_lockSel(
                            uint brushType,
                            __global float* CVs,
                            __global float* texcoords,
                            __global float* selectionSet,
                            __global float* falloffs,
                            __global float* rttFalloffs,
                            __global const uint* visIndices,
                                     const uint  visCount,
                            __global const uint* primitiveInfos,
                            uint primitiveInfoStride,
                            uint primitiveCount,
                            short cursorX,
                            short cursorY,
                            float radius,
                            float4 viewport,
                            float16 mvpmatrix,
                            __read_only image2d_t brushFCImage,
                            __read_only image2d_t rootToTipFCImage)
{
    uint gid = get_global_id(0);
    if (gid >= visCount) return;

    gid = visIndices[gid];
    if (gid >= primitiveCount) return;

    const uint primitiveFlag = primitiveInfos[gid * primitiveInfoStride + 2];
    if (isPrimCulled(primitiveFlag))
        return;

    const uint primitiveOffset = primitiveInfos[gid * primitiveInfoStride];
    const uint primitiveLength = primitiveInfos[gid * primitiveInfoStride + 1];

    // Skip primitive which is completed unselected
    if ( isequal(falloffs[primitiveOffset], -1.0f) ) return;

    const sampler_t sampler = CLK_NORMALIZED_COORDS_TRUE | CLK_ADDRESS_CLAMP_TO_EDGE | CLK_FILTER_LINEAR;
    falloffs[primitiveOffset] = COUNTING_INDEX;
    rttFalloffs[primitiveOffset] = MAXFLOAT;
    for(uint i=primitiveOffset+1; i<primitiveOffset+primitiveLength; ++i) {
        float4 p = (float4)(CVs[i*3], CVs[i*3+1], CVs[i*3+2], 1.0f);
        float4 viewPt = (float4)worldToWindow( p, viewport, mvpmatrix );

        float distanceToCursor = fast_distance((float2)(viewPt.x, viewPt.y), (float2)(cursorX, cursorY));
        if (getSelectFlag(selectionSet[primitiveOffset], SELECT_MASK_HIDDEN)) {
            falloffs[i] = -1;
            rttFalloffs[i] = -1;
        }
        else if( isless(distanceToCursor, radius) ) {
            float4 pixel = read_imagef(brushFCImage, sampler, (float2)(distanceToCursor / radius, 0.0f));
            falloffs[i] = pixel.x;

            pixel = read_imagef(rootToTipFCImage, sampler, (float2)(texcoords[i*2+1], 0.0f));
            rttFalloffs[i] = pixel.x;

            falloffs[primitiveOffset] += 1.0f; // count the affected CV number
        }
        else {
            falloffs[i] = MAXFLOAT;
            rttFalloffs[i] = MAXFLOAT;
        }
    }
}

__kernel void select_kernel_2d_cut(
                            uint brushType,
                            __global float* CVs,
                            __global float* texcoords,
                            __global float* selectionSet,
                            __global float* falloffs,
                            __global float* rttFalloffs,
                            __global const uint* visIndices,
                                     const uint  visCount,
                            __global const uint* primitiveInfos,
                            __global float* meshN,
                            float4 viewDir,
                            uint filterBackface,
                            float filterBackfaceStartAngle,
                            float filterBackfaceEndAngle,
                            uint primitiveInfoStride,
                            uint primitiveCount,
                            short cursorX,
                            short cursorY,
                            float radius,
                            float4 viewport,
                            float16 mvpmatrix)
{
    uint gid = get_global_id(0);
    if (gid >= visCount) return;

    gid = visIndices[gid];
    if (gid >= primitiveCount) return;

    const uint primitiveFlag = primitiveInfos[gid * primitiveInfoStride + 2];
    if (isPrimCulled(primitiveFlag))
        return;

    const float4 meshNormal = (float4)(meshN[gid*3], meshN[gid*3+1], meshN[gid*3+2], 0.0f);
    const float2 sculptPos = (float2)(cursorX, cursorY);
    const float radius2 = radius * radius;
    const float backFaceFactor =
        calBackfaceFactor(filterBackface, meshNormal, viewDir, filterBackfaceStartAngle, filterBackfaceEndAngle);

    const uint primitiveOffset = primitiveInfos[gid * primitiveInfoStride];
    const uint primitiveLength = primitiveInfos[gid * primitiveInfoStride + 1];

    falloffs[primitiveOffset] = COUNTING_INDEX;
    if (!getSelectFlag(selectionSet[primitiveOffset], SELECT_MASK_HIDDEN) && isgreater(backFaceFactor, 0.0f)) {
        const sampler_t sampler = CLK_NORMALIZED_COORDS_TRUE | CLK_ADDRESS_CLAMP_TO_EDGE | CLK_FILTER_LINEAR;
        
        float2 lastPt = worldToWindow((float4)(CVs[primitiveOffset*3], CVs[primitiveOffset*3+1], CVs[primitiveOffset*3+2], 1.0f), viewport, mvpmatrix).xy;
        for(uint i=primitiveOffset+1; i<primitiveOffset+primitiveLength; ++i)
        {

            float4 p = (float4)(CVs[i*3], CVs[i*3+1], CVs[i*3+2], 1.0f);
            float2 curPt = worldToWindow(p, viewport, mvpmatrix).xy;

            // determine the intersection between line segment (primitive segment) and circle (brush)
            float2 A = lastPt - sculptPos;
            if (isgreater(dot(A, A), radius2))
            {
                float2 B = curPt - sculptPos;
                float2 AB = B - A;
                float2 l = normalize( AB );
                float2 AH = -dot( A , l ) * l;
                float2 H = AH + A;
                
                if (islessequal(dot(H, H), radius2))
                {
                    float lenHP = sqrt(radius2 - dot(H, H));
                    float2 HP = -l * lenHP;
                    float2 P = HP + H;
                    
                    if (dot(P-B,l)<=0 && dot(P-A,l)>=0)
                    {
                        // determine the ratio where the intersection divides the line segment
                        float2 AP = P - A;
                        float ratio = sqrt(dot(AP, AP) / dot(AB, AB));
                        falloffs[i] = ratio;
                        for(++i; i<primitiveOffset+primitiveLength; ++i) {
                            falloffs[i] = MAXFLOAT;
                        }
                        falloffs[primitiveOffset] = COUNTING_INDEX + 1.0f;
                        return;
                    }
                }
            }else if (i==primitiveOffset+1)
            {
                // root is inside the circle, so cut completely
                falloffs[i] = 0.0001f;
                for(++i; i<primitiveOffset+primitiveLength; ++i) {
                    falloffs[i] = MAXFLOAT;
                }
                falloffs[primitiveOffset] = COUNTING_INDEX + 1.0f;
                return;
            }
            falloffs[i] = MAXFLOAT;
            lastPt = curPt;
        }
    }

    // Make falloffs all to -1 if completed unselected
    if ( getSelectFlag(selectionSet[primitiveOffset], SELECT_MASK_HIDDEN) || isequal(falloffs[primitiveOffset], COUNTING_INDEX) ) {
        for (uint i = primitiveOffset; i < primitiveOffset+primitiveLength; i++) {
            falloffs[i] = -1.0f;
        }
    } 
}
__kernel void select_kernel_2d_cut_rect(
                            uint brushType,
                            __global float* CVs,
                            __global float* texcoords,
                            __global float* selectionSet,
                            __global float* falloffs,
                            __global float* rttFalloffs,
                            __global const uint* visIndices,
                                     const uint  visCount,
                            __global const uint* primitiveInfos,
                            __global float* meshN,
                            float4 viewDir,
                            uint filterBackface,
                            float filterBackfaceStartAngle,
                            float filterBackfaceEndAngle,
                            uint primitiveInfoStride,
                            uint primitiveCount,
                            short cursorX,
                            short cursorY,
                            short lastCursorX,
                            short lastCursorY,
                            float radius,
                            float4 viewport,
                            float16 mvpmatrix)
{
    uint gid = get_global_id(0);
    if (gid >= visCount) return;

    gid = visIndices[gid];
    if (gid >= primitiveCount) return;

    const uint primitiveFlag = primitiveInfos[gid * primitiveInfoStride + 2];
    if (isPrimCulled(primitiveFlag))
        return;

    const uint primitiveOffset = primitiveInfos[gid * primitiveInfoStride];
    const uint primitiveLength = primitiveInfos[gid * primitiveInfoStride + 1];

    // This kernel should be run right after kernel 'select_kernel_2d_cut',
    // so skip unselected hair at the very beginning based on the current falloff value
    if (isequal(falloffs[primitiveOffset], -1.0f))
        return;

    const float4 meshNormal = (float4)(meshN[gid*3], meshN[gid*3+1], meshN[gid*3+2], 0.0f);
    const float2 sculptPos = (float2)(cursorX, cursorY);
    const float2 oldSculptPos = (float2)(lastCursorX, lastCursorY);
    const float2 stroke = sculptPos - oldSculptPos;
    const float2 strokeOffset = normalize((float2)(-stroke.y, stroke.x)) * radius; // perpendicular to stroke
    const float backFaceFactor =
        calBackfaceFactor(filterBackface, meshNormal, viewDir, filterBackfaceStartAngle, filterBackfaceEndAngle);

    if (isgreater(backFaceFactor, 0.0f)) {
        const sampler_t sampler = CLK_NORMALIZED_COORDS_TRUE | CLK_ADDRESS_CLAMP_TO_EDGE | CLK_FILTER_LINEAR;

        float2 lastPt = worldToWindow((float4)(CVs[primitiveOffset*3], CVs[primitiveOffset*3+1], CVs[primitiveOffset*3+2], 1.0f), viewport, mvpmatrix).xy;

        // If root inside the rectangle
        if (dot(lastPt-oldSculptPos, stroke)>0 && dot(lastPt-sculptPos, stroke)<0 && 
            dot(lastPt-(sculptPos-strokeOffset), strokeOffset) >0 &&
            dot(lastPt-(sculptPos+strokeOffset), strokeOffset) <0)
        {
            if (getSelectFlag(selectionSet[primitiveOffset], SELECT_MASK_HIDDEN)) {
                for (uint i = primitiveOffset + 1; i < primitiveOffset+primitiveLength; i++) {
                    falloffs[i] = -1.0f;
                }
            } 
            else {
                // root inside rect, completely cut
                uint i=primitiveOffset+1;
                falloffs[i] = 0.0001f;
                for(++i; i<primitiveOffset+primitiveLength; ++i) {
                    falloffs[i] = MAXFLOAT;
                }
            }
            falloffs[primitiveOffset] = COUNTING_INDEX + 1.0f;
            return;
        }

        for(uint i=primitiveOffset+1; i<primitiveOffset+primitiveLength; ++i)
        {
            float4 p = (float4)(CVs[i*3], CVs[i*3+1], CVs[i*3+2], 1.0f);
            float2 curPt = worldToWindow(p, viewport, mvpmatrix).xy;

            float2 vSegment = curPt - lastPt;

            // offset stroke line using brush radius as distance (choose one side)
            float2 A, B;
            A = oldSculptPos - strokeOffset;
            B = sculptPos - strokeOffset;

            // determine intersection between two line segments (offseted stroke and primitive segment)
            float denominator = vSegment.x * stroke.y - vSegment.y * stroke.x;
            if (isgreater(fabs(denominator), 0.0f))
            {
                // intersection between two lines exists
                float2 r;
                float cf1, cf2;
                cf1 = (curPt.x * lastPt.y - curPt.y * lastPt.x);
                cf2 = (B.x * A.y - B.y * A.x);
                r.x = (cf1 * stroke.x - vSegment.x * cf2) / denominator;
                r.y = (cf1 * stroke.y - vSegment.y * cf2) / denominator;
                float distToLastPt = MAXFLOAT;
                // one side
                if (dot(r-A,stroke)>=0 && dot(r-B,stroke)<=0 && dot(r-lastPt,vSegment)>=0 && dot(r-curPt,vSegment)<=0)
                {
                    distToLastPt = dot(r-lastPt, r-lastPt);
                }
                // the other side
                A = oldSculptPos + strokeOffset;
                B = sculptPos + strokeOffset;
                cf2 = (B.x * A.y - B.y * A.x);
                r.x = (cf1 * stroke.x - vSegment.x * cf2) / denominator;
                r.y = (cf1 * stroke.y - vSegment.y * cf2) / denominator;
                if (dot(r-A,stroke)>=0 && dot(r-B,stroke)<=0 && dot(r-lastPt,vSegment)>=0 && dot(r-curPt,vSegment)<=0)
                {
                    // possibly intersecting at two positions
                    // choose the nearer one to the beginning of the segment
                    distToLastPt = min(distToLastPt, dot(r-lastPt, r-lastPt));
                }
                if (distToLastPt != MAXFLOAT)
                {
                    if (getSelectFlag(selectionSet[primitiveOffset], SELECT_MASK_HIDDEN)) {
                        for (uint j = primitiveOffset + 1; j < primitiveOffset+primitiveLength; j++) {
                            falloffs[j] = -1.0f;
                        }
                    }
                    else {
                        float ratio = sqrt(distToLastPt / dot(vSegment, vSegment));
                        for (uint j=primitiveOffset+1;j<i;j++) {
                            falloffs[j] = MAXFLOAT;
                        }

                        if (isSelected(falloffs[i])) {
                            falloffs[i] = min(falloffs[i], ratio);
                        }
                        else {
                            falloffs[i] = ratio;
                        }

                        for(++i; i<primitiveOffset+primitiveLength; ++i) {
                            falloffs[i] = MAXFLOAT;
                        }
                    }

                    falloffs[primitiveOffset] = COUNTING_INDEX + 1.0f;
                    break;
                }
            }
            if (isSelected(falloffs[i])) break;
            lastPt = curPt;
        }
    }
}

__kernel void select_kernel_3d(
                            uint brushType,
                            __global float* CVs,
                            __global float* texcoords,
                            __global float* selectionSet,
                            __global float* falloffs,
                            __global float* rttFalloffs,
                            __global const uint* visIndices,
                                     const uint  visCount,
                            __global const uint* primitiveInfos,
                            float4 viewDir,
                            __global float* meshN,
                            uint filterBackface,
                            float filterBackfaceStartAngle,
                            float filterBackfaceEndAngle,
                            uint primitiveInfoStride,
                            uint primitiveCount,
                            __global float* center,
                            float radius,
                            float centerOffset,
                            __read_only image2d_t brushFCImage,
                            __read_only image2d_t rootToTipFCImage)
{
    uint gid = get_global_id(0);
    if (gid >= visCount) return;

    gid = visIndices[gid];
    if (gid >= primitiveCount) return;

    const uint primitiveFlag = primitiveInfos[gid * primitiveInfoStride + 2];
    if (isPrimCulled(primitiveFlag))
        return;

    const float4 meshNormal = (float4)(meshN[gid*3], meshN[gid*3+1], meshN[gid*3+2], 0.0f);
    const float backFaceFactor =
        calBackfaceFactor(filterBackface, meshNormal, viewDir, filterBackfaceStartAngle, filterBackfaceEndAngle);

    const uint primitiveOffset = primitiveInfos[gid * primitiveInfoStride];
    const uint primitiveLength = primitiveInfos[gid * primitiveInfoStride + 1];

    falloffs[primitiveOffset] = COUNTING_INDEX;
    rttFalloffs[primitiveOffset] = MAXFLOAT;
    if (!getSelectFlag(selectionSet[primitiveOffset], SELECT_MASK_HIDDEN) && isgreater(backFaceFactor, 0.0f)) {
        const sampler_t sampler = CLK_NORMALIZED_COORDS_TRUE | CLK_ADDRESS_CLAMP_TO_EDGE | CLK_FILTER_LINEAR;

        float3 c = (float3)(center[2], center[3], center[4]);
        if(isnotequal(centerOffset, 0.0f)) {
            float4 dir = normalize(viewDir);
            c += dir.xyz * centerOffset;
        }

        for(uint i=primitiveOffset+1; i<primitiveOffset+primitiveLength; ++i) {
            float4 p      = (float4)(CVs[i*3], CVs[i*3+1], CVs[i*3+2], 1.0f);
            float pToCenterDist = fast_distance(p.xyz, c.xyz);

            if( isless(pToCenterDist, radius) ) {
                float4 pixel = read_imagef(brushFCImage, sampler, (float2)(pToCenterDist / radius, 0.0f));
                falloffs[i] = pixel.x * backFaceFactor;

                pixel = read_imagef(rootToTipFCImage, sampler, (float2)(texcoords[i*2+1], 0.0f));
                rttFalloffs[i] = pixel.x;

                falloffs[primitiveOffset] += 1.0f; // count the affected CV number
            } else {
                falloffs[i] = MAXFLOAT;
                rttFalloffs[i] = MAXFLOAT;
            }
        }
    }

    // Make falloffs all to -1 if completed unselected
    if ( getSelectFlag(selectionSet[primitiveOffset], SELECT_MASK_HIDDEN) || isequal(falloffs[primitiveOffset], COUNTING_INDEX) ) {
        for (uint i = primitiveOffset; i < primitiveOffset+primitiveLength; i++) {
            falloffs[i] = -1.0f;
            rttFalloffs[i] = -1.0f;
        }
    }
}

__kernel void select_kernel_3d_lockSel(
                            uint brushType,
                            __global float* CVs,
                            __global float* texcoords,
                            __global float* selectionSet,
                            __global float* falloffs,
                            __global float* rttFalloffs,
                            __global const uint* visIndices,
                                     const uint  visCount,
                            __global const uint* primitiveInfos,
                            float4 viewDir,
                            uint primitiveInfoStride,
                            uint primitiveCount,
                            __global float* center,
                            float radius,
                            float centerOffset,
                            __read_only image2d_t brushFCImage,
                            __read_only image2d_t rootToTipFCImage)
{
    uint gid = get_global_id(0);
    if (gid >= visCount) return;

    gid = visIndices[gid];
    if (gid >= primitiveCount) return;

    const uint primitiveFlag = primitiveInfos[gid * primitiveInfoStride + 2];
    if (isPrimCulled(primitiveFlag))
        return;

    const uint primitiveOffset = primitiveInfos[gid * primitiveInfoStride];
    const uint primitiveLength = primitiveInfos[gid * primitiveInfoStride + 1];

    // Skip primitive which is completed unselected
    if ( isequal(falloffs[primitiveOffset], -1.0f) ) return;

    const sampler_t sampler = CLK_NORMALIZED_COORDS_TRUE | CLK_ADDRESS_CLAMP_TO_EDGE | CLK_FILTER_LINEAR;

    float3 c = (float3)(center[2], center[3], center[4]);
    if(isnotequal(centerOffset, 0.0f)) {
        float4 dir = normalize(viewDir);
        c += dir.xyz * centerOffset;
    }

    falloffs[primitiveOffset] = COUNTING_INDEX;
    rttFalloffs[primitiveOffset] = MAXFLOAT;
    for(uint i=primitiveOffset+1; i<primitiveOffset+primitiveLength; ++i) {
        float4 p      = (float4)(CVs[i*3], CVs[i*3+1], CVs[i*3+2], 1.0f);
        float pToCenterDist = fast_distance(p.xyz, c.xyz);

        if (getSelectFlag(selectionSet[primitiveOffset], SELECT_MASK_HIDDEN)) {
            falloffs[i] = -1;
            rttFalloffs[i] = -1;
        }
        else if( isless(pToCenterDist, radius) ) {
            float4 pixel = read_imagef(brushFCImage, sampler, (float2)(pToCenterDist / radius, 0.0f));
            falloffs[i] = pixel.x;

            pixel = read_imagef(rootToTipFCImage, sampler, (float2)(texcoords[i*2+1], 0.0f));
            rttFalloffs[i] = pixel.x;

            falloffs[primitiveOffset] += 1.0f; // count the affected CV number
        }
        else {
            falloffs[i] = MAXFLOAT;
            rttFalloffs[i] = MAXFLOAT;
        }
    }
}

__kernel void select_kernel_3d_cut(
                            uint brushType,
                            __global float* CVs,
                            __global float* texcoords,
                            __global float* selectionSet,
                            __global float* falloffs,
                            __global float* rttFalloffs,
                            __global const uint* visIndices,
                                     const uint  visCount,
                            __global const uint* primitiveInfos,
                            float4 viewDir,
                            __global float* meshN,
                            uint filterBackface,
                            float filterBackfaceStartAngle,
                            float filterBackfaceEndAngle,
                            uint primitiveInfoStride,
                            uint primitiveCount,
                            float3 center,
                            float radius,
                            float centerOffset)
{
    uint gid = get_global_id(0);
    if (gid >= visCount) return;

    gid = visIndices[gid];
    if (gid >= primitiveCount) return;

    const uint primitiveFlag = primitiveInfos[gid * primitiveInfoStride + 2];
    if (isPrimCulled(primitiveFlag))
        return;

    const float4 meshNormal = (float4)(meshN[gid*3], meshN[gid*3+1], meshN[gid*3+2], 0.0f);
    const float radius2 = radius * radius;
    const float backFaceFactor =
        calBackfaceFactor(filterBackface, meshNormal, viewDir, filterBackfaceStartAngle, filterBackfaceEndAngle);

    const uint primitiveOffset = primitiveInfos[gid * primitiveInfoStride];
    const uint primitiveLength = primitiveInfos[gid * primitiveInfoStride + 1];

    falloffs[primitiveOffset] = COUNTING_INDEX;
    if (!getSelectFlag(selectionSet[primitiveOffset], SELECT_MASK_HIDDEN) && isgreater(backFaceFactor, 0.0f)) {
        const sampler_t sampler = CLK_NORMALIZED_COORDS_TRUE | CLK_ADDRESS_CLAMP_TO_EDGE | CLK_FILTER_LINEAR;
        
        float3 c = center + normalize(viewDir.xyz) * centerOffset;
        
        float3 lastp = (float3)(CVs[primitiveOffset*3], CVs[primitiveOffset*3+1], CVs[primitiveOffset*3+2]);

        for(uint i=primitiveOffset+1; i<primitiveOffset+primitiveLength; ++i)
        {
            float3 p = (float3)(CVs[i*3], CVs[i*3+1], CVs[i*3+2]);

            // determine the intersection between line segment (primitive segment) and sphere (brush)
            float3 A = lastp - c;
            if ( isgreater(dot(A, A), radius2) )
            {
                float3 B = p - c;
                float3 vAB = B - A;
                float3 l = normalize( vAB );
                float3 vAH = -dot( A , l ) * l;
                float3 H = vAH + A;
                
                if ( islessequal(dot(H, H), radius2) )
                {
                    float lenHP = sqrt(radius2 - dot(H, H));
                    float3 vHP = -l * lenHP;
                    float3 P = vHP + H;
                    
                    if (islessequal(dot(P-B,l), 0.0f) && isgreaterequal(dot(P-A,l), 0.0f))
                    {
                        // determine the ratio where the intersection divides the line segment
                        float3 vAP = P - A;
                        float ratio = sqrt(dot(vAP, vAP) / dot(vAB, vAB));
                        falloffs[i] = ratio;
                        for(++i; i<primitiveOffset+primitiveLength; ++i) {
                            falloffs[i] = MAXFLOAT;
                        }
                        falloffs[primitiveOffset] += 1.0f;
                        break;
                    }
                }
            }else if (i==primitiveOffset+1)
            {
                // root is inside the sphere, so cut completely
                falloffs[i] = 0.0001f;
                for(++i; i<primitiveOffset+primitiveLength; ++i) {
                    falloffs[i] = MAXFLOAT;
                }
                falloffs[primitiveOffset] = COUNTING_INDEX + 1.0f;;
                return;
            }
            falloffs[i] = MAXFLOAT;
            lastp = p;
        }
    }

    // Make falloffs all to -1 if completed unselected
    if ( getSelectFlag(selectionSet[primitiveOffset], SELECT_MASK_HIDDEN) || isequal(falloffs[primitiveOffset], COUNTING_INDEX) ) {
        for (uint i = primitiveOffset; i < primitiveOffset+primitiveLength; i++) {
            falloffs[i] = -1.0f;
        }
    }
}

__kernel void select_kernel_3d_cut_cylinder(
                            uint brushType,
                            __global float* CVs,
                            __global float* texcoords,
                            __global float* selectionSet,
                            __global float* falloffs,
                            __global float* rttFalloffs,
                            __global const uint* visIndices,
                                     const uint  visCount,
                            __global const uint* primitiveInfos,
                            float4 viewDir,
                            __global float* meshN,
                            uint filterBackface,
                            float filterBackfaceStartAngle,
                            float filterBackfaceEndAngle,
                            uint primitiveInfoStride,
                            uint primitiveCount,
                            float3 center,
                            float3 lastCenter,
                            float radius,
                            float centerOffset)
{
    uint gid = get_global_id(0);
    if (gid >= visCount) return;

    gid = visIndices[gid];
    if (gid >= primitiveCount) return;

    const uint primitiveFlag = primitiveInfos[gid * primitiveInfoStride + 2];
    if (isPrimCulled(primitiveFlag))
        return;

    const uint primitiveOffset = primitiveInfos[gid * primitiveInfoStride];
    const uint primitiveLength = primitiveInfos[gid * primitiveInfoStride + 1];

    // This kernel should be run right after kernel 'select_kernel_3d_cut',
    // so skip unselected hair at the very beginning based on the current falloff value
    if (isequal(falloffs[primitiveOffset], -1.0f))
        return;

    const float4 meshNormal = (float4)(meshN[gid*3], meshN[gid*3+1], meshN[gid*3+2], 0.0f);
    const float radius2 = radius * radius;
    const float backFaceFactor =
        calBackfaceFactor(filterBackface, meshNormal, viewDir, filterBackfaceStartAngle, filterBackfaceEndAngle);

    if (isgreater(backFaceFactor, 0.0f)) {
        const sampler_t sampler = CLK_NORMALIZED_COORDS_TRUE | CLK_ADDRESS_CLAMP_TO_EDGE | CLK_FILTER_LINEAR;
        
        float3 dir = normalize(viewDir.xyz);
        // beginning of the stroke
        const float3 stBeg = lastCenter + dir * centerOffset;
        // end of the stroke
        const float3 stEnd = center + dir * centerOffset;
        
        const float3 stroke = stEnd - stBeg;
        const float strokeLen = fast_length(stroke);
        if (strokeLen<0.001f) return;
        
        // We need to determine line vs cylinder intersection. A simple solution is
        // to transform coordinates so that the center line of the cylinder functions as the Z axis,
        // then we have a 2D problem of intersecting a line with a circle.
        
        // create a UVN matrix, and we'll use it to transform each CV.
        float4 U, V, N;
        N = normalize((float4)(stroke.x, stroke.y, stroke.z, 0.0f));
        V = normalize(cross((float4)(1.0f, 0.0f, 0.0f, 0.0f), N));
        U = normalize(cross(V, N));
        
        float3 p = (float3)(CVs[primitiveOffset*3], CVs[primitiveOffset*3+1], CVs[primitiveOffset*3+2]) - stBeg;
        p = (float3)(dot(p, U.xyz), dot(p, V.xyz), dot(p, N.xyz));
        if (isless(dot(p.xy, p.xy), radius2) && p.z>=0 && p.z<=strokeLen)
        {
            if (getSelectFlag(selectionSet[primitiveOffset], SELECT_MASK_HIDDEN)) {
                for (uint i = primitiveOffset + 1; i < primitiveOffset+primitiveLength; i++) {
                    falloffs[i] = -1.0f;
                }
            }
            else {
                // root of hair inside the cylinder, completely cut
                uint i=primitiveOffset+1;
                falloffs[i] = 0.0001f;
                for(++i; i<primitiveOffset+primitiveLength; ++i) {
                    falloffs[i] = MAXFLOAT;
                }
            }         
            falloffs[primitiveOffset] = COUNTING_INDEX + 1.0f;
            return;
        }
        
        for(uint i=primitiveOffset+1; i<primitiveOffset+primitiveLength; ++i)
        {
            float3 lastp = p;
            p = (float3)(CVs[i*3], CVs[i*3+1], CVs[i*3+2]) - stBeg;
            p = (float3)(dot(p, U.xyz), dot(p, V.xyz), dot(p, N.xyz));
            
            // determine the intersection between line segment and circle
            // the algorithm below is almost the same as the one in select_kernel_2d_cut
            float2 A = lastp.xy;
            if (isgreater(dot(A, A), radius2))
            {
                float2 B = p.xy;
                float2 AB = B - A;
                float2 l = normalize( AB );
                float2 AH = -dot( A , l ) * l;
                float2 H = AH + A;
                if ( isless(dot(H, H), radius2) )
                {
                    float lenHP = sqrt(radius2 - dot(H, H));
                    float2 HP = -l * lenHP;
                    float2 P = HP + H;
                    
                    if (islessequal(dot(P-B,l), 0.0f) && isgreaterequal(dot(P-A,l), 0.0f))
                    {
                        // determine the ratio where the intersection divides the line segment
                        float2 AP = P - A;
                        float ratio = sqrt(dot(AP, AP) / dot(AB, AB));
                        float Pz = lastp.z + (p.z-lastp.z) * ratio;
                        if (Pz>=0 && Pz<=strokeLen)
                        {
                            for (uint j=primitiveOffset+1;j<primitiveOffset+primitiveLength;j++) {
                                falloffs[j] = getSelectFlag(selectionSet[primitiveOffset], SELECT_MASK_HIDDEN) ? -1 : MAXFLOAT;
                            }

                            falloffs[i] = getSelectFlag(selectionSet[primitiveOffset], SELECT_MASK_HIDDEN) ? -1 : ratio;
                            falloffs[primitiveOffset] = COUNTING_INDEX + 1.0f;
                            return;
                        }
                    }
                }
            }
        }
    }
}

__kernel void evaluate_falloff_by_cvcount(
                            __global float* CVs,
                            __global float* texcoords,
                            __global float* falloffs,
                            __global float* rttFalloffs,
                            __global const uint* visIndices,
                                     const uint  visCount,
                            __global const uint* primitiveInfos,
                            uint primitiveInfoStride,
                            uint primitiveCount,
                            float maxAffectedCVs,
                            __read_only image2d_t brushFCImage,
                            __read_only image2d_t rootToTipFCImage)
{
    uint gid = get_global_id(0);
    if (gid >= visCount) return;

    gid = visIndices[gid];
    if (gid >= primitiveCount) return;

    const uint primitiveFlag = primitiveInfos[gid * primitiveInfoStride + 2];
    if (isPrimCulled(primitiveFlag))
        return;

    const uint primitiveOffset = primitiveInfos[gid * primitiveInfoStride];
    const uint primitiveLength = primitiveInfos[gid * primitiveInfoStride + 1];

    if ( isequal(falloffs[primitiveOffset], -1.0f) ) return;

    const sampler_t sampler = CLK_NORMALIZED_COORDS_TRUE | CLK_ADDRESS_CLAMP_TO_EDGE | CLK_FILTER_LINEAR;

    float4 pixel;
    float falloff = -1.0f;
    if( isless(falloffs[primitiveOffset], MAXFLOAT) && isgreater(falloffs[primitiveOffset], COUNTING_INDEX) ){
        
        pixel = read_imagef(brushFCImage, sampler, (float2)( (1.0f- (falloffs[primitiveOffset] - COUNTING_INDEX)/(maxAffectedCVs - COUNTING_INDEX)), 0.0f));
        falloff = pixel.x;
    }

    falloffs[primitiveOffset] = MAXFLOAT;
    rttFalloffs[primitiveOffset] = MAXFLOAT;
    for(uint i = primitiveOffset+1; i < primitiveOffset+primitiveLength; ++i) {
        falloffs[i] = falloff;

        pixel = read_imagef(rootToTipFCImage, sampler, (float2)(texcoords[i*2+1], 0.0f));
        rttFalloffs[i] = pixel.x;
    }
}

__kernel void select_kernel_surface(
                            uint brushType,
                            __global float* CVs,
                            __global float* texcoords,
                            __global float* selectionSet,
                            __global float* falloffs,
                            __global float* rttFalloffs,
                            __global const uint* visIndices,
                                     const uint  visCount,
                            __global const uint* primitiveInfos,
                            __global float* meshN,
                            float4 viewDir,
                            uint filterBackface,
                            float filterBackfaceStartAngle,
                            float filterBackfaceEndAngle,
                            uint primitiveInfoStride,
                            uint primitiveCount,
                            float centerX,
                            float centerY,
                            float centerZ,
                            float radius,
                            __read_only image2d_t brushFCImage,
                            __read_only image2d_t rootToTipFCImage)
{
    uint gid = get_global_id(0);
    if (gid >= visCount) return;

    gid = visIndices[gid];
    if (gid >= primitiveCount) return;

    const uint primitiveFlag = primitiveInfos[gid * primitiveInfoStride + 2];
    if (isPrimCulled(primitiveFlag))
        return;

    const float4 meshNormal = (float4)(meshN[gid*3], meshN[gid*3+1], meshN[gid*3+2], 0.0f);
    const float backFaceFactor =
        calBackfaceFactor(filterBackface, meshNormal, viewDir, filterBackfaceStartAngle, filterBackfaceEndAngle);

    const uint primitiveOffset = primitiveInfos[gid * primitiveInfoStride];
    const uint primitiveLength = primitiveInfos[gid * primitiveInfoStride + 1];

    float4 pixel;
    float falloff = -1.0f;
    falloffs[primitiveOffset] = -1.0f;
    rttFalloffs[primitiveOffset] = -1.0f;

    const sampler_t sampler = CLK_NORMALIZED_COORDS_TRUE | CLK_ADDRESS_CLAMP_TO_EDGE | CLK_FILTER_LINEAR;
        
    if (!getSelectFlag(selectionSet[primitiveOffset], SELECT_MASK_HIDDEN) && isgreater(backFaceFactor, 0.0f)) {
        float4 p = (float4)(CVs[primitiveOffset*3], CVs[primitiveOffset*3+1], CVs[primitiveOffset*3+2], 1.0f);
        float4 center = (float4)(centerX, centerY, centerZ, 1.0f);

        float distanceToCursor = fast_distance(p.xyz, center.xyz);
        if( distanceToCursor < radius ) {
            float4 pixel = read_imagef(brushFCImage, sampler, (float2)(distanceToCursor / radius, 0.0f));
            falloff = pixel.x * backFaceFactor;

            falloffs[primitiveOffset] = MAXFLOAT;
            rttFalloffs[primitiveOffset] = MAXFLOAT;
        }
    }

    for(uint i=primitiveOffset+1; i<primitiveOffset+primitiveLength; ++i) {
        if (getSelectFlag(selectionSet[primitiveOffset], SELECT_MASK_HIDDEN)) {
            falloffs[i] = -1;
            rttFalloffs[i] = -1;
        }
        else {
            falloffs[i] = falloff;
            pixel = read_imagef(rootToTipFCImage, sampler, (float2)(texcoords[i*2+1], 0.0f));
            rttFalloffs[i] = pixel.x;
        }
    }
}

__kernel void select_kernel_surface_lockSel(
                            uint brushType,
                            __global float* CVs,
                            __global float* texcoords,
                            __global float* selectionSet,
                            __global float* falloffs,
                            __global float* rttFalloffs,
                            __global const uint* visIndices,
                                     const uint  visCount,
                            __global const uint* primitiveInfos,
                            uint primitiveInfoStride,
                            uint primitiveCount,
                            float centerX,
                            float centerY,
                            float centerZ,
                            float radius,
                            __read_only image2d_t brushFCImage,
                            __read_only image2d_t rootToTipFCImage)
{
    uint gid = get_global_id(0);
    if (gid >= visCount) return;

    gid = visIndices[gid];
    if (gid >= primitiveCount) return;

    const uint primitiveFlag = primitiveInfos[gid * primitiveInfoStride + 2];
    if (isPrimCulled(primitiveFlag))
        return;

    const uint primitiveOffset = primitiveInfos[gid * primitiveInfoStride];
    const uint primitiveLength = primitiveInfos[gid * primitiveInfoStride + 1];

    // Skip primitive which is completed unselected
    if ( isequal(falloffs[primitiveOffset], -1.0f) ) return;

    float4 pixel;
    float falloff = -1.0f;
    const sampler_t sampler = CLK_NORMALIZED_COORDS_TRUE | CLK_ADDRESS_CLAMP_TO_EDGE | CLK_FILTER_LINEAR;

    float4 p = (float4)(CVs[primitiveOffset*3], CVs[primitiveOffset*3+1], CVs[primitiveOffset*3+2], 1.0f);
    float4 center = (float4)(centerX, centerY, centerZ, 1.0f);

    float distanceToCursor = fast_distance(p.xyz, center.xyz);
    if( !getSelectFlag(selectionSet[primitiveOffset], SELECT_MASK_HIDDEN) && distanceToCursor < radius ) {
        pixel = read_imagef(brushFCImage, sampler, (float2)(distanceToCursor / radius, 0.0f));
        falloff = pixel.x;
    }

    for(uint i=primitiveOffset+1; i<primitiveOffset+primitiveLength; ++i) {
        if (getSelectFlag(selectionSet[primitiveOffset], SELECT_MASK_HIDDEN)) {
            falloffs[i] = -1;
            rttFalloffs[i] = -1;
        }
        else {
            falloffs[i] = falloff;
            pixel = read_imagef(rootToTipFCImage, sampler, (float2)(texcoords[i*2+1], 0.0f));
            rttFalloffs[i] = pixel.x;
        }
    }
}

__kernel void mark_selection_kernel(
                    __global const uint* visIndices,
                             const uint  visCount,
                    __global uint*  info,
                    __global float* falloffs,
                    __global float* selectionSet,
                    __global float* originalSelectionSet,
                    uint infoStride,
                    uint n,
                    uint invert
                    )
{
    uint gid = get_global_id(0);
    if (gid >= visCount) return;

    gid = visIndices[gid];
    if (gid >= n) return;

    const uint primitiveFlag = info[gid * infoStride + 2];
    if (isPrimCulled(primitiveFlag))
        return;

    saveOriginalSelectionSet(info, selectionSet, originalSelectionSet, infoStride, gid);

    const uint primitiveOffset = info[gid * infoStride];
    const uint primitiveLength = info[gid * infoStride + 1];

    for(uint i = primitiveOffset + 1; i < primitiveOffset + primitiveLength; ++i) {
        if (!isSelected(falloffs[i])) continue;

        setSelectFlag(&selectionSet[i], SELECT_MASK_SELECTED, !invert);
    }

    selectionSet[primitiveOffset] = selectionSet[primitiveOffset + 1];
}

__kernel void deselect_all_kernel(
                    __global uint*  info,
                    __global float* selectionSet,
                    __global float* originalSelectionSet,
                    uint infoStride,
                    uint n
                    )
{
    uint gid = get_global_id(0);
    if (gid >= n) return;

    const uint primitiveFlag = info[gid * infoStride + 2];
    if (isPrimCulled(primitiveFlag))
        return;

    saveOriginalSelectionSet(info, selectionSet, originalSelectionSet, infoStride, gid);

    const uint primitiveOffset = info[gid * infoStride];
    const uint primitiveLength = info[gid * infoStride + 1];

    for(uint i = primitiveOffset + 1; i < primitiveOffset + primitiveLength; ++i) {
        if (getSelectFlag(selectionSet[i], SELECT_MASK_HIDDEN)) continue;

        setSelectFlag(&selectionSet[i], SELECT_MASK_SELECTED, false);
    }

    selectionSet[primitiveOffset] = selectionSet[primitiveOffset + 1];
}

__kernel void invert_selection_kernel(
                    __global uint*  info,
                    __global float* selectionSet,
                    __global float* originalSelectionSet,
                    uint infoStride,
                    uint n
                    )
{
    uint gid = get_global_id(0);
    if (gid >= n) return;

    const uint primitiveFlag = info[gid * infoStride + 2];
    if (isPrimCulled(primitiveFlag))
        return;

    saveOriginalSelectionSet(info, selectionSet, originalSelectionSet, infoStride, gid);

    const uint primitiveOffset = info[gid * infoStride];
    const uint primitiveLength = info[gid * infoStride + 1];

    for(uint i = primitiveOffset + 1; i < primitiveOffset + primitiveLength; ++i) {
        if (getSelectFlag(selectionSet[i], SELECT_MASK_HIDDEN)) continue;

        bool selected = getSelectFlag(selectionSet[i], SELECT_MASK_SELECTED);
        setSelectFlag(&selectionSet[i], SELECT_MASK_SELECTED, !selected);
    }

    selectionSet[primitiveOffset] = selectionSet[primitiveOffset + 1];
}

__kernel void hide_selected_kernel(
                    __global uint*  info,
                    __global float* selectionSet,
                    __global float* originalSelectionSet,
                    uint infoStride,
                    uint n
                    )
{
    uint gid = get_global_id(0);
    if (gid >= n) return;

    const uint primitiveFlag = info[gid * infoStride + 2];
    if (isPrimCulled(primitiveFlag))
        return;

    saveOriginalSelectionSet(info, selectionSet, originalSelectionSet, infoStride, gid);

    const uint primitiveOffset = info[gid * infoStride];
    const uint primitiveLength = info[gid * infoStride + 1];

    for(uint i = primitiveOffset + 1; i < primitiveOffset + primitiveLength; ++i) {
        if (getSelectFlag(selectionSet[i], SELECT_MASK_HIDDEN)) continue;

        if (getSelectFlag(selectionSet[i], SELECT_MASK_SELECTED)) {
            setSelectFlag(&selectionSet[i], SELECT_MASK_SELECTED, false);
            setSelectFlag(&selectionSet[i], SELECT_MASK_HIDDEN, true);
        }
    }

    selectionSet[primitiveOffset] = selectionSet[primitiveOffset + 1];
}

__kernel void hide_unselected_kernel(
                    __global uint*  info,
                    __global float* selectionSet,
                    __global float* originalSelectionSet,
                    uint infoStride,
                    uint n
                    )
{
    uint gid = get_global_id(0);
    if (gid >= n) return;

    const uint primitiveFlag = info[gid * infoStride + 2];
    if (isPrimCulled(primitiveFlag))
        return;

    saveOriginalSelectionSet(info, selectionSet, originalSelectionSet, infoStride, gid);

    const uint primitiveOffset = info[gid * infoStride];
    const uint primitiveLength = info[gid * infoStride + 1];

    for(uint i = primitiveOffset + 1; i < primitiveOffset + primitiveLength; ++i) {
        if (getSelectFlag(selectionSet[i], SELECT_MASK_HIDDEN)) continue;

        if (!getSelectFlag(selectionSet[i], SELECT_MASK_SELECTED)) {
            setSelectFlag(&selectionSet[i], SELECT_MASK_HIDDEN, true);
        }
    }

    selectionSet[primitiveOffset] = selectionSet[primitiveOffset + 1];
}

__kernel void unhide_all_kernel(
                    __global uint*  info,
                    __global float* selectionSet,
                    __global float* originalSelectionSet,
                    uint infoStride,
                    uint n
                    )
{
    uint gid = get_global_id(0);
    if (gid >= n) return;

    const uint primitiveFlag = info[gid * infoStride + 2];
    if (isPrimCulled(primitiveFlag))
        return;

    saveOriginalSelectionSet(info, selectionSet, originalSelectionSet, infoStride, gid);

    const uint primitiveOffset = info[gid * infoStride];
    const uint primitiveLength = info[gid * infoStride + 1];

    for(uint i = primitiveOffset + 1; i < primitiveOffset + primitiveLength; ++i) {
        if (getSelectFlag(selectionSet[i], SELECT_MASK_HIDDEN)) {
            setSelectFlag(&selectionSet[i], SELECT_MASK_HIDDEN, false);
        }
    }

    selectionSet[primitiveOffset] = selectionSet[primitiveOffset + 1];
}

__kernel void invert_hidden_kernel(
                    __global uint*  info,
                    __global float* selectionSet,
                    __global float* originalSelectionSet,
                    uint infoStride,
                    uint n
                    )
{
    uint gid = get_global_id(0);
    if (gid >= n) return;

    const uint primitiveFlag = info[gid * infoStride + 2];
    if (isPrimCulled(primitiveFlag))
        return;

    saveOriginalSelectionSet(info, selectionSet, originalSelectionSet, infoStride, gid);

    const uint primitiveOffset = info[gid * infoStride];
    const uint primitiveLength = info[gid * infoStride + 1];

    for(uint i = primitiveOffset + 1; i < primitiveOffset + primitiveLength; ++i) {
        bool hidden = getSelectFlag(selectionSet[i], SELECT_MASK_HIDDEN);
        if (!hidden) {
            setSelectFlag(&selectionSet[i], SELECT_MASK_SELECTED, false);
        }

        setSelectFlag(&selectionSet[i], SELECT_MASK_HIDDEN, !hidden);
    }

    selectionSet[primitiveOffset] = selectionSet[primitiveOffset + 1];
}
