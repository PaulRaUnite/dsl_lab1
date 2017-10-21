# DSL work #1

## Tasks

- [x] create data structure for regular expression syntax tree;
- [x] function to parse expression into AST;
- [x] create data structure for non-deterministic automata;
- [x] create function that transforms regular expression AST into
automata;
- [x] create application that receives representation of regular expression
and some statement and answers the question: does the statement satisfy
the regexp's condition?

## How to install and run

Clone/download the repository and run `python app.py`.

It works on `python3.6`, so please use the same or newer version

### Test set

There are some test sequences into `test_cases.txt`.
Just run `app.py` and input the filename.

Or run `tests.py`, it has other checks and examples.
## About the current realization

### Syntax of current regular expressions

- `|` &mdash; logical `or` statement;
- `ab` &mdash; is `a+b` there `+` is concatenation;
- `a*` &mdash; `*` is Clini closure, it means that expression
to which it is performed cannot occur or occur any number of times;
- parenthesis, as usual, performs prioritization of some subexpression.

So, the following expressions and expressions like them are allowed:
- `(a)(b)`
- `(ab)*`
- `a|(b*c*)*`

#### Escaped symbols
- `\*`
- `\(`
- `\)`
- `\|`

If the symbols are escaped, they can be used as other symbols,
not a special ones.
As example: `\(ab\)\*` requires only expression `(ab)*`.

### How to use the `app.py`

Create file with your regular expressions and expressions that
should be checked in the following format:
- every line should contain 3 substrings with
 colon (`:`) delimiter;
- the first substring is a regular expression. Be careful, for
the regular expressions all symbols matter;
- second and third substrings are expressions that should
be checked;
- first of them are expressions that should match the regexp;
- second of them are expressions that must not match the regexp;
- all cases separated by a semicolon(`;`).

So, the typical line of the testing file will be:
`(ab)*:;ab;abab:aa;bb`

It means, that you can't use colon in your expressions, but
it is the limitation of the current application, not of the
regexp or automata realization.

### About state machines

`automata` package implements non-deterministic finite state machine.
It means that amount of states are finite and from the same state
can exist more than one transition with the same trigger symbol.

Transitions are stored as dictionary of dictionaries of sets 
(or in Python notation `Dict[int, Dict[chr, Set[int]]]`), every
the machine can have only one start state(always `0`), and any number
of final states.

Forks with transitions of the same trigger symbol are allowed.
In the machine, this case is handled by multiple current states
of the machine (to be exact, set of states).
While fork occurs while executing and transitions will be performed,
current state will be split up into multiple states, every of which
will continues its route by its branch.
