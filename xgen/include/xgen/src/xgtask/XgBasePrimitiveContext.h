// Copyright 2015 Autodesk, Inc. All rights reserved. 
//
// Use of this software is subject to the terms of the Autodesk 
// license agreement provided at the time of installation or download, 
// or which otherwise accompanies this software in either electronic 
// or hard copy form.

#ifndef XGBASEPRIMITIVECONTEXT_H
#define XGBASEPRIMITIVECONTEXT_H

#include "xgen/src/sggeom/SgVec3T.h"
#include <porting/XgWinExport.h>
#include <porting/safevector.h>
#include <string>
#include <algorithm>
#include "xgen/src/xgcore/XgGuide.h"
#include "xgen/src/xgtask/XgRendererContext.h"

#ifdef _WIN32
    #ifdef min
        #pragma push_macro("min")
        #undef min
        #define POP_MIN
    #endif
#endif

class XgPatch;
class XgDescription;
class XgBasePrimitive;

class XGEN_EXPORT XgBasePrimitiveContext
{
	friend class XgBasePrimitive;
    friend class XgPrimitive;
	friend class XgSplinePrimitive;
	friend class XgCardPrimitive;
	friend class XgSpherePrimitive;
	friend class XgArchivePrimitive;
    friend class XgSculptPrimitive;
	friend class XgRenderer;

public:
    explicit XgBasePrimitiveContext( XgDescription* descr );
    virtual ~XgBasePrimitiveContext();

    /** Bounding box calculation. */
    virtual SgBox3d boundingBox() const = 0;

    /** Associated description of the context */
    XgDescription* description() const { return _description; }

	void setRendererContext( XgRendererContext& rc ) { _rendererContext = &rc; }
	XgRendererContext& rendererContext() { assert(_rendererContext); return *_rendererContext; }

	//////////////////////////////////////////////////////////////////////////
	//						states from the base primitive
	//////////////////////////////////////////////////////////////////////////

	double cu( bool pref=false ) const { return _cu[(pref?2:3)]; }
	double cv( bool pref=false ) const { return _cv[(pref?2:3)]; }
	const SgVec3d &cP( double u, double v, bool pref=false );
	const SgVec3d &cN( double u, double v, bool pref=false );
	const SgVec3d &cU( double u, double v, bool pref=false );
	const SgVec3d &cV( double u, double v, bool pref=false );
	const SgVec3d &cdPdu( double u, double v, bool pref=false );
	const SgVec3d &cdPdv( double u, double v, bool pref=false );
	const SgVec3d &cPg( double u, double v, bool pref=false );
	const SgVec3d &cNg( double u, double v, bool pref=false );
	const SgVec3d &cUg( double u, double v, bool pref=false );
	const SgVec3d &cVg( double u, double v, bool pref=false );
	const SgVec3d &cdPdug( double u, double v, bool pref=false );
	const SgVec3d &cdPdvg( double u, double v, bool pref=false );
	float cKu( double u, double v, bool pref=false );
	float cKv( double u, double v, bool pref=false );

	/* Helper to evaluate the patch and gather cached geometry values.*/
	void evalPatch( int index, double u, double v );
	void evalCurvature( int index, double u, double v );

	/** @name Primitive geometry */
	//@{

	/* Read-only access to the geometry. */
	const safevector<SgVec3d> &getGeom() const { return _cGeom; }

	/* Read-write access to the geometry. */
	safevector<SgVec3d> &cGeom() { return _cGeom; }
	SgVec3d &cGeom( int i ) { return _cGeom[i]; }

	/* Convert cvs to reference geometry space. */
	void toRefGeomSpace( double u, double v, safevector<SgVec3d> &refCVs );
	//@}

	/** @name Cached value accessors */
	//@{
	unsigned int id() const { return _id; }
	void resetId() { _id = 0; }
	void setId( unsigned int id ) { _id = id; }
    void incrId() { _id++; }

    bool cullPrim() const { return _cull; }
    void setCullPrim( bool b ) { _cull = b; }
	//@}


	/** @name Interpolation values */
	//@{
	const XgPatch *cPatch() const { return _cPatch; }
    void setcPatch(XgPatch &patch) { _cPatch = &patch; }
	int cFaceId() const { return _cFaceId; }
	const safevector<int> &activeGuides() { return _activeGuides; }
	const safevector<double> &weight() { return _ws; }
	double weight(unsigned int i)
	{ return _ws[std::min(i,(unsigned int)_ws.size()-1)]; }
	double weightN() { return _wn; }
	//@}

	/** @name Render Control Methods */
	//@{

	/* Set the patch and face for primitive geometry work. */
	virtual void setActivePatchFace( const XgPatch &patch, int faceId );
	//@}

	bool getAttrValue( const std::string& attrsName, SgVec3d& attrVal, const XgBasePrimitive* primitive );

	//////////////////////////////////////////////////////////////////////////
	//						states from descriptions
	//////////////////////////////////////////////////////////////////////////
	double lodAdjustment() const
	{ return _lodAdjustment; }
	void setLodAdjustment( double val )
	{ _lodAdjustment = val; }

protected:
    virtual void evalGeomWithDisplacement( int index, double u, double v );

	/** Description back pointer. */
	XgDescription* const _description;

	XgRendererContext *_rendererContext;

	//////////////////////////////////////////////////////////////////////////
	//						states from the base primitive
	//////////////////////////////////////////////////////////////////////////

	/* Cached values for pre-displacement pref[0] and base[1], and
	 * post-displacement pref[2] and base[3].
	 */
	double _cu[6];         // u coordinate of face.
	double _cv[6];         // v coordinate of face.
	SgVec3d _cU[4];        // Patch normalized dPdu.
	SgVec3d _cV[4];        // Patch normalized dPdv.
	SgVec3d _cdPdu[4];     // Patch dPdu.
	SgVec3d _cdPdv[4];     // Patch dPdv.
	SgVec3d _cN[4];        // Patch normal.
	SgVec3d _cP[4];        // Patch point.
	float _cKu[2];         // Surface curvature in u
	float _cKv[2];         // surface curvature in v


	/** Cached active patch. */
	XgPatch *_cPatch;

	/** Cached active face. */
	int _cFaceId;

    /** Cull primitive. */
    bool _cull;


	/** Id for the current cached primitive. */
	unsigned int _id;

	/** Cached geometry. */
	safevector<SgVec3d> _cGeom;

	/** Guides currently being used for the primitive. */
	safevector<int> _activeGuides;

	/** Guide weights. */
	safevector<double> _ws;

	/** Weight normalization. */
	double _wn;



	//////////////////////////////////////////////////////////////////////////
	//						states from descriptions
	//////////////////////////////////////////////////////////////////////////
	double _lodAdjustment; 
};

#ifdef POP_MIN
	#pragma pop_macro("min")
	#undef POP_MIN
#endif

#endif

// ==================================================================
// Copyright 2014 Autodesk, Inc.  All rights reserved.
// 
// This computer source code  and related  instructions and comments are
// the unpublished confidential and proprietary information of Autodesk,
// Inc. and are  protected  under applicable  copyright and trade secret
// law. They may not  be disclosed to, copied or used by any third party
// without the prior written consent of Autodesk, Inc.
// ==================================================================
