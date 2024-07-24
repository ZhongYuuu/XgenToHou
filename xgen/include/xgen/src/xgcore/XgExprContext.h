// Copyright 2014 Autodesk, Inc. All rights reserved. 
//
// Use of this software is subject to the terms of the Autodesk 
// license agreement provided at the time of installation or download, 
// or which otherwise accompanies this software in either electronic 
// or hard copy form.

/**
 * @file XgExprContext.h
 * @brief Contains the per thread state when evaluate a expression.
 *
 * @author Nian Wu
 *
 * @version Created 03/18/2013
 */

#ifndef XGEXPRCONTEXT_H
#define XGEXPRCONTEXT_H

#include "xgen/src/xgcore/XgDict.h"
#include "xgen/src/sggeom/SgVec3T.h"
#include <vector>
#include <algorithm>

class XgExpression;
class XgDescription;
class XgPrimitiveContext;
class XgSeExpr;


/**
 * @brief per thread state when evaluate a expression.
 *
 * Expression belongs to description. The state inside description should be 
 * thread local when parallelize the evaluation.
 */
class XgExprContext
{
public:
	XgExprContext() :
        _patchName(NULL),
        _lastFaceId(-1),
        _lastDescriptionId(-1),
        _faceSeed(0),
        _curDescription(NULL)
	{
	}

	~XgExprContext() { }

    void reset( XgPrimitiveContext* primContext );

    // Return the primitive context associated to the given description.
    XgPrimitiveContext* primContext( XgDescription* descr );

    // Return true if we have any primitive context.
    bool primContextOk() const
    {
        return !_primContextList.empty();
    }

	// Is evaluating a nested expression
	bool inNestedExpr()
	{
		return _evaluating.size() > 1;
	}

	// Is evaluating an expression
	bool isEvaluatingExpr()
	{
		return !_evaluating.empty();
	}

	// Is evaluating an expression recursively
	bool isRecursiveEval(XgSeExpr* existExpr)
	{
        bool isExprAlreadyExsit = false;

        if ( !_evaluating.empty() )
        {
            std::vector<XgSeExpr*>::iterator it;
            it = find( _evaluating.begin(), _evaluating.end(), existExpr );
            if (it != _evaluating.end())
            {
                isExprAlreadyExsit = true;
            }
        }

        return isExprAlreadyExsit;
	}

	void intoEval(XgSeExpr* inExpr) 
    {
        _evaluating.push_back(inExpr);
    }
	
    void outEval() 
    { 
        if (!_evaluating.empty())
        {
            _evaluating.pop_back();
        }
    }


	/** For test if a expression has been evaluated. */
    std::vector<XgSeExpr*> _evaluating;

	/** The name of the patch being evaluated (may be null) */
	const std::string *_patchName;

	/** 'u' value being evaluated. */
	double _u;

	/** 'v' value being evaluated. */
	double _v;

	/** face id being evaluated. */
	int _faceId;

	/** The description owning this expression. 
	 *
	 *  For normal object attribute expression, its description is determined.
	 *  For palette attribute expression, it can be called by expression in
	 *  different description (refer to XgSeExpr::XgPalFunc). So the description
	 *  member should be TLS.
	 */
	XgDescription *_curDescription;

	/** face id being evaluated. */
	int _lastFaceId;

	/** Last description ID being evaluated. */
	int _lastDescriptionId;

	/** The name of the last patch being evaluated (may be empty) */
	std::string _lastPatchName;

	/** Random number face seed. */
	double _faceSeed;

    /** A list of primitive contexts for each motion sample */
    std::vector<XgPrimitiveContext*> _primContextList;

    /** Custom variables. */
    XgDict<SgVec3d> _customVariables;
};

#endif
