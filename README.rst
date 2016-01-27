    *At least for the people who send me mail about a new language that they're designing, the general advice is: do it to learn about how to write a compiler. Don't have any expectations that anyone will use it, unless you hook up with some sort of organization in a position to push it hard. It's a lottery, and some can buy a lot of the tickets. There are plenty of beautiful languages (more beautiful than C) that didn't catch on. But someone does win the lottery, and doing a language at least teaches you something.*

    `Dennis Ritchie`_ (1941-2011)
    Creator of the C_ programming language and of Unix_

.. _Dennis Ritchie: http://en.wikipedia.org/wiki/Dennis_Ritchie
.. _C: http://en.wikipedia.org/wiki/C_language
.. _Unix: http://en.wikipedia.org/wiki/Unix


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

* Efficient support for direct and indirect left recursion allows for more intuitive grammars.

The parser-generator, the runtime support, and the generated parsers have measurably low `Cyclomatic complexity`_.  At around 4 KLOC_ of Python_, it is possible to study all its source code in a single session.

The only dependencies are on the Python_ 2.7, 3.4, or PyPy_ 2.3 standard libraries (the proposed regex_ module will be used if installed, colorama_ will be used on trace output if available, and pygraphviz_ is required for generating diagrams). For performance beyond what which Python_ or PyPy_ can provide, take a look at the `Grako++`_ project.

**Grako** is feature-complete and currently being used with complex grammars to parse and translate *hundreds of thousands* of lines of `legacy code`_ in programming languages like NATURAL_, COBOL_, VB6_, and Java_.

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
        usage: grako [-h] [-b] [-d] [-n] [-m NAME] [-o FILE] [-p] [-t] [-v] [-w CHARACTERS]
                    GRAMMAR

        GRAKO (for "grammar compiler") takes grammars in a variation of EBNF as input,
        and outputs a memoizing PEG/Packrat parser in Python.

        positional arguments:
        GRAMMAR               The filename of the Grako grammar

        optional arguments:
        -h, --help            show this help message and exit
        -b, --binary          generate a pickled grammar model (requires --output)
        -d, --draw            generate a diagram of the grammar (requires --output)
        -n, --no-nameguard    allow tokens that are prefixes of others
        -m NAME, --name NAME  Name for the grammar (defaults to GRAMMAR base name)
        -o FILE, --output FILE
                                output file (default is stdout)
        -p, --pretty          prettify the input grammar
        -t, --trace           produce verbose parsing output
        -v, --version         provide version information and exit
        -w CHARACTERS, --whitespace CHARACTERS
                                characters to skip during parsing (use "" to disable)
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

    class MySpecialBuffer(grako.bufferingBuffer):
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

    name = expre ;

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

    ``{ e }+`` or ``{ e }-``
        Positive closure. Match ``e`` one or more times. The AST_ is always a list.

    ``&e``
        Positive lookahead. Try parsing ``e``, but do not consume any input.

    ``!e``
        Negative lookahead. Try parsing ``e`` and fail if there's a match. Do not consume any input whichever the outcome.

    ``>rulename``
        The include operator'. Include the *right hand side* of rule ``rulename`` at this point.

        The following set of declarations::

            includable = exp1 ;

            expanded = exp0 >includable exp2 ;

        Has the same effect as defining *expanded* as::

            expanded = exp0 exp1 exp2 ;

        Note that the included rule must be defined before the rule that includes it.

    ``'text'`` or ``"text"``
        Match the token *text* within the quotation marks.

        Note that if *text* is alphanumeric, then **Grako** will check that the character following the token is not alphanumeric. This is done to prevent tokens like *IN* matching when the text ahead is *INITIALIZE*. This feature can be turned off by passing ``nameguard=False`` to the ``Parser`` or the ``Buffer``, or by using a pattern expression (see below) instead of a token expression.
        Alternatively, the ``@@nameguard`` directive may be specified in the grammar::

            @@nameguard :: False

    ``/regexp/``
        The pattern expression. Match the Python_ regular expression ``regexp`` at the current text position. Unlike other expressions, this one does not advance over whitespace or comments. For that, place the ``regexp`` as the only term in its own rule.

        The ``regexp`` is passed *as-is* to the Python_ re_ module (or regex_ if available), using ``match()`` at the current position in the text. The matched text is the AST_ for the expression.

    ``?/regexp/?``
        Another form of the pattern expression that can be used when there are slashes (``/``) in the pattern.

    ``rulename``
        Invoke the rule named ``rulename``. To help with lexical aspects of grammars, rules with names that begin with an uppercase letter will not advance the input over whitespace or comments.

    ``()``
        The empty expression. Succeed without advancing over input.

    ``!()``
        The *fail* expression. This is actually ``!`` applied to ``()``, which always fails.

    ``~``
        The *cut* expression. After this point, prevent other options from being considered even if the current option fails to parse.

    ``>>``
        Another form of the cut operator. *Deprecated*.

    ``name:e``
        Add the result of ``e`` to the AST_ using ``name`` as key. If ``name`` collides with any attribute or method of ``dict``, an underscore (``_``) will be appended to it in the AST_.

    ``name+:e``
        Add the result of ``e`` to the AST_ using ``name`` as key. Force the entry to be a list even if only one element is added. Collisions with ``dict`` attributes are resolved by appending an underscore to ``name``.

    ``@:e``
        The override operator. Make the AST_ for the complete rule be the AST_ for ``e``.

        The override operator is useful to recover only part of the right hand side of a rule without the need to name it, and then add a semantic action to recover the interesting part.

        This is a typical use of the override operator::

            subexp = '(' @:expre ')' ;

        The AST_ returned for the ``subexp`` rule will be the AST_ recovered from invoking ``expre``, without having to write a semantic action.

    ``@e``
        Another form of the override operator. *Deprecated*.

    ``@+:e``
        Like ``@:e``, but make the AST_ always be a list.

        This operator is convenient in cases such as::

            arglist = '(' @+:arg {',' @+:arg}* ')' ;

        In which the delimiting tokens are of no interest.

    ``$``
        The *end of text* symbol. Verify that the end of the input text has been reached.

    ``(*`` *comment* ``*)``
        Comments may appear anywhere in the text.

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

