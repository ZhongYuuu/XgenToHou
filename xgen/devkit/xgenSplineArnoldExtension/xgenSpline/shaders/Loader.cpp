#include <ai.h>

#include <cstdio>

extern AtNodeMethods* XGenHairMappingMtd;

enum {
    SHADER_XGEN_HAIRMAPPING = 0
};

node_loader
{
    switch (i)
    {
    case SHADER_XGEN_HAIRMAPPING:
        node->methods      = XGenHairMappingMtd;
        node->output_type  = AI_TYPE_POINT2;
        node->name         = "XGenHairMapping";
        node->node_type    = AI_NODE_SHADER;
        break;

    default:
        return false;
    }

    sprintf(node->version, AI_VERSION);
    return true;
}
