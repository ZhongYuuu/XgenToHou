// Copyright 2013 Autodesk, Inc. All rights reserved. 
//
// Use of this software is subject to the terms of the Autodesk 
// license agreement provided at the time of installation or download, 
// or which otherwise accompanies this software in either electronic 
// or hard copy form.

#ifndef XGCACHEUTIL_H
#define XGCACHEUTIL_H

#include <string>
#include <string.h>
#include <map>
#include <memory>

#include "xgen/src/xgcore/alembicBaseObject.h"
#include "porting/safevector.h"
#include "porting/XgWinExport.h"
#include "xgen/src/xgcore/XgDict.h"
#include <Ptex/PtexVersion.h>

PTEX_NAMESPACE_BEGIN
class PtexTexture;
PTEX_NAMESPACE_END

using Ptex::PtexTexture;

class XgDescription;
class XgGuide;
class AlembicVisitor; 
class GeometryObject;
class XgPatch;
class SgSurface;
class XgPrimitive;

class CacheUtil
{
public:
	CacheUtil( const std::string &fileName ):_fileName(fileName){ }
	virtual ~CacheUtil() {}

	/* Read curve data from file into vectors. */
	virtual bool readPosCurves( const double frame,
						const XgDescription* description,
						safevector< safevector< SgVec3f > > &data,
						safevector<std::string> *objectNames = 0 ) = 0;
	virtual bool readPosCurves( const double frame,
						const XgDescription* description,
						safevector< safevector< SgVec3d > > &data,
						safevector<std::string> *objectNames = 0 ) = 0;
	/* Read triangle data from file */
	virtual unsigned int readTriMesh(
				const double frame,
				const XgDescription* description,
				safevector< safevector< SgVec3f > > &vertices,
				safevector< safevector<unsigned int> > &triangles,
				safevector<std::string> *objectNames = 0 ) = 0;
	virtual unsigned int readTriMesh(
				const double frame,
				const XgDescription* description,
				safevector< safevector< SgVec3d > > &vertices,
				safevector< safevector<unsigned int> > &triangles,
				safevector<std::string> *objectNames = 0 ) = 0;

	/* Read triangle data from file */
	virtual unsigned int readQuadMesh( 
				const double frame,
				const XgDescription* description,
				safevector< safevector< SgVec3f > > &vertices,
				safevector< safevector<unsigned int> > &quads,
				bool &animated,
				safevector<safevector< SgVec3f > > *colors = 0,
				safevector<safevector< SgVec3f > > *normals = 0,
				safevector<safevector< float > > *uvs = 0,
				safevector<std::string> *objectNames = 0 ) = 0;
	virtual unsigned int readQuadMesh(
				const double frame,
				const XgDescription* description,
				safevector< safevector< SgVec3d > > &vertices,
				safevector< safevector<unsigned int> > &quads,
				bool &animated, 
				safevector<safevector< SgVec3d > > *colors = 0,
				safevector<safevector< SgVec3d > > *normals = 0,
				safevector<safevector< float > > *uvs = 0,
				safevector<std::string> *objectNames = 0 ) = 0;
	
	/* Override guides with nurbs curves from file */
	virtual unsigned int overrideGuides( 
				const double frame,
				const XgDescription* _description,
				safevector<XgGuide> &_guides ) = 0;
				
	virtual unsigned int getBBox( 
				const double frame,
				const XgDescription* description,
				SgBox3d &box
					) = 0;
					
	virtual bool importGeometry( const std::string &key, double frame,
                  const std::string &interpMethod, XgDict< safevector<XgPatch *> > &patches, 
				  XgDict< SgSurface *> *currentPref, XgDict< SgSurface *> *currentGeom, bool ownPref, const double fps = 0 ) = 0;
					
	virtual bool exportGuidesAttr( XgPrimitive* prim ) = 0;

	void setObjectsList ( const safevector< std::string > &objectNames ) { _objectNames = objectNames; }
						
protected: 
	void packPixel(  SgVec3f  &color, float pix[3], int nchannels );
	void packPixel(  SgVec3d  &color, float pix[3], int nchannels );
	PtexTexture* readColorsPtex( const std::string& objPath, int& nchannels );

	safevector< std::string > _objectNames; 
	std::string _fileName; 
	
};


class CafUtil : public CacheUtil
{
public:
	CafUtil(const std::string &fileName):CacheUtil(fileName){ }

