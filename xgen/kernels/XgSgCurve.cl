static void passthrough(
    __global const  float*  positions,
    __global        float*  positionsOut,
             const  uint    offset,
             const  uint    cvNum)
{
    for ( uint i=0; i<cvNum; ++i )
    {
        float3 pos = vload3(offset + i, positions);
        vstore3(pos, offset + i, positionsOut);
    }
}

static float3 eval(__global float* positions, uint offset, uint length, float t)
{
    float3 pt;

    if (t < FLT_EPSILON)
    {
        pt = vload3(offset, positions);
    }
    else if (t > 0.9999999f)
    {
        pt = vload3(offset + length - 1, positions);
    }
    else
    {
        // Strech across our uniform domain and get between 0,1 for segment
        t = t * (length - 1);
        const int span = (int)t;
        t -= span;

        // Build out basis function / blending weights
        const float sixth = 1.0f / 6.0f;
        const float t2 = t * t;
        const float t3 = t2 * t;
        const float onet = 1.0f - t;
        const float N0 = onet * onet * onet;
        const float N1 = (3.0f * t3 - 6.0f * t2 + 4.0f);
        const float N2 = (-3.0f * t3 + 3.0f * t2 + 3.0f * t + 1.0f);
        const float N3 = t3;

        if (span == 0)
        {
            // construct our phantom point to ensure the curve hits the
            // first control point even though we are using a uniform bspline
            float3 p0 = vload3(offset, positions);
            float3 p1 = vload3(offset + 1, positions);
            float3 p = p0 + (p0 - p1);
            pt = N0 * p;
        }
        else
        {
            pt = N0 * vload3(offset + span - 1, positions);
        }

        pt += N1 * vload3(offset + span, positions);
        pt += N2 * vload3(offset + span + 1, positions);

        if (span + 2 == length)
        {
            // construct our phantom point to ensure the curve hits the
            // last control point even though we are using a uniform bspline
            float3 pEnd = vload3(offset + length - 1, positions);
            float3 p = vload3(offset + length - 2, positions);
            p = pEnd + (pEnd - p);
            pt += N3 * p;
        }
        else
        {
            pt += N3 * vload3(offset + span + 2, positions);
        }

        pt *= sixth;

    }

    return pt;
}

static void cutUtil(
    __global        float*  positions,
    __global        float*  tempPos,
                    uint    offset,
                    uint    cvNum,
                    float   tCut,
                    float   spans)
{
    if (spans < FLT_EPSILON)
        return;

    float param = 0.0f;
    float dt = tCut / spans;

    float3 val = 0.0f;
    for (uint i = 1; i < cvNum; i++) {
        param += dt;
        val = eval(positions, offset, cvNum, param);
        vstore3(val, offset + i, tempPos);
    }

    for (unsigned int i = 1; i < cvNum; i++) {
        vstore3(vload3(offset + i, tempPos), offset + i, positions);
    }
}

static void cut(
    __global        float*  positions,
    __global        float*  tempPos,
                    uint    offset,
                    uint    cvNum,
                    float   tCut,
                    bool    reparam)
{
    float spans = cvNum - 1.0f;

    if (reparam) {
        // replace this section when xgen rebuild is finished
        cutUtil(positions, tempPos, offset, cvNum, tCut, spans);
    } else {

        // small gives correct behavior when exact cv parameter is hit
        uint newNcv = max((uint)3, (uint)(tCut * spans + 2.0f - FLT_EPSILON));

        float3 A, B, C, P;
        if (newNcv == 3) { // does optimal job for 3 point curves after cut

                           // algorithm: move last cv to be on the original curve at
                           //   "tCut" move second to last cv according to
                           //    P = 0.25 * A + 0.5 * B + 0.25 * C, where P, the
                           //    halfway point on the curve between the last cv, C,
                           //    and last unchanged cv, A, is unchanged before and
                           //    after the manipulation to B and C.  that is, after
                           //    moving C to the new end of the curve, B is calculated
                           //    via B = 2*P - A/2 -C/2, where P was evaluated on the
                           //    original curve at the proper parameterization.

                           // position on curve corresponding to last kept cv
            A = vload3(offset, positions);
            // this will be the end point
            C = eval(positions, offset, cvNum, tCut);
            // used for calculating the second to last cv
            P = eval(positions, offset, cvNum, 0.5f * tCut);

            vstore3(C, offset + newNcv - 1, positions);
            vstore3(2.0f * P - 0.5f * (A + C), offset + newNcv - 2, positions);

        } else { // just do something reasonable

               // small here yields correct result for beta when cv
               // parameter hit exactly
            float xCut = tCut * spans - FLT_EPSILON;
            int iCut = (int)xCut;
            // this is a measure of how close C is to its neighbor - 0
            // means close, 1 means far
            float beta = xCut - iCut;
            B = vload3(offset + newNcv - 2, positions);
            A = vload3(offset + newNcv - 3, positions);

            // this will be the new end point
            C = eval(positions, offset, cvNum, tCut);

            float3 Middle = 0.5f * (A + B);
            vstore3(C, offset + newNcv - 1, positions);
            // don't move when beta=1, move linearly to Middle as beta
            // goes to zero
            vstore3(Middle + beta * (B - Middle), offset + newNcv - 2, positions);
        }

        // just stack the remaining cvs on top of one another. a better
        // solution would be to rebuild (as in reparam) but then specify
        // the v for the endpoint to be tCut.
        for (uint i = newNcv; i < cvNum; i++) {
            vstore3(C, offset + i, positions);
        }
    }
}


