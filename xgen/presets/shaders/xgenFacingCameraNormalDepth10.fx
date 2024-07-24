//**************************************************************************/
// Copyright 2015 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk
// license agreement provided at the time of installation or download,
// or which otherwise accompanies this software in either electronic
// or hard copy form.
//**************************************************************************/

#include "SSAO_Common10.fxh"

#ifdef CLIPPING // D3D10 ONLY
    #include "Clipping10.fxh"
#endif

//
// XGen wide spline NormalDepth pass shader
//

// Uniforms
//
uniform float4x4 gWorld                 : world;
uniform float4x4 gWorldInverse          : worldinverse;
uniform float4x4 gWorldViewProjection   : worldviewprojection;
uniform float3   gViewDirection         : viewdirection;
uniform float3   gWorldCameraPosition   : worldcameraposition;
uniform float    gDepthPriority         : depthpriority;
uniform bool     gIsOrthographic        : isorthographic;
uniform float    gProjZSense            : ProjectionZSense;

// Varyings
//
struct VS_INPUT
{
    float3 Pos              : POSITION;
    float3 mayaBitangentIn  : BINORMAL;
    float2 uvCoord          : TEXCOORD0;
    float2 wCoord           : TEXCOORD1;
    float  xgenCVWidth      : TEXCOORD2;
};

struct VS_TO_GS
{
    float3 mayaTangentIn    : TANGENT;
    float3 mayaBitangentIn  : BINORMAL;
    float2 uvCoord          : TEXCOORD0;
    float2 wCoord           : TEXCOORD1;
    float  xgenCVWidth      : TEXCOORD2;
    float4 NormalDepth      : TEXCOORD3;
    float4 HPos             : SV_Position;
};

struct GS_TO_PS
{
    float4 NormalDepth      : TEXCOORD3;
#ifdef CLIPPING // D3D10 ONLY
    float4 ClipDistances0   : SV_ClipDistance0;
    float4 ClipDistances1   : SV_ClipDistance1;
#endif
    float4 HPos             : SV_Position;
};

struct pixelOut2
{
    float4 Normal           : SV_Target0;
    float4 Depth            : SV_Target1;
};

// Vertex Shader
//
float3 ixgenFacingCameraVSToGSTw(float3 Pm, float3 Bw, float4x4 worldInverse, float3 viewDirection, float3 worldCameraPosition, bool isOrthographic)
{
    // Get a view vector from camera to vertex
    float3 viewVector = Pm - mul(float4(worldCameraPosition, 1.0f), worldInverse).xyz;

    // Orthographic camera is directional
    if (isOrthographic)
    {
        float3 viewOrigin = mul(float4(0.0f, 0.0f, 0.0f, 1.0f), worldInverse).xyz;
        float3 viewTarget = mul(float4(viewDirection, 1.0f), worldInverse).xyz;
        viewVector = viewTarget - viewOrigin;
    }

    // Tangent is the cross product of view vector and bitangent
    return normalize(cross(viewVector, Bw));
}

VS_TO_GS VS_NormalDepth(VS_INPUT vsIn)
{
    VS_TO_GS vsOut;

    vsOut.mayaTangentIn   = ixgenFacingCameraVSToGSTw(vsIn.Pos, vsIn.mayaBitangentIn, gWorldInverse, gViewDirection, gWorldCameraPosition, gIsOrthographic);
    vsOut.mayaBitangentIn = normalize(vsIn.mayaBitangentIn);
    vsOut.uvCoord         = vsIn.uvCoord;
    vsOut.wCoord          = vsIn.wCoord;
    vsOut.xgenCVWidth     = vsIn.xgenCVWidth;
    vsOut.HPos            = float4(vsIn.Pos, 1.0f);

    float3 norm           = normalize(cross(vsOut.mayaTangentIn, vsOut.mayaBitangentIn));
    vsOut.NormalDepth.xyz = mul(norm, gWVITXf);
    vsOut.NormalDepth.z   = gProjZSense * vsOut.NormalDepth.z;
    vsOut.NormalDepth.w   = 0.0f;  // Fill in GS

    return vsOut;
}

