// Copyright 2013 Autodesk, Inc. All rights reserved. 
//
// Use of this software is subject to the terms of the Autodesk 
// license agreement provided at the time of installation or download, 
// or which otherwise accompanies this software in either electronic 
// or hard copy form.

/**
 * @file safevector.h
 * @brief Contains the declaration of a safe for debug vector class.
 *
 * <b>CONFIDENTIAL INFORMATION: This software is the confidential and
 * proprietary information of Walt Disney Animation Studios ("WDAS").
 * This software may not be used, disclosed, reproduced or distributed
 * for any purpose without prior written authorization and license
 * from WDAS. Reproduction of any section of this software must include
 *
 * @author Brent Burley
 * @author Thomas V Thompson II
 *
 * @version Created 10/06/06
 */


//*****************************************************************************
/*!
   \file safearray.h
    Copyright 2012 Autodesk, Inc.  All rights reserved.
    Use of this software is subject to the terms of the Autodesk license agreement
    provided at the time of installation or download, or which otherwise accompanies
    this software in either electronic or hard copy form.
*/
//*****************************************************************************


#ifndef SAFEVECTOR_H
#define SAFEVECTOR_H

#include <vector>
#include <cassert>

template<typename _Tp, typename _Alloc = std::allocator<_Tp> >
using safevector = std::vector<_Tp, _Alloc>;

#endif
