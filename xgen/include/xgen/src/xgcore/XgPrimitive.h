// Copyright 2013 Autodesk, Inc. All rights reserved. 
//
// Use of this software is subject to the terms of the Autodesk 
// license agreement provided at the time of installation or download, 
// or which otherwise accompanies this software in either electronic 
// or hard copy form.

/**
 * @file XgPrimitive.h
 * @brief Contains the declaration of the class XgPrimitive.
 *
 * <b>CONFIDENTIAL INFORMATION: This software is the confidential and
 * proprietary information of Walt Disney Animation Studios ("WDAS").
 * This software may not be used, disclosed, reproduced or distributed
 * for any purpose without prior written authorization and license
 * from WDAS. Reproduction of any section of this software must include
 * this legend and all copyright notices.
 * Copyright Disney Enterprises, Inc. All rights reserved.</b>
 *
 * @author Ernie Petti
 * @author Thomas V Thompson II
 * @author Stephen D. Bowline
 * @author Ying Liu
 *
 * @version Created 05/22/02
 */

#ifndef XGPRIMITIVE_H
#define XGPRIMITIVE_H


#include <algorithm>
#include <string>
#include "porting/safevector.h"
#include <map>
#include <set>

#include "xgen/src/xgcore/XgDict.h"
#include "xgen/src/sggeom/SgVec3T.h"
#include "xgen/src/sggeom/SgBox3T.h"
#include "xgen/src/sggeom/SgXform3T.h"
#include "xgen/src/sggeom/SgKdTreeNT.h"
#include "xgen/src/xgcore/XgGuide.h"
#include "xgen/src/xgcore/XgUtil.h"
#include "xgen/src/xgcore/XgBasePrimitive.h"
#include "xgen/src/xgcore/XgExpression.h"
#include "porting/XgWinExport.h"
#include "xgen/src/xgtask/XgPrimitiveContext.h"
#include "xgen/src/xgcore/XgDescription.h"

class XgPatch;
class XgFXModule;
class XgDescription;
class XgGenerator;
class XgPendingGuidesImp;

#ifdef _WIN32
	#ifdef min
		#pragma push_macro("min")
		#undef min
		#define POP_MIN
	#endif
#endif

/**
 * @brief A base primitive to represent primitive types.
 *
 * This class is the base class for all primitives.  It contains all attributes
 * necessary to describe the primitive that will populate a set of patches.
 */
class XGEN_EXPORT XgPrimitive : public XgBasePrimitive
{
    friend class XgPrimitiveContext;

public:

    /* Constructor. */
    XgPrimitive( XgDescription *descr, const std::string &objectType );

    /* Destructor. */
    virtual ~XgPrimitive();

    const XgPrimitiveContext* context() const { return (XgPrimitiveContext*)_context; }
    XgPrimitiveContext* context() { return (XgPrimitiveContext*)_context; }

    /* Make the cached geometry for this primitive. */
	virtual void makeGeometry( double u, double v, XgFXModule *stop=0);
	virtual void makeGeometryInParallel( XgBasePrimitiveContext& context, double u, double v, XgFXModule *stop=0);

    /* Find the appropriate guides and calculate their relative weights. */
	virtual void findGuidesAndWeights( double u, double v );
	virtual void findGuidesAndWeightsInParallel( XgBasePrimitiveContext& context, double u, double v );

    /* Orient the primitive. */
    static void orient( const SgVec3d &P, const SgVec3d &N,
                        const SgVec3d &U, const SgVec3d &V,
                        double offU, double offV, double twist,
                        double offN, double aboutN,
                        safevector<SgVec3d> &cpt,
                        bool oneHemi = true );

    /* Find the local orientation. */
    static void findOrient( safevector<SgVec3d> &cpt, const SgVec3d &N,
                            const SgVec3d &U, const SgVec3d &V,
                            double &offU, double &offV,
                            bool oneHemi = true );
    
