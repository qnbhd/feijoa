#!/usr/bin/env python
from pprint import pprint

import executor

if __name__ == '__main__':
    cmd = "g++-11 --help=optimizers | awk '$1 ~ /^-/ {print $1}'"
    result = executor.execute(cmd, capture=True)
    parsed_flags = [u for u in result.split("\n") if u]
    captured = dict()

    captured['-O'] = {
        "type": "categorical",
        "choices": ["-O0", "-O1", "-O2", "-O3", "-Ofast", "-Og", "-Os"]
    }

    for flag in parsed_flags:
        if '-O' in flag:
            pass
        elif '=' in flag:
            print(f"Parametrized: {flag}")
        else:
            captured[flag] = {
                "type": "categorical",
                "choices": [flag, None]
            }

    template = """- signature: {}
  type: {}
  choices: {}\n\n"""

    out = open("space_wided.yaml", "w")

    for k, v in captured.items():
        flag_type = v['type']
        choices = '[' + ', '.join([u if u else 'null' for u in v['choices']]) + ']'

        out.write(template.format(k, flag_type, choices))

    out.close()


