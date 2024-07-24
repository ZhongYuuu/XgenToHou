#include "XGenHairMappingTranslator.h"
#include "extension/Extension.h"

AtNode* CXgHairMappingTranslator::CreateArnoldNodes()
{
    return ProcessAOVOutput(AddArnoldNode("XGenHairMapping"));
}

void CXgHairMappingTranslator::Export(AtNode* shader)
{
    ProcessParameter(shader, "coverage", AI_TYPE_POINT2);
    ProcessParameter(shader, "translateFrame", AI_TYPE_POINT2);
    ProcessParameter(shader, "repeatUV", AI_TYPE_POINT2);
    ProcessParameter(shader, "offsetUV", AI_TYPE_POINT2, "offset");
}