	/* Read curve data from file into vectors. */
	virtual bool readPosCurves( const double frame,
						const XgDescription* description,
						safevector< safevector< SgVec3f > > &data,
						safevector<std::string> *objectNames = 0 );

	virtual bool readPosCurves( const double frame,
						const XgDescription* description,
						safevector< safevector< SgVec3d > > &data,
						safevector<std::string> *objectNames = 0 );

	/* Read triangle data from file */
	virtual unsigned int readTriMesh(
				const double frame,
				const XgDescription* description,
				safevector< safevector< SgVec3f > > &vertices,
				safevector< safevector<unsigned int> > &triangles,
				safevector<std::string> *objectNames = 0 );

	virtual unsigned int readTriMesh(
				const double frame,
				const XgDescription* description,
				safevector< safevector< SgVec3d > > &vertices,
				safevector< safevector<unsigned int> > &triangles,
				safevector<std::string> *objectNames = 0 );

	/* Read triangle data from file */
	virtual unsigned int readQuadMesh( 
				const double frame,
				const XgDescription* description,
				safevector< safevector< SgVec3f > > &vertices,
				safevector< safevector<unsigned int> > &quads,
				bool &animated,
				safevector<safevector< SgVec3f > > *colors = 0,
				safevector<std::string> *objectNames = 0 );

	virtual unsigned int readQuadMesh(
				const double frame,
				const XgDescription* description,
				safevector< safevector< SgVec3d > > &vertices,
				safevector< safevector<unsigned int> > &quads,
				bool &animated, 
				safevector<safevector< SgVec3d > > *colors = 0,
				safevector<std::string> *objectNames = 0 );
	
	virtual unsigned int overrideGuides( 
				const double frame,
				const XgDescription* _description,
				safevector<XgGuide> &_guides );		

	virtual unsigned int getBBox( 
				const double frame,
				const XgDescription* description,
				SgBox3d &box
					);
	virtual bool importGeometry( const std::string &key, double frame,
                  const std::string &interpMethod, XgDict< safevector<XgPatch *> > &patches, 
				  XgDict< SgSurface *> *currentPref, XgDict< SgSurface *> *currentGeom, bool ownPref, const double fps = 0 );		

	bool exportGuidesAttr(  XgPrimitive* prim ){ return false; }

private:
	template <typename T>
	bool readPosCurvesT( const double frame,
						const XgDescription* description,
						safevector< safevector< SgVec3T<T> > > &data,
						safevector<std::string> *objectNames = 0 );

	template <typename T>
	unsigned int readTriMeshT(
				const double frame,
				const XgDescription* description,
				safevector< safevector< SgVec3T<T> > > &vertices,
				safevector< safevector<unsigned int> > &triangles,
				safevector<std::string> *objectNames = 0 );

	template <typename T>
	unsigned int readQuadMeshT(
				const double frame,
				const XgDescription* description,
				safevector< safevector< SgVec3T<T> > > &vertices,
				safevector< safevector<unsigned int> > &quads,
				bool &animated,
				safevector<safevector< SgVec3T<T> > > *colors = 0,
				safevector<std::string> *objectNames = 0 );

};

class AlembicUtil : public CacheUtil
{
public:
	AlembicUtil(const std::string &fileName):CacheUtil(fileName){ }

	/* Read curve data from file into vectors. */
	virtual bool readPosCurves( const double frame,
						const XgDescription* description,
						safevector< safevector< SgVec3f > > &data,
						safevector<std::string> *objectNames = 0 );

	virtual bool readPosCurves( const double frame,
						const XgDescription* description,
						safevector< safevector< SgVec3d > > &data,
						safevector<std::string> *objectNames = 0 );

	/* Read triangle data from file */
	virtual unsigned int readTriMesh(
				const double frame,
				const XgDescription* description,
				safevector< safevector< SgVec3f > > &vertices,
				safevector< safevector<unsigned int> > &triangles,
				safevector<std::string> *objectNames = 0 );

	virtual unsigned int readTriMesh(
				const double frame,
				const XgDescription* description,
				safevector< safevector< SgVec3d > > &vertices,
				safevector< safevector<unsigned int> > &triangles,
				safevector<std::string> *objectNames = 0 );

	/* Read triangle data from file */
	virtual unsigned int readQuadMesh( 
				const double frame,
				const XgDescription* description,
				safevector< safevector< SgVec3f > > &vertices,
				safevector< safevector<unsigned int> > &quads,
				bool &animated,
				safevector<safevector< SgVec3f > > *colors = 0,
				safevector<safevector< SgVec3f > > *normals = 0,
				safevector<safevector< float > > *uvs = 0,
				safevector<std::string> *objectNames = 0 );

