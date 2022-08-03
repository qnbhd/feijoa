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
from functools import partial
import logging
from typing import List
from typing import Optional

from feijoa.models.configuration import Configuration
from feijoa.search.algorithms import SearchAlgorithm


log = logging.getLogger(__name__)


class SeedAlgorithm(SearchAlgorithm):

    anchor = "seed"
    aliases = (
        "SeedAlgorithm",
        "seed",
    )

    def __init__(self, *seeds, **kwargs):
        super().__init__(*seeds, **kwargs)
        self.seeds: list = list(seeds)
        self.is_emitted = False

    def ask(self, n: int = 1) -> Optional[List[Configuration]]:
        log.debug(
            "Parameter `n` does not affect on configuration's count,"
            f" because {self.__class__.__name__} is sequential."
        )

        cf = partial(Configuration, requestor=self.name)

        if not self.is_emitted:
            self.is_emitted = True
            return [cf(s) for s in self.seeds]
        else:
            return None

    def tell(self, config, result):
        # Tell no needed
        pass
