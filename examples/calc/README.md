# CALC - Expression parser and calculator

[TOC]

**Grako** has lacked a step-by-step example for a long time, and users have suggested that a simple calculator, like the one in the documentation for [PLY] would be useful. Well, here it is.

[AST]: https://en.wikipedia.org/wiki/Abstract_syntax_tree
[PEG]: https://en.wikipedia.org/wiki/Parsing_expression_grammar
[PLY]: http://www.dabeaz.com/ply/ply.html#ply_nn22

## The initial grammar

This is the original [PLY] grammar for arithmetic expressions:

```ebnf
expression : expression + term
           | expression - term
           | term

term       : term * factor
           | term / factor
           | factor

factor     : NUMBER
           | ( expression )
```

And this is the input expression for testing:

```python
3 + 5 * ( 10 - 20 )
```

## The Grako grammar

The first step is to convert the grammar to **Grako** syntax and style, add rules for lexical elements (``NUMBER`` in this case), and add a ``start`` rule that checks for end of input, and a directive to name the generated classes:

```ocaml
@@grammar::CALC


start
    =
    expression $
    ;


expression
    =
    | expression '+' term
    | expression '-' term
    | term
    ;


term
    =
    | term '*' factor
    | term '/' factor
    | factor
    ;


factor
    =
    | '(' expression ')'
    | number
    ;


number
    =
    /\d+/
    ;
```

## Remove left recursion

Left recursion in [PEG] grammars is still a research subject, and existing left-recursion algorithms cannot handle all cases that are intuitivelly correct. It's best to stick to the [PEG] definition, and remove left recursion:

```ocaml
@@grammar::CALC


start
    =
    expression $
    ;


expression
    =
    | term '+' expression
    | term '-' expression
    | term
    ;


term
    =
    | factor '*' term
    | factor '/' term
    | factor
    ;


factor
    =
    | '(' expression ')'
    | number
    ;


number
    =
    /\d+/
    ;
```

## Add _cut_ expressions

_Cut_ expressions make a parser commit to a particular option after certain tokens have been seen.  They make parsing more efficient, because other options are not tried. They also make error messages more precise, because errors will be reported closest to the point of failure in the input.


```ocaml
@@grammar::CALC


start
    =
    expression $
    ;


expression
    =
    | term '+' ~ expression
    | term '-' ~ expression
    | term
    ;


term
    =
    | factor '*' ~ term
    | factor '/' ~ term
    | factor
    ;


factor
    =
    | '(' ~ expression ')'
    | number
    ;


number
    =
    /\d+/
    ;
```

We can now compile the grammar, and test the parser:

```bash
$ PYTHONPATH=../../.. python -m grako -o calc_parser.py calc.ebnf
$ PYTHONPATH=../../.. python calc_parser.py ../input.txt
AST:
[u'3', u'+', [u'5', u'*', [u'(', [u'10', u'-', u'20'], u')']]]

JSON:
[
  "3",
  "+",
  [
    "5",
    "*",
    [
      "(",
      [
        "10",
        "-",
        "20"
      ],
      ")"
    ]
  ]
]
```

The default output for the generated parser consists of the ``__str__`` and [JSON] representations of the [AST] resulting from the parse.

## Adding semantics

Semantics for **Grako** parsers are not specified in the grammar, but in a separate _semantics_ class.

```python
from __future__ import print_function
import sys
from calc_parser import CalcParser


class CalcSemantics(object):
    def number(self, ast):
       return int(ast)

    def factor(self, ast):
       if not isinstance(ast, list):
           return ast
       else:
           return ast[1]

    def term(self, ast):
        if not isinstance(ast, list):
            return ast
        elif ast[1] == '*':
            return ast[0] * ast[2]
        elif ast[1] == '/':
            return ast[0] / ast[2]
        else:
            raise Exception('Unknown operator', ast[1])

    def expression(self, ast):
        if not isinstance(ast, list):
            return ast
        elif ast[1] == '+':
            return ast[0] + ast[2]
        elif ast[1] == '-':
            return ast[0] - ast[2]
        else:
            raise Exception('Unknown operator', ast[1])


def calc(text):
    parser = CalcParser(semantics=CalcSemantics())
    return parser.parse(text)

if __name__ == '__main__':
    text = open(sys.argv[1]).read()
    result = calc(text)
    print(text.strip(), '=', result)
```

```bash
$ PYTHONPATH=../../.. python -m grako -o calc_parser.py calc.ebnf
------------------------------------------------------------------------
          50  lines in grammar
           5  rules in grammar
          41  nodes in AST
$ PYTHONPATH=../../.. python calc.py ../input.txt
3 + 5 * ( 10 - 20 ) = -47
```

## Annotating the grammar

Dealing with [AST]s that are lists of lists leads to code that is difficult to read, and
error-prone. **Grako** allows naming the elements in a rule to produce more humanly-readable [AST]s and to allow for clearer semantics code. This is an annotated version of the grammar:

```ocaml
@@grammar::Calc


start
    =
    expression $
    ;


expression
    =
    | left:term op:'+' ~ right:expression
    | left:term op:'-' ~ right:expression
    | term:term
    ;


term
    =
    | left:factor op:'*' ~ right:term
    | left:factor '/' ~ right:term
    | factor:factor
    ;


factor
    =
    | '(' ~ @:expression ')'
    | number
    ;


number
    =
    /\d+/
    ;
```

And these are the corresponding semantics:

```python
class CalcSemantics(object):
    def number(self, ast):
       return int(ast)

    def term(self, ast):
        if ast.factor:
            return ast.factor
        elif ast.op == '*':
            return ast.left * ast.right
        elif ast.op == '/':
            return ast.left / ast.right
        else:
            raise Exception('Unknown operator', ast.op)

    def expression(self, ast):
        if ast.term:
            return ast.term
        elif ast.op == '+':
            return ast.left + ast.right
        elif ast.op == '-':
            return ast.left - ast.right
        else:
            raise Exception('Unknown operator', ast.op)
```

The result is the same:

```bash
$ PYTHONPATH=../../.. python calc.py ../input.txt
3 + 5 * ( 10 - 20 ) = -47
```

But the [AST] is not too satisfactory:

```json
{
  "left": {
    "factor": "3",
    "left": null,
    "op": null,
    "right": null
  },
  "op": "+",
  "right": {
    "term": {
      "left": "5",
      "op": "*",
      "right": {
        "factor": {
          "left": {
            "factor": "10",
            "left": null,
            "op": null,
            "right": null
          },
          "op": "-",
          "right": {
            "term": {
              "factor": "20",
              "left": null,
              "op": null,
              "right": null
            },
            "left": null,
            "op": null,
            "right": null
          },
          "term": null
        },
        "left": null,
        "op": null,
        "right": null
      },
      "factor": null
    },
    "left": null,
    "op": null,
    "right": null
  },
  "term": null
}
```

## One rule per expression type
