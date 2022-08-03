import glob
from itertools import chain
import logging
import os

import pytest


excluded_loggers = (
    "numba",
    "matplotlib",
)

for log_name in excluded_loggers:
    other_log = logging.getLogger(log_name)
    other_log.setLevel(logging.WARNING)


@pytest.fixture(autouse=True)
def cleanup():
    yield
    for f in chain(
        glob.glob("*.json"), glob.glob("*.yaml"), glob.glob("*.db")
    ):
        os.remove(f)
