import inspect
from itertools import chain
import logging

import dash
import dash_bootstrap_components as dbc


log = logging.getLogger("dash_mixin")


class DashMixin:
    def __init__(self, *external_modules):
        log.critical("Call DashMixin")
        self.app = dash.Dash(
            __name__,
            meta_tags=[
                {
                    "name": "viewport",
                    "content": "width=device-width, initial-scale=1",
                }
            ],
            external_stylesheets=[dbc.themes.CYBORG],
        )

        self.app.title = "Feijoa oracles ranking"

        external_modules = external_modules or []

        source = chain([self], external_modules)

        for obj in source:

            functions_predicate = (
                (lambda x: inspect.ismethod(x))
                if isinstance(obj, DashMixin)
                else (lambda x: inspect.isfunction(x))
            )

            methods = inspect.getmembers(
                obj,
                lambda x: functions_predicate(x)
                and not x.__name__.startswith("_")
                and hasattr(x, "__dash_args__"),
            )

            for name, method in methods:
                arguments = getattr(method, "__dash_args__")
                kw_arguments = getattr(method, "__dash_kwargs__", {})

                if name.startswith("client"):
                    self.app.clientside_callback(
                        method.__doc__, *arguments, **kw_arguments
                    )
                    log.info(
                        f"Clientside callback {name} was registered."
                    )
                    continue

                log.info(f"Callback {name} was registered.")
                self.app.callback(*arguments, **kw_arguments)(method)


def dashed(*args, **kwargs):
    def inner(func):
        setattr(func, "__dash_args__", args)
        setattr(func, "__dash_kwargs__", kwargs)
        return func

    return inner
