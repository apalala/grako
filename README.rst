.. image:: https://badge.fury.io/py/grako.svg
    :target: https://badge.fury.io/py/grako

.. image:: https://img.shields.io/badge/license-BSD-blue.svg
    :target: https://raw.githubusercontent.com/apalala/grako/master/LICENSE.txt

.. image:: https://img.shields.io/pypi/pyversions/grako.svg
    :target: https://pypi.python.org/pypi/grako

.. image:: https://secure.travis-ci.org/apalala/grako.svg
    :target: http://travis-ci.org/apalala/grako

.. image:: https://landscape.io/github/apalala/grako/release/landscape.png
   :target: https://landscape.io/github/apalala/grako/release

----

*At least for the people who send me mail about a new language that they're designing, the general advice is: do it to learn about how to write a compiler. Don't have any expectations that anyone will use it, unless you hook up with some sort of organization in a position to push it hard. It's a lottery, and some can buy a lot of the tickets. There are plenty of beautiful languages (more beautiful than C) that didn't catch on. But someone does win the lottery, and doing a language at least teaches you something.*
     `Dennis Ritchie`_ (1941-2011)
         Creator of the C_ programming language and of Unix_

.. _Dennis Ritchie: http://en.wikipedia.org/wiki/Dennis_Ritchie
.. _C: http://en.wikipedia.org/wiki/C_language
.. _Unix: http://en.wikipedia.org/wiki/Unix

----

=====
Grako
=====

**Grako** (for *grammar compiler*) is a tool that takes grammars in a variation of EBNF_ as input, and outputs memoizing_ (Packrat_) PEG_ parsers in Python_.

**Grako** is *different* from other PEG_ parser generators:

* Generated parsers use Python_'s very efficient exception-handling system to backtrack. **Grako** generated parsers simply assert what must be parsed. There are no complicated *if-then-else* sequences for decision making or backtracking. Memoization allows going over the same input sequence several times in linear time.

* *Positive and negative lookaheads*, and the *cut* element (with its cleaning of the memoization cache) allow for additional, hand-crafted optimizations at the grammar level.

* Delegation to Python_'s re_ module for *lexemes* allows for (Perl_-like) powerful and efficient lexical analysis.

* The use of Python_'s `context managers`_ considerably reduces the size of the generated parsers for code clarity, and enhanced CPU-cache hits.

* Include files, rule inheritance, and rule inclusion give **Grako** grammars considerable expressive power.

* Experimental support for direct and indirect left recursion allows for more intuitive grammars.

The parser generator, the run-time support, and the generated parsers have measurably low `Cyclomatic complexity`_.  At around 5 KLOC_ of Python_, it is possible to study all its source code in a single session.

The only dependencies are on the Python_ or PyPy_ standard libraries (the proposed regex_ module will be used if installed, colorama_ will be used on trace output if available, and pygraphviz_ is required for generating diagrams). For performance beyond what which Python_ or PyPy_ can provide, take a look at the `Grako++`_ project.

**Grako** is feature-complete and currently being used with complex grammars to parse and translate hundreds of thousands of lines of complex text, including program source files and other structured input.

.. _`Cyclomatic complexity`: http://en.wikipedia.org/wiki/Cyclomatic_complexity
.. _KLOC: http://en.wikipedia.org/wiki/KLOC
.. _legacy: http://en.wikipedia.org/wiki/Legacy_code
.. _`legacy code`: http://en.wikipedia.org/wiki/Legacy_code
.. _PyPy: http://pypy.org/
.. _`context managers`: http://docs.python.org/2/library/contextlib.html
.. _Perl: http://www.perl.org/
.. _NATURAL: http://en.wikipedia.org/wiki/NATURAL
.. _COBOL: http://en.wikipedia.org/wiki/Cobol
.. _Java:  http://en.wikipedia.org/wiki/Java_(programming_language)
.. _VB6: http://en.wikipedia.org/wiki/Visual_basic_6
.. _regex: https://pypi.python.org/pypi/regex
.. _re: https://docs.python.org/3.4/library/re.html
.. _pygraphviz: https://pypi.python.org/pypi/pygraphviz
.. _colorama: https://pypi.python.org/pypi/colorama/

Table of Contents
=================
.. contents:: \


Rationale
=========

**Grako** was created to address recurring problems encountered over decades of working with parser generation tools:

* Many languages allow the use of certain *keywords* as identifiers, or have different meanings for symbols depending on context (Ruby_). A parser needs to be able to control the lexical analysis to handle those languages.


* LL and LR grammars become contaminated with myriads of lookahead statements to deal with ambiguous constructs in the source language. PEG_ parsers address ambiguity from the onset.

* Separating the grammar from the code that implements the semantics, and using a variation of a well-known grammar syntax (EBNF_ in this case), allows for full declarative power in language descriptions. General-purpose programming languages are not up to the task.

