# =======================================================================
# Copyright 2020 Autodesk, Inc. All rights reserved.
#
# This computer source code and related instructions and comments are the
# unpublished confidential  and proprietary information of Autodesk, Inc.
# and are protected under applicable copyright and trade secret law. They
# may not be disclosed to, copied  or used by any third party without the
# prior written consent of Autodesk, Inc.
# =======================================================================
import maya
maya.utils.loadStringResourcesForModule(__name__)


import maya.cmds as cmds
import maya.OpenMaya as api
import traceback

__all__ = [ 'XGDebug', 'XGWarning', 'XGError', 'XGTip' ]

XGEN_LABEL = maya.stringTable[u'y_xgenm_xgLog.kXgen' ]
UNKNOWN_FILE = maya.stringTable[u'y_xgenm_xgLog.kUnknownFile' ]

def XGDebug( mesg ):
    """Log a debug message."""
    try:
        file, line = traceback.extract_stack()[-2][0:2]
    except:
        traceback.print_exc()
        file, line = UNKNOWN_FILE, 0
    api.MGlobal.displayInfo (u"{}: {} ({}:{})".format (XGEN_LABEL,mesg,file,line))

def XGWarning( mesg ):
    """Log a warning message."""
    try:
        file, line = traceback.extract_stack()[-2][0:2]
    except:
        traceback.print_exc()
        file, line = UNKNOWN_FILE, 0
    api.MGlobal.displayWarning (u"{}: {} ({}:{})".format (XGEN_LABEL,mesg,file,line))

def XGError( mesg ):
    """Log an error message."""
    try:
        file, line = traceback.extract_stack()[-2][0:2]
    except:
        traceback.print_exc()
        file, line = UNKNOWN_FILE, 0
    api.MGlobal.displayError (u"{}: {} ({}:{})".format (XGEN_LABEL,mesg,file,line))

def XGTip( mesg ):
    """Log an tip message."""
    try:
        file, line = traceback.extract_stack()[-2][0:2]
    except:
        traceback.print_exc()
        file, line = UNKNOWN_FILE, 0
    api.MGlobal.displayInfo (u"{}: {} ({}:{})".format (XGEN_LABEL,mesg,file,line))
    cmds.inViewMessage (msg=mesg, pos="midRight", fade=True)
