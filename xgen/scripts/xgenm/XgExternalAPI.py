# This file was automatically generated by SWIG (http://www.swig.org).
# Version 4.0.1
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.

from sys import version_info as _swig_python_version_info
if _swig_python_version_info < (2, 7, 0):
    raise RuntimeError("Python 2.7 or later required")

# Import the low-level C/C++ module
if __package__ or "." in __name__:
    import importlib as localimplib

    pkg = "xgenm.Python" + str(_swig_python_version_info[0])
    mname = '.'.join((pkg, '_XgExternalAPI')).lstrip('.')
    _XgExternalAPI = localimplib.import_module(mname)

    del localimplib
else:
    import _XgExternalAPI

try:
    import builtins as __builtin__
except ImportError:
    import __builtin__

_swig_new_instance_method = _XgExternalAPI.SWIG_PyInstanceMethod_New
_swig_new_static_method = _XgExternalAPI.SWIG_PyStaticMethod_New

def _swig_repr(self):
    try:
        strthis = "proxy of " + self.this.__repr__()
    except __builtin__.Exception:
        strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)


def _swig_setattr_nondynamic_instance_variable(set):
    def set_instance_attr(self, name, value):
        if name == "thisown":
            self.this.own(value)
        elif name == "this":
            set(self, name, value)
        elif hasattr(self, name) and isinstance(getattr(type(self), name), property):
            set(self, name, value)
        else:
            raise AttributeError("You cannot add instance attributes to %s" % self)
    return set_instance_attr


def _swig_setattr_nondynamic_class_variable(set):
    def set_class_attr(cls, name, value):
        if hasattr(cls, name) and not isinstance(getattr(cls, name), property):
            set(cls, name, value)
        else:
            raise AttributeError("You cannot add class attributes to %s" % cls)
    return set_class_attr


def _swig_add_metaclass(metaclass):
    """Class decorator for adding a metaclass to a SWIG wrapped class - a slimmed down version of six.add_metaclass"""
    def wrapper(cls):
        return metaclass(cls.__name__, cls.__bases__, cls.__dict__.copy())
    return wrapper


class _SwigNonDynamicMeta(type):
    """Meta class to enforce nondynamic attributes (no new attributes) for a class"""
    __setattr__ = _swig_setattr_nondynamic_class_variable(type.__setattr__)


class SwigPyIterator(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc="The membership flag")

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined - class is abstract")
    __repr__ = _swig_repr
    __swig_destroy__ = _XgExternalAPI.delete_SwigPyIterator
    value = _swig_new_instance_method(_XgExternalAPI.SwigPyIterator_value)
    incr = _swig_new_instance_method(_XgExternalAPI.SwigPyIterator_incr)
    decr = _swig_new_instance_method(_XgExternalAPI.SwigPyIterator_decr)
    distance = _swig_new_instance_method(_XgExternalAPI.SwigPyIterator_distance)
    equal = _swig_new_instance_method(_XgExternalAPI.SwigPyIterator_equal)
    copy = _swig_new_instance_method(_XgExternalAPI.SwigPyIterator_copy)
    next = _swig_new_instance_method(_XgExternalAPI.SwigPyIterator_next)
    __next__ = _swig_new_instance_method(_XgExternalAPI.SwigPyIterator___next__)
    previous = _swig_new_instance_method(_XgExternalAPI.SwigPyIterator_previous)
    advance = _swig_new_instance_method(_XgExternalAPI.SwigPyIterator_advance)
    __eq__ = _swig_new_instance_method(_XgExternalAPI.SwigPyIterator___eq__)
    __ne__ = _swig_new_instance_method(_XgExternalAPI.SwigPyIterator___ne__)
    __iadd__ = _swig_new_instance_method(_XgExternalAPI.SwigPyIterator___iadd__)
    __isub__ = _swig_new_instance_method(_XgExternalAPI.SwigPyIterator___isub__)
    __add__ = _swig_new_instance_method(_XgExternalAPI.SwigPyIterator___add__)
    __sub__ = _swig_new_instance_method(_XgExternalAPI.SwigPyIterator___sub__)
    def __iter__(self):
        return self

# Register SwigPyIterator in _XgExternalAPI:
_XgExternalAPI.SwigPyIterator_swigregister(SwigPyIterator)

