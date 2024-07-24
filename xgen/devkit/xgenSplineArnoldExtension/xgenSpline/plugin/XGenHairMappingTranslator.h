#pragma once

#include "translators/shader/ShaderTranslator.h"
#include "translators/NodeTranslator.h"


class CXgHairMappingTranslator : public CShaderTranslator
{
public:
    virtual AtNode* CreateArnoldNodes();
    virtual void Export(AtNode* shader);

    static void* creator()
    {
        return new CXgHairMappingTranslator();
    }

private:
};
