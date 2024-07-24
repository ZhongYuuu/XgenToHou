#ifndef XGPRIMITIVECONTEXT_H
#define XGPRIMITIVECONTEXT_H

#include "xgen/src/sggeom/SgVec3T.h"
#include <porting/XgWinExport.h>
#include <porting/safevector.h>
#include <string>
#include "xgen/src/xgcore/XgGuide.h"
#include "xgen/src/xgtask/XgRendererContext.h"
#include "xgen/src/xgtask/XgGeneratorContext.h"
#include "xgen/src/xgtask/XgBasePrimitiveContext.h"

class XgPatch;
class XgDescription;
class XpdReader;
class XgPrimitive;
class XgExpression;
class XgFXModule;
class XgFXModuleContext;

class XGEN_EXPORT XgPrimitiveContext: public XgBasePrimitiveContext
{
	friend class XgPrimitive;
	friend class XgSplinePrimitive;
	friend class XgCardPrimitive;
	friend class XgSpherePrimitive;
	friend class XgArchivePrimitive;
	friend class XgRenderer;
	friend class XgGenerator;
	friend class XgRandomGenerator;
    friend class XgGuideGenerator;

public:
    explicit XgPrimitiveContext( XgDescription* descr );
    virtual ~XgPrimitiveContext();

    void setGeneratorContext( XgGeneratorContext& gc ) { _generatorContext = &gc; }
    XgGeneratorContext& generatorContext() { assert(_generatorContext); return *_generatorContext; }

    /** @name Motion blur control. */
    //@{
    unsigned int numSamples() const { return (unsigned int)_samples.size()+1; }
    void addSample( XgPrimitiveContext* context ) { _samples.push_back(context); }
    XgPrimitiveContext* sample( unsigned int i )
        { return (i==0 ? this : (_samples.size()>=i ? _samples[i-1] : 0)); }
    //@}

	//////////////////////////////////////////////////////////////////////////
	//						states from modifiers
	//////////////////////////////////////////////////////////////////////////

    /** @name FX Pipeline data. */
    //@{
    bool getPipeData( const std::string &name,
        safevector<SgVec3d> &val );
    void setPipeData( const std::string &name, 
        const safevector<SgVec3d> &val )
    { _pipeData[name.c_str()] = val; }
    void removePipeData( const std::string &name )
    { _pipeData.erase( name.c_str() ); }
    void removeAllPipeData()
    { _pipeData.clear(); }
    //@}

	//////////////////////////////////////////////////////////////////////////
	//						states from the base primitive
	//////////////////////////////////////////////////////////////////////////

	SgVec3d evalColor( const std::string& colorExprStr, const XgExpression& colorExpr, double u, double v, int faceId, const std::string& patchName );
    SgVec3d evalInterpGuideColor( const XgExpression& guideColorExpr, const XgPrimitive* primitive );

    /** Class for passing location of point CV attributes. */
    class Location {
    public:
        Location() {;}
        Location(const std::string &patchName, int faceId, double u, double v)
        { _patchName=patchName;_fuv.setValue((double)faceId,u,v); }
        SgVec3d &fuv() { return _fuv; }
        std::string &patchName() { return _patchName; }
    private:
        SgVec3d _fuv;
        std::string _patchName;
    };

    /** @name CV attributes */
    //@{
    /* Create and get cv attributes. */
    safevector<SgVec3d> *addCVAttr( const std::string &name,
                                    const std::string &type );
    safevector<SgVec3d> *getCVAttr( const std::string &name,
                                    const std::string &type );

    /* Locations for point cv attributes. */
    void setCVAttrLoc( const std::string &name, Location *loc=0 );
    bool getCVAttrLoc( const std::string &name, Location &loc );
    
    XgDict< safevector<SgVec3d> > &cvAttrs() { return _cvAttrs; }
    safevector< safevector<SgVec3d> * > cvAttrs( const std::string &type );

    XgDict<XgPrimitiveContext::Location> &cvAttrsLoc() { return _cvAttrsLoc; } // Turbo: new added function for multi-threaded mode.

    /* Get cv attributes that are animatable (points) in both reference and 
     * animated geometry space. 
     */
    void animatableCVAttrs( safevector< safevector<SgVec3d> > &refCVs,
                            safevector< safevector<SgVec3d> * > &animCVs );
    //@}

