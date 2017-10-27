from typing import List

import ast
from automata import NDAutomata
from tranlator import translate
from util import verify_expression


class AppError(Exception):
    pass


def testing(filename: str, debug: bool) -> bool:
    try:
        file = open(filename)
    except IOError:
        raise AppError("Can't open file {}.".format(filename))

    all_passed = True
    lines: List[str] = file.readlines()
    for i in range(0, len(lines)):
        line = lines[i].rstrip()
        test_case: List[str] = line.split(':')
        if len(test_case) < 1 or len(test_case) > 3:
            raise AppError("The line has to have 2 or 3 expressions divided by colon, has: {}".format(line)) from None

        regexp: str = test_case[0]
        true_exprs: List[str] = []
        if len(test_case) > 1:
            if len(test_case[1]) > 0:
                true_exprs = test_case[1].split(';')
        false_exprs: List[str] = []
        if len(test_case) > 2:
            if len(test_case[2]) > 0:
                false_exprs = test_case[2].split(';')

        if (len(true_exprs) + len(false_exprs)) == 0:
            print(true_exprs, false_exprs, test_case)
            raise AppError("There should be at least one expression.")

        tree: ast.AST = ast.parse(regexp)
        machine: NDAutomata = translate(tree)

        print()
        print(regexp)
        if debug:
            print(test_case)
            print("Automata:")
            print(machine)
        if len(true_exprs) > 0:
            print("Should be True:")

        for j in range(len(true_exprs)):
            ok = verify_expression(machine, true_exprs[j])
            if not ok:
                all_passed = False

            print("#{:03} {:>5}: {}.".format(j, 'True' if ok else 'False', true_exprs[j]))

        if len(false_exprs) > 0:
            print("Should be False:")

        for j in range(len(false_exprs)):
            ok = verify_expression(machine, false_exprs[j])
            if ok:
                all_passed = False

            print("#{:03} {:>5}: {}.".format(j, 'True' if ok else 'False', false_exprs[j]))
    return all_passed


def main():
    while True:
        print("Please, enter filename or `exit` or `q`: ", end="")

        filename = input()
        if filename == "exit" or filename == "q":
            return exit(0)

        try:
            passed = testing(filename, False)
            if passed:
                print("\nAll cases passed.\n")
        except Exception as e:
            print("Error has occured:", e)
            print("Try another file.")


main()
