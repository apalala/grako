# Change Log

**Grako** uses [Semantic Versioning][] for its releases, so parts of the version number may increase without any significant changes or backwards incompatibilities in the software.

[Semantic Versioning]: http://semver.org/


The format of this *Change Log* is inspired by [keeapachangelog.org].

[keeapachangelog.org]: http://keepachangelog.com/


## [X.Y.Z]


## [3.16.1] @ 2016-10-16

### Added
-   Make traces represent recursion failures differently.


### Changed
-   Removed `grako.exceptions.FailedParseBase` as it served no purpose.
-   Refactor the unicode part of traces into a separate module.


### Fixed
-   Fix off-by-one preventing multiple include statemtents to work ([gegenschall][]).
-   Left recursion was enable by default in generated parsers, though the README says its not.  Disabled.
-   Bug fixes, in the commit log.


## [3.16.0] @ 2016-10-01


### Added

-   Test and publish **Grako** using [Travis CI][].
-   Added support for case-insensitivity to `grako.symtables`.
-   A base class can now be specified along with the object model class name in grammar rules:

```ebnf
integer::Integer::Literal
```

### Changed

-   Reduced the memory used by symbol tables by replacing `symtables.SymbolReference` by the referencing `objectmodel.Node`.
-   Now `grako.grammars.Decorator` is public.
-   Demoted support for _left recursion_ to _experimental_. It has been reported that even some simple cases are not handled.


## [3.15.1] @ 2016-09-28


### Added

-   Added `symtables.Namespace.get()` for completenes.

### Changed

