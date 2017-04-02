|fury| |license| |pyversions| |travis| |landscape|

    *At least for the people who send me mail about a new language that
    they're designing, the general advice is: do it to learn about how
    to write a compiler. Don't have any expectations that anyone will
    use it, unless you hook up with some sort of organization in a
    position to push it hard. It's a lottery, and some can buy a lot of
    the tickets. There are plenty of beautiful languages (more beautiful
    than C) that didn't catch on. But someone does win the lottery, and
    doing a language at least teaches you something.*

    `Dennis Ritchie <http://en.wikipedia.org/wiki/Dennis_Ritchie>`__
    (1941-2011) *Creator of the
    `C <http://en.wikipedia.org/wiki/C_language>`__ programming language
    and of `Unix <http://en.wikipedia.org/wiki/Unix>`__*

Grako
=====

::

    Copyright (C) 2017      by Juancarlo Añez
    Copyright (C) 2012-2016 by Juancarlo Añez and Thomas Bragg

    **THE ORIGINAL SOURCE OF FUNDING FOR *GRAKO* DEVELOPMENT HAS ENDED**

    |donate|

    *And my work is moving away from parsing and translation.*

    *If you'd like to contribute to the future development of **Grako**,
    please* **`make a
    donation <https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=P9PV7ZACB669J>`__**.

    *Some of the planned new features are: grammar expressions for left
    and right associativity, new algorithms for left-recursion, a
    unified intermediate model for parsing and translating programming
    languages, and more...*

**Grako** (for *grammar compiler*) is a tool that takes grammars in a
variation of `EBNF <http://en.wikipedia.org/wiki/Ebnf>`__ as input, and
outputs `memoizing <http://en.wikipedia.org/wiki/Memoization>`__
(`Packrat <http://bford.info/packrat/>`__)
`PEG <http://en.wikipedia.org/wiki/Parsing_expression_grammar>`__
parsers in `Python <http://python.org>`__.

**Grako** is *different* from other
`PEG <http://en.wikipedia.org/wiki/Parsing_expression_grammar>`__ parser
generators:

-  Generated parsers use `Python <http://python.org>`__'s very efficient
   exception-handling system to backtrack. **Grako** generated parsers
   simply assert what must be parsed. There are no complicated
   *if-then-else* sequences for decision making or backtracking.
   Memoization allows going over the same input sequence several times
   in linear time.
-  *Positive and negative lookaheads*, and the *cut* element (with its
   cleaning of the memoization cache) allow for additional, hand-crafted
   optimizations at the grammar level.
-  Delegation to `Python <http://python.org>`__'s
   `re <https://docs.python.org/3.4/library/re.html>`__ module for
   *lexemes* allows for (`Perl <http://www.perl.org/>`__-like) powerful
   and efficient lexical analysis.
-  The use of `Python <http://python.org>`__'s `context
   managers <http://docs.python.org/2/library/contextlib.html>`__
   considerably reduces the size of the generated parsers for code
   clarity, and enhanced CPU-cache hits.
-  Include files, rule inheritance, and rule inclusion give **Grako**
   grammars considerable expressive power.
-  Automatic generation of Abstract Syntax Trees\_ and Object Models,
   along with *Model Walkers* and *Code Generators* make analysis and
   translation approachable

The parser generator, the run-time support, and the generated parsers
have measurably low `Cyclomatic
complexity <http://en.wikipedia.org/wiki/Cyclomatic_complexity>`__. At
around 5 `KLOC <http://en.wikipedia.org/wiki/KLOC>`__ of
`Python <http://python.org>`__, it is possible to study all its source
code in a single session.

The only dependencies are on the `Python <http://python.org>`__ standard
library, yet the `regex <https://pypi.python.org/pypi/regex>`__ library
will be used if installed, and
`colorama <https://pypi.python.org/pypi/colorama/>`__ will be used on
trace output if available.
`pygraphviz <https://pypi.python.org/pypi/pygraphviz>`__ is required for
generating diagrams.

**Grako** is feature-complete and currently being used with complex
grammars to parse, analyze, and translate hundreds of thousands of lines
of input text, including source code in several programming languages.

Table of Contents
-----------------

[TOC]

Rationale
---------

**Grako** was created to address some recurring problems encountered
over decades of working with parser generation tools:

-  Some programming languages allow the use of *keywords* as
   identifiers, or have different meanings for symbols depending on
   context (`Ruby <http://www.ruby-lang.org/>`__). A parser needs
   control of lexical analysis to be able to handle those languages.
-  LL and LR grammars become contaminated with myriads of lookahead
   statements to deal with ambiguous constructs in the source language.
   `PEG <http://en.wikipedia.org/wiki/Parsing_expression_grammar>`__
   parsers address ambiguity from the onset.
-  Separating the grammar from the code that implements the semantics,
   and using a variation of a well-known grammar syntax
   (`EBNF <http://en.wikipedia.org/wiki/Ebnf>`__) allows for full
   declarative power in language descriptions. General-purpose
   programming languages are not up to the task.
-  Semantic actions *do not* belong in a grammar. They create yet
   another programming language to deal with when doing parsing and
   translation: the source language, the grammar language, the semantics
   language, the generated parser's language, and the translation's
   target language. Most grammar parsers do not check the syntax of
   embedded semantic actions, so errors get reported at awkward moments,
   and against the generated code, not against the grammar.
-  Preprocessing (like dealing with includes, fixed column formats, or
   structure-through-indentation) belongs in well-designed program code;
   not in the grammar.
-  It is easy to recruit help with knowledge about a mainstream
   programming language like `Python <http://python.org>`__, but help is
   hard to find for working with complex grammar-description languages.
   **Grako** grammars are in the spirit of a *Translators and
   Interpreters 101* course (if something is hard to explain to a
   college student, it's probably too complicated, or not well
   understood).
-  Generated parsers should be easy to read and debug by humans. Looking
   at the generated source code is sometimes the only way to find
   problems in a grammar, the semantic actions, or in the parser
   generator itself. It's inconvenient to trust generated code that one
   cannot understand.
-  `Python <http://python.org>`__ is a great language for working with
   language parsing and translation.

The Generated Parsers
---------------------

A **Grako** generated parser consists of the following classes:

-  A ``MyLanguageBuffer`` class derived from ``grako.buffering.Buffer``
   that handles the grammar definitions for *whitespace*, *comments*,
   and *case significance*.
-  A ``MyLanguageParser`` class derived from ``grako.parsing.Parser``
   which uses a ``MyLanguageBuffer`` for traversing input text, and
   implements the parser using one method for each grammar rule:

.. code:: python

            def _somerulename_(self):
                ...

-  A ``MyLanguageSemantics`` class with one semantic method per grammar
   rule. Each method receives as its single parameter the `Abstract
   Syntax Tree <http://en.wikipedia.org/wiki/Abstract_syntax_tree>`__
   (`AST <http://en.wikipedia.org/wiki/Abstract_syntax_tree>`__) built
   from the rule invocation:

.. code:: python

            def somerulename(self, ast):
                return ast

-  A ``if __name__ == '__main__':`` definition, so the generated parser
   can be executed as a `Python <http://python.org>`__ script.

The methods in the delegate class return the same
`AST <http://en.wikipedia.org/wiki/Abstract_syntax_tree>`__ received as
parameter, but custom semantic classes can override the methods to have
them return anything (for example, a `Semantic
Graph <http://en.wikipedia.org/wiki/Abstract_semantic_graph>`__). The
semantics class can be used as a template for the final semantics
implementation, which can omit methods for the rules that do not need
semantic treatment.

If present, a ``_default()`` method will be called in the semantics
class when no method matched the rule name:

.. code:: python

    def _default(self, ast):
        ...
        return ast

If present, a ``_postproc()`` method will be called in the semantics
class after each rule (including the semantics) is processed. This
method will receive the current parsing context as parameter:

.. code:: python

    def _postproc(self, context, ast):
        ...

Using the Tool
--------------

**Grako** can be run from the command line:

.. code:: bash

    $ python -m grako

Or:

.. code:: bash

    $ scripts/grako

Or just:

.. code:: bash

    $ grako

if **Grako** was installed using *easy\_install* or *pip*.

The *-h* and *--help* parameters provide full usage information:

.. code:: bash

    $ python -m grako -h
    usage: grako [--generate-parser | --draw | --object-model | --pretty]
                [--color] [--trace] [--no-left-recursion] [--name NAME]
                [--no-nameguard] [--outfile FILE] [--object-model-outfile FILE]
                [--whitespace CHARACTERS] [--help] [--version]
                GRAMMAR

    Grako (for "grammar compiler") takes a grammar in a variation of EBNF as
    input, and outputs a memoizing PEG/Packrat parser in Python.

    positional arguments:
    GRAMMAR               the filename of the Grako grammar to parse

    optional arguments:
    --generate-parser     generate parser code from the grammar (default)
    --draw, -d            generate a diagram of the grammar (requires --outfile)
    --object-model, -g    generate object model from the class names given as
                            rule arguments
    --pretty, -p          generate a prettified version of the input grammar

    parse-time options:
    --color, -c           use color in traces (requires the colorama library)
    --trace, -t           produce verbose parsing output

    generation options:
    --no-left-recursion, -l
                            turns left-recusion support off
    --name NAME, -m NAME  Name for the grammar (defaults to GRAMMAR base name)
    --no-nameguard, -n    allow tokens that are prefixes of others
    --outfile FILE, --output FILE, -o FILE
                            output file (default is stdout)
    --object-model-outfile FILE, -G FILE
                            generate object model and save to FILE
    --whitespace CHARACTERS, -w CHARACTERS
                            characters to skip during parsing (use "" to disable)

    common options:
    --help, -h            show this help message and exit
    --version, -v         provide version information and exit
    $

Using the Generated Parser
--------------------------

To use the generated parser, just subclass the base or the abstract
parser, create an instance of it, and invoke its ``parse()`` method
passing the grammar to parse and the starting rule's name as parameter:

.. code:: python

    from myparser import MyParser

    parser = MyParser()
    ast = parser.parse('text to parse', rule_name='start')
    print(ast)
    print(json.dumps(ast, indent=2)) # ASTs are JSON-friendy

The generated parsers' constructors accept named arguments to specify
whitespace characters, the regular expression for comments, case
sensitivity, verbosity, and more (see below).

To add semantic actions, just pass a semantic delegate to the parse
method:

.. code:: python

    model = parser.parse(text, rule_name='start', semantics=MySemantics())

If special lexical treatment is required (as in *80 column* languages),
then a descendant of ``grako.buffering.Buffer`` can be passed instead of
the text:

.. code:: python

    class MySpecialBuffer(MyLanguageBuffer):
        ...

    buf = MySpecialBuffer(text)
    model = parser.parse(buf, rule_name='start', semantics=MySemantics())

The generated parser's module can also be invoked as a script:

.. code:: bash

    $ python myparser.py inputfile startrule

As a script, the generated parser's module accepts several options:

.. code:: bash

    $ python myparser.py -h
    usage: myparser.py [-h] [-c] [-l] [-n] [-t] [-w WHITESPACE] FILE [STARTRULE]

    Simple parser for DBD.

    positional arguments:
        FILE                  the input file to parse
        STARTRULE             the start rule for parsing

    optional arguments:
        -h, --help            show this help message and exit
        -c, --color           use color in traces (requires the colorama library)
        -l, --list            list all rules and exit
        -n, --no-nameguard    disable the 'nameguard' feature
        -t, --trace           output trace information
        -w WHITESPACE, --whitespace WHITESPACE
                            whitespace specification

Grammar Syntax
--------------

**Grako** uses a variant of the standard
`EBNF <http://en.wikipedia.org/wiki/Ebnf>`__ syntax. Syntax definitions
for `VIM <http://www.vim.org/>`__ and for `Sublime
Text <https://www.sublimetext.com>`__ can be found under the ``etc/vim``
and ``etc/sublime`` directories in the source code distribution.

Rules
~~~~~

A grammar consists of a sequence of one or more rules of the form:

.. code:: ocaml

    name = <expre> ;

If a *name* collides with a `Python <http://python.org>`__ keyword, an
underscore (``_``) will be appended to it on the generated parser.

Rule names that start with an uppercase character:

.. code:: ocaml

    FRAGMENT = /[a-z]+/ ;

*do not* advance over whitespace before beginning to parse. This feature
becomes handy when defining complex lexical elements, as it allows
breaking them into several rules.