// Geometry Shader
//
[maxvertexcount(4)]
void GS_NormalDepth(line VS_TO_GS gsIn[2], inout TriangleStream<GS_TO_PS> outStream)
{
    // Early Out
    if( all(gsIn[0].HPos.xyz == gsIn[1].HPos.xyz) )
    {
        return;
    }

    GS_TO_PS gsOut;
    float3 pm;

    pm = gsIn[0].HPos.xyz - gsIn[0].mayaTangentIn * gsIn[0].xgenCVWidth * 0.5f;
    gsOut.HPos = mul(float4(pm, 1.0f), gWorldViewProjection);
    gsOut.HPos.z -= gsOut.HPos.w * gDepthPriority;
    gsOut.NormalDepth.xyz = gsIn[0].NormalDepth.xyz;
    gsOut.NormalDepth.w = gProjZSense * mul(float4(pm, 1.0f), gWVXf).z;
#ifdef CLIPPING // D3D10 ONLY
    {
        float4 HPw = mul(float4(pm, 1.0f), gWXf);
        ComputeClipDistances(HPw, gsOut.ClipDistances0, gsOut.ClipDistances1);
    }
#endif
    outStream.Append(gsOut);

    pm = gsIn[0].HPos.xyz + gsIn[0].mayaTangentIn * gsIn[0].xgenCVWidth * 0.5f;
    gsOut.HPos = mul(float4(pm, 1.0f), gWorldViewProjection);
    gsOut.HPos.z -= gsOut.HPos.w * gDepthPriority;
    gsOut.NormalDepth.xyz = gsIn[0].NormalDepth.xyz;
    gsOut.NormalDepth.w = gProjZSense * mul(float4(pm, 1.0f), gWVXf).z;
#ifdef CLIPPING // D3D10 ONLY
    {
        float4 HPw = mul(float4(pm, 1.0f), gWXf);
        ComputeClipDistances(HPw, gsOut.ClipDistances0, gsOut.ClipDistances1);
    }
#endif
    outStream.Append(gsOut);

    pm = gsIn[1].HPos.xyz - gsIn[1].mayaTangentIn * gsIn[1].xgenCVWidth * 0.5f;
    gsOut.HPos = mul(float4(pm, 1.0f), gWorldViewProjection);
    gsOut.HPos.z -= gsOut.HPos.w * gDepthPriority;
    gsOut.NormalDepth.xyz = gsIn[1].NormalDepth.xyz;
    gsOut.NormalDepth.w = gProjZSense * mul(float4(pm, 1.0f), gWVXf).z;
#ifdef CLIPPING // D3D10 ONLY
    {
        float4 HPw = mul(float4(pm, 1.0f), gWXf);
        ComputeClipDistances(HPw, gsOut.ClipDistances0, gsOut.ClipDistances1);
    }
#endif
    outStream.Append(gsOut);

    pm = gsIn[1].HPos.xyz + gsIn[1].mayaTangentIn * gsIn[1].xgenCVWidth * 0.5f;
    gsOut.HPos = mul(float4(pm, 1.0f), gWorldViewProjection);
    gsOut.HPos.z -= gsOut.HPos.w * gDepthPriority;
    gsOut.NormalDepth.xyz = gsIn[1].NormalDepth.xyz;
    gsOut.NormalDepth.w = gProjZSense * mul(float4(pm, 1.0f), gWVXf).z;
#ifdef CLIPPING // D3D10 ONLY
    {
        float4 HPw = mul(float4(pm, 1.0f), gWXf);
        ComputeClipDistances(HPw, gsOut.ClipDistances0, gsOut.ClipDistances1);
    }
#endif
    outStream.Append(gsOut);

    outStream.RestartStrip();
}

// Pixel Shader
//
pixelOut2 PS_NormalDepth(GS_TO_PS psIn)
{
    pixelOut2 psOut;

    psOut.Normal = float4((normalize(psIn.NormalDepth.xyz) + 1.0f) * 0.5f, 0.0f);
    psOut.Depth  = psIn.NormalDepth.wwww;

    return psOut;
}

// Techniques
//
technique10 main
{
    pass pNormalDepth
    {
        SetVertexShader(CompileShader(vs_4_0, VS_NormalDepth()));
        SetGeometryShader(CompileShader(gs_4_0, GS_NormalDepth()));
        SetPixelShader(CompileShader(ps_4_0, PS_NormalDepth()));
    }
}