    /** Enumerated type for the guide interpolation method being used. */
    enum InterpMethod
    {
        Attribute=0,
        CV=1,
        INVALID_IMETHOD=2
    };
    
    /** @name Render Control Methods */
    //@{
    /* Initialize and finish a description. */
    virtual void initDescription();
    virtual void initDescriptionInParallel( XgBasePrimitiveContext& context);
    virtual void finishDescription();
    virtual void finishDescriptionInParallel( XgBasePrimitiveContext& context);

    
    /* Interpolation initialization */
    virtual bool initInterpolation( const std::string &fileName );

    /* Setup interpolation structures. */
    virtual void setupInterpolation( bool quiet=false );

    /** @name Accessors */
    //@{
    InterpMethod iMethod() const { return _iMethod; }
    const XgExpression &length() const { return _length; }
    const XgExpression &width() const { return _width; }
    const XgExpression &depth() const { return _depth; }
    const XgExpression &offU() const { return _offU; }
    const XgExpression &offV() const { return _offV; }
    const XgExpression &offN() const { return _offN; }
    const XgExpression &aboutN() const { return _aboutN; }
    const std::string  &regionMap() const { return _regionMap; }
    const XgExpression &regionMask() const { return _regionMask; }
    //@}

    virtual unsigned int guideRegion(double u, double v, int faceId, const std::string& patchName);
    virtual double guideRegionMask(double u, double v, int faceId, const std::string& patchName);

    /* Copy attributes from an existing primitive. */
    void copyAttrs( XgPrimitive *prim );
    
    /** @name FX module accessors */
    //@{
    XgFXModule *addFXModule( const std::string &type );
    bool removeFXModule( const std::string &name );
    XgFXModule *findFXModule( const std::string &name, int *idx=0 ) const;
    safevector<XgFXModule *> findFXModules( const std::string &typeName, 
                                          safevector<int> &indices );
    bool moveFXModule( const std::string &name, int dir );
    bool applyFXModules( XgFXModule *stop=NULL );
	bool canRunInParallel( XgFXModule *stop=NULL );
	bool applyFXModulesParallel( XgPrimitiveContext& context, XgFXModule *stop=NULL );
    void deactivateFXModules( unsigned int i, safevector<bool> &origStatus );
    void setFXModulesStatus( unsigned int i, const safevector<bool> &status );

    int bakedGroomManagerPosition() const;

    safevector<XgFXModule *> &modules() { return _modules; }
    XgFXModule *modules( unsigned int i )
        { return (_modules.size()>i ? _modules[i] : 0); }

    std::string uniqueFXName( const std::string &name ) const;
    //@}

    /** @name Cached value accessors */
    //@{
    double cLength() const { return context()->cLength(); }
    void overrideCLength( double v ) { context()->overrideCLength(v);}
    void dirtyCLength() { context()->dirtyCLength(); }
    double cWidth() const { return context()->cWidth(); }
    void overrideCWidth( double v ) { context()->overrideCWidth(v); }
    double cDepth() const { return context()->cDepth(); }
    void overrideCDepth( double v ) { context()->overrideCDepth(v); }
    bool cullPrim() const { return context()->cullPrim(); }
    void setCullPrim( bool b ) { context()->setCullPrim(b); }

	const std::string&  colorExprStr() { return _colorExprStr; }
	const XgExpression& colorExpr() { return _colorExpr; }

	void setColorCache(const std::string& color) { _colorExprStr = color; _colorExpr = color; }
	SgVec3d evalColor( double u, double v, int faceId, const std::string& patchName ) { return context()->evalColor( _colorExprStr, _colorExpr, u, v, faceId, patchName ); }
    SgVec3d evalInterpGuideColor();
    //@}
    