* Semantic actions *do not*  belong in a grammar. They create yet another programming language to deal with when doing parsing and translation: the source language, the grammar language, the semantics language, the generated parser's language, and the translation's target language. Most grammar parsers do not check that the embedded semantic actions have correct syntax, so errors get reported at awkward moments, and against the generated code, not against the source.

* Preprocessing (like dealing with includes, fixed column formats, or structure-through-indentation) belongs in well-designed program code; not in the grammar.

* It is easy to recruit help with knowledge about a mainstream programming language (Python_ in this case), but it's hard for grammar-description languages. **Grako** grammars are in the spirit of a *Translators and Interpreters 101* course (if something is hard to explain to a college student, it's probably too complicated, or not well understood).

* Generated parsers should be easy to read and debug by humans. Looking at the generated source code is sometimes the only way to find problems in a grammar, the semantic actions, or in the parser generator itself. It's inconvenient to trust generated code that you cannot understand.

* Python_ is a great language for working with language parsing and translation.

.. _`Abstract Syntax Tree`: http://en.wikipedia.org/wiki/Abstract_syntax_tree
.. _AST: http://en.wikipedia.org/wiki/Abstract_syntax_tree
.. _ASTs: http://en.wikipedia.org/wiki/Abstract_syntax_tree
.. _CST:  http://en.wikipedia.org/wiki/Concrete_syntax_tree
.. _EBNF: http://en.wikipedia.org/wiki/Ebnf
.. _memoizing: http://en.wikipedia.org/wiki/Memoization
.. _PEG: http://en.wikipedia.org/wiki/Parsing_expression_grammar
.. _Packrat: http://bford.info/packrat/
.. _Python: http://python.org
.. _Ruby: http://www.ruby-lang.org/


The Generated Parsers
=====================

A **Grako** generated parser consists of the following classes:

* A *parser* class derived from ``Parser`` which implements the parser using one method for each grammar rule::

    def _myrulename_(self):

* A *semantics delegate class* with one semantic method per grammar rule. Each method receives as its single parameter the `Abstract Syntax Tree`_ (AST_) built from the rule invocation::

    def myrulename(self, ast):
        return ast

The methods in the delegate class return the same AST_ received as parameter, but custom semantic classes can override the methods to have them return anything (for example, a `Semantic Graph`_). The semantics class can be used as a template for the final semantics implementation, which can omit methods for the rules it is not interested in.

If present, a ``_default()`` method will be called in the semantics class when no method matched the rule name::

    def _default(self, ast):
        ...
        return ast

If present, a ``_postproc()`` method will be called in the semantics class after each rule (including the semantics) is processed. This method will receive the current parsing context as parameter::

    def _postproc(self, context, ast):
        ...

.. _`Semantic Graph`: http://en.wikipedia.org/wiki/Abstract_semantic_graph


Using the Tool
==============

**Grako** can be run from the command line::

    $ python -m grako

Or::

    $ scripts/grako

Or just::

    $ grako

if **Grako** was installed using *easy_install* or *pip*.

The *-h* and *--help* parameters provide full usage information::

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
==========================

To use the generated parser, just subclass the base or the abstract parser, create an instance of it, and invoke its ``parse()`` method passing the grammar to parse and the starting rule's name as parameter::

    parser = MyParser()
    ast = parser.parse('text to parse', rule_name='start')
    print(ast)
    print(json.dumps(ast, indent=2)) # ASTs are JSON-friendy

This is more or less what happens if you invoke the generated parser directly::

    python myparser.py inputfile startrule

The generated parsers' constructors accept named arguments to specify whitespace characters, the regular expression for comments, case sensitivity, verbosity, and more (see below).

To add semantic actions, just pass a semantic delegate to the parse method::

    model = parser.parse(text, rule_name='start', semantics=MySemantics())

