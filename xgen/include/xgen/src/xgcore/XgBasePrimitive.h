// Copyright 2015 Autodesk, Inc. All rights reserved. 
//
// Use of this software is subject to the terms of the Autodesk 
// license agreement provided at the time of installation or download, 
// or which otherwise accompanies this software in either electronic 
// or hard copy form.

#ifndef XGBASEPRIMITIVE_H
#define XGBASEPRIMITIVE_H   

#include <string>
#include <map>
#include "porting/safevector.h"

#include "xgen/src/xgcore/XgDict.h"
#include "xgen/src/sggeom/SgVec3T.h"
#include "xgen/src/sggeom/SgBox3T.h"
#include "xgen/src/sggeom/SgXform3T.h"
#include "xgen/src/sggeom/SgKdTreeNT.h"
#include "xgen/src/xgcore/XgGuide.h"
#include "xgen/src/xgcore/XgUtil.h"
#include "xgen/src/xgcore/XgObject.h"
#include "porting/XgWinExport.h"
#include "xgen/src/xgtask/XgBasePrimitiveContext.h"
#include "xgen/src/xgcore/XgDescription.h"

#include "tbb/concurrent_unordered_map.h"
#include "tbb/concurrent_unordered_set.h"

class XgPatch;
class XgDescription;

#ifdef _WIN32
	#ifdef min
		#pragma push_macro("min")
		#undef min
		#define POP_MIN
	#endif
#endif

class XgFXModule;

/**
 * @brief A base primitive to represent primitive types.
 *
 * This class is the base class for all primitives.  It contains all attributes
 * necessary to describe the primitive that will populate a set of patches.
 */
class XGEN_EXPORT XgBasePrimitive : public XgObject
{
    friend class XgBasePrimitiveContext;

public:

    /* Constructor. */
    XgBasePrimitive( XgDescription *descr );

    /* Destructor. */
    virtual ~XgBasePrimitive();

    /** Bounding box calculation. */
	SgBox3d boundingBox() const { return _context->boundingBox(); };

    /* Make the cached geometry for this primitive. */
	virtual void makeGeometry( double u, double v, XgFXModule *stop=0) = 0;
	virtual void makeGeometryInParallel( XgBasePrimitiveContext& context, double u, double v, XgFXModule *stop=0) = 0;

    /* Get the maximum CV count for active guides. */
    unsigned int maximumCVCount();
    unsigned int maximumCVCountInParallel( XgBasePrimitiveContext& context );
    
    /* Find the appropriate guides and calculate their relative weights. */
	virtual void findGuidesAndWeights( double u, double v );
	virtual void findGuidesAndWeightsInParallel( XgBasePrimitiveContext& context, double u, double v );

    virtual unsigned int guideRegion(double u, double v, int faceId, const std::string& patchName) { return 0; }
    virtual double guideRegionMask(double u, double v, int faceId, const std::string& patchName) { return 1.0; }

    /** @name Render Control Methods */
    //@{
    /* Initialize and finish a description. */
    virtual void initDescription();
    virtual void initDescriptionInParallel( XgBasePrimitiveContext& context);
    virtual void finishDescription();
    virtual void finishDescriptionInParallel( XgBasePrimitiveContext& context);

	XgBasePrimitiveContext* cloneContext()
	{
		XgBasePrimitiveContext* context = cloneContextImp();
		// copy states from the description
		context->setLodAdjustment(context->description()->lodAdjustment());
		return context;
	}

	XgBasePrimitiveContext* context() { return _context; }

    /* Setup interpolation structures. */
    virtual void setupInterpolation( bool quiet=false );
    
    /* Set the patch and face for primitive geometry work. */
    void setActivePatchFace( const XgPatch &patch, int faceId ) { _context->setActivePatchFace( patch, faceId ); }
    //@}
    
    /* Interpolation initialization */
    virtual bool initInterpolation( const std::string &fileName );

    /** Clear out candidate guides if face binding changes. */
    void clearCandidates() { _candidateGuides.clear(); }

    /** @name Cached value accessors */
    //@{
    unsigned int id() const { return _context->id(); }
    void resetId() { _context->resetId(); }
    void setId( unsigned int id ) { _context->setId(id); }
    void incrId() { _context->incrId(); }

    double cu( bool pref=false ) const { return _context->cu(pref); }
    double cv( bool pref=false ) const { return _context->cv(pref); }
    const SgVec3d &cP( double u, double v, bool pref=false ) { return _context->cP(u, v, pref); }
    const SgVec3d &cN( double u, double v, bool pref=false ) { return _context->cN(u, v, pref); }
    const SgVec3d &cU( double u, double v, bool pref=false ) { return _context->cU(u, v, pref); }
    const SgVec3d &cV( double u, double v, bool pref=false ) { return _context->cV(u, v, pref); }
    const SgVec3d &cdPdu( double u, double v, bool pref=false ) { return _context->cdPdu(u, v, pref); }
    const SgVec3d &cdPdv( double u, double v, bool pref=false ) { return _context->cdPdv(u, v, pref); }
    const SgVec3d &cPg( double u, double v, bool pref=false ) { return _context->cPg(u, v, pref); }
    const SgVec3d &cNg( double u, double v, bool pref=false ) { return _context->cNg(u, v, pref); }
    const SgVec3d &cUg( double u, double v, bool pref=false ) { return _context->cUg(u, v, pref); }
    const SgVec3d &cVg( double u, double v, bool pref=false ) { return _context->cVg(u, v, pref); }
    const SgVec3d &cdPdug( double u, double v, bool pref=false ) { return _context->cdPdug(u, v, pref); }
    const SgVec3d &cdPdvg( double u, double v, bool pref=false ) { return _context->cdPdvg(u, v, pref); }
    float cKu( double u, double v, bool pref=false ) { return _context->cKu(u, v, pref); }
    float cKv( double u, double v, bool pref=false ) { return _context->cKv(u, v, pref); }

