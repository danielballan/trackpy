import ast
import sys
import inspect
import logging


ENABLE_NUMBA_ON_IMPORT = True
_numba_capable = dict()


def try_numba_autojit(func):
    module_name = inspect.getmoduleinfo(func.func_globals['__file__']).name
    module_name = '.'.join(['trackpy', module_name])
    _numba_capable[(module_name, func.func_name)] = func
    if ENABLE_NUMBA_ON_IMPORT:
        try:
            import numba
        except ImportError:
            pass
        else:
            hush_llvm()
            return numba.autojit(func)
    else:
        return func


def disable_numba():
    "Do not use numba-accelerated functions, even if numba is available."
    for namespace, func in _numba_capable.items():
        module_name, func_name = namespace 
        setattr(sys.modules[module_name], func_name, func)


def enable_numba():
    "Use numba-accelerated variants of core functions."
    try:
        import numba
    except:
        raise ImportError("To use numba-accelerated variants of core "
                          "functions, you must install numba.")
    else:
        hush_llvm()
        for namespace, func in _numba_capable.items():
            module_name, func_name = namespace
            setattr(sys.modules[module_name], func_name, numba.autojit(func))


def hush_llvm():
    # Necessary for current stable release 0.11.
    # Not necessary in master, probably future release will fix.
    # See http://stackoverflow.com/a/20663852/1221924
    import numba.codegen.debug
    llvmlogger = logging.getLogger('numba.codegen.debug')
    llvmlogger.setLevel(logging.INFO)
