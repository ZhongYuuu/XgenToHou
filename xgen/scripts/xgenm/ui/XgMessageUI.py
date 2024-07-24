import importlib as localimplib
import sys as localsys

pkg = "xgenm.ui.Python" + str(localsys.version_info[0])
mname = '.'.join((pkg, 'XgMessageUI')).lstrip('.')
mod = localimplib.import_module(mname)

names = [x for x in mod.__dict__ if not x.startswith("_")]
globals().update({k: getattr(mod, k) for k in names})

del localsys
del localimplib
# ===========================================================================
# Copyright 2021 Autodesk, Inc. All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license
# agreement provided at the time of installation or download, or which
# otherwise accompanies this software in either electronic or hard copy form.
# ===========================================================================
