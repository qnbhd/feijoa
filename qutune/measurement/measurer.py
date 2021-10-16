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
import json
import logging

import numpy as numpy

from qutune.environment import Environment
from utils.configurations import dump_config
from workloads.workload import Workload

log = logging.getLogger(__name__)


class Measurer:

    def __init__(self, workload: Workload):
        self.workload = workload

        env = Environment()
        self.num_runs = env.num_runs

    def run_test(self, configuration: dict):
        log.debug(f'Trying configuration:[white][italic]\n'
                  f'{self.workload.render(configuration)}')

        self.workload.prepare(configuration)

        results = numpy.array([
            float(self.workload.run())
            for _ in range(self.num_runs)
        ])

        log.debug(f'Result: \n{results}')
        return results.mean()