The parser returns an
`AST <http://en.wikipedia.org/wiki/Abstract_syntax_tree>`__ value for
each rule depending on what was parsed:

-  A single value
-  A list of `AST <http://en.wikipedia.org/wiki/Abstract_syntax_tree>`__
-  A dict-like object for rules with named elements
-  An object, when ModelBuilderSemantics is used
-  None

See the *Abstract Syntax Trees* and *Building Models* sections for more
details.

Expressions
~~~~~~~~~~~

The expressions, in reverse order of operator precedence, can be:

``e1 | e2``
^^^^^^^^^^^

: Choice. Match either ``e1`` or ``e2``.

::

    A `|` be be used before the first option if desired:

        choices
            =
            | e1
            | e2
            | e3
            ;

``e1 e2``
^^^^^^^^^

: Sequence. Match ``e1`` and then match ``e2``.

``( e )``
^^^^^^^^^

: Grouping. Match ``e``. For example: ``('a' | 'b')``.

``[ e ]``
^^^^^^^^^

: Optionally match ``e``.

``{ e }`` or ``{ e }*``
^^^^^^^^^^^^^^^^^^^^^^^

: Closure. Match ``e`` zero or more times. Note that the
`AST <http://en.wikipedia.org/wiki/Abstract_syntax_tree>`__ returned for
a closure is always a list.

``{ e }+``
^^^^^^^^^^

: Positive closure. Match ``e`` one or more times. The
`AST <http://en.wikipedia.org/wiki/Abstract_syntax_tree>`__ is always a
list.

``{}``
^^^^^^

: Empty closure. Match nothing and produce an empty list as
`AST <http://en.wikipedia.org/wiki/Abstract_syntax_tree>`__.

``~``
^^^^^

: The *cut* expression. Commit to the current option and prevent other
options from being considered even if what follows fails to parse.

::

    In this example, other options won't be considered if a
    parenthesis is parsed:

        atom
            =
              '(' ~ @:expre ')'
            | int
            | bool
            ;

``s.{ e }+``
^^^^^^^^^^^^

: Positive join. Inspired by `Python <http://python.org>`__'s
``str.join()``, is equivalent to:

::

        e {s ~ e}

    The `s` part is not included in the resulting [AST][Abstract
    Syntax Tree].

    Use grouping if `s` is more complex than a *token* or a *pattern*:

        (s t).{ e }+

``s.{ e }`` or ``s.{ e }*``
^^^^^^^^^^^^^^^^^^^^^^^^^^^

: Join. Parses the list of ``s``-separated expressions, or nothing.

::

    It is equivalent to:

        s.{e}+|{}

``&e``
^^^^^^

: Positive lookahead. Succeed if ``e`` can be parsed, but do not consume
any input.

``!e``
^^^^^^

: Negative lookahead. Fail if ``e`` can be parsed, and do not consume
any input.

``'text'`` or ``"text"``
^^^^^^^^^^^^^^^^^^^^^^^^

: Match the token *text* within the quotation marks.

::

    Note that if *text* is alphanumeric, then **Grako** will check
    that the character following the token is not alphanumeric. This
    is done to prevent tokens like *IN* matching when the text ahead
    is *INITIALIZE*. This feature can be turned off by passing
    `nameguard=False` to the `Parser` or the `Buffer`, or by using a
    pattern expression (see below) instead of a token expression.
    Alternatively, the `@@nameguard` or `@@namechars` directives may
    be specified in the grammar:

        @@nameguard :: False

    or to specify additional characters that should also be considered
    part of names:

        @@namechars :: '$-.'

``r'text'`` or ``r"text"``
^^^^^^^^^^^^^^^^^^^^^^^^^^

: Match the token *text* within the quotation marks, interpreting *text*
like `Python <http://python.org>`__'s `raw string
literal <https://docs.python.org/3/reference/lexical_analysis.html#string-and-bytes-literals>`__\ s.

``?"regexp"`` or ``?'regexp'``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

: The *pattern* expression. Match the `Python <http://python.org>`__
regular expression ``regexp`` at the current text position. Unlike other
expressions, this one does not advance over whitespace or comments. For
that, place the ``regexp`` as the only term in its own rule.

::

    The *regex* is interpreted as a [Python]'s [raw string literal] and
    passed *as-is* to the [Python][] [re] module (or to
    [regex], if available), using `match()` at the current position in
    the text. The matched text is the [AST][Abstract Syntax Tree] for
    the expression.

    Consecutive patterns are concatenated to form a single one.

-  ``/regexp/``

: Another form of the *pattern* expression.

-  ``+/regexp/``

: Concatenate the given pattern with the preceding one.

```constant``\ \`
^^^^^^^^^^^^^^^^^

: Match nothing, but behave as if ``constant`` had been parsed.

::

    Constants can be used to inject elements into the concrete and
    abstract syntax trees, perhaps avoiding having to write a
    semantic action. For example:

        boolean_option = name ['=' (boolean|`true`) ] ;

``rulename``
^^^^^^^^^^^^

: Invoke the rule named ``rulename``. To help with lexical aspects of
grammars, rules with names that begin with an uppercase letter will not
advance the input over whitespace or comments.

``>rulename``
^^^^^^^^^^^^^

: The include operator. Include the *right hand side* of rule
``rulename`` at this point.

::

    The following set of declarations:

        includable = exp1 ;

        expanded = exp0 >includable exp2 ;

    Has the same effect as defining *expanded* as:

        expanded = exp0 exp1 exp2 ;

    Note that the included rule must be defined before the rule that
    includes it.

``()``
^^^^^^

: The empty expression. Succeed without advancing over input. Its value
is ``None``.

``!()``
^^^^^^^

: The *fail* expression. This is actually ``!`` applied to ``()``, which
always fails.

``name:e``
^^^^^^^^^^

: Add the result of ``e`` to the
`AST <http://en.wikipedia.org/wiki/Abstract_syntax_tree>`__ using
``name`` as key. If ``name`` collides with any attribute or method of
``dict``, or is a `Python <http://python.org>`__ keyword, an underscore
(``_``) will be appended to the name.

``name+:e``
^^^^^^^^^^^