When combined with the ``#include`` directive, rule overrides can be used to create a modificated grammar without altering the original.

Abstract Syntax Trees (ASTs)
============================

By default, and AST_ is either a *list* (for *closures* and rules without named elements), or *dict*-derived object that contains one item for every named element in the grammar rule. Items can be accessed through the standard ``dict`` syntax, ``ast['key']``, or as attributes, ``ast.key``.

AST_ entries are single values if only one item was associated with a name, or lists if more than one item was matched. There's a provision in the grammar syntax (the ``+:`` operator) to force an AST_ entry to be a list even if only one element was matched. The value for named elements that were not found during the parse (perhaps because they are optional) is ``None``.

When the ``parseinfo=True`` keyword argument has been passed to the ``Parser`` constructor, a ``parseinfo`` element is added to AST_ nodes that are *dict*-like. The element contains a ``collections.namedtuple`` with the parse information for the node::

   ParseInfo = namedtuple('ParseInfo', ['buffer', 'rule', 'pos', 'endpos'])

With the help of the ``Buffer.line_info()`` method, it is possible to recover the line, column, and original text parsed for the node. Note that when ``ParseInfo`` is generated, the ``Buffer`` used during parsing is kept in memory for the lifetime of the AST_.


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


Left Recursion
==============

**Grako** provides support for left recursion in PEG_ grammars.

Sometimes, while debugging a grammar, it is useful to turn left-recursion support off::

    parser = MyParser(
        text,
        left_recursion=False,
    )

Left recursion can also be turned off from within the grammar using the
``@@left_recursion`` directive::

        @@left_recursion :: False


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


Templates and Translation
=========================

.. note::
    As of **Grako** 3.2.0, code generation is separated from grammar models through ``grako.codegen.CodeGenerator`` as to allow for code generation targets different from Python_. Still, the use of inline templates and ``rendering.Renderer`` hasn't changed. See the *regex* example for merged modeling and code generation.

**Grako** doesn't impose a way to create translators with it, but it exposes the facilities it uses to generate the Python_ source code for parsers.

Translation in **Grako** is *template-based*, but instead of defining or using a complex templating engine (yet another language), it relies on the simple but powerful ``string.Formatter`` of the Python_ standard library. The templates are simple strings that, in **Grako**'s style, are inlined with the code.

