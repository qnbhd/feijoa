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
import logging
import hashlib
import os
import platform
import random
from os.path import abspath, dirname
from typing import Type, Union

import numpy

from gimeltune import create_job
from gimeltune.models.experiment import Experiment
from gimeltune.search.parameters import ParametersVisitor, Parameter, Integer, Real, Categorical
from gimeltune.search.space import from_yaml, SearchSpace
from gimeltune.utils.logging import init
from executor import execute

init(verbose=True)


class Renderer(ParametersVisitor):
    def __init__(self, experiment):
        super().__init__()
        self.experiment = experiment

    def get_value(self, param: Parameter) -> Union[str, float]:
        value = self.experiment.params[param.name]
        return value

    def visit_common(self, p: Parameter) -> str:
        value = self.get_value(p)
        return f"{p.name}{value}"

    def visit_integer(self, p: Integer):
        return self.visit_common(p)

    def visit_real(self, p: Real) -> str:
        return self.visit_common(p)

    def visit_categorical(self, p: Categorical, **kwargs) -> str:
        value = self.get_value(p)
        if value:
            return f"{value}"
        return ''


def render(experiment: Experiment, space: SearchSpace, renderer_cls: Type[Renderer]) -> str:
    renderer = renderer_cls(experiment)

    rendered = list()

    for p in space:
        result_ = p.accept(renderer)
        rendered.append(result_)

    return " ".join(rendered)


NAME = 'gcc'
METRICS = ('time', 'compile_time', 'size')
SOURCE_FILE = os.path.join(dirname(abspath(__file__)), 'raytracer', 'raytracer.cpp')
SPACE_FILE = os.path.join(dirname(abspath(__file__)), 'space_minimal.yaml')
SPACE = from_yaml(SPACE_FILE)
ERROR_RESULT = 1e10

log = logging.getLogger(__name__)


class GccRenderer(Renderer):

    def visit_integer(self, p):
        value = self.get_value(p)
        return f"--param {p.name}={value}"


def run_command(command: str):
    log.debug(f'RUN COMMAND:\n[cyan][bold]{command}')

    output = execute(command, capture=True)

    decoded = output.strip()
    if decoded:
        log.info(f'[yellow][bold]OUT: {decoded}')

    return decoded


def metric_collector(experiment: Experiment) -> dict[str, float]:
    rendered = render(experiment, SPACE, GccRenderer)

    config_hash = hashlib.sha256(str(hash(experiment.json())).encode()).hexdigest()

    # TODO: check if file is exists and remove random.randint
    binary_out = config_hash + str(random.randint(1, 99999)) + '.out'
    binary_out = os.path.join(dirname(abspath(__file__)), binary_out)

    system_name = platform.system()

    if system_name == 'Linux':
        compile_cmd = f'/usr/bin/time -f \'%e\' g++ -o' \
                      f' {binary_out} {SOURCE_FILE} {rendered} 2>&1'

        run_cmd = f'/usr/bin/time -f \'%e\' {binary_out} 2>&1'

    elif system_name == 'Darwin':
        # gnu-time is required
        compile_cmd = f'gtime -f \'%e\' g++-11 -o' \
                      f' {binary_out} {SOURCE_FILE} {rendered} 2>&1'
        run_cmd = f'gtime -f \'%e\' {binary_out} 2>&1'

    else:
        # TODO (qnbhd): Refine exception type
        raise Exception()

    size_cmd = "wc -c {} | awk {}".format(binary_out, "'{print $1}'")


    try:
        compile_time = float(run_command(compile_cmd))
    except Exception as e:
        run_command(f'rm {binary_out}')
        return {
            'time': ERROR_RESULT,
            'compile_time': ERROR_RESULT,
            'size': ERROR_RESULT,
        }

    try:
        size = int(run_command(size_cmd))
    except Exception as e:
        size = ERROR_RESULT

    try:
        run_time = numpy.array([
            float(run_command(run_cmd))
            for _ in range(5)
        ]).mean()
    except Exception as e:
        run_time = ERROR_RESULT

    run_command(f'rm {binary_out}')

    return {
        'time': run_time,
        'compile_time': compile_time,
        'size': size,
    }


def objective(experiment: Experiment) -> float:
    log.info(f'Trying experiment: {experiment}')
    metrics = metric_collector(experiment)
    return metrics['time']


def run_gcc():
    job = create_job(SPACE)
    job.setup_default_algo()

    for i in range(10):
        experiments = job.ask()

        results = [objective(exp) for exp in experiments]

        for experiment, result in zip(experiments, results):
            experiment.apply(result)

            if abs(result - ERROR_RESULT) < 1e-8:
                log.info(f'Experiments {experiment} has inf result.')
                experiment.error_finish()
            else:
                experiment.success_finish()

            job.tell(experiment)

    return job


if __name__ == '__main__':
    run_gcc()


