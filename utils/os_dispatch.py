import functools
import sys
import types


class UnknownOsException(Exception):
    """Raises if finded unknown OS."""


def os_dispatch(func):
    registry = {}

    def dispatch(platform):
        try:
            return registry[platform]
        except KeyError:
            return registry[None]

    def register(platform, func=None):
        if func is None:
            if isinstance(platform, str):
                return lambda f: register(platform, f)
            platform, func = platform.__name__, platform  # it is a function
        registry[platform] = func
        return func

    def wrapper(*args, **kw):
        return dispatch(sys.platform)(*args, **kw)

    registry[None] = func
    wrapper.register = register
    wrapper.dispatch = dispatch
    wrapper.registry = types.MappingProxyType(registry)
    functools.update_wrapper(wrapper, func)
    return wrapper
