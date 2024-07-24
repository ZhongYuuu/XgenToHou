#include "XGenSplineTranslator.h"
#include "extension/Extension.h"
#include "utils/time.h"

#include <maya/MFnDagNode.h>
#include <maya/MFnPluginData.h>
#include <maya/MPxData.h>
#include <maya/MTime.h>

#include <sstream>
#include <string>
#include <vector>


void CXgSplineDescriptionTranslator::NodeInitializer(CAbTranslator context)
{
    CExtensionAttrHelper helper = CExtensionAttrHelper(context.maya, "procedural");
    CShapeTranslator::MakeCommonAttributes(helper);

    CAttrData data;

    data.defaultValue.FLT = 0.0f;
    data.name = "aiMinPixelWidth";
    data.shortName = "ai_min_pixel_width";
    helper.MakeInputFloat(data);

    MStringArray curveTypeEnum;
    curveTypeEnum.append("Ribbon");
    curveTypeEnum.append("Thick");
    data.defaultValue.INT = 0;
    data.name = "aiMode";
    data.shortName = "ai_mode";
    data.enums= curveTypeEnum;
    helper.MakeInputEnum(data);
}

AtNode* CXgSplineDescriptionTranslator::CreateArnoldNodes()
{
    return AddArnoldNode("procedural");
}

void CXgSplineDescriptionTranslator::Export(AtNode* procedural)
{
    Update(procedural);
}

void CXgSplineDescriptionTranslator::Update(AtNode* procedural)
{
    static const std::string sDSO = std::string(getenv("MTOA_PATH")) + std::string("/procedurals/xgenSpline_procedural.so");
    MStatus status;

    MFnDagNode fnDagNode(m_dagPath);

    // Set matrix for step 0
    ExportMatrix(procedural, 0);

    // Export render flags
    ProcessRenderFlags(procedural);
    ExportLightLinking(procedural);

    // Export shaders
    MPlug shadingGroupPlug = GetNodeShadingGroup(m_dagPath.node(), 0);
    if (!shadingGroupPlug.isNull())
    {
        AtNode* shader = ExportNode(shadingGroupPlug);
        if (shader)
        {
            AiNodeSetPtr(procedural, "shader", shader);
        }
    }

    // Set node name
    {
        char buf[512];
        AiNodeSetStr(procedural, "name", NodeUniqueName(procedural, buf));
    }

    // Set procedural parameters
    {
        AiNodeSetBool(procedural, "load_at_init", true);
        AiNodeSetPnt(procedural, "min", -1.0f, -1.0f, -1.0f);
        AiNodeSetPnt(procedural, "max",  1.0f,  1.0f,  1.0f);
        AiNodeSetStr(procedural, "dso", sDSO.c_str());
    }

    // Export the sample frames
    AiNodeDeclare(procedural, "sampleTimes", "constant ARRAY FLOAT");
    if (IsMotionBlurEnabled(MTOA_MBLUR_DEFORM))
    {
        // Motion blur is enabled. Output the motion frames.
        const std::vector<double> motionFrames = GetSession()->GetMotionFrames();

        AtArray* sampleTimes = AiArrayAllocate(motionFrames.size(), 1, AI_TYPE_FLOAT);
        for (size_t i = 0; i < motionFrames.size(); i++)
            AiArraySetFlt(sampleTimes, i, float(motionFrames[i]));
        AiNodeSetArray(procedural, "sampleTimes", sampleTimes);
    }
    else
    {
        // No motion blur. Output the current frame.
        const double sampleFrame = GetExportFrame();

        AtArray* sampleTimes = AiArrayAllocate(1, 1, AI_TYPE_FLOAT);
            AiArraySetFlt(sampleTimes, 0, float(sampleFrame));
        AiNodeSetArray(procedural, "sampleTimes", sampleTimes);
    }

    // Export frame-per-second
    {
        const float fps = float(MTime(1.0, MTime::kSeconds).asUnits(MTime::uiUnit()));
        AiNodeDeclare(procedural, "fps", "constant FLOAT");
        AiNodeSetFlt(procedural, "fps", fps);
    }

    // Export the spline data (opaque)
    ExportSplineData(procedural, 0);

    // aiMinPixelWidth
    {
        AiNodeDeclare(procedural, "ai_min_pixel_width", "constant FLOAT");
        AiNodeSetFlt(procedural, "ai_min_pixel_width", fnDagNode.findPlug("ai_min_pixel_width").asFloat());
    }

    // aiMode
    {
        AiNodeDeclare(procedural, "ai_mode", "constant INT");
        AiNodeSetInt(procedural, "ai_mode", fnDagNode.findPlug("ai_mode").asInt());
    }

	// bFaceCamera
	{
		bool isFaceCamera = true;
		if (!fnDagNode.findPlug("faceCamera").isNull())
		{
			isFaceCamera = fnDagNode.findPlug("faceCamera").asBool();
		}
		AiNodeDeclare(procedural, "b_face_camera", "constant INT");
		AiNodeSetInt(procedural, "b_face_camera", isFaceCamera?1:0);
	}
}

void CXgSplineDescriptionTranslator::ExportMotion(AtNode* procedural, unsigned int step)
{
    // Check if motionblur is enabled and early out if it's not.
    if (!IsMotionBlurEnabled()) return;

    // Set transform matrix
    ExportMatrix(procedural, step);

    // Same for object deformation, early out if it's not set.
    if (!IsMotionBlurEnabled(MTOA_MBLUR_DEFORM)) return;

    ExportSplineData(procedural, step);
}

void CXgSplineDescriptionTranslator::ExportSplineData(AtNode* procedural, unsigned int step)
{
    MFnDagNode fnDagNode(m_dagPath);

    // Apply the render overrides
    static const MString sApplyRenderOverrideCmd = "xgmSplineApplyRenderOverride ";
    MGlobal::executeCommand(sApplyRenderOverrideCmd + fnDagNode.partialPathName());

    // Stream out the spline data
    std::string data;
    MPlug       outPlug = fnDagNode.findPlug("outRenderData");
    MObject     outObj  = outPlug.asMObject();
    MPxData*    outData = MFnPluginData(outObj).data();
    if (outData)
    {
        std::ostringstream opaqueStrm;
        outData->writeBinary(opaqueStrm);
        data = opaqueStrm.str();
    }

    // Compute the padding bytes and number of array elements
    const unsigned int tail    = data.size() % sizeof(unsigned int);
    const unsigned int padding = (tail > 0) ? sizeof(unsigned int) - tail : 0;
    const unsigned int nelements = data.size() / sizeof(unsigned int) + (tail > 0 ? 1 : 0);

    // Set the padding size (useless trailing bytes)
    const MString paddingParam = MString("samplePadding_") + step;
    AiNodeDeclare(procedural, paddingParam.asChar(), "constant UINT");
    AiNodeSetUInt(procedural, paddingParam.asChar(), padding);

    // Set the data as array parameter
    const MString dataParam = MString("sampleData_") + step;
    AiNodeDeclare(procedural, dataParam.asChar(), "constant ARRAY UINT");

    AtArray* dataArray = AiArrayAllocate(nelements, 1, AI_TYPE_UINT);
    memcpy(dataArray->data, &data[0], data.size());
    AiNodeSetArray(procedural, dataParam.asChar(), dataArray);
}

