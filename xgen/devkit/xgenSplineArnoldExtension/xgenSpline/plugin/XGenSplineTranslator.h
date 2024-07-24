#pragma once

#include "translators/shape/ShapeTranslator.h"
#include "translators/NodeTranslator.h"

// Translate xgmSplineDescription shape to xgenSpline_procedural
//
class CXgSplineDescriptionTranslator : public CShapeTranslator
{
public:
    virtual AtNode* CreateArnoldNodes();
    virtual void Export(AtNode* procedural);
    virtual void Update(AtNode* procedural);
    virtual void ExportMotion(AtNode* procedural, unsigned int step);

    static void NodeInitializer(CAbTranslator context);
    static void* creator()
    {
        return new CXgSplineDescriptionTranslator();
    }

private:
    void ExportSplineData(AtNode* procedural, unsigned int step);
};