To generate a parser, **Grako** constructs an object model of the parsed grammar. Each node in the model is a descendant of ``rendering.Renderer``, and knows how to render itself. Templates are left-trimmed on whitespace, like Python_ *doc-comments* are. This is an example taken from **Grako**'s source code::

    class LookaheadGrammar(_DecoratorGrammar):

        ...

        template = '''\
                    with self._if():
                    {exp:1::}\
                    '''

Every *attribute* of the object that doesn't start with an underscore (``_``) may be used as a template field, and fields can be added or modified by overriding the ``render_fields()`` method.  Fields themselves are *lazily rendered* before being expanded by the template, so a field may be an instance of a ``Renderer`` descendant.

The ``rendering`` module uses a ``Formatter`` enhanced to support the rendering of items in an *iterable* one by one. The syntax to achieve that is::

    {fieldname:ind:sep:fmt}

All of ``ind``, ``sep``, and ``fmt`` are optional, but the three *colons* are not. Such a field will be rendered using::

     indent(sep.join(fmt % render(v) for v in value), ind)

The extended format can also be used with non-iterables, in which case the rendering will be::

     indent(fmt % render(value), ind)

The default multiplier for ``ind`` is ``4``, but that can be overridden using ``n*m`` (for example ``3*1``) in the format.

**Note**
    Using a newline (``\\n``) as separator will interfere with left trimming and indentation of templates. To use newline as separator, specify it as ``\\\\n``, and the renderer will understand the intention.


Examples
========

Grako
-----

The file ``etc/grako.ebnf`` contains a grammar for the **Grako** EBNF_ language written in the same language. It is used in the *bootstrap* test suite to prove that **Grako** can generate a parser to parse its own language, and the resulting parser is made the bootstrap parser every time **Grako** is stable (see ``grako/bootstrap.py`` for the generated parser). **Grako** uses **Grako** to translate grammars into parsers, so it is a good example of end-to-end translation.

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

**Grako** is Copyright (C) 2012-2014 by `Thomas Bragg`_ and  `Juancarlo Añez`_

.. _`Thomas Bragg`:  http://www.resqsoft.com/
.. _ResQSoft:  http://www.resqsoft.com/
.. _`Juancarlo Añez`: mailto:apalala@gmail.com

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

* **Guido van Rossum** created and has lead the development of the Python_ programming environment for over a decade. A tool like **Grako**, at under five thousand lines of code, would not have been possible without Python_.

* **Kota Mizushima** welcomed me to the `CSAIL at MIT`_ `PEG and Packrat parsing mailing list`_, and immediately offered ideas and pointed me to documentation about the implementation of *cut* in modern parsers. The optimization of memoization information in **Grako** is thanks to one of his papers.

* **My students** at UCAB_ inspired me to think about how grammar-based parser generation could be made more approachable.

* **Gustavo Lau** was my professor of *Language Theory* at USB_, and he was kind enough to be my tutor in a thesis project on programming languages that was more than I could chew. My peers, and then teaching advisers **Alberto Torres**, and **Enzo Chiariotti** formed a team with **Gustavo** to challenge us with programming languages like *LATORTA* and term exams that went well into the eight hours. And, of course, there was also the *pirate patch* that should be worn on the left or right eye depending on the *LL* or *LR* challenge.

* **Manuel Rey** led me through another, unfinished thesis project that taught me about what languages (spoken languages in general, and programming languages in particular) are about. I learned why languages use declensions_, and why, although the underlying words are in English_, the structure of the programs we write is more like Japanese_.

* `Marcus Brinkmann`_ has kindly submitted patches that have resolved obscure bugs in **Grako**'s implementation, and that have made the tool more user-friendly, specially for newcomers to parsing and translation.

* `Robert Speer`_ cleaned up the nonsense in trying to have Unicode handling be compatible with 2.7.x and 3.x, and figured out the canonical way of honoring escape sequences in grammar tokens without throwing off the encoding.

* `Basel Shishani`_ has been an incredibly throrough peer-reviewer of **Grako**.

* `Paul Sargent`_ implemented `Warth et al`_'s algorithm for supporting direct and indirect left recursion in PEG_ parsers.

* `Kathryn Long`_ proposed better support for UNICODE in the treatment of whitespace and regular expressions (patterns) in general. Her other contributions have made **Grako** more congruent, and more user-friendly.

