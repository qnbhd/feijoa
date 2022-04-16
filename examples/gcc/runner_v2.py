import logging
import hashlib
import os
import platform
import random
from os.path import abspath, dirname
from typing import Type, Union, Dict, Optional, Tuple

import numpy

from gimeltune import create_job
from gimeltune.models.experiment import Experiment
from gimeltune.search.parameters import ParametersVisitor, Parameter, Integer, Real, Categorical
from gimeltune.search.space import from_yaml, SearchSpace
from gimeltune.utils.logging import init
from gimeltune.search.space import SearchSpace
from executor import execute, ExternalCommandFailed

init(verbose=True)

SOURCE_FILE = os.path.join(dirname(abspath(__file__)), 'raytracer', 'raytracer.cpp')
SPACE_FILE = os.path.join(dirname(abspath(__file__)), 'space_wided.yaml')
SPACE = SearchSpace.from_yaml_file(SPACE_FILE)
ERROR_RESULT = 1e10
OBJECTIVE_METRIC = 'time'
ITERATIONS = 20

log = logging.getLogger(__name__)


class GccRenderer(ParametersVisitor):
    def __init__(self, experiment):
        super().__init__()
        self.experiment = experiment

    def get_value(self, param: Parameter) -> Union[str, float]:
        value = self.experiment.params[param.name]
        return value

    def visit_common(self, p: Parameter) -> Optional[str]:
        value = self.get_value(p)
        return f"--param {p.name}={value}" if value else None

    def visit_integer(self, p: Integer) -> Optional[str]:
        return self.visit_common(p)

    def visit_real(self, p: Real) -> Optional[str]:
        return self.visit_common(p)

    def visit_categorical(self, p: Categorical, **kwargs) -> Optional[str]:
        value = self.get_value(p)
        if value:
            return f"{value}"
        return None


def render(experiment: Experiment, space: SearchSpace, renderer_cls) -> str:
    renderer = renderer_cls(experiment)

    rendered = list()

    for p in space:
        result_ = p.accept(renderer)
        if not result_:
            continue
        rendered.append(result_)

    return " ".join(rendered)


def run_command_and_capture_stdout(command: str) -> Optional[str]:
    log.debug(f'RUN COMMAND:\n[cyan][bold]{command}')

    try:
        output = execute(command, capture=True)

        decoded = output.strip()
        if decoded:
            log.info(f'[yellow][bold]OUT: {decoded}')

        return decoded
    except ExternalCommandFailed as e:
        log.error(e.error_message)
        return None


def compile_source(source_file: str, rendered_opts, out_file: str) -> Optional[float]:

    system_name = platform.system()

    if system_name == 'Linux':
        compile_cmd = f'/usr/bin/time -f \'%e\' /usr/local/bin/g++-11 -o' \
                      f' {out_file} {source_file} {rendered_opts} 2>&1'

    elif system_name == 'Darwin':
        # gnu-time is required
        compile_cmd = f'/usr/local/bin/gtime -f \'%e\' /usr/local/bin/g++-11 -o' \
                      f' {out_file} {source_file} {rendered_opts} 2>&1'

    else:
        raise RuntimeError()

    stdout = run_command_and_capture_stdout(compile_cmd)

    try:
        compile_time = float(stdout)
    except ValueError:
        return None

    return compile_time


def run_binary(binary_name, iterations) -> Optional[Tuple[float, float, float, float, float]]:
    system_name = platform.system()

    if system_name == 'Linux':
        run_cmd = f'/usr/bin/time -f \'%e\' {binary_name} 2>&1'
    elif system_name == 'Darwin':
        # gnu-time is required
        run_cmd = f'/usr/local/bin/gtime -f \'%e\' {binary_name} 2>&1'
    else:
        raise RuntimeError()

    buff = numpy.array([])
    for _ in range(iterations):
        stdout = run_command_and_capture_stdout(run_cmd)

        if stdout is None:
            return None

        try:
            run_time = float(stdout)
        except ValueError:
            return None

        buff = numpy.append(buff, run_time)

    run_time = buff.mean()
    std = buff.std()
    cv = std / buff.mean()
    low = min(buff)
    high = max(buff)

    return run_time, std, cv, low, high


def get_binary_size(binary_name) -> float:
    size_cmd = "wc -c {} | awk {}".format(binary_name, "'{print $1}'")
    size_out = run_command_and_capture_stdout(size_cmd)
    return int(size_out)


def objective(experiment: Experiment):
    metrics = {
        'compile_time': ERROR_RESULT,
        'time': ERROR_RESULT,
        'size': ERROR_RESULT,
        'std': ERROR_RESULT,
        'cv': ERROR_RESULT,
        'low': ERROR_RESULT,
        'high': ERROR_RESULT
    }

    experiment.metrics = metrics

    config_hash = hashlib.sha256(str(hash(experiment.json())).encode()).hexdigest()

    # TODO: check if file is exists and remove random.randint
    binary_out = config_hash + str(random.randint(1, 99999)) + '.out'
    binary_out = os.path.join(dirname(abspath(__file__)), binary_out)

    rendered_opts = render(experiment, SPACE, GccRenderer)

    compile_result = compile_source(SOURCE_FILE, rendered_opts, binary_out)

    if not compile_result:
        # run_command_and_capture_stdout(f'rm {binary_out}')
        return experiment.metrics[OBJECTIVE_METRIC]

    experiment.metrics['compile_time'] = compile_result

    run_result = run_binary(binary_out, ITERATIONS)

    if not run_result:
        run_command_and_capture_stdout(f'rm {binary_out}')
        return experiment.metrics[OBJECTIVE_METRIC]

    run_time, std, cv, low, high = run_result

    experiment.metrics['time'] = run_time
    experiment.metrics['std'] = std
    experiment.metrics['cv'] = cv
    experiment.metrics['low'] = low
    experiment.metrics['high'] = high

    size = get_binary_size(binary_out)

    experiment.metrics['size'] = size

    run_command_and_capture_stdout(f'rm {binary_out}')
    return experiment.metrics[OBJECTIVE_METRIC]


def run_gcc(n_trials):
    job = create_job(search_space=SPACE)
    job.setup_default_algo()

    # Let's assume we can and run compile without errors baselines
    compile_source(SOURCE_FILE, '-O3', os.path.join(dirname(abspath(__file__)), 'baselineO3.out'))
    compile_source(SOURCE_FILE, '-O2', os.path.join(dirname(abspath(__file__)), 'baselineO2.out'))
    compile_source(SOURCE_FILE, '-O1', os.path.join(dirname(abspath(__file__)), 'baselineO1.out'))

    baselines = {
        'O3': run_binary(os.path.join(dirname(abspath(__file__)), 'baselineO3.out'), ITERATIONS),
        'O2': run_binary(os.path.join(dirname(abspath(__file__)), 'baselineO2.out'), ITERATIONS),
        'O1': run_binary(os.path.join(dirname(abspath(__file__)), 'baselineO1.out'), ITERATIONS),
    }

    for i in range(n_trials):
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

    return baselines, job


if __name__ == '__main__':
    baselines, job = run_gcc(10)
    print(baselines)