class IntVector(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc="The membership flag")
    __repr__ = _swig_repr
    iterator = _swig_new_instance_method(_XgExternalAPI.IntVector_iterator)
    def __iter__(self):
        return self.iterator()
    __nonzero__ = _swig_new_instance_method(_XgExternalAPI.IntVector___nonzero__)
    __bool__ = _swig_new_instance_method(_XgExternalAPI.IntVector___bool__)
    __len__ = _swig_new_instance_method(_XgExternalAPI.IntVector___len__)
    __getslice__ = _swig_new_instance_method(_XgExternalAPI.IntVector___getslice__)
    __setslice__ = _swig_new_instance_method(_XgExternalAPI.IntVector___setslice__)
    __delslice__ = _swig_new_instance_method(_XgExternalAPI.IntVector___delslice__)
    __delitem__ = _swig_new_instance_method(_XgExternalAPI.IntVector___delitem__)
    __getitem__ = _swig_new_instance_method(_XgExternalAPI.IntVector___getitem__)
    __setitem__ = _swig_new_instance_method(_XgExternalAPI.IntVector___setitem__)
    pop = _swig_new_instance_method(_XgExternalAPI.IntVector_pop)
    append = _swig_new_instance_method(_XgExternalAPI.IntVector_append)
    empty = _swig_new_instance_method(_XgExternalAPI.IntVector_empty)
    size = _swig_new_instance_method(_XgExternalAPI.IntVector_size)
    swap = _swig_new_instance_method(_XgExternalAPI.IntVector_swap)
    begin = _swig_new_instance_method(_XgExternalAPI.IntVector_begin)
    end = _swig_new_instance_method(_XgExternalAPI.IntVector_end)
    rbegin = _swig_new_instance_method(_XgExternalAPI.IntVector_rbegin)
    rend = _swig_new_instance_method(_XgExternalAPI.IntVector_rend)
    clear = _swig_new_instance_method(_XgExternalAPI.IntVector_clear)
    get_allocator = _swig_new_instance_method(_XgExternalAPI.IntVector_get_allocator)
    pop_back = _swig_new_instance_method(_XgExternalAPI.IntVector_pop_back)
    erase = _swig_new_instance_method(_XgExternalAPI.IntVector_erase)

    def __init__(self, *args):
        _XgExternalAPI.IntVector_swiginit(self, _XgExternalAPI.new_IntVector(*args))
    push_back = _swig_new_instance_method(_XgExternalAPI.IntVector_push_back)
    front = _swig_new_instance_method(_XgExternalAPI.IntVector_front)
    back = _swig_new_instance_method(_XgExternalAPI.IntVector_back)
    assign = _swig_new_instance_method(_XgExternalAPI.IntVector_assign)
    resize = _swig_new_instance_method(_XgExternalAPI.IntVector_resize)
    insert = _swig_new_instance_method(_XgExternalAPI.IntVector_insert)
    reserve = _swig_new_instance_method(_XgExternalAPI.IntVector_reserve)
    capacity = _swig_new_instance_method(_XgExternalAPI.IntVector_capacity)

# Register IntVector in _XgExternalAPI:
_XgExternalAPI.IntVector_swigregister(IntVector)

class StringVector(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc="The membership flag")
    __repr__ = _swig_repr
    iterator = _swig_new_instance_method(_XgExternalAPI.StringVector_iterator)
    def __iter__(self):
        return self.iterator()
    __nonzero__ = _swig_new_instance_method(_XgExternalAPI.StringVector___nonzero__)
    __bool__ = _swig_new_instance_method(_XgExternalAPI.StringVector___bool__)
    __len__ = _swig_new_instance_method(_XgExternalAPI.StringVector___len__)
    __getslice__ = _swig_new_instance_method(_XgExternalAPI.StringVector___getslice__)
    __setslice__ = _swig_new_instance_method(_XgExternalAPI.StringVector___setslice__)
    __delslice__ = _swig_new_instance_method(_XgExternalAPI.StringVector___delslice__)
    __delitem__ = _swig_new_instance_method(_XgExternalAPI.StringVector___delitem__)
    __getitem__ = _swig_new_instance_method(_XgExternalAPI.StringVector___getitem__)
    __setitem__ = _swig_new_instance_method(_XgExternalAPI.StringVector___setitem__)
    pop = _swig_new_instance_method(_XgExternalAPI.StringVector_pop)
    append = _swig_new_instance_method(_XgExternalAPI.StringVector_append)
    empty = _swig_new_instance_method(_XgExternalAPI.StringVector_empty)
    size = _swig_new_instance_method(_XgExternalAPI.StringVector_size)
    swap = _swig_new_instance_method(_XgExternalAPI.StringVector_swap)
    begin = _swig_new_instance_method(_XgExternalAPI.StringVector_begin)
    end = _swig_new_instance_method(_XgExternalAPI.StringVector_end)
    rbegin = _swig_new_instance_method(_XgExternalAPI.StringVector_rbegin)
    rend = _swig_new_instance_method(_XgExternalAPI.StringVector_rend)
    clear = _swig_new_instance_method(_XgExternalAPI.StringVector_clear)
    get_allocator = _swig_new_instance_method(_XgExternalAPI.StringVector_get_allocator)
    pop_back = _swig_new_instance_method(_XgExternalAPI.StringVector_pop_back)
    erase = _swig_new_instance_method(_XgExternalAPI.StringVector_erase)

    def __init__(self, *args):
        _XgExternalAPI.StringVector_swiginit(self, _XgExternalAPI.new_StringVector(*args))
    push_back = _swig_new_instance_method(_XgExternalAPI.StringVector_push_back)
    front = _swig_new_instance_method(_XgExternalAPI.StringVector_front)
    back = _swig_new_instance_method(_XgExternalAPI.StringVector_back)
    assign = _swig_new_instance_method(_XgExternalAPI.StringVector_assign)
    resize = _swig_new_instance_method(_XgExternalAPI.StringVector_resize)
    insert = _swig_new_instance_method(_XgExternalAPI.StringVector_insert)
    reserve = _swig_new_instance_method(_XgExternalAPI.StringVector_reserve)
    capacity = _swig_new_instance_method(_XgExternalAPI.StringVector_capacity)

