import glob
import os
from itertools import chain

import pytest

from gimeltune.utils.logging import init


@pytest.fixture(autouse=True)
def cleanup():
    init(verbose=True)
    yield
    for f in chain(glob.glob("*.json"), glob.glob("*.yaml"),
                   glob.glob("*.db")):
        os.remove(f)