    //@}
    
    /** @name Primitive geometry */
    //@{

    /* Read-only access to the geometry. */
    const safevector<SgVec3d> &getGeom() const { return _context->getGeom(); }

    /* Read-write access to the geometry. */
    safevector<SgVec3d> &cGeom() { return _context->cGeom(); }
    SgVec3d &cGeom( int i ) { return _context->cGeom(i); }

    /* Convert cvs to reference geometry space. */
    void toRefGeomSpace( double u, double v, safevector<SgVec3d> &refCVs ) { return _context->toRefGeomSpace(u, v, refCVs); }
    //@}
    
	//@{
    /* Bounding box for the cached guide. */
    virtual SgBox3d guideBoundingBox( unsigned int index ) const = 0;
    /* Minimum number of CVs allowed for a guide of this primitive. */
    virtual unsigned int minGuideCVCount() const = 0;
    /* Default shape for a new guide. */
    virtual void defaultGuideGeom( XgGuide &guide ) = 0;
    /* Transform guides to surface. */
    void transformGuidesToSurface();
    /* Strip guides that use a given patch. */
    void stripGuidePatch( const XgPatch *patch );
    /** Verify the validity of potential guide geometry. */
    virtual void verifyGuideGeom( safevector<SgVec3d> &cpts ) {}
    /** Prepare the guide cached geometry. */
    virtual void prepGuideCGeom( unsigned int index )
        { _guides[index].cGuideGeomRef() = _guides[index].iGuideGeom(); }
    /* Create guides based on another primitives guides. */
    bool newCopiedGuides( XgBasePrimitive *otherPrim );

	/** Resize the guide array (prepare for pushing new guides.) */
	void setGuideCount( unsigned int count ) { _guides.resize( count ); }
	/** Reserve space for guides during import. */
	void reserveGuideSpace( unsigned int count ) { _guides.reserve( count ); }
	/** Get the number of guides. */
	int numGuides() { return (int)_guides.size(); }
	/** Get a guide from the primitive. */
	XgGuide *guide( unsigned int i ) { return (i<_guides.size() ? &_guides[i] : NULL); }
	const XgGuide *guide( unsigned int i ) const { return (i<_guides.size() ? &_guides[i] : NULL); }
	XgGuide *guide( const std::string& id );
    //@}

    /** @name Interpolation values */
    //@{
    const XgPatch *cPatch() const { return _context->cPatch(); }
    void setcPatch(XgPatch &patch) { _context->setcPatch(patch); }
    int cFaceId() const { return _context->cFaceId(); }
    const safevector<int> &activeGuides() { return _context->activeGuides(); }
    const safevector<double> &weight() { return _context->weight(); }
    double weight(unsigned int i) { return _context->weight(i); }
    double weightN() { return _context->weightN(); }
    //@}

    /* Set class attributes. */
    virtual bool setAttr( const std::string &name, 
                          const std::string &value, 
                          const std::string &type="float",
			  const std::string &uiHint="" );
    
    /** Return the name of this type of primitive. */
    virtual std::string typeName() const = 0;

    virtual void getExternalContext(XgExternalContentInfoTable& table, const std::string& prefix) const;

protected:

    /** No definition by design to prevent accidental default construction. */
    XgBasePrimitive();
    
    /** No definition by design so accidental copying is prevented. */
    XgBasePrimitive( const XgBasePrimitive &primitive );

    /** No definition by design so accidental assignment is prevented. */
    XgBasePrimitive &operator=( const XgBasePrimitive &primitive );

	virtual XgBasePrimitiveContext* cloneContextImp() = 0;

    /* Helper to evaluate the patch and gather cached geometry values.*/
    void evalPatch( int index, double u, double v ) { _context->evalPatch(index, u, v); }
    void evalCurvature( int index, double u, double v ) { _context->evalCurvature(index, u, v); }

    /* Calculate the weights for interpolation. */
    void calcCVWeights( double u, double v );
	void calcCVWeightsInParallel( XgBasePrimitiveContext& context, double u, double v );

    /** Let derived class build its type specific geometry. */
    virtual void mkGeometry( double u, double v ) = 0;
	virtual void mkGeometryInParallel( XgBasePrimitiveContext& context, double u, double v )
	{}

    /* Interpolation initialization. */
    void gatherNeighbors( safevector<SgVec3d> &basePoint,
                          safevector<SgVec3d> &norm,
                          safevector< tbb::concurrent_unordered_set<int> > &neighbor );
    void processGuides( const safevector<SgVec3d> &basePoint,
                        const safevector<SgVec3d> &norm,
                        const safevector< tbb::concurrent_unordered_set<int> > &neighbor,
                        const std::string &fileName );



	XgBasePrimitiveContext* _context;

    safevector<std::string> _patchNames;
    //@}
    
	/** Guides for this primitive. */
	safevector<XgGuide> _guides;

    /** Interpolation variables. */
    //@{

    /** Candidate guides per face. */
	/* Written in:
	 * XgBasePrimitive::setupInterpolation()
	 * XgBasePrimitive::clearCandidates()
	 */
    XgDict< std::map< int, safevector<int> > > _candidateGuides;
    //@}
};

#ifdef POP_MIN
#pragma pop_macro("min")
#undef POP_MIN
#endif

#endif