# Register StringVector in _XgExternalAPI:
_XgExternalAPI.StringVector_swigregister(StringVector)

class IntSet(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc="The membership flag")
    __repr__ = _swig_repr
    iterator = _swig_new_instance_method(_XgExternalAPI.IntSet_iterator)
    def __iter__(self):
        return self.iterator()
    __nonzero__ = _swig_new_instance_method(_XgExternalAPI.IntSet___nonzero__)
    __bool__ = _swig_new_instance_method(_XgExternalAPI.IntSet___bool__)
    __len__ = _swig_new_instance_method(_XgExternalAPI.IntSet___len__)
    append = _swig_new_instance_method(_XgExternalAPI.IntSet_append)
    __contains__ = _swig_new_instance_method(_XgExternalAPI.IntSet___contains__)
    __getitem__ = _swig_new_instance_method(_XgExternalAPI.IntSet___getitem__)
    add = _swig_new_instance_method(_XgExternalAPI.IntSet_add)
    discard = _swig_new_instance_method(_XgExternalAPI.IntSet_discard)

    def __init__(self, *args):
        _XgExternalAPI.IntSet_swiginit(self, _XgExternalAPI.new_IntSet(*args))
    empty = _swig_new_instance_method(_XgExternalAPI.IntSet_empty)
    size = _swig_new_instance_method(_XgExternalAPI.IntSet_size)
    clear = _swig_new_instance_method(_XgExternalAPI.IntSet_clear)
    swap = _swig_new_instance_method(_XgExternalAPI.IntSet_swap)
    count = _swig_new_instance_method(_XgExternalAPI.IntSet_count)
    begin = _swig_new_instance_method(_XgExternalAPI.IntSet_begin)
    end = _swig_new_instance_method(_XgExternalAPI.IntSet_end)
    rbegin = _swig_new_instance_method(_XgExternalAPI.IntSet_rbegin)
    rend = _swig_new_instance_method(_XgExternalAPI.IntSet_rend)
    erase = _swig_new_instance_method(_XgExternalAPI.IntSet_erase)
    find = _swig_new_instance_method(_XgExternalAPI.IntSet_find)
    lower_bound = _swig_new_instance_method(_XgExternalAPI.IntSet_lower_bound)
    upper_bound = _swig_new_instance_method(_XgExternalAPI.IntSet_upper_bound)
    equal_range = _swig_new_instance_method(_XgExternalAPI.IntSet_equal_range)
    insert = _swig_new_instance_method(_XgExternalAPI.IntSet_insert)

# Register IntSet in _XgExternalAPI:
_XgExternalAPI.IntSet_swigregister(IntSet)


