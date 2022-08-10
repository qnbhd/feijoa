from contextlib import redirect_stderr
import io

from ply import lex
from ply import yacc


__all__ = ["_OracleParser"]


def flatten(x):
    if isinstance(x, (list, tuple, set)):
        return [a for i in x for a in flatten(i)]
    else:
        return [x]


# noinspection SpellCheckingInspection,PyPep8Naming,PyMethodMayBeStatic
class _OracleLexer:
    tokens = (
        "WORD",
        "ANGLEBRACKETL",
        "ANGLEBRACKETR",
        "SQBRACKETL",
        "SQBRACKETR",
        "COMMA",
        "PLUS",
        "EQ",
        "INTEGER",
        "FLOAT",
    )

    ident = r"[a-zA-Z_]\w*"

    t_WORD = ident
    t_ANGLEBRACKETL = r"\<"
    t_ANGLEBRACKETR = r"\>"
    t_SQBRACKETL = r"\["
    t_SQBRACKETR = r"\]"
    t_PLUS = r"\+"
    t_COMMA = r"\,"
    t_EQ = r"\="

    def t_FLOAT(self, t):
        r"""[-+]?[0-9]+(\.([0-9]+)?([eE][-+]?[0-9]+)?|[eE][-+]?[0-9]+)"""
        t.value = float(t.value)
        return t

    def t_INTEGER(self, t):
        r"""\d+"""
        t.value = int(t.value)
        return t

    t_ignore = " \r\n\t\f"

    def t_error(self, t):
        self.exception_message = (
            f"Illegal character `{t.value[0]}` on {t.lineno} line,"
            f" {t.lexpos} position"
        )
        t.lexer.skip(1)

    def t_newline(self, t):
        r"""\n+"""
        t.lexer.lineno += len(t.value)

    def __init__(self):
        self.lexer = lex.lex(module=self)
        self.exception_message = ""


# noinspection PyMethodMayBeStatic,DuplicatedCode
class _OracleParser:
    tokens = _OracleLexer.tokens

    def p_super_oracle(self, p):
        """
        super_oracle : WORD ANGLEBRACKETL oracle-list ANGLEBRACKETR
                     | WORD ANGLEBRACKETL oracle-list ANGLEBRACKETR SQBRACKETL params-list SQBRACKETR
                     | oracle
        """

        if len(p) == 2:
            p[0] = {"top-oracle": p[1]["name"], **p[1]}
            p[0].pop("name")
        if len(p) == 5:
            p[0] = {"top-oracle": p[1], "oracles": p[3]}
        elif len(p) == 8:
            p[0] = {
                "top-oracle": p[1],
                "oracles": p[3],
                "params": p[6],
            }

    def p_oracle(self, p):
        """
        oracle : WORD
               | WORD SQBRACKETL params-list SQBRACKETR
               | WORD PLUS plugins-list
               | WORD SQBRACKETL params-list SQBRACKETR PLUS plugins-list
        """

        if len(p) == 2:
            p[0] = {"name": p[1]}
        elif len(p) == 4:
            p[0] = {"name": p[1], "plugins": p[3]}
        elif len(p) == 5:
            p[0] = {"name": p[1], "params": p[3]}
        elif len(p) == 7:
            p[0] = {"name": p[1], "params": p[3], "plugins": p[6]}

    def p_plugin(self, p):
        """
        plugin : WORD
               | WORD SQBRACKETL params-list SQBRACKETR
        """

        if len(p) == 2:
            p[0] = {"name": p[1]}
        elif len(p) == 5:
            p[0] = {"name": p[1], "params": p[3]}

    def p_plugins_list(self, p):
        """
        plugins-list : plugin
                     | plugins-list PLUS plugin
        """

        p[0] = [p[i] for i in range(1, len(p), 2)]
        p[0] = flatten(p[0])

    def p_oracle_list(self, p):
        """
        oracle-list : oracle
                    | oracle-list COMMA oracle
        """

        params = [p[i] for i in range(1, len(p), 2)]
        total_oracles = []

        def iterate(obj):
            nonlocal total_oracles

            if isinstance(obj, dict):
                total_oracles.append(obj)

            if isinstance(obj, list):
                for o in obj:
                    iterate(o)

        iterate(params)

        p[0] = total_oracles

    def p_value(self, p):
        """
        value : INTEGER
              | FLOAT
              | WORD
        """

        p[0] = p[1]

    def p_param(self, p):
        """param : WORD EQ value"""

        p[0] = {p[1]: p[3]}

    def p_params_list(self, p):
        """
        params-list : param
                    | params-list COMMA param
        """

        params = [p[i] for i in range(1, len(p), 2)]

        total_params = {}

        def iterate(obj):
            nonlocal total_params

            if isinstance(obj, dict):
                if "params" in obj.keys():
                    for o in obj["params"]:
                        iterate(o)
                else:
                    total_params = {**total_params, **obj}

            if isinstance(obj, list):
                for o in obj:
                    iterate(o)

        iterate(params)

        p[0] = total_params

    def p_error(self, p):
        if p is None:
            return
        self.exception_message = (
            f"Error parsing `{p.value}` "
            f"at {p.lineno} line in {p.lexpos} position."
        )

    def __init__(self):

        self.exception_message = ""
        self.lexer = _OracleLexer()

        # suppress ply logs
        with io.StringIO() as buf, redirect_stderr(buf):
            self.parser = yacc.yacc(module=self)

    def parse(self, doc):
        self.exception_message = ""

        with io.StringIO() as buf, redirect_stderr(buf):
            tree = self.parser.parse(
                doc, lexer=self.lexer.lexer, debug=1
            )

            if self.lexer.exception_message:
                # intercept lexer error message
                self.exception_message = self.lexer.exception_message

            # try pick up error message from lexer debug output
            if not tree and not self.exception_message:
                error_line = next(
                    (
                        line
                        for line in buf.getvalue().splitlines()
                        if "ERROR" in line
                    ),
                )
                self.exception_message = (
                    "Error while parsing at end of line. Description:\n"
                    f"\t{error_line}"
                )

        if self.exception_message:
            raise SyntaxError(self.exception_message)

        return tree