    /** @name CV attributes */
    //@{
    /* Create and get cv attributes. */
    safevector<SgVec3d> *addCVAttr( const std::string &name,
                                    const std::string &type ) { return context()->addCVAttr( name, type); }
    safevector<SgVec3d> *getCVAttr( const std::string &name,
                                    const std::string &type ) { return context()->getCVAttr( name, type); }

    /* Locations for point cv attributes. */
    void setCVAttrLoc( const std::string &name, XgPrimitiveContext::Location *loc=0 ) { context()->setCVAttrLoc( name, loc); }
    bool getCVAttrLoc( const std::string &name, XgPrimitiveContext::Location &loc ) { return context()->getCVAttrLoc( name, loc); }
    
    XgDict< safevector<SgVec3d> > &cvAttrs() { return context()->cvAttrs(); }
    safevector< safevector<SgVec3d> * > cvAttrs( const std::string &type ) { return context()->cvAttrs( type ); }

    /* Get cv attributes that are animatable (points) in both reference and 
     * animated geometry space. 
     */
    void animatableCVAttrs( safevector< safevector<SgVec3d> > &refCVs,
                            safevector< safevector<SgVec3d> * > &animCVs ) { context()->animatableCVAttrs( refCVs, animCVs ); }
    //@}

	//@{
    /* Bounding box for the cached guide. */
    virtual SgBox3d guideBoundingBox( unsigned int index ) const = 0;
    /* Minimum number of CVs allowed for a guide of this primitive. */
    virtual unsigned int minGuideCVCount() const = 0;
    /* Default shape for a new guide. */
    virtual void defaultGuideGeom( XgGuide &guide ) = 0;
    /** Verify the validity of potential guide geometry. */
    virtual void verifyGuideGeom( safevector<SgVec3d> &cpts ) {}
    /** Prepare the guide cached geometry. */
    virtual void prepGuideCGeom( unsigned int index )
        { _guides[index].cGuideGeomRef() = _guides[index].iGuideGeom(); }
    /* Override guides with data from a cache file. */
    virtual bool overrideGuidesWithCache();
    //@}

    /** Pending guides */
    //@{
    void setOriginalPatchBBox(const SgVec3d& origin, const SgVec3d& offset)
    { _originalPatchBBox.setOrigin(origin); _originalPatchBBox.setOffset(offset); }
    const SgBox3d& originalPatchBBox() { return _originalPatchBBox; }
    void appendPendingGuide(unsigned int faceId, double u, double v, double patchU, double patchV,
        const SgVec3d& normal, const SgVec3d& uTangent, const SgVec3d& vTangent,
        double blend, std::string interp, safevector<SgVec3d>& cvs);
    size_t numOfPendingGuides();
    void getPendingGuide(size_t index, unsigned int* faceId, double* u, double* v,
        double* patchU, double* patchV,	SgVec3d* normal, SgVec3d* uTangent, SgVec3d* vTangent,
        safevector<SgVec3d>** cvs);
    void setPendingGuidePos(size_t index, unsigned int faceId, double u, double v,
        const SgVec3d& normal, const SgVec3d& uTangent, const SgVec3d& vTangent);
    void clearPendingGuide();
    static safevector<XgPrimitive*>& primitivesWithPendingGuides();
    static void clearPrimitivesWithPendingGuides();
    //@}

    /** Cached attributes */
    //@{
    /**
     * version 3: Add "index" and "frame" field for archive primitive. MAYA-42448 2014/11/28
     */
    virtual int versionAttrs() { return 3; }
    virtual unsigned int finalCVCount() = 0;
    void packAttrs( safevector<float> &data,
                     SgVec3d *X=0, SgVec3d *Y=0, SgVec3d *Z=0 ) { context()->packAttrs(data, X, Y, Z); }
    void unpackAttrs( int version,
                              const safevector<float> &data,
                              unsigned int &index,
                              SgVec3d *X=0, SgVec3d *Y=0, SgVec3d *Z=0 ) { context()->unpackAttrs(version, data, index, X, Y, Z); }
    void packCVAttrs( safevector<float> &data,
                      const std::map<std::string,int> &keyToId ) { context()->packCVAttrs( data, keyToId ); }
    void unpackCVAttrs( const safevector<float> &data, unsigned int &index,
                        const safevector<std::string> &keys ) { context()->unpackCVAttrs( data, index, keys ); }
    //@}

