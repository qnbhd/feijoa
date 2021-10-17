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
import io
import logging
from typing import Any, Dict
from qutune.search.parameters import Parameter
from utils.helpers import configuration_hash
from workloads.workload import Workload as BaseWorkload
import random

import subprocess

log = logging.getLogger(__name__)


class Workload(BaseWorkload):

    def __init__(self, **kwargs):
        super().__init__()
        self.source_file = kwargs['source_file']
        self.binary_out = ''

    def prepare(self, configuration: Dict[Parameter, Any]):
        d = {p.name: v for p, v in configuration.items()}
        self.binary_out = configuration_hash(d) + str(random.randint(1, 999999)) + '.out'
        rendered = self.render(configuration)
        self.run_command(f'g++ -o {self.binary_out} {self.source_file} {rendered}')

    def run(self):
        run_out = subprocess.check_output(
            f'/usr/bin/time -f \'%e\' ./{self.binary_out}',
            shell=True, stderr=subprocess.STDOUT)

        decoded = run_out.decode('utf-8')
        log.info(f'RUN OUT:\n{decoded}')

        splitted = decoded.strip().split('\n')
        real = splitted[-1]
        return real

    def teardown(self):
        self.run_command(f'rm {self.binary_out}')