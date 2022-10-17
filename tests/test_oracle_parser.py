import pytest as pytest

# noinspection PyUnresolvedReferences,PyProtectedMember
from feijoa.utils._oracle_parser import _OracleParser


@pytest.mark.parametrize(
    "input_line,expected",
    [
        (
            "ucb<bayesian>",
            {"oracles": [{"name": "bayesian"}], "top-oracle": "ucb"},
        ),
        (
            "thompson<random>",
            {
                "oracles": [{"name": "random"}],
                "top-oracle": "thompson",
            },
        ),
        (
            "ucb<random, bayesian>",
            {
                "oracles": [{"name": "random"}, {"name": "bayesian"}],
                "top-oracle": "ucb",
            },
        ),
        (
            "ucb<cmaes+reducer>",
            {
                "oracles": [
                    {
                        "name": "cmaes",
                        "plugins": [{"name": "reducer"}],
                    }
                ],
                "top-oracle": "ucb",
            },
        ),
        (
            "ucb<cmaes + reducer + plugin2>",
            {
                "oracles": [
                    {
                        "name": "cmaes",
                        "plugins": [
                            {"name": "reducer"},
                            {"name": "plugin2"},
                        ],
                    }
                ],
                "top-oracle": "ucb",
            },
        ),
        (
            "ucbtuned<pso[pop_size=10]+reducer, bayesian>",
            {
                "oracles": [
                    {
                        "name": "pso",
                        "params": {"pop_size": 10},
                        "plugins": [{"name": "reducer"}],
                    },
                    {"name": "bayesian"},
                ],
                "top-oracle": "ucbtuned",
            },
        ),
        (
            "ucb<bayesian[acq=ei]+reducer, random[dist=normal], cmaes>[ranking=5]",
            {
                "oracles": [
                    {
                        "name": "bayesian",
                        "params": {"acq": "ei"},
                        "plugins": [{"name": "reducer"}],
                    },
                    {"name": "random", "params": {"dist": "normal"}},
                    {"name": "cmaes"},
                ],
                "params": {"ranking": 5},
                "top-oracle": "ucb",
            },
        ),
        (
            "ucb<bayesian+reducer>[foo=1.23]",
            {
                "oracles": [
                    {
                        "name": "bayesian",
                        "plugins": [{"name": "reducer"}],
                    }
                ],
                "params": {"foo": 1.23},
                "top-oracle": "ucb",
            },
        ),
        (
            "ucb<bayesian+reducer>[foo=1e+10]",
            {
                "oracles": [
                    {
                        "name": "bayesian",
                        "plugins": [{"name": "reducer"}],
                    }
                ],
                "params": {"foo": 1e10},
                "top-oracle": "ucb",
            },
        ),
        (
            "ucb<random>[foo=5e-10]",
            {
                "oracles": [{"name": "random"}],
                "params": {"foo": 5e-10},
                "top-oracle": "ucb",
            },
        ),
        (
            "ucb<random+reducer[gamma_osc=0.8]>",
            {
                "oracles": [
                    {
                        "name": "random",
                        "plugins": [
                            {
                                "name": "reducer",
                                "params": {"gamma_osc": 0.8},
                            }
                        ],
                    }
                ],
                "top-oracle": "ucb",
            },
        ),
        ("bayesian", {"top-oracle": "bayesian"}),
        (
            "bayesian+reducer",
            {
                "plugins": [{"name": "reducer"}],
                "top-oracle": "bayesian",
            },
        ),
        (
            "bayesian[foo=2]+reducer",
            {
                "params": {"foo": 2},
                "plugins": [{"name": "reducer"}],
                "top-oracle": "bayesian",
            },
        ),
        (
            "ucb<bayesian[acq=naive0, regr=RandomForestRegressor]>",
            {
                "oracles": [
                    {
                        "name": "bayesian",
                        "params": {
                            "acq": "naive0",
                            "regr": "RandomForestRegressor",
                        },
                    }
                ],
                "top-oracle": "ucb",
            },
        ),
    ],
)
def test_oracle_parser_correct(input_line, expected):
    parser = _OracleParser()
    assert parser.parse(input_line) == expected


@pytest.mark.parametrize(
    "input_line, expected_message",
    [
        (
            "ucb<bayesian",
            "SyntaxError('Error while parsing at end of line."
            " Description:\n\tERROR: Error  : WORD ANGLEBRACKETL WORD . $end')",
        ),
        (
            "ucb<>",
            "Error parsing `>` at 1 line in 4 position.",
        ),
        (
            "ucb<bayesian>[1=1]",
            "Error parsing `1` at 1 line in 14 position.",
        ),
        (
            "thompson<foo[woo=[]]>>",
            "Error parsing `[` at 1 line in 17 position.",
        ),
    ],
)
def test_oracle_parser_incorrect(input_line, expected_message):
    parser = _OracleParser()

    with pytest.raises(SyntaxError) as e:
        parser.parse(input_line)

    assert str(e.value) in expected_message
