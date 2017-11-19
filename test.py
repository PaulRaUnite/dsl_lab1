from typing import Tuple, List

import ast
from automaton.dfa import DFA
from tranlator import translate
from util import verify_expression

expressions = ["d(a|b)e*(g|k)", "aa*a|(aa*)***", "**", "a|", "*|a", "(acd(a)*|a)|(ab*|a)",
               "a|a|a|(ab)*", "(a)*(a)*", "aa", "(ab)*", "a|(a*b*)*", "((ab)"]

for expr in expressions:
    print("{:20} -> ".format(expr), end="")
    try:
        print(ast.parse(expr))
    except Exception as e:
        print("{:40}error: {}".format(expr, e))

Test = Tuple[str, List[str], List[bool]]
tests: List[Test] = [("", ["", "a", "b"], [True, False, False]),
                     ("a|b", ["a", "b", "ab"], [True, True, False]),
                     ("ab*", ["a", "ab", "aab", "abb"], [True, True, False, True]),
                     ("d(a|b)e*(g|k)", ["daeg", "dbk", "dbeeek", "dcegk", ], [True, True, True, False]),
                     ("a(b|a|c)d*", ["abdddd", "aadd", "acd", "add", "ab", "acc"],
                      [True, True, True, False, True, False]),
                     ("(ab*)(ab)*", ["a", "aab", "abbab", "abb", "abaa"], [True, True, True, True, False])]

passed = True
for expr in tests:
    tree = ast.parse(expr[0])
    machine = DFA.from_ndfa(translate(tree)).minimize()

    for i in range(0, len(expr[1])):
        if verify_expression(machine, expr[1][i]) != expr[2][i]:
            raise Exception(expr[0], "{}".format(tree), i, expr[1][i], expr[2][i],
                            "{}".format(machine),
                            "{}".format(tree))
if passed:
    print("\nAll tests passed.")
