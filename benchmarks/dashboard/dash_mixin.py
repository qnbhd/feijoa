import inspect
import os
from os.path import abspath
from os.path import dirname

from benchmarks.dashboard.layout import make_layout
import dash


class DashMixin:
    def __init__(self):
        self.app = dash.Dash(
            __name__,
            meta_tags=[
                {
                    "name": "viewport",
                    "content": "width=device-width, initial-scale=1",
                }
            ],
        )

        self.app.title = "Feijoa oracles ranking"
        self.app.layout = make_layout(self.app)

        methods = inspect.getmembers(
            self,
            lambda x: inspect.ismethod(x)
            and not x.__name__.startswith("_")
            and hasattr(x, "__dash_args__"),
        )

        for name, method in methods:
            arguments = getattr(method, "__dash_args__")
            kw_arguments = getattr(method, "__dash_kwargs__", {})
            self.app.callback(*arguments, **kw_arguments)(method)


def dashed(*args, **kwargs):
    def inner(func):
        setattr(func, "__dash_args__", args)
        setattr(func, "__dash_kwargs__", kwargs)
        return func

    return inner
