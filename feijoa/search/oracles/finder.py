import contextlib
from functools import lru_cache
import importlib.util
import inspect
from itertools import chain
import pathlib
import sys

from feijoa import __feijoa_folder__
from feijoa.exceptions import PackageNotInstalledError
from feijoa.exceptions import SearchOracleNotFoundedError
from feijoa.plugins.plugin import Plugin
from feijoa.search.oracles.meta.meta import MetaOracle
from feijoa.search.oracles.oracle import Oracle
from feijoa.search.space import SearchSpace

# noinspection PyProtectedMember
from feijoa.utils._oracle_parser import _OracleParser


SEARCH_FOLDER = pathlib.Path(__feijoa_folder__) / "search"
ALGORITHMS_FOLDER = SEARCH_FOLDER / "oracles"
PLUGINS_FOLDER = pathlib.Path(__feijoa_folder__) / "plugins"
INTEGRATION_FOLDER = (
    pathlib.Path(__feijoa_folder__).parent / "integration"
)


@lru_cache(maxsize=None)
def fetch_classes(base_class, *folders, only_anchors=False):
    """
    Fetch oracle from specified oracles folders.

    By default, uses:
        - integration folder
        - default oracles folder

    :returns: all founded oracle's classes.
    """

    assert len(folders) >= 1, "Folders must be passed"

    pool = dict()

    target = (
        script
        for script in chain(
            *[
                pathlib.Path(folder).rglob("*.py")
                for folder in folders
            ]
        )
        if "__" not in script.name
    )

    for script in target:
        spec = importlib.util.spec_from_file_location(
            script.stem, str(script)
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[module.__name__] = module

        with contextlib.suppress(PackageNotInstalledError):
            spec.loader.exec_module(module)

        iterable = (
            obj
            for obj in inspect.getmembers(module, inspect.isclass)
            if (
                obj[1].__module__ == module.__name__
                and issubclass(obj[1], base_class)
            )
        )

        for name, cls in iterable:
            pool[cls.anchor] = cls

            if not only_anchors:
                pool[name] = cls

                with contextlib.suppress(TypeError):
                    for al in cls.aliases:
                        pool[al] = cls

    return pool


def fetch_oracles():
    oracles = fetch_classes(
        Oracle, ALGORITHMS_FOLDER, INTEGRATION_FOLDER
    )
    return oracles


def fetch_plugins():
    plugins = fetch_classes(
        Plugin, PLUGINS_FOLDER, INTEGRATION_FOLDER
    )
    return plugins


def fetch_top_oracles():
    top_oracles = fetch_classes(
        MetaOracle, SEARCH_FOLDER, INTEGRATION_FOLDER
    )
    return top_oracles


def get_algo(name):
    """Get oracle class by name"""

    classes = fetch_oracles()
    cls = classes.get(name)

    if not cls:
        raise SearchOracleNotFoundedError()

    return cls


def get_top_oracle(name):

    classes = fetch_top_oracles()
    cls = classes.get(name)

    if not cls:
        raise SearchOracleNotFoundedError()

    return cls


def get_plugin(name):
    classes = fetch_plugins()
    cls = classes.get(name)

    if not cls:
        raise SearchOracleNotFoundedError()

    return cls


def maker(line, search_space: SearchSpace):
    parser = _OracleParser()
    parsed = parser.parse(line)

    top_oracle = parsed["top-oracle"]
    top_oracle_params = parsed.get("params", {})
    top_oracle_plugins = parsed.get("plugins", [])
    oracles = parsed.get("oracles")

    if not oracles:
        top_oracle_cls = get_algo(top_oracle)
        # if passed only oracle

        plugins = []

        for plug in top_oracle_plugins:
            plug_name = plug["name"]
            plug_params = plug.get("params", {})
            plug_cls = get_plugin(plug_name)
            plugins.append(plug_cls(**plug_params))

        oracle_instance = top_oracle_cls(
            search_space=search_space, **top_oracle_params
        )

        for p in plugins:
            p.subscribers = [oracle_instance]

        return oracle_instance

    top_oracle_cls = get_top_oracle(top_oracle)

    top_oracle_params = parsed.get("params", {})

    oracles_pool = []

    for oracle in oracles:
        o_name = oracle["name"]
        o_plugins = oracle.get("plugins", [])
        o_params = oracle.get("params", {})
        o_cls = get_algo(o_name)

        plugins = []

        for plug in o_plugins:
            plug_name = plug["name"]
            plug_params = plug.get("params", {})
            plug_cls = get_plugin(plug_name)
            plugins.append(plug_cls(**plug_params))

        oracle_instance = o_cls(search_space=search_space, **o_params)

        for p in plugins:
            p.subscribers = [oracle_instance]

        oracle_instance.subscribers = plugins

        oracles_pool.append(oracle_instance)

    top_oracle_instance = top_oracle_cls(
        *oracles_pool, **top_oracle_params
    )
    return top_oracle_instance
