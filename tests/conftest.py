import glob
import os
from itertools import chain

import pytest


@pytest.fixture(autouse=True)
def cleanup():
    yield
    for f in chain(glob.glob("*.json"), glob.glob("*.yaml"),
                   glob.glob("*.db")):
        os.remove(f)
