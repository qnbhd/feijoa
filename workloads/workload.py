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
import abc
import logging
import os
import subprocess
import sys
from typing import Any, Dict

import rich
from executor import execute
from rich.console import Console
from rich.syntax import Syntax

from polytune.models.configuration import Configuration
from polytune.search.parameters import Parameter
from polytune.search.renderer import Renderer

log = logging.getLogger(__name__)


class Workload(metaclass=abc.ABCMeta):

    def __init__(self, **kwargs):
        pass

    @staticmethod
    def render(configuration: Dict[Parameter, Any]):
        r = Renderer()

        rendered = []
        for p, v in configuration.items():
            if v is not None:
                result = p.accept(r, value=v)
                rendered.append(result)

        rendered = ' '.join(rendered)

        return rendered

    def run_command(self, command: str):
        log.debug(f'RUN COMMAND:\n[cyan][bold]{command}')

        output = subprocess.check_output(
            command, shell=True, stderr=subprocess.STDOUT)

        decoded = output.decode('utf-8').strip()
        if decoded:
            log.debug(f'[yellow][bold]OUT:\n{decoded}"')

    @abc.abstractmethod
    def run(self, rendered):
        pass

    @abc.abstractmethod
    def teardown(self):
        pass