* `David Röthlisberger`_ provided the definitive patch that allows the use of Python_ keywords as rule names.

* **Grako** would not have been possible without the vision, the funding, and the trust provided by **Thomas Bragg** through ResQSoft_.

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
.. _`Marcus Brinkmann`: http://blog.marcus-brinkmann.de/
.. _Marcus: http://blog.marcus-brinkmann.de/
.. _lambdafu: http://blog.marcus-brinkmann.de/
.. _`Robert Speer`: https://bitbucket.org/r_speer
.. _`Basel Shishani`: https://bitbucket.org/basel-shishani
.. _`Paul Sargent`: https://bitbucket.org/PaulS/
.. _`Warth et al`: http://www.vpri.org/pdf/tr2007002_packrat.pdf
.. _`Kathryn Long`: https://bitbucket.org/starkat
.. _starkat: https://bitbucket.org/starkat
.. _nehz: https://bitbucket.org/nehz/grako
.. _jimon: https://bitbucket.org/jimon/
.. _pgebhard: https://github.com/pgebhard?tab=repositories
.. _drothlis: https://bitbucket.org/drothlis/
.. _`David Röthlisberger`: https://bitbucket.org/drothlis/


Changes
=======

**Grako** uses `Semantic Versioning`_ for its releases, so parts of the version number may increase without any significant changes or backwards incompatibilities in the software.

.. _`Semantic Versioning`: http://semver.org/

3.6.7
-----

* **BUG** Detect anf fail promptly on empty tokens in grammars.
* More reasonable treatment for ANTLR_  ``token`` definitions in the ``antlr2grako`` example.

3.6.6
-----

* All tests pass with Python_ 3.5.

* 59_ Python_ keywords can now actually be used as rule names in grammars (drothlis_).

* 60_ ``@@`` directives were not pressent in the output of the ``--pretty`` option.

.. _59: https://bitbucket.org/apalala/grako/issues/59/
.. _60: https://bitbucket.org/apalala/grako/issues/60/


3.6.5
-----

* 58_ The parameters to the constructor of generated parsers were being ignored (pgebhard).

* **BUG** ``grammars.py`` would call ``ctx.error()`` instead of ``ctx._error()`` on failed rule references.

* Overall cleanup of the code and of the development requirements.

.. _58: https://bitbucket.org/apalala/grako/issues/58/

3.6.3
-----

* 56_ Using @@whitespace generated invalid python programs

* The ``@@whitespace`` directive was not working for regular expressions (nehz_).

.. _56: https://bitbucket.org/apalala/grako/issues/56/

3.6.2
-----

* BUG: Left recursion in the grammar was checked for in the wrong place when disabled.

* Added basic support for output of an AST_ in YAML_ format.

.. _YAML: https://en.wikipedia.org/wiki/YAML

3.6.1
-----

* Added ``@@whitespace`` directive to specify whitespace regular expression within the grammar (starkat_).

* Added ``@@nameguard`` and ``@@ignorecase`` directives to toggle the respective boolean parameters within the grammar (starkat_).

* 52_ Build with Cython failed on Windows.

* Applied Flake8_ suggestions.

* Upgraded development libraries to their latest versions (see ``requirements.txt``).

.. _52: https://bitbucket.org/apalala/grako/issue/45


3.5.1
-----

* 45_ The ``grako`` tool now produces basic statistics about the processed grammar.

* 46_ Left recursion support can be turned off using the ``left_recursion=`` parameter to parser constructors.

* 47_ New ``@@comments`` and ``@@eol_comments`` can be used within a grammar to specify the respective regular expressions.

* 48_ Rules can now be overriden/redefined using the ``@override`` decorator.

* Added backwards compatibility with ``Buffer.whitespace``.

* Added ``AST.asjson()`` to not have to import ``grako.util.asjson()`` for the same purpose.

.. _45: https://bitbucket.org/apalala/grako/issue/45
.. _46: https://bitbucket.org/apalala/grako/issue/46
.. _47: https://bitbucket.org/apalala/grako/issue/47
.. _48: https://bitbucket.org/apalala/grako/issue/48

3.4.3
-----

* Minor improvements to ``buffering.Buffer``.

* *BUG* 42_ ``setup.py`` might give errors under some locales because of the non-ASCII characters in  ``README.rst``.

