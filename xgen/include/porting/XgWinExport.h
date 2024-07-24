// Copyright 2013 Autodesk, Inc. All rights reserved. 
//
// Use of this software is subject to the terms of the Autodesk 
// license agreement provided at the time of installation or download, 
// or which otherwise accompanies this software in either electronic 
// or hard copy form.

#ifndef XgExport_h
#define XgExport_h


#if defined(_WIN32)
	// C4231: Disable warnings on extern before template instantiation
	// C4251: 'identifier' : class 'type' needs to have dll-interface to be used by clients of class 'type2'
	// - For example when exporting a class that contains a STL member we get this warning
	// C4275: non  DLL-interface classkey 'identifier' used as base for DLL-interface classkey 'identifier'
	// - For example when exporting a class that derives from boost
	#pragma warning (disable : 4231 4251 4275)
#endif

#ifndef DLL_EXPORT
	#if defined(_WIN32)
		// C4231: Disable warnings on extern before template instantiation
		// C4251: 'identifier' : class 'type' needs to have dll-interface to be used by clients of class 'type2'
		// - For example when exporting a class that contains a STL member we get this warning
		// C4275: non  DLL-interface classkey 'identifier' used as base for DLL-interface classkey 'identifier'
		// - For example when exporting a class that derives from boost
		#pragma warning (disable : 4231 4251 4275)

		#define DLL_EXPORT __declspec(dllexport)
		#define DLL_IMPORT __declspec(dllimport)
	#else
		#define DLL_EXPORT __attribute__ ((visibility ("default")))
		#define DLL_IMPORT __attribute__ ((visibility ("default")))
	#endif
#endif

/* FabricGeom */
#if defined( XGEN_FABRICGEOM_DLL )       // Defined when building FabricGeom DLL
	#define XGEN_FABRICGEOM_EXPORT DLL_EXPORT
	#define XGEN_FABRICGEOM_EXTERN
#else
	#define XGEN_FABRICGEOM_EXPORT DLL_IMPORT
	#define XGEN_FABRICGEOM_EXTERN extern
#endif

/* FabricMath */
#if defined( XGEN_FABRICMATH_DLL )       // Defined when building FabricMath DLL
	#define XGEN_FABRICMATH_EXPORT DLL_EXPORT
	#define XGEN_FABRICMATH_EXTERN
#else
	#define XGEN_FABRICMATH_EXPORT DLL_IMPORT
	#define XGEN_FABRICMATH_EXTERN extern
#endif

/* GLee */
#if defined( XGEN_GLEE_DLL )       // Defined when building GLee DLL
#define XGEN_GLEE_EXPORT DLL_EXPORT
#define XGEN_GLEE_EXTERN
#else
#define XGEN_GLEE_EXPORT DLL_IMPORT
#define XGEN_GLEE_EXTERN extern
#endif

/* libcaf */
#if defined( XGEN_LIBCAF_DLL )       // Defined when building libcaf DLL
#define XGEN_LIBCAF_EXPORT DLL_EXPORT
#define XGEN_LIBCAF_EXTERN
#else
#define XGEN_LIBCAF_EXPORT DLL_IMPORT
#define XGEN_LIBCAF_EXTERN extern
#endif

/* partio */
#if defined( XGEN_PARTIO_DLL )       // Defined when building partio DLL
#define XGEN_PARTIO_EXPORT DLL_EXPORT
#define XGEN_PARTIO_EXTERN
#else
#define XGEN_PARTIO_EXPORT DLL_IMPORT
#define XGEN_PARTIO_EXTERN extern
#endif

/* SeExpr */
#if defined( XGEN_SEEXPR_DLL )       // Defined when building SeExpr DLL
#define XGEN_SEEXPR_EXPORT DLL_EXPORT
#define XGEN_SEEXPR_EXTERN
#else
#define XGEN_SEEXPR_EXPORT DLL_IMPORT
#define XGEN_SEEXPR_EXTERN extern
#endif

/* SubEngine */
#if defined( XGEN_SUBENGINE_DLL )       // Defined when building SubEngine DLL
#define XGEN_SUBENGINE_EXPORT DLL_EXPORT
#define XGEN_SUBENGINE_EXTERN
#else
#define XGEN_SUBENGINE_EXPORT DLL_IMPORT
#define XGEN_SUBENGINE_EXTERN extern
#endif

/* XGen - the core */
#if defined( XGEN_DLL )               // Defined when building XGen DLL
#define XGEN_EXPORT DLL_EXPORT
#define XGEN_EXTERN
#else
#define XGEN_EXPORT DLL_IMPORT
#define XGEN_EXTERN extern
#endif

/* XpdFile */
#if defined( XGEN_XPDFILE_DLL )       // Defined when building XpdFile DLL
#define XGEN_XPDFILE_EXPORT DLL_EXPORT
#define XGEN_XPDFILE_EXTERN
#else
#define XGEN_XPDFILE_EXPORT DLL_IMPORT
#define XGEN_XPDFILE_EXTERN extern
#endif

/* XgUI */
#if defined( XGEN_XGUI_DLL )       // Defined when building XgUI DLL
#define XGEN_XGUI_EXPORT DLL_EXPORT
#define XGEN_XGUI_EXTERN
#else
#define XGEN_XGUI_EXPORT DLL_IMPORT
#define XGEN_XGUI_EXTERN extern
#endif

/* XgAminoOps */
#if defined( XGEN_XGAMINOOPS_DLL )  // Defined when building XgAminoOps DLL
#define XGEN_XGAMINOOPS_EXPORT DLL_EXPORT
#define XGEN_XGAMINOOPS_EXTERN
#else
#define XGEN_XGAMINOOPS_EXPORT DLL_IMPORT
#define XGEN_XGAMINOOPS_EXTERN extern
#endif

#endif // XgExport_h