: Add the result of ``e`` to the
`AST <http://en.wikipedia.org/wiki/Abstract_syntax_tree>`__ using
``name`` as key. Force the entry to be a list even if only one element
is added. Collisions with ``dict`` attributes or
`Python <http://python.org>`__ keywords are resolved by appending an
underscore to ``name``.

``@:e``
^^^^^^^

: The override operator. Make the
`AST <http://en.wikipedia.org/wiki/Abstract_syntax_tree>`__ for the
complete rule be the
`AST <http://en.wikipedia.org/wiki/Abstract_syntax_tree>`__ for ``e``.

::

    The override operator is useful to recover only part of the right
    hand side of a rule without the need to name it, or add a
    semantic action.

    This is a typical use of the override operator:

        subexp = '(' @:expre ')' ;

    The [AST][Abstract Syntax Tree] returned for the `subexp` rule
    will be the [AST][Abstract Syntax Tree] recovered from invoking
    `expre`.

``@+:e``
^^^^^^^^

: Like ``@:e``, but make the
`AST <http://en.wikipedia.org/wiki/Abstract_syntax_tree>`__ always be a
list.

::

    This operator is convenient in cases such as:

        arglist = '(' @+:arg {',' @+:arg}* ')' ;

    In which the delimiting tokens are of no interest.

``$``
^^^^^

: The *end of text* symbol. Verify that the end of the input text has
been reached.

``#`` *comment*
^^^^^^^^^^^^^^^

: `Python <http://python.org>`__-style comments are also allowed.

When there are no named items in a rule, the
`AST <http://en.wikipedia.org/wiki/Abstract_syntax_tree>`__ consists of
the elements parsed by the rule, either a single item or a list. This
default behavior makes it easier to write simple rules:

.. code:: ocaml

    number = /[0-9]+/ ;

Without having to write:

.. code:: ocaml

    number = number:/[0-9]+/ ;

When a rule has named elements, the unnamed ones are excluded from the
`AST <http://en.wikipedia.org/wiki/Abstract_syntax_tree>`__ (they are
ignored).

Deprecated Expressions
~~~~~~~~~~~~~~~~~~~~~~

The following expressions are still recognized in grammars, but they are
considered deprecated, and will be removed in a future version of
**Grako**.

-  ``?/regexp/?``

: Another form of the pattern expression that can be used when there are
slashes (``/``) in the pattern. Use the ``?"regexp"`` or ``?'regexp'``
forms instead.

-  ``(*`` *comment* ``*)``

: Comments may appear anywhere in the text. Use the
`Python <http://python.org>`__-style comments instead.

Rules with Arguments
~~~~~~~~~~~~~~~~~~~~

**Grako** allows rules to specify `Python <http://python.org>`__-style
arguments:

.. code:: ocaml

    addition(Add, op='+')
        =
        addend '+' addend
        ;

The arguments values are fixed at grammar-compilation time.

An alternative syntax is available if no *keyword parameters* are
required:

.. code:: ocaml

    addition::Add, '+'
        =
        addend '+' addend
        ;

Semantic methods must be ready to receive any arguments declared in the
corresponding rule:

.. code:: python

    def addition(self, ast, name, op=None):
        ...

When working with rule arguments, it is good to define a ``_default()``
method that is ready to take any combination of standard and keyword
arguments:

.. code:: python

    def _default(self, ast, *args, **kwargs):
        ...

Based Rules
~~~~~~~~~~~

Rules may extend previously defined rules using the ``<`` operator. The
*base rule* must be defined previously in the grammar.

The following set of declarations:

.. code:: ocaml

    base::Param = exp1 ;

    extended < base = exp2 ;

Has the same effect as defining *extended* as:

.. code:: ocaml

    extended::Param = exp1 exp2 ;

Parameters from the *base rule* are copied to the new rule if the new
rule doesn't define its own. Repeated inheritance should be possible,
but it *hasn't been tested*.

Rule Overrides
~~~~~~~~~~~~~~

A grammar rule may be redefined by using the ``@override`` decorator:

.. code:: ocaml

    start = ab $;

    ab = 'xyz' ;

    @override
    ab = @:'a' {@:'b'} ;

When combined with the ``#include`` directive, rule overrides can be
used to create a modified grammar without altering the original.

Abstract Syntax Trees (ASTs)
----------------------------

By default, and
`AST <http://en.wikipedia.org/wiki/Abstract_syntax_tree>`__ is either a
*list* (for *closures* and rules without named elements), or
*dict*-derived object that contains one item for every named element in
the grammar rule. Items can be accessed through the standard ``dict``
syntax (``ast['key']``), or as attributes (``ast.key``).

`AST <http://en.wikipedia.org/wiki/Abstract_syntax_tree>`__ entries are
single values if only one item was associated with a name, or lists if
more than one item was matched. There's a provision in the grammar
syntax (the ``+:`` operator) to force an
`AST <http://en.wikipedia.org/wiki/Abstract_syntax_tree>`__ entry to be
a list even if only one element was matched. The value for named
elements that were not found during the parse (perhaps because they are
optional) is ``None``.

When the ``parseinfo=True`` keyword argument has been passed to the
``Parser`` constructor, a ``parseinfo`` element is added to
`AST <http://en.wikipedia.org/wiki/Abstract_syntax_tree>`__ nodes that
are *dict*-like. The element contains a ``collections.namedtuple`` with
the parse information for the node:

.. code:: python

    ParseInfo = namedtuple(
        'ParseInfo',
        [
            'buffer',
            'rule',
            'pos',
            'endpos',
            'line',
            'endline',
        ]
    )

With the help of the ``Buffer.line_info()`` method, it is possible to
recover the line, column, and original text parsed for the node. Note
that when ``ParseInfo`` is generated, the ``Buffer`` used during parsing
is kept in memory for the lifetime of the
`AST <http://en.wikipedia.org/wiki/Abstract_syntax_tree>`__.

Generation of ``parseinfo`` can also be controlled using the
``@@parseinfo :: True`` grammar directive.

Grammar Name
------------

The prefix to be used in classes generated by **Grako** can be passed to
the command-line tool using the ``-m`` option:

.. code:: bash

    $ grako -m MyLanguage mygrammar.ebnf

will generate:

.. code:: python

    class MyLanguageParser(Parser):
        ...

The name can also be specified within the grammar using the
``@@grammar`` directive:

.. code:: ocaml

    @@grammar :: MyLanguage

Whitespace
----------

By default, **Grako** generated parsers skip the usual whitespace
characters with the regular expression ``r'\s+'`` using the
``re.UNICODE`` flag (or with the ``Pattern_White_Space`` property if the
`regex <https://pypi.python.org/pypi/regex>`__ module is available), but
you can change that behavior by passing a ``whitespace`` parameter to
your parser.

For example, the following will skip over *tab* (``\t``) and *space*
characters, but not so with other typical whitespace characters such as
*newline* (``\n``):

.. code:: python

    parser = MyParser(text, whitespace='\t ')

The character string is converted into a regular expression character
set before starting to parse.

You can also provide a regular expression directly instead of a string.
The following is equivalent to the above example:

.. code:: python

    parser = MyParser(text, whitespace=re.compile(r'[\t ]+'))

Note that the regular expression must be pre-compiled to let **Grako**
distinguish it from plain string.

If you do not define any whitespace characters, then you will have to
handle whitespace in your grammar rules (as it's often done in
`PEG <http://en.wikipedia.org/wiki/Parsing_expression_grammar>`__
parsers):

.. code:: python

    parser = MyParser(text, whitespace='')

Whitespace may also be specified within the grammar using the
``@@whitespace`` directive, although any of the above methods will
overwrite the setting in the grammar:

.. code:: ocaml

    @@whitespace :: /[\t ]+/

Case Sensitivity
----------------

If the source language is case insensitive, it can be specified in the
parser by using the ``ignorecase`` parameter:

.. code:: python

    parser = MyParser(text, ignorecase=True)

You may also specify case insensitivity within the grammar using the
``@@ignorecase`` directive:

.. code:: ocaml

    @@ignorecase :: True

The change will affect both token and pattern matching.

Comments
--------

Parsers will skip over comments specified as a regular expression using
the ``comments_re`` parameter:

.. code:: python

    parser = MyParser(text, comments_re="\(\*.*?\*\)")

For more complex comment handling, you can override the
``Buffer.eat_comments()`` method.

For flexibility, it is possible to specify a pattern for end-of-line
comments separately:

.. code:: python

    parser = MyParser(
        text,
        comments_re="\(\*.*?\*\)",
        eol_comments_re="#.*?$"
    )

Both patterns may also be specified within a grammar using the
``@@comments`` and ``@@eol_comments`` directives:

.. code:: ocaml

    @@comments :: /\(\*.*?\*\)/
    @@eol_comments :: /#.*?$/

Reserved Words and Keywords
---------------------------

Some languages must reserve the use of certain tokens as valid
identifiers because the tokens are used to mark particular constructs in
the language. Those reserved tokens are known as `Reserved
Words <https://en.wikipedia.org/wiki/Reserved_word>`__ or
`Keywords <https://en.wikipedia.org/wiki/Reserved_word>`__

**Grako** provides support for preventing the use of
`keywords <https://en.wikipedia.org/wiki/Reserved_word>`__ as
identifiers though the ``@@ keyword`` directive,and the ``@ name``
decorator.

A grammar may specify reserved tokens providing a list of them in one or
more ``@@ keyword`` directives:

.. code:: ocaml

    @@keyword :: if endif
    @@keyword :: else elseif

The ``@ name`` decorator checks that the result of a grammar rule does
not match a token defined as a
`keyword <https://en.wikipedia.org/wiki/Reserved_word>`__:

.. code:: ocaml

    @name
    identifier = /(?!\d)\w+/ ;

There are situations in which a token is reserved only in a very
specific context. In those cases, a negative lookahead will prevent the
use of the token:

.. code:: ocaml

    statements = {!'END' statement}+ ;

Semantic Actions
----------------

There are no constructs for semantic actions in **Grako** grammars. This
is on purpose, because semantic actions obscure the declarative nature
of grammars and provide for poor modularization from the
parser-execution perspective.

Semantic actions are defined in a class, and applied by passing an
object of the class to the ``parse()`` method of the parser as the
``semantics=`` parameter. **Grako** will invoke the method that matches
the name of the grammar rule every time the rule parses. The argument to
the method will be the
`AST <http://en.wikipedia.org/wiki/Abstract_syntax_tree>`__ constructed
from the right-hand-side of the rule:

.. code:: python

    class MySemantics(object):
        def some_rule_name(self, ast):
            return ''.join(ast)

        def _default(self, ast):
            pass

If there's no method matching the rule's name, **Grako** will try to
invoke a ``_default()`` method if it's defined:

.. code:: python

    def _default(self, ast):
        ...

Nothing will happen if neither the per-rule method nor ``_default()``
are defined.

The per-rule methods in classes implementing the semantics provide
enough opportunity to do rule post-processing operations, like
verifications (for inadequate use of keywords as identifiers), or
`AST <http://en.wikipedia.org/wiki/Abstract_syntax_tree>`__
transformation:

.. code:: python

    class MyLanguageSemantics(object):
        def identifier(self, ast):
            if my_lange_module.is_keyword(ast):
                raise FailedSemantics('"%s" is a keyword' % str(ast))
            return ast

For finer-grained control it is enough to declare more rules, as the
impact on the parsing times will be minimal.

If preprocessing is required at some point, it is enough to place
invocations of empty rules where appropriate:

.. code:: python

    myrule = first_part preproc {second_part} ;

    preproc = () ;

The abstract parser will honor as a semantic action a method declared
as:

.. code:: python

    def preproc(self, ast):
        ...

Include Directive
-----------------

**Grako** grammars support file inclusion through the include directive:

.. code:: ocaml

    #include :: "filename"

The resolution of the *filename* is relative to the directory/folder of
the source. Absolute paths and ``../`` navigations are honored.

The functionality required for implementing includes is available to all
**Grako**-generated parsers through the ``Buffer`` class; see the
``EBNFBuffer`` class in the ``grako.parser`` module for an example.

Building Models
---------------

Naming elements in grammar rules makes the parser discard uninteresting
parts of the input, like punctuation, to produce an *Abstract Syntax
Tree* (`AST <http://en.wikipedia.org/wiki/Abstract_syntax_tree>`__) that
reflects the semantic structure of what was parsed. But an
`AST <http://en.wikipedia.org/wiki/Abstract_syntax_tree>`__ doesn't
carry information about the rule that generated it, so navigating the
trees may be difficult.