* Added a ``--no-nameguard`` command-line option to generated parsers.

* Allow *Buffer* descendants to customize how text is split into lines (starkat_).

* Now the ``re.UNICODE`` flag is consistently used in pattern, comment, and whitespace matching. A re_ regular expression is now accepted for whitespace matching. Character sets provided as ``str``, ``list``, or ``set`` are converted to the corresponding regular expression (starkat_).

* If installed, the regex_ module will be used instead of re_ in all pattern matching (starkat_). See the section about *whitespace* above.

* Added a ``--version`` option to the commandline tool. A ``grako.__version__`` variable is now available.

.. _42: https://bitbucket.org/apalala/grako/issue/42


3.3.0
-----

* Refactorings to enhance consistency in parsing between models and and generated parsers.

* 37_ Block comments are preserved when using  the ``--pretty`` option.

* 38_ Trace output uses color if the colorama_ package is installed. Also, the vertical size of trace logs was reduced to three lines per entry.

* 40_ The widht and the separator used in parse traces are now configurable with keyword arguments.

.. _37: https://bitbucket.org/apalala/grako/issue/37/
.. _38: https://bitbucket.org/apalala/grako/issue/38/
.. _40: https://bitbucket.org/apalala/grako/issue/40/

.. _colorama: https://pypi.python.org/pypi/colorama/

3.2.1
-----

* Now rule parameters and ``model.ModelBuilderSemantics`` are used to produce grammar models with a minimal set of semantic methods.

* Code generation is now separtate from the grammar model, so translation targets differen from Python_ are easier to implement.

* Removed attribute assignment to the underlying ``dict`` in ``AST``. It was the source of obscure bugs for **Grako** users.

* Now an ``eol_comments_re=`` parameter can be passed to ``Parser`` and ``Buffer``.

* *BUG* Need to allow newline (``\n``) characters within grammar patterns.

* *BUG* 36_ Keyword arguments in rules were not being parsed correctly (Franz_G_).

* Several *BUGs* in the advanced features were fixed. See the `Bitbucket commits`_ for details.

.. _36: https://bitbucket.org/apalala/grako/issue/36
.. _Franz_G: https://bitbucket.org/Franz_G

3.1.2
-----

* **Grako** now supports direct and indirect left recursion thanks to the implementation done by `Paul Sargent`_ of the work by `Warth et al`_. Performance for non-left-recursive grammars is unaffected.

* The old grammar syntax is now supported with deprecation warnings. Use the ``--pretty`` option to upgrade a grammar.

* If there are no slashes in a pattern, they can now be specified without the opening and closing question marks.

* *BUG* 33_ Closures were sometimes being treated as plain lists, and that produced inconsistent results for named elements (lambdafu_).

* *BUG* The bootstrap parser contained errors due to the previous bug in ``util.ustr()``.

* *BUG* 30_  Make sure that escapes in ``--whitespace`` are evaluated before being passed to the model.

* *BUG* 30_ Make sure that ``--whitespace`` and ``--no-nameguard`` indeed affect the behavior of the generated parser as expected.

.. _30: https://bitbucket.org/apalala/grako/issue/30/
.. _33: https://bitbucket.org/apalala/grako/issue/33/


3.0.4
-----

* The bump in the major version number is because the grammar syntax changed to accomodate new features better, and to remove sources of ambituity and hard-to-find bugs. The naming changes in some of the advanced features (*Walker*) should impact only complex projects.

* The *cut* operator is now ``~``, the tilde.

* Now name overrides must always be specified with a colon, ``@:e``.

* Grammar rules may declare Python_-style arguments that get passed to their corresponding semantic methods.

* Grammar rules may now *inherit* the contents of other rules using the ``<`` operator.

* The *right hand side* of a rule may be included in another rule using the ``>`` operator.

* Grammars may include other files using the ``#include ::`` directive.

* Multiple definitions of grammar rules with the same name are now disallowed. They created ambiguity with new features such as rule parameters, based rules, and rule inclusion, and they were an opportunity for hard-to-find bugs (*import this*).

* Added a ``--pretty`` option to the command-line tool, and refactored pretty-printing (``__str__()`` in grammar models) enough to make its output a norm for grammar format.

* Internals and examples were upgraded to use the latest **Grako** features.

