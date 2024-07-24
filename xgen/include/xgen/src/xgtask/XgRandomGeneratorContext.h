// ==================================================================
// Copyright 2017 Autodesk, Inc.  All rights reserved.
// 
// This computer source code  and related  instructions and comments are
// the unpublished confidential and proprietary information of Autodesk,
// Inc. and are  protected  under applicable  copyright and trade secret
// law. They may not  be disclosed to, copied or used by any third party
// without the prior written consent of Autodesk, Inc.
// ==================================================================

#ifndef XGRANDOMGENERATORCONTEXT_H
#define XGRANDOMGENERATORCONTEXT_H

#include <porting/XgWinExport.h>
#include <xgen/src/xgtask/XgGeneratorContext.h>

#include <string>

class XpdReader;


class XGEN_EXPORT XgRandomGeneratorContext : public XgGeneratorContext
{
public:
    explicit XgRandomGeneratorContext();
    virtual ~XgRandomGeneratorContext();

    /** Reset to initial state */
    void reset();

    /** File name. */
    std::string& fileName() { return _fileName; }

    /** I/O control for xuv data. */
    XpdReader*& xFile() { return _xFile; }
    std::string& currentGeom() { return _currentGeom; }
    int& blockIndex() { return _blockIndex; }

    /** Flag for indicating an error has occurred. */
    bool isErrOccurred() const { return _errOccurred; }
    void setErrOccurred() { _errOccurred = true; }

private:
    /** File name. */
    std::string _fileName;

    /** I/O control for xuv data. */
    XpdReader *_xFile;
    std::string _currentGeom;
    int _blockIndex;

    /** Flag for indicating an error has occurred. */
    bool _errOccurred;
};

#endif // XGRANDOMGENERATORCONTEXT_H
