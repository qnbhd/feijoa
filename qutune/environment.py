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
from pprint import pformat

from utils.singleton_meta import SingletonMeta
import yaml

class Environment(metaclass=SingletonMeta):

    def __init__(self):
        self.env = dict()

    def load_from_file(self, env_file):
        with open(env_file) as file:
            self.env = yaml.safe_load(file)

    def __repr__(self):
        return pformat(self.env)

    def get(self, item):
        assert isinstance(item, str), 'Attr must be str'
        return self.env.get(item, None)

    @property
    def num_runs(self):
        return self.env.get('num_runs')

    @property
    def test_limit(self):
        return self.env.get('test_limit')

    @property
    def workload_name(self):
        return self.env.get('workload_name')

    @property
    def space(self):
        return self.env.get('space')