If special lexical treatment is required (like in Python_'s structure-through-indentation), then a descendant of ``grako.buffering.Buffer`` can be passed instead of the text::

    class MySpecialBuffer(grako.buffering.Buffer):
        ...

    buf = MySpecialBuffer(text)
    model = parser.parse(buf, rule_name='start', semantics=MySemantics())



The EBNF Grammar Syntax
=======================

**Grako** uses a variant of the standard EBNF_ syntax. Syntax definitions for VIM_ can be found under the ``etc/vim`` directory in the source code distribution.

.. _VIM: http://www.vim.org/

Rules
-----

A grammar consists of a sequence of one or more rules of the form::

    name = <expre> ;

If a *name* collides with a Python_ keyword, an underscore (``_``) will be appended to it on the generated parser.

Rule names that start with an uppercase character::

   FRAGMENT = /[a-z]+/ ;

*do not* advance over whitespace before beginning to parse. This feature becomes handy when defining complex lexical elements, as it allows breaking them into several rules.

Expressions
-----------

The expressions, in reverse order of operator precedence, can be:

    ``e1 | e2``
        Match either ``e1`` or ``e2``.

    ``e1 e2``
        Match ``e1`` and then match ``e2``.

    ``( e )``
        Grouping. Match ``e``. For example: ``('a' | 'b')``.

    ``[ e ]``
        Optionally match ``e``.

    ``{ e }`` or ``{ e }*``
        Closure. Match ``e`` zero or more times. Note that the AST_ returned for a closure is always a list.

    ``{ e }+``
        Positive closure. Match ``e`` one or more times. The AST_ is always a list.

    ``{}``
        Empty closure. Match nothing and produce an empty list as AST_.

    ``s.{ e }+``
        Positive join. Inspired by Python_'s ``str.join()``, is equivalent to::

           e {s ~ e}

        The ``s`` part is not included in the resulting AST_.

        Use grouping if ``s`` is more complex than a *token* or a *pattern*::

            (s t).{ e }+

    ``s.{ e }`` or ``s.{ e }*``
        Join. Parses the list of ``s``-separated expressions, or nothing.

        It is equivalent to::

            ( s.{e}+|{} )

    ``&e``
        Positive lookahead. Try parsing ``e``, but do not consume any input.

    ``!e``
        Negative lookahead. Try parsing ``e`` and fail if there's a match. Do not consume any input whichever the outcome.

    ``>rulename``
        The include operator. Include the *right hand side* of rule ``rulename`` at this point.

        The following set of declarations::

            includable = exp1 ;

            expanded = exp0 >includable exp2 ;

        Has the same effect as defining *expanded* as::

            expanded = exp0 exp1 exp2 ;

        Note that the included rule must be defined before the rule that includes it.

    ``'text'`` or ``"text"``
        Match the token *text* within the quotation marks.

        Note that if *text* is alphanumeric, then **Grako** will check that the character following the token is not alphanumeric. This is done to prevent tokens like *IN* matching when the text ahead is *INITIALIZE*. This feature can be turned off by passing ``nameguard=False`` to the ``Parser`` or the ``Buffer``, or by using a pattern expression (see below) instead of a token expression.
        Alternatively, the ``@@nameguard``  or ``@@namechars`` directives may be specified in the grammar::

            @@nameguard :: False

        or to specify additional characters that should also be considered part of names::

            @@namechars :: '$-.'

    ``/regexp/``
        The pattern expression. Match the Python_ regular expression ``regexp`` at the current text position. Unlike other expressions, this one does not advance over whitespace or comments. For that, place the ``regexp`` as the only term in its own rule.

        The ``regexp`` is passed *as-is* to the Python_ re_ module (or regex_ if available), using ``match()`` at the current position in the text. The matched text is the AST_ for the expression.

    ``?/regexp/?``
        Another form of the pattern expression that can be used when there are slashes (``/``) in the pattern.

    ``+/regexp/``
        Concatenate the given pattern with the preceding one.

    ```constant```
        Match nothing, but behave as if ``constant`` had been parsed.

        Constants can be used to inject elements into the concrete and abstract syntax trees, perhaps avoiding having to write a semantic action. For example::

            boolean_option = name ['=' (boolean|`true`) ] ;

    ``rulename``
        Invoke the rule named ``rulename``. To help with lexical aspects of grammars, rules with names that begin with an uppercase letter will not advance the input over whitespace or comments.

    ``()``
        The empty expression. Succeed without advancing over input. Its value is ``None``.


    ``!()``
        The *fail* expression. This is actually ``!`` applied to ``()``, which always fails.

    ``~``
        The *cut* expression. After this point, prevent other options from being considered even if the current option fails to parse.

    ``name:e``
        Add the result of ``e`` to the AST_ using ``name`` as key. If ``name`` collides with any attribute or method of ``dict``, or is a Python_ keyword, an underscore (``_``) will be appended to the name.

    ``name+:e``
        Add the result of ``e`` to the AST_ using ``name`` as key. Force the entry to be a list even if only one element is added. Collisions with ``dict`` attributes or Python_ keywords are resolved by appending an underscore to ``name``.

    ``@:e``
        The override operator. Make the AST_ for the complete rule be the AST_ for ``e``.

        The override operator is useful to recover only part of the right hand side of a rule without the need to name it, or add a semantic action.

        This is a typical use of the override operator::

            subexp = '(' @:expre ')' ;

        The AST_ returned for the ``subexp`` rule will be the AST_ recovered from invoking ``expre``.

    ``@+:e``
        Like ``@:e``, but make the AST_ always be a list.

        This operator is convenient in cases such as::

            arglist = '(' @+:arg {',' @+:arg}* ')' ;

        In which the delimiting tokens are of no interest.

    ``$``
        The *end of text* symbol. Verify that the end of the input text has been reached.

    ``(*`` *comment* ``*)``
        Comments may appear anywhere in the text.

    ``#`` *comment*
        Python_-style comments are also allowed.

When there are no named items in a rule, the AST_ consists of the elements parsed by the rule, either a single item or a list. This default behavior makes it easier to write simple rules::

    number = /[0-9]+/ ;

Without having to write::

    number = number:/[0-9]+/ ;

When a rule has named elements, the unnamed ones are excluded from the AST_ (they are ignored).


Rules with Arguments
--------------------

**Grako** allows rules to specify Python_-style arguments::

    addition(Add, op='+')
        =
        addend '+' addend
        ;

The arguments values are fixed at grammar-compilation time.

An alternative syntax is available if no *keyword parameters* are required::

    addition::Add, '+'
        =
        addend '+' addend
        ;

Semantic methods must be ready to receive any arguments declared in the corresponding rule::

    def addition(self, ast, name, op=None):
        ...

When working with rule arguments, it is good to define a ``_default()`` method that is ready to take any combination of standard and keyword arguments::

    def _default(self, ast, *args, **kwargs):
        ...


Based Rules
-----------

Rules may extend previously defined rules using the ``<`` operator.  The *base rule* must be defined previously in the grammar.

The following set of declarations::

    base::Param = exp1 ;

    extended < base = exp2 ;

Has the same effect as defining *extended* as::

    extended::Param = exp1 exp2 ;


Parameters from the *base rule* are copied to the new rule if the new rule doesn't define its own.  Repeated inheritance should be possible, but it *hasn't been tested*.


Rule Overrides
--------------

A grammar rule may be redefined by using the
``@override`` decorator::

    start = ab $;

    ab = 'xyz' ;

    @override
    ab = @:'a' {@:'b'} ;

When combined with the ``#include`` directive, rule overrides can be used to create a modified grammar without altering the original.


Abstract Syntax Trees (ASTs)
============================

By default, and AST_ is either a *list* (for *closures* and rules without named elements), or *dict*-derived object that contains one item for every named element in the grammar rule. Items can be accessed through the standard ``dict`` syntax (``ast['key']``), or as attributes (``ast.key``).

AST_ entries are single values if only one item was associated with a name, or lists if more than one item was matched. There's a provision in the grammar syntax (the ``+:`` operator) to force an AST_ entry to be a list even if only one element was matched. The value for named elements that were not found during the parse (perhaps because they are optional) is ``None``.

When the ``parseinfo=True`` keyword argument has been passed to the ``Parser`` constructor, a ``parseinfo`` element is added to AST_ nodes that are *dict*-like. The element contains a ``collections.namedtuple`` with the parse information for the node::

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

With the help of the ``Buffer.line_info()`` method, it is possible to recover the line, column, and original text parsed for the node. Note that when ``ParseInfo`` is generated, the ``Buffer`` used during parsing is kept in memory for the lifetime of the AST_.

Generation of ``parseinfo`` can also be controlled using the ``@@parseinfo :: True`` grammar directive.


Grammar Name
============

The prefix to be used in classes generated by **Grako** can be passed to the command-line tool using the ``-m`` option::

    grako -m My mygrammar.ebnf

will generate::

    class MyParser(Parser):

The name can also be specified within the grammar using the ``@@grammar`` directive::

    @@grammar :: My


Whitespace
==========

By default, **Grako** generated parsers skip the usual whitespace characters with the regular expression ``r'\s+'`` using the ``re.UNICODE`` flag (or with the ``Pattern_White_Space`` property if the regex_ module is available), but you can change that behavior by passing a ``whitespace`` parameter to your parser.

For example, the following will skip over *tab* (``\t``) and *space* characters, but not so with other typical whitespace characters such as *newline* (``\n``)::

    parser = MyParser(text, whitespace='\t ')

The character string is converted into a regular expression character set before starting to parse.

You can also provide a regular expression directly instead of a string. The following is equivalent to the above example::

    parser = MyParser(text, whitespace=re.compile(r'[\t ]+'))

Note that the regular expression must be pre-compiled to let **Grako** distinguish it from plain string.

If you do not define any whitespace characters, then you will have to handle whitespace in your grammar rules (as it's often done in PEG_ parsers)::

    parser = MyParser(text, whitespace='')

Whitespace may also be specified within the grammar using the ``@@whitespace`` directive, although any of the above methods will overwrite the grammar directive::

    @@whitespace :: /[\t ]+/


Case Sensitivity
================

If the source language is case insensitive, you can tell your parser by using the ``ignorecase`` parameter::

    parser = MyParser(text, ignorecase=True)

You may also specify case insensitivity within the grammar using the ``@@ignorecase`` directive::

    @@ignorecase :: True

The change will affect both token and pattern matching.


Comments
========

Parsers will skip over comments specified as a regular expression using the ``comments_re`` parameter::

    parser = MyParser(text, comments_re="\(\*.*?\*\)")

For more complex comment handling, you can override the ``Buffer.eat_comments()`` method.

For flexibility, it is possible to specify a pattern for end-of-line comments separately::

    parser = MyParser(
        text,
        comments_re="\(\*.*?\*\)",
        eol_comments_re="#.*?$"
    )

Both patterns may also be specified within a grammar using the ``@@comments`` and
``@@eol_comments`` directives::

        @@comments :: /\(\*.*?\*\)/
        @@eol_comments :: /#.*?$/


Reserved Words and Keywords
===========================

Some languages must reserve the use of certain tokens as valid identifiers because the tokens are used to mark particular constructs in the language. Those reserved tokens are known as `Reserved Words`_ or `Keywords`_

.. _`keyword`: https://en.wikipedia.org/wiki/Reserved_word
.. _`keywords`: https://en.wikipedia.org/wiki/Reserved_word
.. _`Keywords`: https://en.wikipedia.org/wiki/Reserved_word
.. _`Reserved Words`: https://en.wikipedia.org/wiki/Reserved_word

**Grako** provides support for preventing the use of keywords_ as identifiers though the ``@@ keyword`` directive,and the ``@ name`` decorator.

A grammar may specify reserved tokens providing a list of them in one or more ``@@ keyword`` directives::

    @@keyword :: if endif
    @@keyword :: else elseif

The ``@ name`` decorator checks that the result of a grammar rule does not match a token defined as a keyword_::

    @name
    identifier = /(?!\d)\w+/ ;

There are situations in which a token is reserved only in a very specific context. In those cases, a negative lookahead will prevent the use of the token::

    statements = {!'END' statement}+ ;


Semantic Actions
================

There are no constructs for semantic actions in **Grako** grammars. This is on purpose, because semantic actions obscure the declarative nature of grammars and provide for poor modularization from the parser-execution perspective.

Semantic actions are defined in a class, and applied by passing an object of the class to the ``parse()`` method of the parser as the ``semantics=`` parameter. **Grako** will invoke the method that matches the name of the grammar rule every time the rule parses. The argument to the method will be the AST_ constructed from the right-hand-side of the rule::

    class MySemantics(object):
        def some_rule_name(self, ast):
            return ''.join(ast)

        def _default(self, ast):
            pass

If there's no method matching the rule's name, **Grako** will try to invoke a ``_default()`` method if it's defined::

    def _default(self, ast):

Nothing will happen if neither the per-rule method nor ``_default()`` are defined.

The per-rule methods in classes implementing the semantics provide enough opportunity to do rule post-processing operations, like verifications (for inadequate use of keywords as identifiers), or AST_ transformation::

    class MyLanguageSemantics(object):
        def identifier(self, ast):
            if my_lange_module.is_keyword(ast):
                raise FailedSemantics('"%s" is a keyword' % str(ast))
            return ast

For finer-grained control it is enough to declare more rules, as the impact on the parsing times will be minimal.

If preprocessing is required at some point, it is enough to place invocations of empty rules where appropriate::

    myrule = first_part preproc {second_part} ;

    preproc = () ;

The abstract parser will honor as a semantic action a method declared as::

    def preproc(self, ast):

Include Directive
=================

**Grako** grammars support file inclusion through the include directive::

    #include :: "filename"

The resolution of the *filename* is relative to the directory/folder of the source. Absolute paths and ``../`` navigations are honored.

The functionality required for implementing includes is available to all **Grako**-generated parsers through the ``Buffer`` class; see the ``GrakoBuffer`` class in the ``grako.parser`` module for an example.


Building Models
===============

Naming elements in grammar rules makes the parser discard uninteresting parts of the input, like punctuation, to produce an *Abstract Syntax Tree* (AST_) that reflects the semantic structure of what was parsed. But an AST_ doesn't carry information about the rule that generated it, so navigating the trees may be difficult.

**Grako** defines the ``grako.model.ModelBuilderSemantics`` semantics class which helps
construct object models from abtract syntax trees::

   from grako.model import ModelBuilderSemantics

   parser = MyParser(semantics=ModelBuilderSemantics())

Then you add the desired node type as first parameter to each grammar rule::

    addition::AddOperator = left:mulexpre '+' right:addition ;

``ModelBuilderSemantics`` will synthesize an ``AddOperator(Node)`` class and use it to construct the node. The synthesized class will have one attribute with the same name as the named elements in the rule.

You can also use Python_'s built-in types as node types, and ``ModelBuilderSemantics`` will do the right thing::

    integer::int = /[0-9]+/ ;

``ModelBuilderSemantics`` acts as any other semantics class, so its default behavior can be overidden by defining a method to handle the result of any particular grammar rule.


Traversing Models
-----------------

The class ``grako.model.NodeWalker`` allows for the easy traversal (*walk*) a model constructed with a ``ModelBuilderSemantics`` instance::

    from grako.model import NodeWalker

    class MyNodeWalker(NodeWalker):

        def walk_AddOperator(self, node):
            left = self.walk(node.left)
            right = self.walk(node.right)

            print('ADDED', left, right)

    model = MyParser(semantics=ModelBuilderSemantics()).parse(input)

    walker = MyNodeWalker()
    walker.walk(model)

When a method with a name like ``walk_NodeClassName`` is defined, it will be called when a node of that type is *walked*.

Predeclared classes can be passed to ``ModelBuilderSemantics`` instances through the ``types=`` parameter::

    from mymodel import AddOperator, MulOperator

    semantics=ModelBuilderSemantics(types=[AddOperator, MulOperator])


``ModelBuilderSemantics`` assumes nothing about ``types=``, so any constructor (a function, or a partial function) can be used.


Model Class Hierarchies
-----------------------

It is possible to specify a a base class for generated model nodes::

    addition::AddOperator::Operator = left:mulexpre op:'+' right:addition ;
    substraction::SubstractOperator::Operator = left:mulexpre op:'-' right:addition ;

**Grako** will generate the base class if it's not already known.

Base classes can be used as the target class in *walkers*, and in *code generators*::

    class MyNodeWalker(NodeWalker):
        def walk_Operator(self, node):
            left = self.walk(node.left)
            right = self.walk(node.right)
            op = self.walk(node.op)

            print(type(node).__name__, op, left, right)


    class Operator(ModelRenderer):
        template = '{left} {op} {right}'


Templates and Translation
=========================

.. note::
    As of **Grako** 3.2.0, code generation is separated from grammar models through ``grako.codegen.CodeGenerator`` as to allow for code generation targets different from Python_. Still, the use of inline templates and ``rendering.Renderer`` hasn't changed. See the *regex* example for merged modeling and code generation.

**Grako** doesn't impose a way to create translators with it, but it exposes the facilities it uses to generate the Python_ source code for parsers.

Translation in **Grako** is *template-based*, but instead of defining or using a complex templating engine (yet another language), it relies on the simple but powerful ``string.Formatter`` of the Python_ standard library. The templates are simple strings that, in **Grako**'s style, are inlined with the code.

To generate a parser, **Grako** constructs an object model of the parsed grammar. A
``grako.codegen.CodeGenerator`` instance matches model objects to classes that descend from ``grako.codegen.ModelRenderer`` and implement the translation and rendering using string templates. Templates are left-trimmed on whitespace, like Python_ *doc-comments* are. This is an example taken from **Grako**'s source code::

    class Lookahead(ModelRenderer):
        template = '''\
                    with self._if():
                    {exp:1::}\
                    '''

Every *attribute* of the object that doesn't start with an underscore (``_``) may be used as a template field, and fields can be added or modified by overriding the ``render_fields(fields)`` method.  Fields themselves are *lazily rendered* before being expanded by the template, so a field may be an instance of a ``ModelRenderer`` descendant.

The ``rendering`` module defines a ``Formatter`` enhanced to support the rendering of items in an *iterable* one by one. The syntax to achieve that is::

    {fieldname:ind:sep:fmt}

All of ``ind``, ``sep``, and ``fmt`` are optional, but the three *colons* are not. A field specified that way will be rendered using::

     indent(sep.join(fmt % render(v) for v in value), ind)

The extended format can also be used with non-iterables, in which case the rendering will be::

     indent(fmt % render(value), ind)

The default multiplier for ``ind`` is ``4``, but that can be overridden using ``n*m`` (for example ``3*1``) in the format.

**Note**
    Using a newline (``\\n``) as separator will interfere with left trimming and indentation of templates. To use newline as separator, specify it as ``\\n``, and the renderer will understand the intention.


Left Recursion
==============

**Grako** provides experimental support for left recursion in PEG_ grammars. The implementation of left recursion is ongoing; it does not yet handle all cases.

Sometimes, while debugging a grammar, it is useful to turn left-recursion support on or off::

    parser = MyParser(
        text,
        left_recursion=False,
    )

Left recursion can also be turned off from within the grammar using the ``@@left_recursion`` directive::

        @@left_recursion :: False


Examples
========

Grako
-----

The file ``etc/grako.ebnf`` contains a grammar for the **Grako** EBNF_ language written in the same **Grako** grammar language. It is used in the *bootstrap* test suite to prove that **Grako** can generate a parser to parse its own language, and the resulting parser is made the bootstrap parser every time **Grako** is stable (see ``grako/bootstrap.py`` for the generated parser). **Grako** uses **Grako** to translate grammars into parsers, so it is a good example of end-to-end translation.

Regex
-----

The project ``examples/regexp`` contains a regexp-to-EBNF translator and parser generator. The project has no practical use, but it's a complete, end-to-end example of how to implement a translator using **Grako**.

antlr2grako
-----------

The project ``examples/antlr2grako`` contains a ANTLR_ to **Grako** grammar translator.  The project is a good example of the use of models and templates in translation. The program, ``antlr2grako.py`` generates the **Grako** grammar on standard output, but because the model used is **Grako**'s own, the same code can be used to directly generate a parser from an ANTLR_ grammar. Please take a look at the examples *README* to know about limitations.

Other Open-source Examples
==========================

* **Christian Ledermann** wrote  parsewkt_ a parser for `Well-known text`_ (WTK_) using **Grako**.

* **Marcus Brinkmann** (lambdafu_) wrote smc.mw_, a parser for a MediaWiki_-style language.

* **Marcus Brinkmann** (lambdafu_) is working on a *C++ code generator* for **Grako** called `Grako++`_. Help in the form of testing, test cases, and pull requests is welcome.

.. _parsewkt: https://github.com/cleder/parsewkt
.. _`Well-known text`: http://en.wikipedia.org/wiki/Well-known_text
.. _WTK: http://en.wikipedia.org/wiki/Well-known_text
.. _smc.mw: https://github.com/lambdafu/smc.mw
.. _MediaWiki: http://www.mediawiki.org/wiki/MediaWiki
.. _`Grako++`: https://github.com/lambdafu/grakopp/


License
=======

**Grako** is Copyright (C) 2012-2016 by `Thomas Bragg`_ and  `Juancarlo Añez`_

.. _`Juancarlo Añez`: mailto:apalala@gmail.com
.. _`Thomas Bragg`: mailto:tbragg95@gmail.com

You may use the tool under the terms of the BSD_-style license described in the enclosed **LICENSE.txt** file. *If your project requires different licensing* please email_.

.. _BSD: http://en.wikipedia.org/wiki/BSD_licenses#2-clause_license_.28.22Simplified_BSD_License.22_or_.22FreeBSD_License.22.29
.. _email: mailto:apalala@gmail.com


Contact and Updates
===================

For general Q&A, please use the ``[grako]`` tag on StackOverflow_.

To discuss **Grako** and to receive notifications about new releases, please join the low-volume `Grako Forum`_ at *Google Groups*.

You can also follow the latest **Grako** developments with `@GrakoPEG`_ on Twitter_.

.. _StackOverflow: http://stackoverflow.com/tags/grako/info
.. _`Grako Forum`:  https://groups.google.com/forum/?fromgroups#!forum/grako
.. _`@GrakoPEG`: https://twitter.com/GrakoPEG
.. _Twitter: https://twitter.com/GrakoPEG


Credits
=======

The following must be mentioned as contributors of thoughts, ideas, code, *and funding* to the **Grako** project:

* **Niklaus Wirth** was the chief designer of the programming languages Euler_, `Algol W`_, Pascal_, Modula_, Modula-2_, Oberon_, and Oberon-2_. In the last chapter of his 1976 book `Algorithms + Data Structures = Programs`_, Wirth_ creates a top-down, descent parser with recovery for the Pascal_-like, `LL(1)`_ programming language `PL/0`_. The structure of the program is that of a PEG_ parser, though the concept of PEG_ wasn't formalized until 2004.

* **Bryan Ford** introduced_ PEG_ (parsing expression grammars) in 2004.

* Other parser generators like `PEG.js`_ by **David Majda** inspired the work in **Grako**.

* **William Thompson** inspired the use of context managers with his `blog post`_ that I knew about through the invaluable `Python Weekly`_ newsletter, curated by **Rahul Chaudhary**

* **Jeff Knupp** explains why **Grako**'s use of exceptions_ is sound, so I don't have to.

* **Terence Parr** created ANTLR_, probably the most solid and professional parser generator out there. *Ter*, *ANTLR*, and the folks on the *ANLTR* forums helped me shape my ideas about **Grako**.

* **JavaCC** (originally Jack_) looks like an abandoned project. It was the first parser generator I used while teaching.

* **Grako** is very fast. But dealing with millions of lines of legacy source code in a matter of minutes would be impossible without PyPy_, the work of **Armin Rigo** and the `PyPy team`_.

* **Guido van Rossum** created and has lead the development of the Python_ programming environment for over a decade. A tool like **Grako**, at under six thousand lines of code, would not have been possible without Python_.

* **Kota Mizushima** welcomed me to the `CSAIL at MIT`_ `PEG and Packrat parsing mailing list`_, and immediately offered ideas and pointed me to documentation about the implementation of *cut* in modern parsers. The optimization of memoization information in **Grako** is thanks to one of his papers.

* **My students** at UCAB_ inspired me to think about how grammar-based parser generation could be made more approachable.

* **Gustavo Lau** was my professor of *Language Theory* at USB_, and he was kind enough to be my tutor in a thesis project on programming languages that was more than I could chew. My peers, and then teaching advisers **Alberto Torres**, and **Enzo Chiariotti** formed a team with **Gustavo** to challenge us with programming languages like *LATORTA* and term exams that went well into the eight hours. And, of course, there was also the *pirate patch* that should be worn on the left or right eye depending on the *LL* or *LR* challenge.

* **Manuel Rey** led me through another, unfinished, thesis project that taught me about what languages (spoken languages in general, and programming languages in particular) are about. I learned why languages use declensions_, and why, although the underlying words are in English_, the structure of the programs we write is more like Japanese_.

* `Marcus Brinkmann`_ has kindly submitted patches that have resolved obscure bugs in **Grako**'s implementation, and that have made the tool more user-friendly, specially for newcomers to parsing and translation.

* `Robert Speer`_ cleaned up the nonsense in trying to have Unicode handling be compatible with 2.7.x and 3.x, and figured out the canonical way of honoring escape sequences in grammar tokens without throwing off the encoding.

* `Basel Shishani`_ has been an incredibly throrough peer-reviewer of **Grako**.

* `Paul Sargent`_ implemented `Warth et al`_'s algorithm for supporting direct and indirect left recursion in PEG_ parsers.

* `Kathryn Long`_ proposed better support for UNICODE in the treatment of whitespace and regular expressions (patterns) in general. Her other contributions have made **Grako** more congruent, and more user-friendly.

* `David Röthlisberger`_ provided the definitive patch that allows the use of Python_ keywords as rule names.

.. _Wirth: http://en.wikipedia.org/wiki/Niklaus_Wirth
.. _Euler: http://en.wikipedia.org/wiki/Euler_programming_language
.. _`Algol W`: http://en.wikipedia.org/wiki/Algol_W
.. _Pascal: http://en.wikipedia.org/wiki/Pascal_programming_language
.. _Modula: http://en.wikipedia.org/wiki/Modula
.. _Modula-2: http://en.wikipedia.org/wiki/Modula-2
.. _Oberon: http://en.wikipedia.org/wiki/Oberon_(programming_language)
.. _Oberon-2: http://en.wikipedia.org/wiki/Oberon-2
.. _`PL/0`: http://en.wikipedia.org/wiki/PL/0
.. _`LL(1)`: http://en.wikipedia.org/wiki/LL(1)
.. _`Algorithms + Data Structures = Programs`: http://www.amazon.com/Algorithms-Structures-Prentice-Hall-Automatic-Computation/dp/0130224189/
.. _`blog post`: http://dietbuddha.blogspot.com/2012/12/52python-encapsulating-exceptions-with.html
.. _`Python Weekly`: http://www.pythonweekly.com/
.. _introduced: http://dl.acm.org/citation.cfm?id=964001.964011
.. _`PEG.js`: http://pegjs.majda.cz/
.. _UCAB: http://www.ucab.edu.ve/
.. _USB: http://www.usb.ve/
.. _ANTLR: http://www.antlr.org/
.. _Jack: http://en.wikipedia.org/wiki/Javacc
.. _exceptions: http://www.jeffknupp.com/blog/2013/02/06/write-cleaner-python-use-exceptions/
.. _`PyPy team`: http://pypy.org/people.html
.. _declensions: http://en.wikipedia.org/wiki/Declension
.. _English: http://en.wikipedia.org/wiki/English_grammar
.. _Japanese: http://en.wikipedia.org/wiki/Japanese_grammar
.. _`CSAIL at MIT`:  http://www.csail.mit.edu/
.. _`PEG and Packrat parsing mailing list`: https://lists.csail.mit.edu/mailman/listinfo/peg
.. _`Warth et al`: http://www.vpri.org/pdf/tr2007002_packrat.pdf
.. _`Marcus Brinkmann`: http://blog.marcus-brinkmann.de/
.. _Marcus: http://blog.marcus-brinkmann.de/
.. _lambdafu: http://blog.marcus-brinkmann.de/
.. _`Robert Speer`: https://bitbucket.org/r_speer
.. _r_speer: https://bitbucket.org/r_speer
.. _`Basel Shishani`: https://bitbucket.org/basel-shishani
.. _basel-shishani: https://bitbucket.org/basel-shishani
.. _`Paul Sargent`: https://bitbucket.org/PaulS/
.. _PaulS: https://bitbucket.org/PaulS/
.. _`Kathryn Long`: https://bitbucket.org/starkat
.. _starkat: https://bitbucket.org/starkat
.. _nehz: https://bitbucket.org/nehz/grako
.. _jimon: https://bitbucket.org/jimon/
.. _pgebhard: https://github.com/pgebhard?tab=repositories
.. _drothlis: https://bitbucket.org/drothlis/
.. _`David Röthlisberger`: https://bitbucket.org/drothlis/
.. _gkimbar: https://bitbucket.org/gkimbar/
.. _neumond: https://bitbucket.org/neumond/
.. _siemer: https://bitbucket.org/siemer/
.. _gapag: https://bitbucket.org/gapag/
.. _linkdd: https://bitbucket.org/linkdd/
.. _vmuriart: https://bitbucket.org/vmuriart/
.. _Franz_G: https://bitbucket.org/Franz_G
.. _gegenschall: https://bitbucket.org/gegenschall/


Contributors
------------

The following, among others, have contributted to **Grako** with features, bug fixes, or suggestions: franz_g_, marcus_, pauls_, basel-shishani_, drothlis_, gapag_, gkimbar_, jimon_, lambdafu_, linkdd_, nehz_, neumond_, pgebhard_, r_speer_, siemer_, starkat_, vmuriart_, gegenschall_.


Changes
=======


See the CHANGELOG_ for details.

.. _CHANGELOG: https://bitbucket.org/apalala/grako/src/default/CHANGELOG.md


.. Google Analytics Script
    <script>
    (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
    (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
    m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
    })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
    ga('create', 'UA-37745872-1', 'auto');
    ga('send', 'pageview');
    </script>
