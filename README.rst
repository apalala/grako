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

**Grako** is *different* from other PEG_ parser generators in that the generated parsers use Python_'s very efficient exception-handling system to backtrack. **Grako** generated parsers simply assert what must be parsed; there are no complicated *if-then-else* sequences for decision making or backtracking. *Positive and negative lookaheads*, and the *cut* element with its cleaning of the memoization cache allow for additional, hand-crafted optimizations at the grammar level, and delegation to Python_'s re_ module for *lexemes* allows for (Perl_-like) powerful and efficient lexical analysis. The use of Python_'s `context managers`_ considerably reduces the size of the generated parsers for enhanced CPU-cache hits.

**Grako**, the runtime support, and the generated parsers have measurably low `Cyclomatic complexity`_.  At around 3000 lines of Python_, it is possible to study all its source code in a single session. **Grako**'s only dependencies are on the Python_ 2.7, 3.3, or PyPy_ standard libraries.

.. _`Cyclomatic complexity`: http://en.wikipedia.org/wiki/Cyclomatic_complexity

**Grako** is feature complete and currently being used over very large grammars to parse and translate hundreds of thousands of lines of legacy_ code.

.. _KLOC: http://en.wikipedia.org/wiki/KLOC
.. _legacy: http://en.wikipedia.org/wiki/Legacy_code
.. _PyPy: http://pypy.org/
.. _`context managers`: http://docs.python.org/2/library/contextlib.html
.. _re: http://docs.python.org/2/library/re.html
.. _Perl: http://www.perl.org/


Table of Contents
=================
.. contents:: \


Rationale
=========

**Grako** was created to address recurring problems encountered over decades of working with parser generation tools:

