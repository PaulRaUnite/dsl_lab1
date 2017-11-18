from typing import Tuple, List

import ast
from automata.dfa import DFA
from tranlator import translate
from util import verify_expression

print(translate(ast.parse("(b)*")))
expressions = ["d(a|b)e*(g|k)", "aa*a|(aa*)***", "**", "a|", "*|a", "(acd(a)*|a)|(ab*|a)",
               "a|a|a|(ab)*", "(a)*(a)*", "aa", "(ab)*", "a|(a*b*)*", "((ab)"]

for expression in expressions:
    print("{:20} -> ".format(expression), end="")
    try:
        print(ast.parse(expression))
    except Exception as e:
        print("{:40}error: {}".format(expression, e))

Test = Tuple[str, List[str], List[bool]]
tests: List[Test] = [("a|b", ["a", "b", "ab"], [True, True, False]),
                     ("ab*", ["a", "ab", "aab", "abb"], [True, True, False, True]),
                     ("d(a|b)e*(g|k)", ["daeg", "dbk", "dbeeek", "dcegk", ], [True, True, True, False]),
                     ("a(b|a|c)d*", ["abdddd", "aadd", "acd", "add", "ab", "acc"],
                      [True, True, True, False, True, False]),
                     ("(ab*)(ab)*", ["a", "aab", "abbab","abb","abaa"], [True, True, True, True, False])]

passed = True
for expression in tests:
    tree = ast.parse(expression[0])
    machine = DFA.from_ndfa(translate(tree)).minify()

    for i in range(0, len(expression[1])):
        if verify_expression(machine, expression[1][i]) != expression[2][i]:
            raise Exception(expression[0], "{}".format(tree), i, expression[1][i], expression[2][i],
                            "{}".format(machine),
                            "{}".format(tree))
if passed:
    print("\nAll tests passed.")