**Grako** defines the ``grako.model.ModelBuilderSemantics`` semantics
class which helps construct object models from abtract syntax trees:

.. code:: python

    from grako.model import ModelBuilderSemantics

    parser = MyParser(semantics=ModelBuilderSemantics())

Then you add the desired node type as first parameter to each grammar
rule:

.. code:: ocaml

    addition::AddOperator = left:mulexpre '+' right:addition ;

``ModelBuilderSemantics`` will synthesize a ``class AddOperator(Node):``
class and use it to construct the node. The synthesized class will have
one attribute with the same name as the named elements in the rule.

You can also use `Python <http://python.org>`__'s built-in types as node
types, and ``ModelBuilderSemantics`` will do the right thing:

.. code:: ocaml

    integer::int = /[0-9]+/ ;

``ModelBuilderSemantics`` acts as any other semantics class, so its
default behavior can be overidden by defining a method to handle the
result of any particular grammar rule.

Walking Models
~~~~~~~~~~~~~~

The class ``grako.model.NodeWalker`` allows for the easy traversal
(*walk*) a model constructed with a ``ModelBuilderSemantics`` instance:

.. code:: python

    from grako.model import NodeWalker

    class MyNodeWalker(NodeWalker):

        def walk_AddOperator(self, node):
            left = self.walk(node.left)
            right = self.walk(node.right)

            print('ADDED', left, right)

    model = MyParser(semantics=ModelBuilderSemantics()).parse(input)

    walker = MyNodeWalker()
    walker.walk(model)

