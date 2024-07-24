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
set(PROJECT_NAME xgenSampleModules)


# set SOURCE_FILES
set(SOURCE_FILES
	XgGravityFXModule.cpp
	XgCrossGenerator.cpp
	XgOFFRenderer.cpp 
	XgGravityFXModule.h
	XgCrossGenerator.h
	XgOFFRenderer.h 
	README.txt
	ui.py
)

# set linking libraries
set(LIBRARIES
    AdskXGen
)


# find tbb
find_tbb()

find_package(XGen REQUIRED)
if (XGEN_FOUND)
    set(INCLUDE_DIRS ${INCLUDE_DIRS} ${XGEN_INCLUDE_DIR})
    set(LIBRARY_DIRS ${LIBRARY_DIRS} ${XGEN_LIB_DIR})
endif()

find_package(Maya REQUIRED)
if (MAYA_FOUND)
	set(INCLUDE_DIRS ${INCLUDE_DIRS} ${MAYA_INCLUDE_DIR})
endif()

# Build plugin
build_plugin()

