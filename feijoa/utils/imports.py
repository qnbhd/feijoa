# MIT License
#
# Copyright (c) 2021-2022 Templin Konstantin
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
import importlib
import types
from typing import Any

import pytest

from feijoa.exceptions import PackageNotInstalledError


class ImportWrapper:
    """Context manager to wrap import messages."""

    def __enter__(self):
        pass

    def __exit__(self, exctype, excinst, exctb):
        if exctype == ModuleNotFoundError:
            module = str(excinst).split()[-1]
            message = (
                f"Tried to import {module} but failed."
                " Please make sure that the package is"
                " installed correctly to use this feature."
            )
            raise PackageNotInstalledError(message)
        return True


def import_or_skip(module, reason=""):
    """Import module or skip test in
    pytest framework.

    Args:
        module:
            Python module.
        reason:
            Reason of skipping.

    Raises:
        AnyError: If anything bad happens.

    """

    try:
        return pytest.importorskip(module, reason=reason)
    except PackageNotInstalledError:
        return pytest.skip(reason=reason, allow_module_level=True)


class LazyModuleImportProxy(types.ModuleType):
    """Class for lazy modules importing."""

    def __init__(self, module: str) -> None:
        super().__init__(module)
        self.module = module

    def _load(self) -> types.ModuleType:
        module = importlib.import_module(self.module)
        self.__dict__.update(module.__dict__)
        return module

    def __getattr__(self, item: str) -> Any:
        return getattr(self._load(), item)