* To deal with programming languages in which important statement words (can't call them keywords) may be used as identifiers in programs, the parser must be able to lead the lexer. The parser must also lead the lexer to parse languages in which the meaning of input symbols may change with context, like Ruby_.

* When ambiguity is the norm in the parsed language (as is the case in several legacy_ ones), an LL or LR grammar becomes contaminated with myriads of lookaheads. PEG_ parsers address ambiguity from the onset. Memoization, and relying on the exception-handling system makes backtracking very efficient.

* Semantic actions, like `Abstract Syntax Tree`_ (AST_)  transformation, *do not*  belong in the grammar. Semantic actions in the grammar create yet another programming language to deal with when doing parsing and translation: the source language, the grammar language, the semantics language, the generated parser's language, and the translation's target language. Most grammar parsers do not check that the embedded semantic actions have correct syntax, so errors get reported at awkward moments, and against the generated code, not against the source.

* Pre-processing (like dealing with includes, fixed column formats, or Python_'s structure through indentation) belongs in well-designed program code, and not in the grammar.

* It is easy to recruit help with knowledge about a mainstream programming language (Python_ in this case). It is not so for grammar description languages. As a grammar language becomes more complex it becomes increasingly difficult to find who can maintain a parser. **Grako** grammars are in the spirit of a *Translators and Interpreters 101* course (if something is hard to explain to an college student, it's probably too complicated, or not well understood).

* Generated parsers should be humanly-readable and debuggable. Looking at the generated source code is sometimes the only way to find problems in a grammar, the semantic actions, or in the parser generator itself. It's inconvenient to trust generated code that you cannot understand.

* Python_ is a great language for working in language parsing and translation.

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


.. _`Semantic Graph`: http://en.wikipedia.org/wiki/Abstract_semantic_graph


Using the Tool
==============

**Grako** is run from the command line::

    $ python -m grako

or::

    $ scripts/grako

or just::

    $ grako

if **Grako** was installed using *easy_install* or *pip*.

The *-h* and *--help* parameters provide full usage information::

        $ python -m grako -h
        usage: grako [-h] [-m name] [-o outfile] [-t] [--whitespace characters] [--no-nameguard] [-b] [-d] grammar

        Grako (for grammar compiler) takes grammars in a variation of EBNF as input,
        and outputs a memoizing PEG parser in Python.

        positional arguments:
        grammar               The filename of the grammar to generate a parser for

        optional arguments:
        -h, --help            show this help message and exit
        -m name, --name name  An optional name for the grammar. It defaults to the basename of the grammar file's name
        -o outfile, --outfile outfile specify where the output should go (default is stdout)
        -t, --trace           produce verbose parsing output
        -w, --whitespace characters
                              whitespace characters (use empty string to disable automatic whitespace)
        -n, --no-nameguard    do not protect alphanumeric tokens that are prefixes of others
        -b, --binary          generate a pickled grammar model instead of a parser
        -d, --draw            generate a diagram of the grammar

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



The EBNF Grammar Syntax
=======================

**Grako** uses a variant of the standard EBNF_ syntax. A grammar consists of a sequence of one or more rules of the form::

    name = expre ;

or::

    name = expre .

Both the semicolon (``;``) and the period (``.``) are accepted as rule definition terminators.

If a *name* collides with a Python_ keyword, an underscore (``_``) will be appended to it on the generated parser.

If you define more than one rule with the same name::

    name = expre1 ;
    name = expre2 ;

The result will be equivalent to applying the choice operator to the
right-hand-side expressions::

    name = expre1 | expre2 ;

Rule names that start with an uppercase character::

   FRAGMENT = ?/[a-z]+/?

*do not* advance over whitespace before beginning to parse. This feature becomes handy when defining complex lexical elements, as it allows breaking them into several rules.

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
        Closure+1. Match ``e`` one or more times.

    ``&e``
        Positive lookahead. Try parsing ``e``, but do not consume any input.

    ``!e``
        Negative lookahead. Try parsing ``e`` and fail if there's a match. Do not consume any input whichever the outcome.

    ``'text'`` or ``"text"``
        Match the token text within the quotation marks.

        **Note that** if *text* is alphanumeric, then **Grako** will check that the character following the token is not alphanumeric. This is done to prevent tokens like *IN* matching when the text ahead is *INITIALIZE*. This feature can be turned off by passing ``nameguard=False`` to the ``Parser`` or the ``Buffer``, or by using a pattern expression (see below) instead of a token expression.

    ``?/regexp/?``
        The pattern expression. Match the Python_ regular expression ``regexp`` at the current text position. Unlike other expressions, this one does not advance over whitespace or comments. For that, place the ``regexp`` as the only term in its own rule.

        The ``regexp`` is passed *as-is* to the Python_ *re* module, using ``re.match()`` at the current position in the text. The matched text is the AST_ for the expression.

    ``rulename``
        Invoke the rule named ``rulename``. To help with lexical aspects of grammars, rules with names that begin with an uppercase letter will not advance the input over whitespace or comments.

    ``()``
        The empty expression. Succeed without advancing over input.

    ``!()``
        The *fail* expression. This is actually ``!`` applied to ``()``, which always fails.

    ``>>``
        The cut expression. After this point, prevent other options from being considered even if the current option fails to parse.

    ``name:e``
        Add the result of ``e`` to the AST_ using ``name`` as key. If more than one item is added with the same ``name``, the entry is converted to a list.

    ``name+:e``
        Add the result of ``e`` to the AST_ using ``name`` as key. Force the entry to be a list even if only one element is added.

    ``@:e``
        The override operator. Make the AST_ for the complete rule be the AST_ for ``e``. If more than one item is added, the entry is converted to a list.

        The override operator is useful to recover only part of the right hand side of a rule without the need to name it, and then add a semantic action to recover the interesting part.

        This is a typical use of the override operator::

            subexp = '(' @:expre ')' .

        The AST_ returned for the ``subexp`` rule will be the AST_ recovered from invoking ``expre``, without having to write a semantic action.

    ``@+:e``
        Like ``@:e``, but make the AST_ always be a list.

        This operator is convenient in cases such as::

            arglist = '(' @+:arg {',' @+:arg}* ')' .

        in which the delimiting tokens are of no interest.

    ``@e``
        A convenient shortcut for ``@:e``.

    ``$``
        The *end of text* symbol. Verify that the end of the input text has been reached.

    ``(*`` *comment* ``*)``
        Comments may appear anywhere in the text.

When there are no named items in a rule, the AST_ consists of the elements parsed by the rule, either a single item or a list. This default behavior makes it easier to write simple rules::

    number = ?/[0-9]+/? .

without having to write::

    number = number:?/[0-9]+/?

When a rule has named elements, the unnamed ones are excluded from the AST_ (they are ignored).

..    It is also possible to add an AST_ name to a rule::

..      name:rule = expre;

..    That will make the default AST_ returned to be a dict with a single item ``name`` as key, and the AST_ from the right-hand side of the rule as value.


Abstract Syntax Trees (ASTs)
============================

By default, and AST_ is either a *list* (for *closures* and rules without named elements), or *dict*-derived object that contains one item for every named element in the grammar rule. Items can be accessed through the standard ``dict`` syntax, ``ast['key']``, or as attributes, ``ast.key``.

AST_ entries are single values if only one item was associated with a name, or lists if more than one item was matched. There's a provision in the grammar syntax (the ``+:`` operator) to force an AST_ entry to be a list even if only one element was matched. The value for named elements that were not found during the parse (perhaps because they are optional) is ``None``.

When the ``parseinfo=True`` keyword argument has been passed to the ``Parser`` constructor, a ``parseinfo`` element is added to AST_ nodes that are *dict*-like. The element contains a *namedtuple* with the parse information for the node::

   ParseInfo = namedtuple('ParseInfo', ['buffer', 'rule', 'pos', 'endpos'])

With the help of the ``Buffer.line_info()`` method, it is possible to recover the line, column, and original text parsed for the node. Note that when *parseinfo* is generated, the *buffer* used during parsing is kept in memory with the AST_.

Whitespace
==========

By default, **Grako** generated parsers skip the usual whitespace characters (whatever Python_ defines as ``string.whitespace``), but you can change that behaviour by passing a ``whitespace`` parameter to your parser. For example::

    parser = MyParser(text, whitespace='\t ')

will consider the tab (``\t``) and space characters to be whitespace, but not so with other typical whitespace characters such as the end-of-line (``\n``).

If you don't define any whitespace characters::

    parser = MyParser(text, whitespace='')

then you will have to handle whitespace in your grammar rules (as it's often done in PEG_ parsers).


Case Sensitivity
================

If the source language is case insensitive, you can tell your parser by using the ``ignorecase`` parameter::

    parser = MyParser(text, ignorecase=True)

The change will affect both token and pattern matching.


Comments
========

Parsers will skip over comments specified as a regular expression using the ``comments_re`` parameter::

    parser = MyParser(text, comments_re="\(\*.*?\*\)")

For more complex comment handling, you can override the ``Parser._eatcomments()`` method.


Semantic Actions
================

There are no constructs for semantic actions in **Grako** grammars. This is on purpose, as we believe that semantic actions obscure the declarative nature of grammars and provide for poor modularization from the parser execution perspective.

Semantic actions are defined in a class, and applied by passing an object of the class to the `parse()` method of the parser as the `semantics=` paramenter. **Grako** will invoke the method that matches the name of the grammar rule every time the rule parses. The argument to the method will be the AST_ constructed from the right-hand-side of the rule::

    class MySemantics(object):
        def some_rule_name(self, ast):
            return ''.join(ast)

        def _default(self, ast):
            pass

If there's no method matching the rule's name, **Grako** will try to invoke a `_default()` method if it's defined::

    def _default(self, ast):

Nothing will happen neither the per-rule method nor `_default()` are defined.

The per-rule methods in classes implementing the semantics provide enough opportunity to do rule post-processing operations, like verifications (for inadequate use of keywords as identifiers), or AST_ transformation.

For finer-grained control it is enough to declare more rules, as the impact on the parsing times will be minimal.

If pre-processing is required at some point, it is enough to place invocations of empty rules where appropriate::

    myrule = first_part preproc {second_part} ;

    preproc = () ;

The abstract parser will honor as a semantic action a method declared as::

    def preproc(self, ast):


Templates and Translation
=========================

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
    Using a newline (`\\n`) as separator will interfere with left trimming and indentation of templates. To use newline as separator, specify it as `\\\\n`, and the renderer will understand the intention.

Examples
========

Grako
-----

The file ``etc/grako.ebnf`` contains a grammar for the **Grako** EBNF_ language written in the same language. It is used in the *bootstrap* test suite to prove that **Grako** can generate a parser to parse its own language.

Regex
-----

The project ``examples/regexp`` contains a regexp-to-EBNF translator and parser generator. The project has no practical use, but it's a complete, end-to-end example of how to implement a translator using **Grako**.

antlr2grako
-----------

The project ``examples/antlr2grako`` contains a ANTLR_ to **Grako** grammar tanslator.  The project is a good example of the use of models and templates in translation. The program, ``antlr2grako.py`` generates the **Grako** gramar on standard ouput, but because the model used is **Grako**'s own, the same code can be used to directly generate a parser from an ANTLR_ grammar. Please take a look at the examples *README* to know about limitations.

Other Open-source Examples
==========================

* **Christian Ledermann** wrote  parsewkt_ a parser for `Well-known text`_ (WTK_) using **Grako**.

.. _parsewkt: https://github.com/cleder/parsewkt
.. _`Well-known text`: http://en.wikipedia.org/wiki/Well-known_text
.. _WTK: http://en.wikipedia.org/wiki/Well-known_text


* **Marcus Brinkmann** wrote smc.mw_ a parser for a MediaWiki_-style language.

.. _smc.mw: https://github.com/lambdafu/smc.mw
.. _MediaWiki: http://www.mediawiki.org/wiki/MediaWiki


License
=======

**Grako** is Copyright (C) 2012-2014 by `ResQSoft Inc.`_ and  `Juancarlo Añez`_

.. _`ResQSoft Inc.`:  http://www.resqsoft.com/
.. _ResQSoft:  http://www.resqsoft.com/
.. _`Juancarlo Añez`: mailto:apalala@gmail.com

You may use the tool under the terms of the BSD_-style license described in the enclosed **LICENSE.txt** file.

*If your project requires different licensing* please contact
`info@resqsoft.com`_.

.. _BSD: http://en.wikipedia.org/wiki/BSD_licenses#2-clause_license_.28.22Simplified_BSD_License.22_or_.22FreeBSD_License.22.29
.. _`info@resqsoft.com`: mailto:info@resqsoft.com


Contact and Updates
===================

To discuss **Grako** and to receive notifications about new releases, please join the low-volume `Grako Forum`_ at *Google Groups*.

.. _`Grako Forum`:  https://groups.google.com/forum/?fromgroups#!forum/grako


Credits
=======

The following must be mentioned as contributors of thoughts, ideas, code, *and funding* to the **Grako** project:

* **Niklaus Wirth** was the chief designer of the programming languages Euler_, `Algol W`_, Pascal_, Modula_, Modula-2_, Oberon_, and Oberon-2_. In the last chapter of his 1976 book `Algorithms + Data Structures = Programs`_, Wirth_ creates a top-down, descent parser with recovery for the Pascal_-like, `LL(1)`_ programming language `PL/0`_. The structure of the program is that of a PEG_ parser, though the concept of PEG_ wasn't formalized until 2004.

.. _Wirth: http://en.wikipedia.org/wiki/Niklaus_Wirth
.. _Euler: http://en.wikipedia.org/wiki/Euler_programming_language
.. _`Algol W`: http://en.wikipedia.org/wiki/Algol_W
.. _Pascal: http://en.wikipedia.org/wiki/Pascal_programming_language
.. _Modula: http://en.wikipedia.org/wiki/Modula
.. _Modula-2: http://en.wikipedia.org/wiki/Modula-2
.. _Oberon: http://en.wikipedia.org/wiki/Oberon_(programming_language)
.. _Oberon-2: http://en.wikipedia.org/wiki/Oberon-2
.. _`PL/0`: http://en.wikipedia.org/wiki/PL/0

* **Bryan Ford** introduced_ PEG_ (parsing expression grammars) in 2004.

* Other parser generators like `PEG.js`_ by **David Majda** inspired the work in **Grako**.

* **William Thompson** inspired the use of context managers with his `blog post`_ that I knew about through the invaluable `Python Weekly`_ newsletter, curated by **Rahul Chaudhary**

* **Jeff Knupp** explains why **Grako**'s use of exceptions_ is sound, so I don't have to.

* **Terence Parr** created ANTLR_, probably the most solid and professional parser generator out there. Ter, *ANTLR*, and the folks on the *ANLTR* forums helped me shape my ideas about **Grako**.

* **JavaCC** (originally Jack_) looks like an abandoned project. It was the first parser generator I used while teaching.

* **Grako** is very fast. But dealing with millions of lines of legacy source code in a matter of minutes would be impossible without PyPy_, the work of **Armin Rigo** and the `PyPy team`_.

* **Guido van Rossum** created and has lead the development of the Python_ programming environment for over a decade. A tool like **Grako**, at under three thousand lines of code, would not have been possible without Python_.

* **Kota Mizushima** welcomed me to the `CSAIL at MIT`_ `PEG and Packrat parsing mailing list`_, and immediately offered ideas and pointed me to documentation about the implementation of **cut** in modern parsers. The optimization of memoization information is thanks to one of his papers.

* **My students** at UCAB_ inspired me to think about how grammar-based parser generation could be made more approachable.

* **Gustavo Lau** was my professor of *Language Theory* at USB_, and he was kind enough to be my tutor in a thesis project on programming languages that was more than I could chew. My peers, and then teaching advisers **Alberto Torres**, and **Enzo Chiariotti** formed a team with **Gustavo** to challenge us with programming languages like *LATORTA* and term exams that went well into the eight hours. And, of course, there was also the *pirate patch* that should be worn on the left or right eye depending on the *LL* or *LR* challenge.

* **Manuel Rey** led me through another, unfinished thesis project that taught me about what languages (spoken languages in general, and programming languages in particular) are about. I learned why languages use declensions_, and why, although the underlying words are in English_, the structure of the programs we write is more like Japanese_.

* `Marcus Brinkmann`_ has kindly submitted patches that have resolved obscure bugs in **Grako**'s implementation, and that have made the tool more user-friendly, specially for newcomers to parsing and translation.

* **Grako** would not have been possible without the vision, the funding, and the trust provided by **Thomas Bragg** through ResQSoft_.

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

Changes
=======

2.4.1
-----
    * *BUG* The `whitespace` parameter was not being passed consistently, and its
      interaction with the `nameguard` parameter was not well thought out (no
      `whitespace=''` mustimply `nameguard=False`).

    * Added `--whitespace` parameter to generated `main()`.

    * Tested agains Python_ 3.4.

2.4.0
-----

    * The aim of this release is to make the minimum changes necessary to allow downstream translators to have different target languages with as little code replication as possible.

    * There's new functionality pulled from downstream in ``grako.model`` and ``grako.rendering``. ``grako.model`` is now a module instead of a package.

    * The `Visitor Pattern`_ doesn't make much sense in a dynamically typed language, so the functionality was replaced by more flexible ``Traverser`` classes. The new ``_traverse_XX()`` methods in `Traverser` classes carry a leading underscore to remind that they shouldn't be used outside of the protocol.

    * Now a `_default()` method is called in the semantics delegate when no specific method is found. This allows for producing meaningful errors when something in the semantics is missing.

    * Added compatiblity with tox_, and now tests are performed against the latest releases of Python_ 2.7.x and 3.2.y, and PyPy_ 2.2.x.

    * There are **no bugs detected or fixed** in this release. All efforts have been made to maintain backwards compatibility, but only testing will tell.

.. _tox: https://testrun.org/tox/latest/


2.3.0
-----
    * Now the ``@`` operator behaves as a special case of the ``name:`` operator, allowing for simplification of the grammar, parser, semantics, and **Grako** grammars. It also allows for expressions such as `@+:e`, with the expected semantics.

    * *Refactoring* The functionality that was almost identical in generated parsers and in models was refactored into ``Context``.

    * *BUG!* Improve consistency of use Unicode between Python_ 2.7 and 3.3.

    * *BUG!* Compability betweein Python_ 2.7/3.x `print()` statements.

2.2.2
-----

    * *BUG!* The choice operator must restore context even when some of the choices match partially and then fail.
    * *BUG!* ``Grammar.parse()`` needs to initialize the AST_ stack.

    * *BUG!* ``AST.copy()`` was too shallow, so an AST_ could be modified by a closure iteration that matched partially and eventually failed. Now ``AST.copy()`` clones AST_ values of type ``list`` to avoid that situation.

    * *BUG!* A failed ``cut`` must trickle up the rule-call hierarchy so parsing errors are reported as close to their source as possible.
    * Optionally, do not memoize during positive or negative lookaheads. This allows lookaheads to fail semantically without committing to the fail.

    * Fixed the implementation of the *optional* operator so the AST_/CST_ generated when the *optional* succeeds is exactly the same as if the expression had been mandatory.
    * Grouping expressions no longer produce a list as CST_.
    * *BUG*! Again, make sure tha closures always return a list.
    * Added infrastructure for stateful rules (lambdafu_, see the `pull request <https://bitbucket.org/apalala/grako/pull-request/13/stateful-parsing-for-grako/diff>`_ ).
    * Again, protect the names of methods for rules with a leading and trailing underscore.  It's the only way to avoid unexpected name clashes.
    * The bootstrap parser is now the one generated by **Grako** from the bootstrap grammar.
    * Several minor bug fixes (lambdafu_).

2.0.4
-----
    * **Grako** no longer assumes that parsers implement the semantics. A separate semantics implementation must be provided. This allows for less poluted namespaces and smaller classes.
    * A ``last_node`` protocol allowed the removal of all mentions of variable ``_e`` from generated parsers, which are thus more readable.
    * Refactored *closures* to be more pythonic (there are **no** anonymous blocks in Python_!).
    * Fixes to the *antlr2grako* example to let it convert over 6000 lines of an ANTLR_ gramar to **Grako**.
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
    * *BUG!* Sometimes the AST_ for a closure ({}) was not a list.
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
    * *(minor) BUG!* ``FailedCut`` exceptions must translate to their nested exeption so the reported line and column make sense.
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
    * First feature-complete release.

.. _`Visitor Pattern`: http://en.wikipedia.org/wiki/Visitor_pattern
.. _pygraphviz: https://pypi.python.org/pypi/pygraphviz/
.. _`Vim spell`:  http://vimdoc.sourceforge.net/htmldoc/spell.html
.. _flake8: https://pypi.python.org/pypi/flake8
.. _Bitbucket: https://bitbucket.org/apalala/grako
.. _PyPi: https://pypi.python.org/pypi/grako
