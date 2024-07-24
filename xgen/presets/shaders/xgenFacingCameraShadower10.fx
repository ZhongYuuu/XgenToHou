//**************************************************************************/
// Copyright 2015 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk
// license agreement provided at the time of installation or download,
// or which otherwise accompanies this software in either electronic
// or hard copy form.
//**************************************************************************/

//
// XGen wide spline Shadow pass shader
//

// Uniforms
//
uniform float4x4 gWorld                 : world;
uniform float4x4 gWorldInverse          : worldinverse;
uniform float4x4 gWorldViewProjection   : worldviewprojection;
uniform float4x4 gViewProjection        : viewprojection; 
uniform float3   gViewDirection         : viewdirection;
uniform float3   gWorldCameraPosition   : worldcameraposition;
uniform float    gDepthPriority         : depthpriority;
uniform bool     gIsOrthographic        : isorthographic;

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
    float4 HPos             : SV_Position;
};

struct GS_TO_PS
{
    float3 Pw               : TEXCOORD2;
    float4 HPos             : SV_Position;
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

VS_TO_GS VS_Shadower(VS_INPUT vsIn)
{
    VS_TO_GS vsOut;

    vsOut.mayaTangentIn   = ixgenFacingCameraVSToGSTw(vsIn.Pos, vsIn.mayaBitangentIn, gWorldInverse, gViewDirection, gWorldCameraPosition, gIsOrthographic);
    vsOut.mayaBitangentIn = normalize(vsIn.mayaBitangentIn);
    vsOut.uvCoord         = vsIn.uvCoord;
    vsOut.wCoord          = vsIn.wCoord;
    vsOut.xgenCVWidth     = vsIn.xgenCVWidth;
    vsOut.HPos            = float4(vsIn.Pos, 1.0f);

    return vsOut;
}

// Geometry Shader
//
[maxvertexcount(4)]
void GS_Shadower(line VS_TO_GS gsIn[2], inout TriangleStream<GS_TO_PS> outStream)
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
    gsOut.Pw = mul(float4(pm, 1.0f), gWorld).xyz;
    outStream.Append(gsOut);

    pm = gsIn[0].HPos.xyz + gsIn[0].mayaTangentIn * gsIn[0].xgenCVWidth * 0.5f;
    gsOut.HPos = mul(float4(pm, 1.0f), gWorldViewProjection);
    gsOut.HPos.z -= gsOut.HPos.w * gDepthPriority;
    gsOut.Pw = mul(float4(pm, 1.0f), gWorld).xyz;
    outStream.Append(gsOut);

    pm = gsIn[1].HPos.xyz - gsIn[1].mayaTangentIn * gsIn[1].xgenCVWidth * 0.5f;
    gsOut.HPos = mul(float4(pm, 1.0f), gWorldViewProjection);
    gsOut.HPos.z -= gsOut.HPos.w * gDepthPriority;
    gsOut.Pw = mul(float4(pm, 1.0f), gWorld).xyz;
    outStream.Append(gsOut);

    pm = gsIn[1].HPos.xyz + gsIn[1].mayaTangentIn * gsIn[1].xgenCVWidth * 0.5f;
    gsOut.HPos = mul(float4(pm, 1.0f), gWorldViewProjection);
    gsOut.HPos.z -= gsOut.HPos.w * gDepthPriority;
    gsOut.Pw = mul(float4(pm, 1.0f), gWorld).xyz;
    outStream.Append(gsOut);

    outStream.RestartStrip();
}

// Pixel Shader
//
float4 mayaCreateShadowMapPS( float3 Pw, float4x4 shadowViewProj )
{
    float4 Pndc = mul( float4(Pw,1.0f), shadowViewProj );
    float retZ = Pndc.z / Pndc.w;
    retZ += fwidth(retZ);
    return (retZ).xxxx;
}

float4 PS_Shadower(GS_TO_PS psIn) : SV_Target
{
    return mayaCreateShadowMapPS(psIn.Pw, gViewProjection);
}

// Techniques
//
technique10 main
{
    pass pShadower
    {
        SetVertexShader(CompileShader(vs_4_0, VS_Shadower()));
        SetGeometryShader(CompileShader(gs_4_0, GS_Shadower()));
        SetPixelShader(CompileShader(ps_4_0, PS_Shadower()));
    }
}