	virtual unsigned int readQuadMesh(
				const double frame,
				const XgDescription* description,
				safevector< safevector< SgVec3d > > &vertices,
				safevector< safevector<unsigned int> > &quads,
				bool &animated, 
				safevector<safevector< SgVec3d > > *colors = 0,
				safevector<safevector< SgVec3d > > *normals = 0,
				safevector<safevector< float > > *uvs = 0,
				safevector<std::string> *objectNames = 0 );
	
	virtual unsigned int overrideGuides( 
				const double frame,
				const XgDescription* _description,
				safevector<XgGuide> &_guides );	

	virtual unsigned int getBBox( 
				const double frame,
				const XgDescription* description,
				SgBox3d &box
				);
	
	virtual bool importGeometry( const std::string &key, double frame,
                  const std::string &interpMethod, XgDict< safevector<XgPatch *> > &patches, 
				  XgDict< SgSurface *> *currentPref, XgDict< SgSurface *> *currentGeom, bool ownPref, const double fps = 0 );
	
	
	bool exportGuidesAttr( XgPrimitive* prim ); 

private: 
	unsigned int init( const double frame, const double fps, const std::string &interpMethod, AlembicVisitor &alembicHelper ); 
	bool initObject( std::shared_ptr<GeometryObject> baseObj, GeometryObject::Type type, const double frame, int &sample, safevector<std::string> *objectNames = 0, bool *animated = 0);
	bool getAttr( std::shared_ptr<GeometryObject> baseObj, const double frame, int sample, std::map<std::string,SgVec3d>& attr );
	bool getAttr( std::shared_ptr<GeometryObject> baseObj, int sample, int attrIndex, int& val);
	
	bool importGuidesAttr(AlembicVisitor &alembicVisitor, XgPatch *patch, const double frame);
	bool importGuidesAttrFromGuidesFile(AlembicVisitor &alembicVisitor, XgPatch *patch, const double frame );

	GeometryObject::Interpolation _interpType; 
	double _time;
	bool _worldSpace;
	bool _objectSpace;
	
	template <typename T>
	bool readPosCurvesT( const double frame,
						const XgDescription* description,
						safevector< safevector< SgVec3T<T> > > &data,
						safevector<std::string> *objectNames = 0 );

	template <typename T>
	unsigned int readTriMeshT(
				const double frame,
				const XgDescription* description,
				safevector< safevector< SgVec3T<T> > > &vertices,
				safevector< safevector<unsigned int> > &triangles,
				safevector<std::string> *objectNames = 0 );

	template <typename T>
	unsigned int readQuadMeshT(
				const double frame,
				const XgDescription* description,
				safevector< safevector< SgVec3T<T> > > &vertices,
				safevector< safevector<unsigned int> > &quads,
				bool &animated,
				safevector<safevector< SgVec3T<T> > > *colors = 0,
				safevector<safevector< SgVec3T<T> > > *normals = 0,
				safevector<safevector< float > > *uvs = 0,
				safevector<std::string> *objectNames = 0 );

};

class XGEN_EXPORT CacheUtilHandle
{
public:
	CacheUtilHandle( const std::string &fileName )
	{
		_cacheUtilPtr = NULL; 
		_cacheUtilPtr = createCacheUtil(fileName); 
	}
	~CacheUtilHandle()
	{
		delete _cacheUtilPtr; 
	}
	CacheUtil* getCacheUtil(){ return _cacheUtilPtr; }
	bool isValid(){ return _cacheUtilPtr != NULL; }
private:
	CacheUtilHandle(); 
	CacheUtil* createCacheUtil( const std::string &fileName );
	CacheUtil* _cacheUtilPtr;
};

class XGEN_EXPORT XgCacheState
{
public:
	virtual ~XgCacheState() = default;

	XgCacheState()
	{
		_fileTime = 0;
		_fileSize = 0;
	}

	// Method to override in descendant classes
	virtual void makeAllDirty()
	{
		_fileTime = 0;
		_fileSize = 0;
		_filePath.clear();
	}

	bool testFile( const std::string& filepath );
	void acceptFile( const std::string& filepath );

private:
	time_t		_fileTime, _tmpFileTime;
	size_t		_fileSize, _tmpFileSize;
	std::string _filePath;
};

#endif
