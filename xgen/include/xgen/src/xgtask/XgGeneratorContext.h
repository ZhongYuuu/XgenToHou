#ifndef XGGENERATORCONTEXT_H
#define XGGENERATORCONTEXT_H

class XGEN_EXPORT XgGeneratorContext
{
    friend class XgGenerator;
    friend class XgFileGenerator;

public:
    XgGeneratorContext()
        : _lodWidth(0.0)
        , _numCulled(0)
    {}

    virtual ~XgGeneratorContext()
    {}

    unsigned int numCulled() const { return _numCulled; }
    void resetNumCulled() { _numCulled = 0; }
    void addNumCulled(unsigned int i) { _numCulled += i; }

private:
    double _lodWidth;

    /** Number of primitives that were culled */
    unsigned int  _numCulled;
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