    /* Set class attributes. */
    virtual bool setAttr( const std::string &name, 
                          const std::string &value, 
                          const std::string &type="float",
			  const std::string &uiHint="" );

    /** @name IO functions */
    //@{
    bool exportFXModules( std::ostream &os ) const;
    bool exportFXModulesAsPreset( std::ostream &os, bool activeModuleOnly = false ) const;
    bool exportGuides( std::ostream &os, XgPatch *patch ) const;
    bool importGuides( std::istream &is, XgPatch *patch );
    void bindPendingGuide(size_t index, XgPatch *patch, unsigned int faceId, double u, double v,
        const SgVec3d& normal, const SgVec3d& uTangent, const SgVec3d& vTangent, bool useRawCV);
	//@}

	bool getAttrValue( const std::string& attrsName, SgVec3d& attrVal );
    bool getAttrValueInParallel( XgPrimitiveContext& context, const std::string& attrsName, SgVec3d& attrVal );
    void getFXTextures( safevector<std::string> &textures ) const;
	bool setFXTexture(const std::string& object, const std::string& attr, const std::string &texture);

	safevector<std::string> &wireNames( const std::string patchName );

    virtual void initModules() {;}
    virtual void finishModules() {;}

    virtual void getExternalContext(XgExternalContentInfoTable& table, const std::string& prefix) const;

protected:

    /** No definition by design to prevent accidental default construction. */
    XgPrimitive();
    
    /** No definition by design so accidental copying is prevented. */
    XgPrimitive( const XgPrimitive &primitive );

    /** No definition by design so accidental assignment is prevented. */
    XgPrimitive &operator=( const XgPrimitive &primitive );

    /** Opportunity for derived class to 'touch-up' after fx are applied. */
    virtual bool postApplyFX() { return true;}
    virtual bool postApplyFxInParallel(XgPrimitiveContext& context) { return true;}


    /* Allow derived classes a way to compute the length. */
    double computeLength() const
        { return context()->computeLength(); }

    /** @name Generic attributes. */
    //@{
    XgExpression _length;
    XgExpression _width;
    XgExpression _depth;
    XgExpression _offU;
    XgExpression _offV;
    XgExpression _offN;
    XgExpression _aboutN;
    //@}

    /** FX Modules. */
    safevector<XgFXModule *> _modules;

    /** Region control. */
    //@{
    bool _regionFlag;
    XgExpression _regionMask;
    XgExpression _regionExpr;
    std::string _regionMap;
    //@}

    /** Animated guide control. */
    //@{
    bool _useCache;
    std::string _cacheFileName;

	/** Flag to get the curves cv from Maya */
	bool _liveMode;

    /** Name of the anim wires. */
    safevector<std::string> _wireNames;

	XgDict< safevector<std::string> > _patchWireNames;
	
	/** Put the wireNames to the right patch */
	bool setWireNames( );

    //@}
    
	/** Guides for this primitive. */
    XgExpression _guideColorExpr;

    /** Color for this primitive. */
    std::string  _colorExprStr;
    XgExpression _colorExpr;

    /** Name of live generator. */
    std::string _liveGen;

    /** Interpolation variables. */
    //@{

    /** Interpolation method. */
    InterpMethod _iMethod;

    //@}

    SgBox3d _originalPatchBBox;
    XgPendingGuidesImp* _pendingGuides;
    static safevector<XgPrimitive*> _pendingPrimitives;
};

#ifdef POP_MIN
#pragma pop_macro("min")
#undef POP_MIN
#endif

#endif