* Parsing exceptions will now show the sequence of rule invocations that led to the failure.

* Renamed ``Traverser`` and ``traverse`` to ``Walker`` and ``walk``.

* Now the keys in ``grako.ast.AST`` are ordered like in ``collections.OrderedDict``.

* **Grako** models are now more JSON_-friendly with the help of ``grako.ast.AST.__json__()``, ``grako.model.Node.__json__()`` and ``grako.util.asjon()``.

* Added compatibility with Cython_.

* Removed checking for compatibility with Python_ 3.3 (use 3.4 instead).
* Incorporated `Robert Speer`_'s solution to honoring escape sequences without messing up the encoding.

* *BUG* Honor simple escape sequences in tokens while trying not to corrupt unicode input.  Projects using non-ASCII characters in grammars should prefer to use unicode character literals instead of Python_ ``\x`` or ``\o`` escape sequences.  There is no standard/stable way to unscape a Python_ string with escaped escape sequences. Unicode is broken in Python_ 2.x.

* *BUG* The ``--list`` option was not working in Python_ 3.4.1.

* *BUG* 22_ Always exit with non-zero exit code on failure.

* *BUG* 23_ Incorrect encoding of Python_ escape sequences in grammar tokens.

* *BUG* 24_ Incorrect template for *--pretty* of multi-line optionals.

.. _22: https://bitbucket.org/apalala/grako/issue/22/grako-script-returns-exit_success-on
.. _23: https://bitbucket.org/apalala/grako/issue/23/pretty-output-escaping-incorrect
.. _24: https://bitbucket.org/apalala/grako/issue/24/pretty-output-changes-optional-match-into


.. _Cython: http://cython.org/
.. _JSON: http://www.json.org/

2.4.3
-----

* Changes to allow downstream translators to have different target languages with as little code replication as possible.  There's new functionality pulled from downstream in ``grako.model`` and ``grako.rendering``. ``grako.model`` is now a module instead of a package.

* The `Visitor Pattern`_ doesn't make much sense in a dynamically typed language, so the functionality was replaced by more flexible ``Traverser`` classes. The new ``_traverse_XX()`` methods in `Traverser` classes carry a leading underscore to remind that they shouldn't be used outside of the protocol.

* Now a ``_default()`` method is called in the semantics delegate when no specific method is found. This allows, for example, generating meaningful errors when something in the semantics is missing.

* Added compatibility with tox_. Now tests are performed against the latest releases of Python_ 2.7.x and 3.x, and PyPy_ 2.x.

* Added ``--whitespace`` parameter to generated ``main()``.

* Applied Flake8_ to project and to generated parsers.

.. _Flake8: https://pypi.python.org/pypi/flake8
.. _tox: https://testrun.org/tox/latest/


2.3.0
-----

* Now the ``@`` operator behaves as a special case of the ``name:`` operator, allowing for simplification of the grammar, parser, semantics, and **Grako** grammars. It also allows for expressions such as ``@+:e``, with the expected semantics.

* *Refactoring* The functionality that was almost identical in generated parsers and in models was refactored into ``Context``.

* *BUG!* Improve consistency of use Unicode between Python_ 2.7 and 3.x.

* *BUG!* Compatibility between Python_ 2.7/3.x `print()` statements.

2.2.2
-----

* Optionally, do not memoize during positive or negative lookaheads. This allows lookaheads to fail semantically without committing to the fail.

* Fixed the implementation of the *optional* operator so the AST_/CST_ generated when the *optional* succeeds is exactly the same as if the expression had been mandatory.

* Grouping expressions no longer produce a list as CST_.

* *BUG*! Again, make sure closures always return a list.

* Added infrastructure for stateful rules (lambdafu_, see the `pull request <https://bitbucket.org/apalala/grako/pull-request/13/stateful-parsing-for-grako/diff>`_ ).

* Again, protect the names of methods for rules with a leading and trailing underscore.  It's the only way to avoid unexpected name clashes.

* The bootstrap parser is now the one generated by **Grako** from the bootstrap grammar.

* Several minor bug fixes (lambdafu_).

* *BUG!* The choice operator must restore context even when some of the choices match partially and then fail.

* *BUG!* ``Grammar.parse()`` needs to initialize the AST_ stack.

