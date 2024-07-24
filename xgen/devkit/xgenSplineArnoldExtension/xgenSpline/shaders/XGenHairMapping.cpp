#include <ai.h>

AI_SHADER_NODE_EXPORT_METHODS(XGenHairMappingMtd);

enum XGenHairMappingParams
{
    p_coverage = 0,
    p_translate_frame,
    p_repeat,
    p_offset
};

inline static float Mod(float n, float d)
{
    return (n - (floor(n / d) * d));
}

node_parameters
{
    AiParameterPNT2("coverage", 1.0f, 1.0f);
    AiParameterPNT2("translateFrame", 0.0f, 0.0f);
    AiParameterPNT2("repeatUV", 1.0f, 1.0f);
    AiParameterPNT2("offsetUV", 0.0f, 0.0f);

    AiMetaDataSetBool(mds, NULL, "maya.hide", true);
}

node_initialize
{
}

node_update
{
}

node_finish
{
}

shader_evaluate
{
    const AtPoint2 coverage  = AiShaderEvalParamPnt2(p_coverage);
    const AtPoint2 translate = AiShaderEvalParamPnt2(p_translate_frame);
    const AtPoint2 repeat    = AiShaderEvalParamPnt2(p_repeat);
    const AtPoint2 offset    = AiShaderEvalParamPnt2(p_offset);
    const bool     wrapU     = false;
    const bool     wrapV     = false;

    // Is there a way to get the original sg->u and sg->v after they are
    // overwritten by aiHair node ?
    // Curve's sg->bu is not consistent between ribbon and thick mode.
    // Even in ribbon mode, it seems that sg->bu is 0 in the middle and 1 
    // on the edge. We would like 0 on the left and 1 on the right.
    // So we don't use sg->bu for the U mapping.. just ue sg->bv for length.
    const AtPoint2 inUV = {0.0f, sg->bv};

    float outU = inUV.x;
    float outV = inUV.y;

    outU -= translate.x;
    outV -= translate.y;

    // If coverage.x or coverage.y are <= 1.0f
    // Check of the wrapped u or v coordinades respectively wraps in a valid range
    // If wrap is off, check incoming coordinate is in the range [0, 1]
    if (Mod(outU, 1.0f) > coverage.x ||
        Mod(outV, 1.0f) > coverage.y ||
        (!wrapU && (outU < 0 || outU > coverage.x)) ||
        (!wrapV && (outV < 0 || outV > coverage.y)))
    {
        // We are out of the texture frame, return invalid u,v
        outU = -1000000.0f;
        outV = -1000000.0f;
    }
    else
    {
        if (coverage.x < 1.0f)
        {
            outU = Mod(outU, 1.0f);
        }

        if (coverage.y < 1.0f)
        {
            outV = Mod(outV, 1.0f);
        }

        outU /= coverage.x;
        outV /= coverage.y;

        // Apply repetition factor
        outU *= repeat.x;
        outV *= repeat.y;

        // For UVs, translate first, then rotate
        outU += offset.x;
        outV += offset.y;
    }

    sg->out.PNT2.x = outU;
    sg->out.PNT2.y = outV;
}