	/** @name Cached value accessors */
	//@{
	double cLength() const { return (_dirtyCLength?computeLength():_cLength); }
	void overrideCLength( double v ) { _cLength = v; _dirtyCLength = false;}
	void dirtyCLength() { _dirtyCLength = true; }
	double cWidth() const { return _cWidth; }
	void overrideCWidth( double v ) { _cWidth = v; }
	double cDepth() const { return _cDepth; }
	void overrideCDepth( double v ) { _cDepth = v; }
	//@}

    /** Cached attributes */
    //@{
    virtual void packAttrs( safevector<float> &data,
        SgVec3d *X=0, SgVec3d *Y=0, SgVec3d *Z=0 ) = 0;
    virtual void unpackAttrs( int version,
        const safevector<float> &data,
        unsigned int &index,
        SgVec3d *X=0, SgVec3d *Y=0, SgVec3d *Z=0 ) = 0;
    void packCVAttrs( safevector<float> &data,
                      const std::map<std::string,int> &keyToId );
    void unpackCVAttrs( const safevector<float> &data, unsigned int &index,
                        const safevector<std::string> &keys );
    //@}

	/* Allow derived classes a way to compute the length. */
	virtual double computeLength() const
	{ _dirtyCLength=false; _cLength=0.0; return _cLength; }

    /** @name Render Control Methods */
    //@{

    /* Set the patch and face for primitive geometry work. */
    virtual void setActivePatchFace( const XgPatch &patch, int faceId );
    //@}

	//////////////////////////////////////////////////////////////////////////
	//						states from descriptions
	//////////////////////////////////////////////////////////////////////////
	double lodAdjustment() const
	{ return _lodAdjustment; }
	void setLodAdjustment( double val )
	{ _lodAdjustment = val; }

	//////////////////////////////////////////////////////////////////////////
	//						states from modifiers
	//////////////////////////////////////////////////////////////////////////
	XgFXModuleContext &fxModuleContext( const XgFXModule& module );
	void addModuleContext( const XgFXModule& module );
	void removeAllModuleContext();

protected:
    virtual void evalGeomWithDisplacement( int index, double u, double v );

    XgGeneratorContext *_generatorContext;

    /** Motion samples. */
    safevector<XgPrimitiveContext*> _samples;

	//////////////////////////////////////////////////////////////////////////
	//						states from the base primitive
	//////////////////////////////////////////////////////////////////////////


	/* Cached attributes (see getNumCachedAttr()). */
	mutable double _cLength;
	double _cWidth;
	double _cDepth;
	mutable bool _dirtyCLength;



    /** Collection of cv attributes. */
    XgDict< safevector<SgVec3d> > _cvAttrs;

    /** Collection of point cv attribute locations. */
    XgDict<XgPrimitiveContext::Location> _cvAttrsLoc;

    // UV color support
    struct UVColor
    {
        static SgVec3d bad;

        double _uv[2];
        SgVec3d _color;
        bool _recurse;
        UVColor() : _recurse(false)
        {
            reset();
        }

        bool match( double u, double v, SgVec3d& color )
        {
            if ( _uv[0] != u || _uv[1] != v ) 
                return false;
            color = _color;
            return true;
        }

        void reset()
        {
            _uv[0] = _uv[1] = -1.0;
            _color = 0.0;
            _recurse = false;
        }

        void update( double u, double v, SgVec3d& color )
        {
            _uv[0] = u;
            _uv[1] = v;
            if ( !_recurse )
                _color = color;
        }

        bool& recursive()
        {
            return _recurse;
        }
    };
	UVColor _uvColor;

	//////////////////////////////////////////////////////////////////////////
	//						states from modifiers
	//////////////////////////////////////////////////////////////////////////

    /**
     * FX pipeline data. This can be used to store data that can be created
     * in one module and then used in another. It is the responsibility
     * of the FX modules to not step on each other when creating entries.
     */
    XgDict< safevector<SgVec3d> > _pipeData;

	//////////////////////////////////////////////////////////////////////////
	//						states from modifiers
	//////////////////////////////////////////////////////////////////////////
	safevector<XgFXModuleContext*> _fxModuleContexts;
    size_t _currentModuleIndex;

};

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
