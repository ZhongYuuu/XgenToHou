#include "XGenSplineTranslator.h"
#include "XGenHairMappingTranslator.h"

#include "extension/Extension.h"

extern "C"
{
#ifdef ENABLE_XGEN
    
    DLLEXPORT void initializeExtension ( CExtension& extension )
    {
        MStatus status;

        extension.Requires ( "xgenToolkit" );
        extension.LoadArnoldPlugin("xgenSpline_shaders");

        status = extension.RegisterTranslator ( "xgmSplineDescription",
                                                "",
                                                CXgSplineDescriptionTranslator::creator,
                                                CXgSplineDescriptionTranslator::NodeInitializer );

        status = extension.RegisterTranslator ( "xgmHairMapping",
                                                "",
                                                CXgHairMappingTranslator::creator );
    }

    DLLEXPORT void deinitializeExtension ( CExtension& extension )
    {
    }

#endif
}