static float cutFromTip(
    __global        float*  positions,
    __global        float*  tempPos,
                    uint    offset,
                    uint    cvNum,
                    float   len,
                    bool    reparam)
{
    float tCut = 0.0f;       // 0 to 1 location of cut;

    // When the length to cut is too small, do nothing
    if (len < FLT_EPSILON) {
        // Still call cut to get at least the effects of the reparam to
        // maintain consistency across frames
        cut(positions, tempPos,  offset, cvNum, 1.0f, reparam);
        return 1.0f;
    }

    // calculated length to cut from the tip - This will walk down the
    // curve from the top, reversed from the cutToLength() procedure
    // above. It will stop after the goal length to cut is exceeded
    // and using linear interpolation to revise parameter estimate for
    // hitting 'length'
    float dt = 1.0f / (4.0f + cvNum * 2.0f);
    float lenSum = 0.0f;
    float3 a, b;   // test points
    float ta, tb;  // test parameter values ta < tb.

    // Start from the top and walk down
    ta = 1.0f;
    a = vload3(offset + cvNum - 1, positions);

    while (1) {
        tb = max(0.0f, ta - dt);
        b = eval(positions, offset, cvNum, tb);
        float lenSeg = length(a - b);
        lenSum += lenSeg;
        if (lenSum >= len) {
            float alpha = (lenSum - len) / lenSeg;
            tCut = tb + alpha * (ta - tb);
            break;
        }

        a = b;
        ta = tb;
        if (tb <= FLT_EPSILON) {
            // Curve is cut completely (culled), stack all cvs at the base
            float3 base = vload3(offset, positions);
            for (unsigned int i = 0; i < cvNum; i++) {
                vstore3(base, offset + i, positions);
            }
            return 0.0f;
        }
    }

    // We need to always do the cut so we have consistency across frames.
    cut(positions, tempPos, offset, cvNum, min(1.0f, tCut), reparam);
    return tCut;
}

static float cutToLength(
    __global        float*  positions,
    __global        float*  tempPos,
                    uint    offset,
                    uint    cvNum,
                    float   len,
                    bool    reparam)
{

    float tCut = 0.0f;       // 0 to 1 location of cut;

    if (len < FLT_EPSILON) {
        // Curve is cut completely (culled), stack all cvs at the base 
        float3 base = vload3(offset, positions);
        for (unsigned int i = 0; i < cvNum; i++) {
            vstore3(base, offset + i, positions);
        }
        return 0.0f;
    }

    // calculated length - stopping after goal length is exceeded and
    //                     using linear interpolation to revise parameter
    //                     estimate for hitting 'length'
    float dt = 1.0f / (4.0f + cvNum * 2.0f);
    float lenSum = 0.0f;
    float3 a, b;  // test points
    float ta, tb;  // test parameter values ta < tb.

    ta = 0.0f;
    a = vload3(offset, positions);

    while (true) {
        tb = min(1.0f, ta + dt);
        b = eval(positions, offset, cvNum, tb);
        float lenSeg = length(b - a);
        lenSum += lenSeg;
        if (lenSum >= len) {
            float alpha = (lenSum - len) / lenSeg;
            tCut = tb + alpha * (ta - tb);
            break;
        }

        a = b;
        ta = tb;
        if (tb >= 1.0f) {
            tCut = 1.0f;
            break;
        }
    }

    // We need to always do the cut so we have consistency across frames. 
    cut(positions, tempPos, offset, cvNum, min(1.0f, tCut), reparam);
    return tCut;
}

static float cpolyLength(
    __global        float*  positions,
                    uint    offset,
                    uint    cvNum )
{
    float curveLen = 0.0f;
    for (uint i = 0; i < cvNum - 1; i++) 
    {
        float3 pos1 = vload3(offset + i, positions);
        float3 pos2 = vload3(offset + i + 1, positions);
        float segLen = length(pos2 - pos1);
        curveLen += segLen;
    }
    return curveLen;
}