When a method with a name like ``walk_AddOperator()`` is defined, it
will be called when a node of that type is *walked* (the *pythonic*
version of the class name may also be used for the *walk* method:
``walk_add_operator()``.

If a *walk* method for a node class is not found, then a method for the
class's bases is searched, so it is possible to write *catch-all*
methods such as:

.. code:: python

    def walk_Node(self, node):
        print('Reached Node', node)

    def walk_str(self, s):
        return s

    def walk_object(self, o):
        raise Exception('Unexpected tyle %s walked', type(o).__name__)

Predeclared classes can be passed to ``ModelBuilderSemantics`` instances
through the ``types=`` parameter:

.. code:: python

    from mymodel import AddOperator, MulOperator

    semantics=ModelBuilderSemantics(types=[AddOperator, MulOperator])

``ModelBuilderSemantics`` assumes nothing about ``types=``, so any
constructor (a function, or a partial function) can be used.

Model Class Hierarchies
~~~~~~~~~~~~~~~~~~~~~~~

It is possible to specify a a base class for generated model nodes:

.. code:: ocaml

    additive
        =
        | addition
        | substraction
        ;

    addition::AddOperator::Operator
        =
        left:mulexpre op:'+' right:additive
        ;

    substraction::SubstractOperator::Operator
        =
        left:mulexpre op:'-' right:additive
        ;

**Grako** will generate the base class if it's not already known.

Base classes can be used as the target class in *walkers*, and in *code
generators*:

.. code:: python

    class MyNodeWalker(NodeWalker):
        def walk_Operator(self, node):
            left = self.walk(node.left)
            right = self.walk(node.right)
            op = self.walk(node.op)

            print(type(node).__name__, op, left, right)


    class Operator(ModelRenderer):
        template = '{left} {op} {right}'

Templates and Translation
-------------------------

**note**
    As of **Grako** 3.2.0, code generation is separated from grammar
    models through ``grako.codegen.CodeGenerator`` as to allow for code
    generation targets different from `Python <http://python.org>`__.
    Still, the use of inline templates and ``rendering.Renderer`` hasn't
    changed. See the *regex* example for merged modeling and code
    generation.

**Grako** doesn't impose a way to create translators with it, but it
exposes the facilities it uses to generate the
`Python <http://python.org>`__ source code for parsers.

Translation in **Grako** is *template-based*, but instead of defining or
using a complex templating engine (yet another language), it relies on
the simple but powerful ``string.Formatter`` of the
`Python <http://python.org>`__ standard library. The templates are
simple strings that, in **Grako**'s style, are inlined with the code.

To generate a parser, **Grako** constructs an object model of the parsed
grammar. A ``grako.codegen.CodeGenerator`` instance matches model
objects to classes that descend from ``grako.codegen.ModelRenderer`` and
implement the translation and rendering using string templates.
Templates are left-trimmed on whitespace, like
`Python <http://python.org>`__ *doc-comments* are. This is an example
taken from **Grako**'s source code:

.. code:: python

    class Lookahead(ModelRenderer):
        template = '''\
                    with self._if():
                    {exp:1::}\
                    '''

Every *attribute* of the object that doesn't start with an underscore
(``_``) may be used as a template field, and fields can be added or
modified by overriding the ``render_fields(fields)`` method. Fields
themselves are *lazily rendered* before being expanded by the template,
so a field may be an instance of a ``ModelRenderer`` descendant.

The ``rendering`` module defines a ``Formatter`` enhanced to support the
rendering of items in an *iterable* one by one. The syntax to achieve
that is:

.. code:: python

        '''
        {fieldname:ind:sep:fmt}
        '''

All of ``ind``, ``sep``, and ``fmt`` are optional, but the three
*colons* are not. A field specified that way will be rendered using:

.. code:: python

    indent(sep.join(fmt % render(v) for v in value), ind)

The extended format can also be used with non-iterables, in which case
the rendering will be:

.. code:: python

    indent(fmt % render(value), ind)

The default multiplier for ``ind`` is ``4``, but that can be overridden
using ``n*m`` (for example ``3*1``) in the format.

**note**
    Using a newline character (``\n``) as separator will interfere with
    left trimming and indentation of templates. To use a newline as
    separator, specify it as ``\\n``, and the renderer will understand
    the intention.

Left Recursion
--------------

**Grako** provides experimental support for left recursion in
`PEG <http://en.wikipedia.org/wiki/Parsing_expression_grammar>`__
grammars. The implementation of left recursion is ongoing; it does not
yet handle all cases. The algorithm used is `Warth et
al <http://www.vpri.org/pdf/tr2007002_packrat.pdf>`__'s.

Sometimes, while debugging a grammar, it is useful to turn
left-recursion support on or off:

.. code:: python

    parser = MyParser(
        text,
        left_recursion=True,
    )

Left recursion can also be turned off from within the grammar using the
``@@left_recursion`` directive:

.. code:: ocaml

    @@left_recursion :: False

Examples
--------

Grako
~~~~~

The file ``etc/grako.ebnf`` contains a grammar for the **Grako** grammar
language written in its own grammar language. It is used in the
*bootstrap* test suite to prove that **Grako** can generate a parser to
parse its own language, and the resulting parser is made the bootstrap
parser every time **Grako** is stable (see ``grako/bootstrap.py`` for
the generated parser).

**Grako** uses **Grako** to translate grammars into parsers, so it is a
good example of end-to-end translation.

Regex
~~~~~

The project ``examples/regexp`` contains a regexp-to-EBNF translator and
parser generator. The project has no practical use, but it's a complete,
end-to-end example of how to implement a translator using **Grako**.

Calc
~~~~

The project ``examples/calc`` implements a calculator for simple
expressions, and is written as a tutorial over most of the features
provided by **Grako**.

antlr2grako
~~~~~~~~~~~

The project ``examples/antlr2grako`` contains a
`ANTLR <http://www.antlr.org/>`__ to **Grako** grammar translator. The
project is a good example of the use of models and templates in
translation. The program, ``antlr2grako.py`` generates the **Grako**
grammar on standard output, but because the model used is **Grako**'s
own, the same code can be used to directly generate a parser from an
`ANTLR <http://www.antlr.org/>`__ grammar. Please take a look at the
examples *README* to know about limitations.

Other open-source Examples
~~~~~~~~~~~~~~~~~~~~~~~~~~

-  **Christian Ledermann** wrote
   `parsewkt <https://github.com/cleder/parsewkt>`__ a parser for
   `Well-known text <http://en.wikipedia.org/wiki/Well-known_text>`__
   (`WTK <http://en.wikipedia.org/wiki/Well-known_text>`__) using
   **Grako**.
-  **Marcus Brinkmann**
   (`lambdafu <http://blog.marcus-brinkmann.de/>`__) wrote
   `smc.mw <https://github.com/lambdafu/smc.mw>`__, a parser for a
   `MediaWiki <http://www.mediawiki.org/wiki/MediaWiki>`__-style
   language.
-  **Marcus Brinkmann**
   (`lambdafu <http://blog.marcus-brinkmann.de/>`__) is working on a
   *C++ code generator* for **Grako** called
   `Grako++ <https://github.com/lambdafu/grakopp/>`__. Help in the form
   of testing, test cases, and pull requests is welcome.

License
-------

You may use **Grako** under the terms of the
`BSD <http://en.wikipedia.org/wiki/BSD_licenses#2-clause_license_.28.22Simplified_BSD_License.22_or_.22FreeBSD_License.22.29>`__-style
license described in the enclosed **LICENSE.txt** file. *If your project
requires different licensing* please
`email <mailto:apalala@gmail.com>`__.

Contact and Updates
-------------------

For general Q&A, please use the ``[grako]`` tag on
`StackOverflow <http://stackoverflow.com/tags/grako/info>`__.

To discuss **Grako** and to receive notifications about new releases,
please join the low-volume `Grako
Forum <https://groups.google.com/forum/?fromgroups#!forum/grako>`__ at
*Google Groups*.

You can also follow the latest **Grako** developments with [@GrakoPEG]
on [Twitter][@GrakoPEG].

Credits
-------

The following must be mentioned as contributors of thoughts, ideas,
code, *and funding* to the **Grako** project:

-  **Niklaus Wirth** was the chief designer of the programming languages
   `Euler <http://en.wikipedia.org/wiki/Euler_programming_language>`__,
   `Algol W <http://en.wikipedia.org/wiki/Algol_W>`__,
   `Pascal <http://en.wikipedia.org/wiki/Pascal_programming_language>`__,
   `Modula <http://en.wikipedia.org/wiki/Modula>`__,
   `Modula-2 <http://en.wikipedia.org/wiki/Modula-2>`__,
   `Oberon <http://en.wikipedia.org/wiki/Oberon_(programming_language)>`__,
   and `Oberon-2 <http://en.wikipedia.org/wiki/Oberon-2>`__. In the last
   chapter of his 1976 book `Algorithms + Data Structures =
   Programs <http://www.amazon.com/Algorithms-Structures-Prentice-Hall-Automatic-Computation/dp/0130224189/>`__,
   `Wirth <http://en.wikipedia.org/wiki/Niklaus_Wirth>`__ creates a
   top-down, descent parser with recovery for the
   `Pascal <http://en.wikipedia.org/wiki/Pascal_programming_language>`__-like,
   `LL(1) <http://en.wikipedia.org/wiki/LL(1)>`__ programming language
   `PL/0 <http://en.wikipedia.org/wiki/PL/0>`__. The structure of the
   program is that of a
   `PEG <http://en.wikipedia.org/wiki/Parsing_expression_grammar>`__
   parser, though the concept of
   `PEG <http://en.wikipedia.org/wiki/Parsing_expression_grammar>`__
   wasn't formalized until 2004.
-  **Bryan Ford**
   `introduced <http://dl.acm.org/citation.cfm?id=964001.964011>`__
   `PEG <http://en.wikipedia.org/wiki/Parsing_expression_grammar>`__
   (parsing expression grammars) in 2004.
-  Other parser generators like `PEG.js <http://pegjs.majda.cz/>`__ by
   **David Majda** inspired the work in **Grako**.
-  **William Thompson** inspired the use of context managers with his
   `blog
   post <http://dietbuddha.blogspot.com/2012/12/52python-encapsulating-exceptions-with.html>`__
   that I knew about through the invaluable `Python
   Weekly <http://www.pythonweekly.com/>`__ newsletter, curated by
   **Rahul Chaudhary**
-  **Jeff Knupp** explains why **Grako**'s use of
   `exceptions <http://www.jeffknupp.com/blog/2013/02/06/write-cleaner-python-use-exceptions/>`__
   is sound, so I don't have to.
-  **Terence Parr** created `ANTLR <http://www.antlr.org/>`__, probably
   the most solid and professional parser generator out there. *Ter*,
   *ANTLR*, and the folks on the *ANLTR* forums helped me shape my ideas
   about **Grako**.
-  **JavaCC** (originally
   `Jack <http://en.wikipedia.org/wiki/Javacc>`__) looks like an
   abandoned project. It was the first parser generator I used while
   teaching.
-  **Grako** is very fast. But dealing with millions of lines of legacy
   source code in a matter of minutes would be impossible without
   `PyPy <http://pypy.org/>`__, the work of **Armin Rigo** and the `PyPy
   team <http://pypy.org/people.html>`__.
-  **Guido van Rossum** created and has lead the development of the
   `Python <http://python.org>`__ programming environment for over a
   decade. A tool like **Grako**, at under six thousand lines of code,
   would not have been possible without `Python <http://python.org>`__.
-  **Kota Mizushima** welcomed me to the `CSAIL at
   MIT <http://www.csail.mit.edu/>`__ `PEG and Packrat parsing mailing
   list <https://lists.csail.mit.edu/mailman/listinfo/peg>`__, and
   immediately offered ideas and pointed me to documentation about the
   implementation of *cut* in modern parsers. The optimization of
   memoization information in **Grako** is thanks to one of his papers.
-  **My students** at `UCAB <http://www.ucab.edu.ve/>`__ inspired me to
   think about how grammar-based parser generation could be made more
   approachable.
-  **Gustavo Lau** was my professor of *Language Theory* at
   `USB <http://www.usb.ve/>`__, and he was kind enough to be my tutor
   in a thesis project on programming languages that was more than I
   could chew. My peers, and then teaching advisers **Alberto Torres**,
   and **Enzo Chiariotti** formed a team with **Gustavo** to challenge
   us with programming languages like *LATORTA* and term exams that went
   well into the eight hours. And, of course, there was also the *pirate
   patch* that should be worn on the left or right eye depending on the
   *LL* or *LR* challenge.
-  **Manuel Rey** led me through another, unfinished, thesis project
   that taught me about what languages (spoken languages in general, and
   programming languages in particular) are about. I learned why
   languages use
   `declensions <http://en.wikipedia.org/wiki/Declension>`__, and why,
   although the underlying words are in
   `English <http://en.wikipedia.org/wiki/English_grammar>`__, the
   structure of the programs we write is more like
   `Japanese <http://en.wikipedia.org/wiki/Japanese_grammar>`__.
-  `Marcus Brinkmann <http://blog.marcus-brinkmann.de/>`__ has kindly
   submitted patches that have resolved obscure bugs in **Grako**'s
   implementation, and that have made the tool more user-friendly,
   specially for newcomers to parsing and translation.
-  `Robert Speer <https://bitbucket.org/r_speer>`__ cleaned up the
   nonsense in trying to have Unicode handling be compatible with 2.7.x
   and 3.x, and figured out the canonical way of honoring escape
   sequences in grammar tokens without throwing off the encoding.
-  `Basel Shishani <https://bitbucket.org/basel-shishani>`__ has been an
   incredibly throrough peer-reviewer of **Grako**.
-  `Paul Sargent <https://bitbucket.org/PaulS/>`__ implemented `Warth et
   al <http://www.vpri.org/pdf/tr2007002_packrat.pdf>`__'s algorithm for
   supporting direct and indirect left recursion in
   `PEG <http://en.wikipedia.org/wiki/Parsing_expression_grammar>`__
   parsers.
-  `Kathryn Long <https://bitbucket.org/starkat>`__ proposed better
   support for UNICODE in the treatment of whitespace and regular
   expressions (patterns) in general. Her other contributions have made
   **Grako** more congruent, and more user-friendly.
-  `David Röthlisberger <https://bitbucket.org/drothlis/>`__ provided
   the definitive patch that allows the use of
   `Python <http://python.org>`__ keywords as rule names.

Contributors
------------

The following, among others, have contributted to **Grako** with
features, bug fixes, or suggestions:
`franz\_g <https://bitbucket.org/Franz_G>`__,
`marcus <http://blog.marcus-brinkmann.de/>`__,
`pauls <https://bitbucket.org/PaulS/>`__,
`basel-shishani <https://bitbucket.org/basel-shishani>`__,
`drothlis <https://bitbucket.org/drothlis/>`__,
`gapag <https://bitbucket.org/gapag/>`__,
`gkimbar <https://bitbucket.org/gkimbar/>`__,
`jimon <https://bitbucket.org/jimon/>`__,
`lambdafu <http://blog.marcus-brinkmann.de/>`__,
`linkdd <https://bitbucket.org/linkdd/>`__,
`nehz <https://bitbucket.org/nehz/grako>`__,
`neumond <https://bitbucket.org/neumond/>`__,
`pgebhard <https://github.com/pgebhard?tab=repositories>`__,
`r\_speer <https://bitbucket.org/r_speer>`__,
`siemer <https://bitbucket.org/siemer/>`__,
`starkat <https://bitbucket.org/starkat>`__,
`vmuriart <https://bitbucket.org/vmuriart/>`__,
`gegenschall <https://bitbucket.org/gegenschall/>`__,
`tonico\_strasser <https://bitbucket.org/tonico_strasser/>`__,
`vinay.sajip <https://bitbucket.org/vinay.sajip/>`__,
`sjbrownBitbucket <https://bitbucket.org/sjbrownBitbucket/>`__.

Changes
-------

See the
`CHANGELOG <https://bitbucket.org/apalala/grako/src/default/CHANGELOG.md>`__
for details.

.. |fury| image:: https://badge.fury.io/py/grako.svg
   :target: https://badge.fury.io/py/grako
.. |license| image:: https://img.shields.io/badge/license-BSD-blue.svg
   :target: https://raw.githubusercontent.com/apalala/grako/master/LICENSE.txt
.. |pyversions| image:: https://img.shields.io/pypi/pyversions/grako.svg
   :target: https://pypi.python.org/pypi/grako
.. |travis| image:: https://secure.travis-ci.org/apalala/grako.svg
   :target: http://travis-ci.org/apalala/grako
.. |landscape| image:: https://landscape.io/github/apalala/grako/release/landscape.png
   :target: https://landscape.io/github/apalala/grako/release
.. |donate| image:: https://www.paypalobjects.com/en_US/i/btn/btn_donate_SM.gif
   :target: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=P9PV7ZACB669J
