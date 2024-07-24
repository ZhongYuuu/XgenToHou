#-
# ==========================================================================
# Copyright (c) 2018 Autodesk, Inc.
# All rights reserved.
# 
# These coded instructions, statements, and computer programs contain
# unpublished proprietary information written by Autodesk, Inc., and are
# protected by Federal copyright law. They may not be disclosed to third
# parties or copied or duplicated in any form, in whole or in part, without
# the prior written consent of Autodesk, Inc.
# ==========================================================================
#+


cmake_minimum_required(VERSION 2.8)

# include the project setting file
include($ENV{DEVKIT_LOCATION}/cmake/pluginEntry.cmake)


# specify project name
set(PROJECT_NAME xgenMtoaExtension)


# set SOURCE_FILES
set(SOURCE_FILES
	XgMtoaExtension.cpp
	XgMtoaExtension.h
)

# set linking libraries
set(LIBRARIES
   OpenMaya
)

# Find Arnold
find_arnold()

find_package(MtoA REQUIRED)
if (MTOA_FOUND)
    set(INCLUDE_DIRS ${INCLUDE_DIRS} ${MTOA_INCLUDE_DIR})
    set(PACKAGE_LIBS ${PACKAGE_LIBS} ${MTOA_LIB_DIR})
endif()

# Build plugin
build_plugin()