* *BUG!* ``AST.copy()`` was too shallow, so an AST_ could be modified by a closure iteration that matched partially and eventually failed. Now ``AST.copy()`` clones AST_ values of type ``list`` to avoid that situation.

* *BUG!* A failed ``cut`` must trickle up the rule-call hierarchy so parsing errors are reported as close to their source as possible.


2.0.4
-----
* **Grako** no longer assumes that parsers implement the semantics. A separate semantics implementation must be provided. This allows for less polluted namespaces and smaller classes.
* A ``last_node`` protocol allowed the removal of all mentions of variable ``_e`` from generated parsers, which are thus more readable.
* Refactored *closures* to be more pythonic (there are **no** anonymous blocks in Python_!).
* Fixes to the *antlr2grako* example to let it convert over 6000 lines of an ANTLR_ grammar to **Grako**.
* Improved rendering of grammars by grammar models.
* Now *tokens* accept Python_ escape sequences.
* Added a simple `Visitor Pattern`_ for ``Renderer`` nodes. Used it to implement diagramming.
* Create a basic diagram of a grammar if pygraphviz_ is available.  Added the ``--draw`` option to the command-line tool.
* *BUG!* Trace information off by one character (thanks to lambdafu_).
* *BUG!* The AST_ for a closure might fold repeated symbols (thanks to lambdafu_).
* *BUG!* It was not possible to pass buffering parameters such as ``whitespace`` to the parser's constructor (thanks to lambdafu_).
* Added command-line and parser options to specify the buffering treatment of ``whitespace`` and ``nameguard`` (lambdafu_).
* Several improvements and bug fixes (mostly by lambdafu_).

1.4.0
-----
* *BUG!* Sometimes the AST_ for a closure (``{}``) was not a list.
* Semantic actions can now be implemented by a delegate.
* Reset synthetic method count and use decorators to increase readability of generated parsers.
* The **Grako** EBNF_ grammar and the bootstrap parser now align, so the grammar can be used to bootstrap **Grako**.
* The bootstrap parser was refactored to use semantic delegates.
* Proved that grammar models can be pickled, unpickled, and reused.
* Added the *antlr* example with an ANTLR_-to-**Grako** grammar translator.
* Changed the licensing to simplified BSD_.


1.3.0
-----
* *Important memory optimization!* Remove the memoization information that a *cut* makes obsolete (thanks to Kota Mizushima).
* Make sure that *cut* actually applies to the nearest fork.
* Finish aligning model parsing with generated code parsing.
* Report all the rules missing in a grammar before aborting.
* Align the sample *etc/grako.ebnf* grammar to the language parsed by the bootstrap parser.
* Ensure compatibility with Python_ 2.7.4 and 3.3.1.
* Update credits.

1.2.1
-----
* Lazy rendering of template fields.
* Optimization of *rendering engine*'s ``indent()`` and ``trim()``.
* Rendering of iterables using a specified separator, indent, and format.
* Basic documentation of the *rendering engine*.
* Added a cache of compiled regexps to ``Buffer``.
* Align bootstrap parser with generated parser framework.
* Add *cuts* to bootstrap parser so errors are reported closer to their origin.
* *(minor) BUG!* ``FailedCut`` exceptions must translate to their nested exception so the reported line and column make sense.
* Prettify the sample **Grako** grammar.
* Remove or comment-out code for tagged/named rule names (they don't work, and their usefulness is doubtful).
* Spell-check this document with `Vim spell`_.
* Lint using flake8_.

1.1.0
-----
* *BUG!* Need to preserve state when closure iterations match partially.
* Improved performance by also memoizing exception results and advancement over whitespace and comments.
* Work with Unicode while rendering.
* Improved consistency between the way generated parsers and models parse.
* Added a table of contents to this *README*.
* Document ``parseinfo`` and default it to *False*.
* Mention the use of *context managers*.

1.0.0
-----
* First public release.

.. _`Visitor Pattern`: http://en.wikipedia.org/wiki/Visitor_pattern
.. _`Vim spell`:  http://vimdoc.sourceforge.net/htmldoc/spell.html
.. _flake8: https://pypi.python.org/pypi/flake8
.. _Bitbucket: https://bitbucket.org/apalala/grako
.. _`Bitbucket commits`: https://bitbucket.org/apalala/grako/commits/
.. _PyPi: https://pypi.python.org/pypi/grako
