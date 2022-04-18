#!/usr/bin/env python
import json
import os
import re
from os.path import dirname, abspath

import executor

APP = os.path.join(dirname(dirname(abspath(__file__))), 'raytracer', 'raytracer.cpp')


def check_is_working_flag(flag):
    cmd = f'g++-11 {APP} {flag} 2>&1'
    try:
        result = executor.execute(cmd, capture=True)
    except executor.ExternalCommandFailed:
        return False
    return result == ''


NOT_NEEDED = [
    'fsave-optimization-record',
    'fipa',
    'flive',
    'fassociative-math',
    'logical-op-non-short-circuit',
    'vect-max-peeling-for-alignment',
]


if __name__ == '__main__':
    if not os.path.exists('temp_captured.json'):
        cmd_flags = "g++-11 --help=optimizers | awk '$1 ~ /^-/ {print $1}'"
        cmd_opts = "g++-11 --help=params | awk '$1 ~ /^-/ {print $1}'"

        result_flags = executor.execute(cmd_flags, capture=True)
        parsed_flags = [u for u in result_flags.split("\n") if u]

        result_params = executor.execute(cmd_opts, capture=True)
        parsed_params = [u for u in result_params.split("\n") if u]

        with open('cc_params_defaults.json') as f:
            defaults = json.loads(f.read())

        captured = dict()

        captured['-O'] = {
            "type": "categorical",
            "choices": ["-O0", "-O1", "-O2", "-O3"]
        }


        def invert_gcc_flag(flag_):
            assert flag_[:2] == '-f'
            if flag_[2:5] != 'no-':
                return '-fno-' + flag_[2:]
            return '-f' + flag_[5:]


        for flag in parsed_flags:
            if '-O' in flag:
                pass
            elif '=' in flag:
                print(f"Parametrized: {flag}")
            else:
                if not check_is_working_flag(flag):
                    continue

                choices = [flag]
                if check_is_working_flag(invert_gcc_flag(flag)):
                    choices.append(invert_gcc_flag(flag))

                choices.append(None)

                captured[flag] = {
                    "type": "categorical",
                    "choices": choices
                }

        param_prefix = '--param='
        prefix_len = len(param_prefix)
        re_template = re.compile(r'--param=(.*?)=(.*)')
        bounds_re_template = re.compile(r'<(.*?),(.*?)>')

        for param in parsed_params:
            param_match = re_template.match(param)
            param_name = param_match.group(1)
            param_bounds = param_match.group(2)

            low = None
            high = None

            if param_bounds:
                bounds_match = bounds_re_template.match(param_bounds)
                if bounds_match:
                    low = bounds_match.group(1)
                    high = bounds_match.group(2)
                    low = int(low)
                    high = int(high)
            else:
                bounds_from_file = defaults.get(param_name)
                if bounds_from_file:
                    low = bounds_from_file['min']
                    high = bounds_from_file['max']

            if not low:
                continue

            if low > high:
                low, high = high, low

            captured[param_name] = {
                "type": "integer",
                "range": [low, high]
            }

            print('Check')
            print(check_is_working_flag(f'--param={param_name}={low}'))

        with open('temp_captured.json', 'w') as f:
            f.write(json.dumps(captured))
    else:
        with open('temp_captured.json') as f:
            captured = json.loads(f.read())

    captured_keys = list(captured.keys())

    for f_bug in NOT_NEEDED:
        for fc in captured_keys:
            if 'fipa' in fc:
                print(fc)
            if f_bug in fc:
                del captured[fc]

    template = """- signature: {}
  type: {}
  choices: {}\n\n"""

    integer_template = """- signature: {}
  type: {}
  range: {}\n\n"""

    out = open("../space_wided.yaml", "w")

    for k, v in captured.items():
        flag_type = v['type']
        if flag_type == 'categorical':
            choices = '[' + ', '.join([u if u else 'null' for u in v['choices']]) + ']'
            out.write(template.format(k, flag_type, choices))
        elif flag_type == 'integer':
            out.write(integer_template.format(k, flag_type, v['range']))

    out.close()


