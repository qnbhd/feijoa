# MIT License
#
# Copyright (c) 2021 Templin Konstantin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import contextlib
from functools import lru_cache
import importlib.util
import inspect
from itertools import chain
import pathlib
import sys

from feijoa import __feijoa_folder__
from feijoa.exceptions import PackageNotInstalledError
from feijoa.exceptions import SearchAlgorithmNotFoundedError
from feijoa.search.algorithms.algorithm import SearchAlgorithm


ALGORITHMS_FOLDER = (
    pathlib.Path(__feijoa_folder__) / "search" / "algorithms"
)
INTEGRATION_FOLDER = (
    pathlib.Path(__feijoa_folder__).parent
    / "integration"
    / "algorithms"
)


@lru_cache(maxsize=None)
def fetch_algorithms(only_anchors=False, **folders):
    """
    Fetch algorithm from specified algorithms folders.

    By default, uses:
        - integration.algorithms folder
        - default algorithms folder

    :returns: all finded algorithm's classes.
    """

    folders = folders or (
        ALGORITHMS_FOLDER,
        INTEGRATION_FOLDER,
    )

    pool = dict()

    target = (
        script
        for script in chain(
            *[folder.rglob("*.py") for folder in folders]
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
                and issubclass(obj[1], SearchAlgorithm)
            )
        )

        for name, cls in iterable:
            pool[cls.anchor] = cls

            if not only_anchors:
                pool[name] = cls

                for al in cls.aliases:
                    pool[al] = cls

    return pool


def get_algo(name):
    """Get algorithm class by name"""

    classes = fetch_algorithms()
    cls = classes.get(name)

    if not cls:
        raise SearchAlgorithmNotFoundedError()

    return cls
