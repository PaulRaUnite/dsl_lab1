# DSL course: individual work #1

## Tasks

- [x] create data structure for regular expression syntax tree;
- [x] function to parse expression into AST;
- [x] create data structure for non-deterministic automata;
- [x] create function that transforms regular expression AST into
automata;
- [x] create an application that receives the representation of regular expression and some expression and checks whether the statement satisfies the regexp condition.
- [ ] create data structure for deterministic automata;
- [ ] create algorithm for determinization(with deletion of dead-end and unreachable states);
- [ ] create algorithm for minimization(reduction);
- [ ] create algorithm for defragmentation(do index numbers of states consistent).

## How to install and run

Clone/download the repository and execute `python lab1_app.py`. There is no external dependencies, only standard types and type annotations.

It works on `python3.6`, so please use the same or newer version.

### Test set

There are some test sequences inside `test_cases.txt`. Just run `lab1_app.py` and input the filename.

There is `tests.py`, run it, it has other checks and examples. To understand what is going on there, open the script is required.

## About the implementation

### Syntax of the regular expressions

- `a` &mdash; just any symbol, UTF-8 symbols can be used;
- `|` &mdash; logical `or` statement (priority __1__);
- `ab` &mdash; is `a+b` there `+` is concatenation (priority __2__);
- `a*` &mdash; `*` is Clini closure (priority __3__), it means that expression
to which it is performed cannot occur or occur any number of times;
- parenthesis `(` and `)`, as usual, performs prioritization of some subexpression.

So, the following expressions and like them are allowed:
- `(a)(b)`
- `(ab)*`
- `a|(b*c*)*`

#### Escaped symbols
- `\*`
- `\(`
- `\)`
- `\|`

If the symbols are escaped, they can be used as other symbols, not a special ones.
As example: regexp `\(ab\)\*` can be satisfied by only expression `(ab)*`.

### How to use the `app.py`

Create file with your regular expressions and expressions that should be checked in the following format:
- every line should contain 2 or 3 substrings with colon (`:`) delimiter;
- the first substring is a regular expression. Be careful, for the regular expressions all symbols matter (including spacing);
- second and third substrings are expressions that should be checked;
- first of them are expressions that must match the regexp;
- second of them are expressions that must not match the regexp;
- all expressions for checking separated by a semicolon(`;`).
- you can keep the first list of expressions empty, but colons should be placed.

So, the typical line of the testing file can be:

- `(ab)*:;ab;abab:aa;bb` &mdash; regexp + true + false expressions
- `hii*:hi;hiiii` &mdash; regexp + only true expressions
- `ab*::b;bb;ba` &mdash; regexp + empty + only false expressions

It means, that you can't use colon and semicolon in your expressions, but it is the limitation of the current verifying application, not of the regexp or state machine implementation.

### About state machines

`automata` package implements non-deterministic finite state machine. It means that amount of states are finite and from the same state can exist more than one transition with the same trigger symbol.

Transitions are stored as dictionary of dictionaries of sets (or in Python notation `Dict[int, Dict[chr, Set[int]]]`), each machine can have any number of start and final states.

Forks with transitions of the same trigger symbol are allowed, of course. In the machine, this case is handled by multiple current states of the machine (to be exact, set of states). If fork occurs while executing and a few transitions of the same symbol are performed, current state will be split up into multiple states, every of which will continues its "route" on its branch.

### About regular expression parsing

After [scanning](/ast/scanner.py) (it looks really simple), parsing is performed. List of tokens is recursively separated by one of the above operators with respect to their priority and parenthesis.

__Note__: 
All the actions occur on the "first layer" of the expression, and here is what I mean.

Let's say that we have regular expression `(ab)|(c|d)`. The "first layer" of the expression is `group1|group2`, where `group1` is `(ab)`, `group2` is `(c|d)` and `|` is binary operator. Every iteration of the algorithm works only with parts of the first layer (operators inside groups are not visible by algorithm).

### About translating

There is some function, that recursively performs the following steps:
- receive children for the following nodes;
- if there are:
    - 0 child: it must be leaf with symbol;
    - 1 child: it must be only clini node;
    - 2 children: it can be "OR" as well as "AND";
- **here recursy goes**: it performs appropriate class function from the non-deterministic automata class: `by_value` for leaf symbols, `by_concatenation` or `by_decision` for machines of its children and `by_clini` for only one child.

#### About algorithms of machine joining

At first, let me define all sets:
- <code>&Sigma;</code> is a vocabulary of symbols;
- `S` is a set of states;
- `I` is a set of initial(start) states, where `I ∈ S`;
- `F` is a set of final states, where `F ∈ S`;
- `T` is a set of transitions, where <code>T ∈ S x &Sigma; x S</code>

So, following rules are applied to join state machines each other:

|RegExp                 | Machine creation |
|-----------------------|------------------|
| <code>a ∈ &Sigma;</code>:<br><code>a ∈ RegExp</code>| <code>S = {s<sub>0</sub>, s<sub>1</sub>}</code>, <code>I = {s<sub>0</sub>}</code><br><code>F = {s<sub>1</sub>}</code>, <code>T = {<s<sub>0</sub>, a, s<sub>1</sub>>}</code>|
| <code>e<sub>1</sub> ∈ RegExp</code>, <code>e<sub>2</sub> ∈ RegExp</code>:<br><code>(e<sub>1</sub> OR e<sub>2</sub>) ∈ RegExp</code> | <code>S = S<sub>1</sub> + S<sub>2</sub></code>, <code>I = I<sub>1</sub> + I<sub>2</sub></code><br><code>F = F<sub>1</sub> + F<sub>2</sub></code>, <code>T = T<sub>1</sub> + T<sub>2</sub></code>|
| <code>e<sub>1</sub> ∈ RegExp</code>, <code>e<sub>2</sub> ∈ RegExp</code>:<br><code>(e<sub>1</sub> AND e<sub>2</sub>) ∈ RegExp</code> | <code>S = S<sub>1</sub> + S<sub>2</sub></code>, <code>I = I<sub>1</sub> + I<sup>'</sup></code><br><code>F = F<sub>2</sub></code>, <code>T = T<sub>1</sub> + T<sub>2</sub> + T<sup>'</sup></code><br>where:<br>if <code>I<sub>1</sub> <b>⋂</b> F<sub>1</sub></code> than <code>I<sup>'</sup> = I<sub>2</sub></code> else <code>I<sup>'</sup> = ∅</code><br>and <code>T<sup>'</sup> = {<s<sub>1</sub>, a, s<sub>2</sub>> ∈ S<sub>1</sub> x &Sigma; x I<sub>2</sub>: <s<sub>1</sub>, a, s<sub>1</sub><sup>'</sup>> ∈ T<sub>1</sub></code> for some <code>s<sub>1</sub><sup>'</sup> ∈ F<sub>1</sub>}</code>|
| <code>e ∈ RegExp</code>:<br><code>e<sup>*</sup> ∈ RegExp</code> | <code>S<sub>*</sub> = S</code>, <code>I<sub>*</sub> = I</code><br><code>F<sub>*</sub> = F + I</code>, <code>T = T + T<sup>'</sup></code><br>where:<br><code>T<sup>'</sup> = {<s<sub>1</sub>, a, s<sub>2</sub>> ∈ S x &Sigma; x I: <s<sub>1</sub>, a, s<sub>1</sub><sup>'</sup>> ∈ T</code> for some <code>s<sub>1</sub><sup>'</sup> ∈ F}</code> |