__all__ = ['createDescription','createPalette',
           'deletePalette','deleteDescription',
           'palettes','descriptions','palette','getActive','setActive',
           'objects','initInterpolation',
           'attrExists','getAttr','setAttr','setTextureAttr','attrs','addCustomAttr',
           'remCustomAttr','customAttrs','allAttrs','getAttrFromFile',
           'objNameSpace','stripNameSpace','objBaseNameSpace',
           'availableModules', 'fxModules',
           'fxModuleType','addFXModule','removeFXModule',
           'moveFXModule', 'fxModuleIncludedInPreset',
           'culledPrimPatches','culledPrimFaces','culledPrims',
           'boundGeometry','boundFaces',
           'importPalette','exportPalette','initSnapshot','canCreateDelta','createDelta','applyDelta',
           'importDescription','exportDescription','importDescriptionAsPreset','exportDescriptionAsPreset','importFXModule',
           'exportFXModule',
           'setMessageLevel','getMessageLevel',
           'rootDir','iconDir','docsDir','version','globalRepo','localRepo', 'initConfig', 'setProjectPath','getProjectPath',
           'userRepo','fileCleanup','promoteFunc','prepForEditor','prepForAttribute', 'expandFilepath', 'findFileInXgDataPath']

createDescription = _XgExternalAPI.createDescription
createPalette = _XgExternalAPI.createPalette
deletePalette = _XgExternalAPI.deletePalette
deleteDescription = _XgExternalAPI.deleteDescription
palettes = _XgExternalAPI.palettes
descriptions = _XgExternalAPI.descriptions
palette = _XgExternalAPI.palette
getActive = _XgExternalAPI.getActive
setActive = _XgExternalAPI.setActive
objects = _XgExternalAPI.objects
initInterpolation = _XgExternalAPI.initInterpolation
attrExists = _XgExternalAPI.attrExists
getAttr = _XgExternalAPI.getAttr
setAttr = _XgExternalAPI.setAttr
setTextureAttr = _XgExternalAPI.setTextureAttr
attrs = _XgExternalAPI.attrs
addCustomAttr = _XgExternalAPI.addCustomAttr
remCustomAttr = _XgExternalAPI.remCustomAttr
customAttrs = _XgExternalAPI.customAttrs
allAttrs = _XgExternalAPI.allAttrs
getAttrFromFile = _XgExternalAPI.getAttrFromFile
objNameSpace = _XgExternalAPI.objNameSpace
objBaseNameSpace = _XgExternalAPI.objBaseNameSpace
stripNameSpace = _XgExternalAPI.stripNameSpace
availableModules = _XgExternalAPI.availableModules
fxModules = _XgExternalAPI.fxModules
fxModuleType = _XgExternalAPI.fxModuleType
addFXModule = _XgExternalAPI.addFXModule
removeFXModule = _XgExternalAPI.removeFXModule
moveFXModule = _XgExternalAPI.moveFXModule
fxModuleIncludedInPreset = _XgExternalAPI.fxModuleIncludedInPreset
culledPrimPatches = _XgExternalAPI.culledPrimPatches
culledPrimFaces = _XgExternalAPI.culledPrimFaces
culledPrims = _XgExternalAPI.culledPrims
boundGeometry = _XgExternalAPI.boundGeometry
boundFaces = _XgExternalAPI.boundFaces
importPalette = _XgExternalAPI.importPalette
exportPalette = _XgExternalAPI.exportPalette
initSnapshot = _XgExternalAPI.initSnapshot
canCreateDelta = _XgExternalAPI.canCreateDelta
createDelta = _XgExternalAPI.createDelta
applyDelta = _XgExternalAPI.applyDelta
importDescription = _XgExternalAPI.importDescription
exportDescription = _XgExternalAPI.exportDescription
importDescriptionAsPreset = _XgExternalAPI.importDescriptionAsPreset
exportDescriptionAsPreset = _XgExternalAPI.exportDescriptionAsPreset
importFXModule = _XgExternalAPI.importFXModule
exportFXModule = _XgExternalAPI.exportFXModule
setMessageLevel = _XgExternalAPI.setMessageLevel
getMessageLevel = _XgExternalAPI.getMessageLevel
rootDir = _XgExternalAPI.rootDir
iconDir = _XgExternalAPI.iconDir
version = _XgExternalAPI.version
globalRepo = _XgExternalAPI.globalRepo
localRepo = _XgExternalAPI.localRepo
userRepo = _XgExternalAPI.userRepo
docsDir = _XgExternalAPI.docsDir
fileCleanup = _XgExternalAPI.fileCleanup
expandFilepath = _XgExternalAPI.expandFilepath
promoteFunc = _XgExternalAPI.promoteFunc
prepForEditor = _XgExternalAPI.prepForEditor
prepForAttribute = _XgExternalAPI.prepForAttribute
findFileInXgDataPath = _XgExternalAPI.findFileInXgDataPath
initConfig = _XgExternalAPI.initConfig
setProjectPath = _XgExternalAPI.setProjectPath
getProjectPath = _XgExternalAPI.getProjectPath


