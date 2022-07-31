import pytest

from feijoa.exceptions import PackageNotInstalledError


class ImportWrapper:
    """Context manager to wrap import messages."""

    def __enter__(self):
        pass

    def __exit__(self, exctype, excinst, exctb):
        if exctype == ModuleNotFoundError:
            module = str(excinst).split()[-1]
            message = (f"Tried to import {module} but failed."
                       " Please make sure that the package is"
                       " installed correctly to use this feature.")
            raise PackageNotInstalledError(message)
        return True


def import_or_skip(module, reason=''):
    try:
        return pytest.importorskip(module, reason=reason)
    except PackageNotInstalledError:
        return pytest.skip(reason=reason, allow_module_level=True)
