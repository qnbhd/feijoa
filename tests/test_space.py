from gimeltune.search import SearchSpace


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
'''

    space = SearchSpace.from_yaml(yaml)

    assert str(space) == '''SearchSpace:
	Categorical('-O', choices=['-O1', '-O2', '-O3', None])
	Categorical('align-functions', choices=['-falign-functions', '-fno-align-functions', None])
	Integer('iv-max-considered-uses, low=0, high=1000)'''