-   The result of `grako.model.Node.children()` now defaults to `Node.children_list()`. It was too unexpected that the child nodes might be out of order.
-   Simplified the `main()` function in generated parsers.
-   Moved `Node` into the new `grako.objectmodel`. Moved `NodeWalker` and descendants into the new `grako.walkers` module. Moved `ModelBuilderSemantics` into the `grako.semantics` module. The `grako.model` module was updated for backwards compatibility.
-   Generated parsers and models no longer carry the current date as a version tag. The tags served only to confuse version control.
-   Use `weakref.proxy` for back-references (like `grako.objectmodel.Node._parent`) to make it easier for the [Python][] garbage collector.
-   Walker will now also recognize walk methods where the class name has the upper case characters replaced by an underscore followed by the characeter in lower case (`walk_NegativeLookahead()` or `walk__negative_lookahead()`.

### Fixed

-   Added a patch for bakcwards compatibility with parsers generated before the switch from `prefix=` to `sep=` in generated calls to closures.
-   Restored special treatment of first line in `grako.util.trim()` (as in Python
    _doc-comnents_). There were unexpected results without the special treatment.
-   Use `_args_` and `_kwargs_` in generated models to avoid conflicts with grammar elelemts that use the standard [Python][] names.
-   The generated parser was overriding `Buffer` creation without regard for settings passed to the `Parser` class. There's now a `buffer_class` _kwarg_ to the `Context`, `Parser`, and the generated parser classes.
-   Deprecation warnings were always being enabled by `grako.util`.
-   Found programs that expect `grako.ast.AST` to be reexported from `grako.model`, so the re-export was re-instated.


## [3.14.0] @ 2016-08-19

### Added

-   Now `grako.symtables.Namespace` supports duplicate entries.


### Changed

-   Use upercase ``-V`` instead of ``-v`` to report the tool version, as to be compatible with almost everyone else.


### Fixed

-   The new `grako.symtables.Symbol` tried to serialize unknown fields to [JSON][].
-   Add `grako.symtables.SymbolReference` to the [JSON][] representation of namespaces.
-   The new `grako.model.DepthFirstWalker` could reach recursion limit when filtering for Iterables.  Now the filter is for `list`, which is the only container used in models.
-   The definition `grako.grammars.GrakoBuffer` was not overriding the bootstrap buffer, so `#include` was not working, among other possibly undetected (and serious) consequences.
-   The separator character for rules in the trace logs (``C_DERIVE`` in `grako.contexts`) was undefined for non-[POSIX][] platforms (traces could not be used on Windows).


## [3.13.0] @ 2016-08-18


### Added

-   Added this new *change log*.
-   The `--pretty-lean` command-line option will produce `--pretty` output, discarding `named:` elements and rule `::Parameters`.
-   A `@@parseinfo` directive controls the generation of parse information from the grammar.


### Changed

-   Traded memory for simplicity and replaced the line-based line cache in `buffering.Buffer` for a position-based cache.
-   Tab characters are left unchanged by `buffering.Buffer` as to keep references
    to positions in the original text relevant.
-   Refactored the ever-growing *grammar_test.py* into multiple files under *grako/test/grammar/*.

### Fixed

- In traces, the error column pointer was off when tab characters were involved.


## [3.12.1] @ 2016-08-06


### Added

-   Also generate a `buffering.Buffer` descendant specific to the grammar for parsers that need to customize the `parsing.Parser.parse()` method.
-   Added the `grako.synth` module which makes synthetic `grako.model.Node` classes pickable.
-   Now patterns may be concatenated to split a complex pattern into parts, possibly accross several lines: `/regexp/ + /regexp/`.
-   Added basic support for symbol tables in `grako.symtables`.
-   Syntax file for [Sublime Text][] ([vmuriart][]).


### Changed

-   Distinguish between positive and normal joins: `s.{e}+` and `s.{e}`.  Having `s.{e}` use a positive closure was too unexpected.
-   Now `model.ParseModel` is an alias for `model.Node`.
-   Improved `examples/antlr2grako` so it generates more usable **Grako** grammars.


### Fixed

-   The latest changes to `grako.util.trim()` were incomplete.
-   Fixed several inconsistencies in the implementation and use of `buffering.Buffer` line indexing.
-   Repeated parameters to object model constructors.

## [3.10.1] @ 2016-07-17


### Added

-   Enhancements to `grako.tool` and the command-line help [siemer].


### Changed

-   Unlink output file before attempting parser generation.
-   A `-G FILE` command-line option forces saving of the object model.
-   The function `grako.util.trim()` now also considers the first text ine.
-   Tested with [Python][] 3.6.0a3.


### Fixed

-   `grako.model.Node._adopt_children()` was incorrect, so `Node.parent` was not being set. Adopted a simple-approach solution based on suggestions by [linkdd].
-   Avoid recovering the same comment against the same line in `grako.buffering.Buffer`.
-   Recovering comments and end-of-line comments together was incorrect.
-   `model.Node` parenting still broken.
-   [73][] The `--draw` option did not recognize the new object model node types `Join` and `Constant`. Now `--draw` works with [Python][] 3.x
    using [pygraphviz][] 1.3.1.
-   [77][] [81][] Advance over whitespace before memoization or left recursion.

## [3.9.3] @ 2016-07-15


### Added

-   Added `@@grammar` directive to grammars as to avoid having to pass a `-m NAME` through the command line.
-   Added the `@@namechars` directive to allow specifying additional characters that may be part of tokens considerd names by `@@nameguard :: True`.
-   Now a choice expression may start with a leading `'|'`.
-   The `--object-model` command-line option will generate a python module with definitions for the class names specified as rule parameters (untested).


### Changed

-   Simplified the regular expression for floats in the **Grako** grammar [siemer]
-   Set all [flake8][] options in `tox.ini` [siemer].
-   Simplfied `__str__()` for directives [siemer].
-   Now `STARTRULE` defaults to `start` in generated parsers.
-   Now the [AST][] for a `grako.model.Node` is saved as `Node.ast`.
-   Several simplifications and refactorings by [siemer].

### Fixed

-   Fixes and improvements to generation of child sets and list in `model.Node` [gapag].
-   `@@keyword` not working correctly with `@@ignorecase`.
-   Fix for `@@keyword` and `@name` by moving check for `FailedSemantics` upper in the parsing chain.
-   Several important bug fixes to the object model generator [neumond]
-   Both `grako.grammars` and `grako.codegen.python` were manipulating the names defined in a grammar rule.
-   [74] `grako.model.Node.children()` returned an empty list even when traversing attributes that with names starting in `'_'`.
-   [57] Still bugs in handling of `@@whitespace` in the generated parser's [gkimbar].
-   Guard against recursive structures in `grako.util.asjson()`.
-   Cleaned up the grammar in `examples/python`; still untested.
-   Removed outdated information from the *README*.

## [3.8.2] @ 2016-04-23

### Added

-   Added grammar support for [keywords] in the source language through the `@@keyword::` directive and the `@name` decorator for rules.


### Changed

-   Make `ModelBuilderSemantics` support built-in types.


### Fixed

-   Wrong version number (RC) in this document.
-   [73] Keywords were not being passed to the base class of the generated parser.

## [3.7.0] @ 2016-03-05


### Added

-   Added suport for `` `constant` `` expressions which don't consume any input yet return the specified constant.
-   Now an empty closure (`{}`) consumes no input and generates an empty list as [AST].
-   Added the [Python]-inspired *join* operator, `s.{e}`, as a convenient syntax for parsing sequences with separators.


### Changed

-   Removed the `--binary` command-line option. It went unused, it was untested, and it was incorrectly implemented.
-   Generated parsers `pass` on `KeyboardInterrupt`.
-   Moved the bulk of the entry code for generated parsers to `util.generic_main()`. This allows for the verbose code to be verified by the usual tools.
-   Deprecate `{e}-` by removing it from the documentation.

## [3.6.7] @ 2016-01-27


### Added

-   Added `@@whitespace` directive to specify whitespace regular expression within the grammar [starkat].
-   Added `@@nameguard` and `@@ignorecase` directives to toggle the respective boolean parameters within the grammar [starkat].
-   All tests pass with [Python][] 3.5.
-   Added basic support for output of an [AST] in [YAML] format.
-   Applied [flake8] suggestions.


### Changed
-   More reasonable treatment for [ANTLR] `token` definitions in the `antlr2grako` example.
-   Upgraded development libraries to their latest versions (see `requirements.txt`).


### Fixed

-   Detect and fail promptly on empty tokens in grammars.
-   [52] Build with Cython failed on Windows.
-   [59][] [Python][] keywords can now actually be used as rule names in grammars [drothlis].
-   [60] `@@` directives were not pressent in the output of the `--pretty` option.
-   [58] The parameters to the constructor of generated parsers were being ignored (pgebhard).
-   `grammars.py` would call `ctx.error()` instead of `ctx._error()` on failed rule references.
-   Overall cleanup of the code and of the development requirements.
-   [56] Using @@whitespace generated invalid python programs
-   The `@@whitespace` directive was not working for regular expressions [nehz].
-   Left recursion in the grammar was checked for in the wrong place when disabled.


## [3.5.1] @ 2015-03-12


### Changed

-   Added backwards compatibility with `Buffer.whitespace`.
-   Added `AST.asjson()` to not have to import `grako.util.asjson()` for the same purpose.


### Fixed
-   [45] The `grako` tool now produces basic statistics about the processed grammar.
-   [46] Left recursion support can be turned off using the `left_recursion=` parameter to parser constructors.
-   [47] New `@@comments` and `@@eol_comments` can be used within a grammar to specify the respective regular expressions.
-   [48] Rules can now be overriden/redefined using the `@override` decorator.


## [3.4.3] @ 2014-11-27


### Added

-   Added a `--no-nameguard` command-line option to generated parsers.
-   Allow *Buffer* descendants to customize how text is split into lines [starkat].
-   Added a `--version` option to the commandline tool. A `grako.__version__` variable is now available.
-   A [re] regular expression is now accepted for whitespace matching. Character sets provided as `str`, `list`, or `set` are converted to the corresponding regular expression [starkat].
-   If installed, the [regex] module will be used instead of [re] in all pattern matching [starkat]. See the section about *whitespace* above.


### Changed

-   Minor improvements to `buffering.Buffer`.
-   Now the `re.UNICODE` flag is consistently used in pattern, comment, and whitespace matching.


### Fixed

-   [42] `setup.py` might give errors under some locales because of the non-ASCII characters in `README.rst`.



## [3.3.0] @ 2014-07-22

### Added

-   [40] The widtn and the separator used in parse traces are now configurable with keyword arguments.
-   [38] Trace output uses color if the [colorama] package is installed.

### Changed

-   Refactorings to enhance consistency in parsing between models and and generated parsers.
-   The vertical size of trace logs was reduced to three lines per entry.


### Fixed

-   [37] Block comments are preserved when using the `--pretty` option.


## [3.2.1] @ 2014-07-21


### Added
-   Now an `eol_comments_re=` parameter can be passed to `Parser` and `Buffer`.


### Changed

-   Now rule parameters and `model.ModelBuilderSemantics` are used to produce grammar models with a minimal set of semantic methods.
-   Code generation is now separtate from the grammar model, so translation targets different from [Python][] are easier to implement.


### Fixed

-   Need to allow newline (`\n`) characters within grammar patterns.
-   [36] Keyword arguments in rules were not being parsed correctly ([franz_g]).
-   Removed attribute assignment to the underlying `dict` in `AST`. It was the source of obscure bugs for **Grako** users.

## [3.1.2] @ 2014-07-14


### Added

-   **Grako** now supports direct and indirect left recursion thanks to the implementation done by Paul [Sargent] of the work by [Warth et al]. Performance for non-left-recursive grammars is unaffected.
-   The old grammar syntax is now supported with deprecation warnings.  Use the `--pretty` option to upgrade a grammar.
-   If there are no slashes in a pattern, they can now be specified without the opening and closing question marks.


### Fixed

-   [33] Closures were sometimes being treated as plain lists, and that produced inconsistent results for named elements [lambdafu].
-   The bootstrap parser contained errors due to the previous bug in `util.ustr()`.
-   [30] Make sure that escapes in `--whitespace` are evaluated before being passed to the model.
-   [30] Make sure that `--whitespace` and `--no-nameguard` indeed affect the behavior of the generated parser as expected.


## [3.0.4] @ 2014-07-01


### Added

-   The bump in the major version number is because the grammar syntax changed to accomodate new features better, and to remove sources of ambituity and hard-to-find bugs. The naming changes in some of the advanced features (*Walker*) should impact only complex projects.
-   Grammars may include other files using the `#include ::` directive.
-   Grammar rules may now *inherit* the contents of other rules using the `<` operator.
-   The *right hand side* of a rule may be included in another rule using the `>` operator.
-   Added a `--pretty` option to the command-line tool, and refactored pretty-printing (`__str__()` in grammar models) enough to make its output a norm for grammar format.
-   Added compatibility with [Cython].


### Changed

-   The *cut* operator is now `~`, the tilde.
-   Now name overrides must always be specified with a colon, `@:e`.  -   Grammar rules may declare [Python]-style arguments that get passed to their corresponding semantic methods.
-   Multiple definitions of grammar rules with the same name are now disallowed. They created ambiguity with new features such as rule parameters, based rules, and rule inclusion, and they were an opportunity for hard-to-find bugs (*import this*).
-   Internals and examples were upgraded to use the latest **Grako** features.
-   Parsing exceptions will now show the sequence of rule invocations that led to the failure.
-   Renamed `Traverser` and `traverse` to `Walker` and `walk`.
-   Now the keys in `grako.ast.AST` are ordered like in `collections.OrderedDict`.
-   **Grako** models are now more [JSON]-friendly with the help of `grako.ast.AST.__json__()`, `grako.model.Node.__json__()` and `grako.util.asjon()`.
-   Removed checking for compatibility with [Python][] 3.3 (use 3.4 instead).
-   Incorporated Robert [Speer]'s solution to honoring escape sequences without messing up the encoding.
-   Honor simple escape sequences in tokens while trying not to corrupt unicode input. Projects using non-ASCII characters in grammars should prefer to use unicode character literals instead of [Python][] `\x` or `\o` escape sequences. There is no standard/stable way to unscape a [Python][] string with escaped escape sequences.  Unicode is broken in [Python][] 2.x.


### Fixed

-   The `--list` option was not working in [Python][] 3.4.1.
-   [22] Always exit with non-zero exit code on failure.
-   [23] Incorrect encoding of [Python][] escape sequences in grammar tokens.
-   [24] Incorrect template for *--pretty* of multi-line optionals.


## [2.4.3] @ 2014-06-08


### Added

-   Added `--whitespace` parameter to generated `main()`.
-   Applied [flake8] to project and to generated parsers.
-   Now a `_default()` method is called in the semantics delegate when no specific method is found. This allows, for example, generating meaningful errors when something in the semantics is missing.
-   Changes to allow downstream translators to have different target languages with as little code replication as possible. There's new functionality pulled from downstream in `grako.model` and `grako.rendering`. `grako.model` is now a module instead of a package.
-   Added compatibility with [tox]. Now tests are performed against the latest releases of [Python][] 2.7.x and 3.x, and [PyPy] 2.x.


### Changed

-   The [Visitor Pattern] doesn't make much sense in a dynamically typed language, so the functionality was replaced by more flexible `Traverser` classes. The new `_traverse_XX()` methods in Traverser classes carry a leading underscore to remind that they shouldn't be used outside of the protocol.


## [2.3.0] @ 2013-11-27


### Added

-   Now the `@` operator behaves as a special case of the `name:` operator, allowing for simplification of the grammar, parser, semantics, and **Grako** grammars. It also allows for expressions such as `@+:e`, with the expected semantics.


### Changed

-   *Refactoring* The functionality that was almost identical in generated parsers and in models was refactored into `Context`.
-   Improve consistency of use Unicode between [Python][] 2.7 and 3.x.


### Fixed

-   Compatibility between [Python][] 2.7/3.x print() statements.

## [2.2.2] @ 2013-11-06


### Added

-   Optionally, do not memoize during positive or negative lookaheads.  This allows lookaheads to fail semantically without committing to the fail.
-   Added infrastructure for stateful rules ([lambdafu], see the [pull request] ).


### Changed

-   Grouping expressions no longer produce a list as [CST].
-   The bootstrap parser is now the one generated by **Grako** from the bootstrap grammar.
-   Protect the names of methods for rules with a leading and trailing underscore. It's the only way to avoid unexpected name clashes.


### Fixed

-   Fixed the implementation of the *optional* operator so the [AST]/CST\_ generated when the *optional* succeeds is exactly the same as if the expression had been mandatory.
-   Make sure closures always return a list.
-   The choice operator must restore context even when some of the choices match partially and then fail.
-   `Grammar.parse()` needs to initialize the [AST] stack.
-   `AST.copy()` was too shallow, so an [AST] could be modified by a closure iteration that matched partially and eventually failed.  Now `AST.copy()` clones [AST] values of type `list` to avoid that situation.
-   A failed `cut` must trickle up the rule-call hierarchy so parsing errors are reported as close to their source as possible.
-   Several minor bug fixes [lambdafu].


## [2.0.4] @ 2013-08-15


### Added

-   Now *tokens* accept [Python][] escape sequences.
-   Added a simple [Visitor Pattern] for `Renderer` nodes. Used it to implement diagramming.
-   Create a basic diagram of a grammar if [pygraphviz] is available.  Added the `--draw` option to the command-line tool.
-   Added command-line and parser options to specify the buffering treatment of `whitespace` and `nameguard` [lambdafu].
-   It was not possible to pass buffering parameters such as `whitespace` to the parser's constructor [lambdafu].


### Changed

-   **Grako** no longer assumes that parsers implement the semantics. A separate semantics implementation must be provided. This allows for less polluted namespaces and smaller classes.
-   A `last_node` protocol allowed the removal of all mentions of variable `_e` from generated parsers, which are thus more readable.
-   Refactored *closures* to be more pythonic (there are **no** anonymous blocks in [Python]!).
-   Improved rendering of grammars by grammar models.


### Fixed
-   Fixes to the *antlr2grako* example to let it convert over 6000 lines of an [ANTLR] grammar to **Grako**.
-   The [AST] for a closure might fold repeated symbols (thanks to [lambdafu]).
-   Trace information off by one character (thanks to [lambdafu]).
-   Several improvements and bug fixes mostly by [lambdafu].


## [1.4.0] @ 2013-05-02


### Added

-   Added the *antlr* example with an [ANTLR]-to-**Grako** grammar translator.
-   Semantic actions can now be implemented by a delegate.
-   The **Grako** [EBNF] grammar and the bootstrap parser now align, so the grammar can be used to bootstrap **Grako**.
-   Proved that grammar models can be pickled, unpickled, and reused.
-   Reset synthetic method count and use decorators to increase readability of generated parsers.


### Changed

-   The bootstrap parser was refactored to use semantic delegates.
-   Changed the licensing to simplified [BSD].


### Fixed

-   Sometimes the [AST] for a closure (`{}`) was not a list.


## [1.3.0] @ 2013-04-11


### Added
-   Optimization: Remove the memoization information that a *cut* makes obsolete (thanks to Kota Mizushima).
-   Report all the rules missing in a grammar before aborting.


### Changed

-   Make sure that *cut* actually applies to the nearest fork.
-   Finish aligning model parsing with generated code parsing.
-   Align the sample *etc/grako.ebnf* grammar to the language parsed by the bootstrap parser.

### Changed

-   Ensure compatibility with [Python][] 2.7.4 and 3.3.1.
-   Update credits.


## [1.2.1] @ 2013-03-19


### Added

-   Lazy rendering of template fields.
-   Rendering of iterables using a specified separator, indent, and format.
-   Added a cache of compiled regexps to `Buffer`.
-   Basic documentation of the *rendering engine*.
-   Lint using [flake8].


### Changed

-   Optimization of *rendering engine*'s `indent()` and `trim()`.
-   Align bootstrap parser with generated parser framework.
-   Add *cuts* to bootstrap parser so errors are reported closer to their origin.
-   Prettify the sample **Grako** grammar.

### Fixed

-   `FailedCut` exceptions must translate to their nested exception so the reported line and column make sense.
-   Remove or comment-out code for tagged/named rule names (they don't work, and their usefulness is doubtful).
-   Spell-check this document with [Vim spell].

## [1.1.0] @ 2013-02-22

### Changed

-   Improved performance by also memoizing exception results and advancement over whitespace and comments.
-   Improved consistency between the way generated parsers and models parse.
-   Added a table of contents to this *README*.
-   Document `parseinfo` and default it to *False*.
-   Mention the use of *context managers*.

### Fixed

-   Need to preserve state when closure iterations match partially.
-   Work with Unicode while rendering.

## [1.0.0] @ 2013-02-09

-   First public release.

[ANTLR]: http://www.antlr.org
[AST]: http://en.wikipedia.org/wiki/Abstract_syntax_tree
[ASTs]: http://en.wikipedia.org/wiki/Abstract_syntax_tree
[Abstract Syntax Tree]: http://en.wikipedia.org/wiki/Abstract_syntax_tree
[BSD]: http://en.wikipedia.org/wiki/BSD_licenses
[COBOL]: http://en.wikipedia.org/wiki/Cobol
[CST]:  http://en.wikipedia.org/wiki/Concrete_syntax_tree
[Cyclomatic complexity]: http://en.wikipedia.org/wiki/Cyclomatic_complexity
[Cython]: http://cython.org/
[EBNF]: http://en.wikipedia.org/wiki/Ebnf
[Franz\_G]: https://bitbucket.org/Franz_G
[JSON]: http://www.json.org/
[Java]:  http://en.wikipedia.org/wiki/Java_(programming_language)
[KLOC]: http://en.wikipedia.org/wiki/KLOC
[NATURAL]: http://en.wikipedia.org/wiki/NATURAL
[PEG]: http://en.wikipedia.org/wiki/Parsing_expression_grammar
[Packrat]: http://bford.info/packrat/
[Perl]: http://www.perl.org/
[POSIX]: https://en.wikipedia.org/wiki/POSIX
[PyPy]: http://pypy.org/
[Python]: http://python.org
[Ruby]: http://www.ruby-lang.org/
[Sublime Text]: https://www.sublimetext.com
[Travis CI]: https://travis-ci.org
[VB6]: http://en.wikipedia.org/wiki/Visual_basic_6
[Vim spell]: http://vimdoc.sourceforge.net/htmldoc/spell.html
[Visitor Pattern]: http://en.wikipedia.org/wiki/Visitor_pattern
[Warth et al]: http://www.vpri.org/pdf/tr2007002_packrat.pdf
[YAML]: https://en.wikipedia.org/wiki/YAML
[colorama]: https://pypi.python.org/pypi/colorama/
[commit log]: https://bitbucket.org/apalala/grako/commits/
[context managers]: http://docs.python.org/2/library/contextlib.html
[email]: mailto:apalala@gmail.com
[flake8]: https://pypi.python.org/pypi/flake8
[keywords]: https://en.wikipedia.org/wiki/Reserved_word
[legacy code]: http://en.wikipedia.org/wiki/Legacy_code
[legacy]: http://en.wikipedia.org/wiki/Legacy_code
[memoizing]: http://en.wikipedia.org/wiki/Memoization
[pull request]: https://bitbucket.org/apalala/grako/pull-request/13/
[pygraphviz]: https://pypi.python.org/pypi/pygraphviz
[re]: https://docs.python.org/3.4/library/re.html
[regex]: https://pypi.python.org/pypi/regex
[tox]: https://testrun.org/tox/latest/

[Sargent]: https://bitbucket.org/PaulS/
[Speer]: https://bitbucket.org/r_speer
[basel-shishani]: https://bitbucket.org/basel-shishani
[drothlis]: https://bitbucket.org/drothlis/
[franz_g]: https://bitbucket.org/Franz_G
[gapag]: https://bitbucket.org/gapag/
[gegenschall]: https://bitbucket.org/gegenschall/
[gkimbar]: https://bitbucket.org/gkimbar/
[jimon]: https://bitbucket.org/jimon/
[lambdafu]: http://blog.marcus-brinkmann.de/
[linkdd]: https://bitbucket.org/linkdd/
[marcus]: http://blog.marcus-brinkmann.de/
[nehz]: https://bitbucket.org/nehz/grako
[neumond]: https://bitbucket.org/neumond/
[pauls]: https://bitbucket.org/PaulS/
[pgebhard]: https://github.com/pgebhard?tab=repositories
[r_speer]: https://bitbucket.org/r_speer
[siemer]: https://bitbucket.org/siemer/
[starkat]: https://bitbucket.org/starkat
[vmuriart]: https://bitbucket.org/vmuriart/

[22]: https://bitbucket.org/apalala/grako/issue/22
[23]: https://bitbucket.org/apalala/grako/issue/23
[24]: https://bitbucket.org/apalala/grako/issue/24
[30]: https://bitbucket.org/apalala/grako/issue/30/
[33]: https://bitbucket.org/apalala/grako/issue/33/
[36]: https://bitbucket.org/apalala/grako/issue/36
[37]: https://bitbucket.org/apalala/grako/issue/37/
[38]: https://bitbucket.org/apalala/grako/issue/38/
[40]: https://bitbucket.org/apalala/grako/issue/40/
[42]: https://bitbucket.org/apalala/grako/issue/42
[45]: https://bitbucket.org/apalala/grako/issue/45
[46]: https://bitbucket.org/apalala/grako/issue/46
[47]: https://bitbucket.org/apalala/grako/issue/47
[48]: https://bitbucket.org/apalala/grako/issue/48
[52]: https://bitbucket.org/apalala/grako/issue/52
[56]: https://bitbucket.org/apalala/grako/issues/56/
[57]: https://bitbucket.org/apalala/grako/issue/57
[58]: https://bitbucket.org/apalala/grako/issues/58/
[59]: https://bitbucket.org/apalala/grako/issues/59/
[60]: https://bitbucket.org/apalala/grako/issues/60/
[73]: https://bitbucket.org/apalala/grako/issue/73
[74]: https://bitbucket.org/apalala/grako/issue/74
[77]: https://bitbucket.org/apalala/grako/issue/77
[81]: https://bitbucket.org/apalala/grako/issue/81

[X.Y.Z]: https://bitbucket.org/apalala/grako/branches/compare/default%0D3.16.1
[3.16.1]: https://bitbucket.org/apalala/grako/branches/compare/3.16.1%0D3.16.0
[3.16.0]: https://bitbucket.org/apalala/grako/branches/compare/3.16.0%0D3.15.1
[3.15.1]: https://bitbucket.org/apalala/grako/branches/compare/3.15.1%0D3.14.0
[3.14.0]: https://bitbucket.org/apalala/grako/branches/compare/3.14.0%0D3.13.0
[3.13.0]: https://bitbucket.org/apalala/grako/branches/compare/3.13.0%0D3.12.1
[3.12.1]: https://bitbucket.org/apalala/grako/branches/compare/3.12.1%0D3.11.0
[3.11.0]: https://bitbucket.org/apalala/grako/branches/compare/3.11.0%0D3.10.1
[3.10.1]: https://bitbucket.org/apalala/grako/branches/compare/3.10.1%0D3.9.3
[3.9.3]: https://bitbucket.org/apalala/grako/branches/compare/3.9.3%0D3.8.2
[3.8.2]: https://bitbucket.org/apalala/grako/branches/compare/3.8.2%0D3.7.0
[3.7.0]: https://bitbucket.org/apalala/grako/branches/compare/3.7.0%0D3.6.7
[3.6.7]: https://bitbucket.org/apalala/grako/branches/compare/3.6.7%0D3.5.1
[3.5.1]: https://bitbucket.org/apalala/grako/branches/compare/3.5.1%0D3.4.3
[3.4.3]: https://bitbucket.org/apalala/grako/branches/compare/3.4.3%0D3.3.0
[3.3.0]: https://bitbucket.org/apalala/grako/branches/compare/3.3.0%0D3.2.1
[3.2.1]: https://bitbucket.org/apalala/grako/branches/compare/3.2.1%0D3.1.2
[3.1.2]: https://bitbucket.org/apalala/grako/branches/compare/3.1.2%0D3.0.4
[3.0.4]: https://bitbucket.org/apalala/grako/branches/compare/3.0.4%0D2.4.3
[2.4.3]: https://bitbucket.org/apalala/grako/branches/compare/2.4.3%0D2.3.0
[2.3.0]: https://bitbucket.org/apalala/grako/branches/compare/2.3.0%0D2.2.1
[2.2.2]: https://bitbucket.org/apalala/grako/branches/compare/2.2.2%0D2.1.0
[2.1.0]: https://bitbucket.org/apalala/grako/branches/compare/2.1.0%0D2.0.4
[2.0.4]: https://bitbucket.org/apalala/grako/branches/compare/2.0.4%0D1.4.0
[1.4.0]: https://bitbucket.org/apalala/grako/branches/compare/1.4.0%0D1.3.0
[1.3.0]: https://bitbucket.org/apalala/grako/branches/compare/1.3.0%0D1.2.1
[1.2.1]: https://bitbucket.org/apalala/grako/branches/compare/1.2.1%0D1.1.0
[1.1.0]: https://bitbucket.org/apalala/grako/branches/compare/1.1.0%0D1.0.0
[1.0.0]: https://bitbucket.org/apalala/grako/commits/tag/1.0.0
