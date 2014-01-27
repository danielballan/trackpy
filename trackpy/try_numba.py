import ast
import inspect
import logging


_numba_capable = dict()


def try_numba_autojit(func):
    module_name = inspect.getmoduleinfo(func.func_globals['__file__']).name
    namespace = '.'.join(['trackpy', module_name])
    _numba_capable[(namespace, func.func_name)] = func


def disable_numba():
    for func_info, func in _numba_capable.items():
        namespace, func_name = func_info
        reference = getattr(__import__(namespace), func_name)
        reference = func


def enable_numba():
    try:
        import numba
    except:
        pass
    else:
        hush_llvm()
        for func_info, func in _numba_capable.items():
            namespace, func_name = func_info
            reference = getattr(__import__(namespace), func_name)
            reference = numba.autojit(func)


def hush_llvm():
    # Necessary for current stable release 0.11.
    # Not necessary in master, probably future release will fix.
    # See http://stackoverflow.com/a/20663852/1221924
    import numba.codegen.debug
    llvmlogger = logging.getLogger('numba.codegen.debug')
    llvmlogger.setLevel(logging.INFO)
