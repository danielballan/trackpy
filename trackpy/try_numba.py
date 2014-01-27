import logging


_numba_enabled = True

def numba_enabled():
    return _numba_enabled


def disable_numba():
    global _numba_enabled
    _numba_enabled = False

def enable_numba():
    global _numba_enabled
    _numba_enabled = True


def hush_llvm():
    # Necessary for current stable release 0.11.
    # Not necessary in master, probably future release will fix.
    # See http://stackoverflow.com/a/20663852/1221924
    import numba.codegen.debug
    llvmlogger = logging.getLogger('numba.codegen.debug')
    llvmlogger.setLevel(logging.INFO)


def try_numba_autojit(func):
    def func_(*args):
        if numba_enabled():
            try:
                import numba
            except:
                pass
            else:
                hush_llvm()
                return numba.autojit(func)(*args)
        return func(*args)
    return func_

# import numba
# try_numba_autojit = numba.autojit  # Is the wrapper causing trouble?
