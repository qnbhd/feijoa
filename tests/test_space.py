import pytest

from gimeltune.search import SearchSpace
from gimeltune.search.space import from_yaml


def test_space_from_yaml():
    yaml = '''- signature: -O
  type: categorical
  choices: [-O1, -O2, -O3, null]

- signature: align-functions
  type: categorical
  choices: [-falign-functions, -fno-align-functions, null]

- signature: iv-max-considered-uses
  type: integer
  range: [0, 1000]
  
- signature: foo
  type: integer
  low: 0
  high: 1000
  
- signature: boo
  type: real
  low: 0.0
  high: 1.0
'''

    space = SearchSpace.from_yaml(yaml)

    assert space.get('boo').name == 'boo'

    with open('foo.yaml', 'w') as yf:
        yf.write(yaml)

    with pytest.deprecated_call():
        from_yaml('foo.yaml')

    space_from_file = SearchSpace.from_yaml_file('foo.yaml')

    assert str(space) == '''SearchSpace:
	Categorical('-O', choices=['-O1', '-O2', '-O3', None])
	Categorical('align-functions', choices=['-falign-functions', '-fno-align-functions', None])
	Integer('iv-max-considered-uses, low=0, high=1000)
	Integer('foo, low=0, high=1000)
	Real('boo', self.low=0.0, self.high=1.0]'''

    assert str(space_from_file) == '''SearchSpace:
	Categorical('-O', choices=['-O1', '-O2', '-O3', None])
	Categorical('align-functions', choices=['-falign-functions', '-fno-align-functions', None])
	Integer('iv-max-considered-uses, low=0, high=1000)
	Integer('foo, low=0, high=1000)
	Real('boo', self.low=0.0, self.high=1.0]'''

