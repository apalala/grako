# Change Log

**Grako** uses [Semantic Versioning] for its releases, so parts of the version number may increase without any significant changes or backwards incompatibilities in the software.

[Semantic Versioning]: http://semver.org/


The format of this *Change Log* is inspired by [Keep a CHANGELOG]

[Keep a CHANGELOG]: http://keepachangelog.com/

## [3.12.1]

### Added

-   Also generate a `buffering.Buffer` descendant specific to the grammar for parsers that need to customize the `parsing.Parser.parse()` method.

-   Added the `grako.synth` module which makes synthetic `grako.model.Node` classes pickable.

-   Now patterns may be concatenated to split a complex pattern into parts, possibly accross several lines: `/regexp/ + /regexp/`.

-   Added basic support for symbol tables in `grako.symtables`.

-   Syntax file for [Sublime Text] [vmuriart]


### Changed

-   Distinguish between positive and normal joins: `s.{e}+` and `s.{e}`.  Having `s.{e}` use a positive closure was too unexpected.

-   Traded memory for simplicity and replaced the line-based line cache in `buffering.Buffer` for a position-based cache. Buffering needs to continue being `str`-based for complex `re` patterns to work as expected.

-   Now `model.ParseModel` is an alias for `model.Node`.

-   Improved `examples/antlr2grako` so it generates more usable **Grako** grammars.

### Fixed

-   The latest changes to `grako.util.trim()` were incomplete.
-   Fixed several inconsistencies in the implementation and use of `buffering.Buffer` line indexing.
-   Repeated parameters to object model constructors.

## [3.10.1]

-   *BUG!* `grako.model.Node._adopt_children()` was incorrect, so
    `Node.parent` was not being set. Adopted a simple-approach solution
    based on suggestions by linkdd\_.
-   *BUG!* Avoid recovering the same comment against the same line in
    `grako.buffering.Buffer`.
-   *BUG!* Recovering comments and end-of-line comments together
    was incorrect.
-   *BUG!* `model.Node` parenting still broken. Fixed!
-   [73] The `--draw` option did not recognize the new object model node
    types `Join` and `Constant`. Now `--draw` works with Python\_ 3.x
    using pygraphviz\_ 1.3.1.
-   [77][] [81] Advance over whitespace before memoization or
    left recursion.
-   Enhancements to `grako.tool` and the command-line help (siemer\_).
-   Unlink output file before attempting parser generation.
-   A `-G FILE` command-line option forces saving of the object model.
-   The function `grako.util.trim()` now also considers the first
    text ine.
-   Tested with Python\_ 3.6.0a3.

## [3.9.3]

-   *BUG!* Fixes and improvements to generation of child sets and list
    in `model.Node` (gapag\_).
-   *BUG!* `@@keyword` not working correctly with `@@ignorecase`.
-   *BUG!* Fix for `@@keyword` and `@name` by moving check for
    `FailedSemantics` upper in the parsing chain.
-   Several simplifications and refactorings by siemer\_.
-   *BUG!* Several important bug fixes to the object model
    generator (neumond\_)
-   Simplified the regular expression for floats in the **Grako**
    grammar (siemer\_)
-   Set all [flake8] options in `tox.ini` (siemer\_).
-   Simplfied `__str__()` for directives (siemer\_).
-   Added the `@@namechars` directive to allow specifying additional
    characters that may be part of tokens considerd names by
    `@@nameguard :: True`.
-   Now a choice expression may start with a leading `'|'`.
-   Guard against recursive structures in `grako.util.asjson()`.
-   Added `@@grammar` directive to grammars as to avoid having to pass a
    `-m NAME` through the command line.
-   Now `STARTRULE` defaults to `start` in generated parsers.
-   Now the AST\_ for a `grako.model.Node` is saved as `Node.ast`.
-   The `--object-model` command-line option will generate a python
    module with definitions for the class names specified as rule
    parameters (untested).
-   Removed outdated information from the *README*.
-   *BUG!* Both `grako.grammars` and `grako.codegen.python` were
    manipulating the names defined in a grammar rule.
-   Cleaned up the grammar in `examples/python`; still untested.
-   [74] `grako.model.Node.children()` returned an empty list even when
    traversing attributes that with names starting in `'_'`.
-   [57] Still bugs in handling of `@@whitespace` in the generated
    parser's (gkimbar\_).

## [3.8.2]

-   [73] Keywords were not being passed to the base class of the
    generated parser.
-   Wrong version number (RC) in this document.
-   Added grammar support for keywords\_ in the source language through
    the `@@keyword::` directive and the `@name` decorator for rules.
-   Make `ModelBuilderSemantics` support built-in types.

## [3.7.0]

-   Added suport for `` `constant ``\` expressions which don't consume
    any input yet return the specified constant.
-   Now an empty closure (`{}`) consumes no input and generates an empty
    list as AST\_.
-   Removed the `--binary` command-line option. It went unused, it was
    untested, and it was incorrectly implemented.
-   Generated parsers `pass` on `KeyboardInterrupt`.
-   Moved the bulk of the entry code for generated parsers to
    `util.generic_main()`. This allows for the verbose code to be
    verified by the usual tools.
-   Deprecate `{e}*` and `{e}-` by removing them from the documentation.
-   Added the Python\_-inspired *join* operator, `s.{e}`, as a
    convenient syntax for parsing sequences with separators.

## [3.6.7]

-   Several minor **bug** fixes. See the [commit log] for details.
-   **BUG** Detect and fail promptly on empty tokens in grammars.
-   More reasonable treatment for ANTLR\_ `token` definitions in the
    `antlr2grako` example.
-   All tests pass with Python\_ 3.5.
-   [59] Python\_ keywords can now actually be used as rule names in
    grammars (drothlis\_).
-   [60] `@@` directives were not pressent in the output of the
    `--pretty` option.
-   [58] The parameters to the constructor of generated parsers were
    being ignored (pgebhard).
-   **BUG** `grammars.py` would call `ctx.error()` instead of
    `ctx._error()` on failed rule references.
-   Overall cleanup of the code and of the development requirements.
-   [56] Using @@whitespace generated invalid python programs
-   The `@@whitespace` directive was not working for regular
    expressions (nehz\_).
-   BUG: Left recursion in the grammar was checked for in the wrong
    place when disabled.
-   Added basic support for output of an AST\_ in [YAML] format.
-   Added `@@whitespace` directive to specify whitespace regular
    expression within the grammar (starkat\_).
-   Added `@@nameguard` and `@@ignorecase` directives to toggle the
    respective boolean parameters within the grammar (starkat\_).
-   [52] Build with Cython failed on Windows.
-   Applied [flake8] suggestions.
-   Upgraded development libraries to their latest versions (see
    `requirements.txt`).

## [3.5.1]

-   [45] The `grako` tool now produces basic statistics about the
    processed grammar.
-   [46] Left recursion support can be turned off using the
    `left_recursion=` parameter to parser constructors.
-   [47] New `@@comments` and `@@eol_comments` can be used within a
    grammar to specify the respective regular expressions.
-   [48] Rules can now be overriden/redefined using the
    `@override` decorator.
-   Added backwards compatibility with `Buffer.whitespace`.
-   Added `AST.asjson()` to not have to import `grako.util.asjson()` for
    the same purpose.

## [3.4.3]

-   Minor improvements to `buffering.Buffer`.
-   *BUG* [42] `setup.py` might give errors under some locales because
    of the non-ASCII characters in `README.rst`.
-   Added a `--no-nameguard` command-line option to generated parsers.
-   Allow *Buffer* descendants to customize how text is split into
    lines (starkat\_).
-   Now the `re.UNICODE` flag is consistently used in pattern, comment,
    and whitespace matching. A re\_ regular expression is now accepted
    for whitespace matching. Character sets provided as `str`, `list`,
    or `set` are converted to the corresponding regular
    expression (starkat\_).
-   If installed, the regex\_ module will be used instead of re\_ in all
    pattern matching (starkat\_). See the section about
    *whitespace* above.
-   Added a `--version` option to the commandline tool. A
    `grako.__version__` variable is now available.

## [3.3.0]

-   Refactorings to enhance consistency in parsing between models and
    and generated parsers.
-   [37] Block comments are preserved when using the `--pretty` option.
-   [38] Trace output uses color if the [colorama] package is installed.
    Also, the vertical size of trace logs was reduced to three lines
    per entry.
-   [40] The widtn and the separator used in parse traces are now
    configurable with keyword arguments.

## [3.2.1]

-   Now rule parameters and `model.ModelBuilderSemantics` are used to
    produce grammar models with a minimal set of semantic methods.
-   Code generation is now separtate from the grammar model, so
    translation targets differen from Python\_ are easier to implement.
-   Removed attribute assignment to the underlying `dict` in `AST`. It
    was the source of obscure bugs for **Grako** users.
-   Now an `eol_comments_re=` parameter can be passed to `Parser` and
    `Buffer`.
-   *BUG* Need to allow newline (`\n`) characters within
    grammar patterns.
-   *BUG* [36] Keyword arguments in rules were not being parsed
    correctly ([Franz\_G]).
-   Several *BUGs* in the advanced features were fixed. See the
    [Bitbucket commits][commit log] for details.

## [3.1.2]

-   **Grako** now supports direct and indirect left recursion thanks to
    the implementation done by Paul Sargent\_ of the work
    by Warth et al\_. Performance for non-left-recursive grammars
    is unaffected.
-   The old grammar syntax is now supported with deprecation warnings.
    Use the `--pretty` option to upgrade a grammar.
-   If there are no slashes in a pattern, they can now be specified
    without the opening and closing question marks.
-   *BUG* [33] Closures were sometimes being treated as plain lists, and
    that produced inconsistent results for named elements (lambdafu\_).
-   *BUG* The bootstrap parser contained errors due to the previous bug
    in `util.ustr()`.
-   *BUG* [30] Make sure that escapes in `--whitespace` are evaluated
    before being passed to the model.
-   *BUG* [30] Make sure that `--whitespace` and `--no-nameguard` indeed
    affect the behavior of the generated parser as expected.

## [3.0.4]

-   The bump in the major version number is because the grammar syntax
    changed to accomodate new features better, and to remove sources of
    ambituity and hard-to-find bugs. The naming changes in some of the
    advanced features (*Walker*) should impact only complex projects.
-   The *cut* operator is now `~`, the tilde.
-   Now name overrides must always be specified with a colon, `@:e`.
-   Grammar rules may declare Python\_-style arguments that get passed
    to their corresponding semantic methods.
-   Grammar rules may now *inherit* the contents of other rules using
    the `<` operator.
-   The *right hand side* of a rule may be included in another rule
    using the `>` operator.
-   Grammars may include other files using the `#include ::` directive.
-   Multiple definitions of grammar rules with the same name are
    now disallowed. They created ambiguity with new features such as
    rule parameters, based rules, and rule inclusion, and they were an
    opportunity for hard-to-find bugs (*import this*).
-   Added a `--pretty` option to the command-line tool, and refactored
    pretty-printing (`__str__()` in grammar models) enough to make its
    output a norm for grammar format.
-   Internals and examples were upgraded to use the latest
    **Grako** features.
-   Parsing exceptions will now show the sequence of rule invocations
    that led to the failure.
-   Renamed `Traverser` and `traverse` to `Walker` and `walk`.
-   Now the keys in `grako.ast.AST` are ordered like in
    `collections.OrderedDict`.
-   **Grako** models are now more [JSON]-friendly with the help of
    `grako.ast.AST.__json__()`, `grako.model.Node.__json__()` and
    `grako.util.asjon()`.
-   Added compatibility with [Cython].
-   Removed checking for compatibility with Python\_ 3.3 (use
    3.4 instead).
-   Incorporated Robert Speer\_'s solution to honoring escape sequences
    without messing up the encoding.
-   *BUG* Honor simple escape sequences in tokens while trying not to
    corrupt unicode input. Projects using non-ASCII characters in
    grammars should prefer to use unicode character literals instead of
    Python\_ `\x` or `\o` escape sequences. There is no standard/stable
    way to unscape a Python\_ string with escaped escape sequences.
    Unicode is broken in Python\_ 2.x.
-   *BUG* The `--list` option was not working in Python\_ 3.4.1.
-   *BUG* [22] Always exit with non-zero exit code on failure.
-   *BUG* [23] Incorrect encoding of Python\_ escape sequences in
    grammar tokens.
-   *BUG* [24] Incorrect template for *--pretty* of
    multi-line optionals.

## [2.4.3]

-   Changes to allow downstream translators to have different target
    languages with as little code replication as possible. There's new
    functionality pulled from downstream in `grako.model` and
    `grako.rendering`. `grako.model` is now a module instead of
    a package.
-   The [Visitor Pattern] doesn't make much sense in a dynamically typed
    language, so the functionality was replaced by more flexible
    `Traverser` classes. The new `_traverse_XX()` methods in Traverser
    classes carry a leading underscore to remind that they shouldn't be
    used outside of the protocol.
-   Now a `_default()` method is called in the semantics delegate when
    no specific method is found. This allows, for example, generating
    meaningful errors when something in the semantics is missing.
-   Added compatibility with [tox]. Now tests are performed against the
    latest releases of Python\_ 2.7.x and 3.x, and PyPy\_ 2.x.
-   Added `--whitespace` parameter to generated `main()`.
-   Applied [flake8] to project and to generated parsers.

## [2.3.0]

-   Now the `@` operator behaves as a special case of the `name:`
    operator, allowing for simplification of the grammar, parser,
    semantics, and **Grako** grammars. It also allows for expressions
    such as `@+:e`, with the expected semantics.
-   *Refactoring* The functionality that was almost identical in
    generated parsers and in models was refactored into `Context`.
-   *BUG!* Improve consistency of use Unicode between Python\_ 2.7
    and 3.x.
-   *BUG!* Compatibility between Python\_ 2.7/3.x print() statements.

## [2.2.2]

-   Optionally, do not memoize during positive or negative lookaheads.
    This allows lookaheads to fail semantically without committing to
    the fail.
-   Fixed the implementation of the *optional* operator so the
    AST\_/CST\_ generated when the *optional* succeeds is exactly the
    same as if the expression had been mandatory.
-   Grouping expressions no longer produce a list as CST\_.
-   *BUG*! Again, make sure closures always return a list.
-   Added infrastructure for stateful rules (lambdafu\_, see the [pull
    request] ).
-   Again, protect the names of methods for rules with a leading and
    trailing underscore. It's the only way to avoid unexpected
    name clashes.
-   The bootstrap parser is now the one generated by **Grako** from the
    bootstrap grammar.
-   Several minor bug fixes (lambdafu\_).
-   *BUG!* The choice operator must restore context even when some of
    the choices match partially and then fail.
-   *BUG!* `Grammar.parse()` needs to initialize the AST\_ stack.
-   *BUG!* `AST.copy()` was too shallow, so an AST\_ could be modified
    by a closure iteration that matched partially and eventually failed.
    Now `AST.copy()` clones AST\_ values of type `list` to avoid
    that situation.
-   *BUG!* A failed `cut` must trickle up the rule-call hierarchy so
    parsing errors are reported as close to their source as possible.

## [2.0.4]

-   **Grako** no longer assumes that parsers implement the semantics. A
    separate semantics implementation must be provided. This allows for
    less polluted namespaces and smaller classes.
-   A `last_node` protocol allowed the removal of all mentions of
    variable `_e` from generated parsers, which are thus more readable.
-   Refactored *closures* to be more pythonic (there are **no**
    anonymous blocks in Python\_!).
-   Fixes to the *antlr2grako* example to let it convert over 6000 lines
    of an ANTLR\_ grammar to **Grako**.
-   Improved rendering of grammars by grammar models.
-   Now *tokens* accept Python\_ escape sequences.
-   Added a simple [Visitor Pattern] for `Renderer` nodes. Used it to
    implement diagramming.
-   Create a basic diagram of a grammar if pygraphviz\_ is available.
    Added the `--draw` option to the command-line tool.
-   *BUG!* Trace information off by one character (thanks
    to lambdafu\_).
-   *BUG!* The AST\_ for a closure might fold repeated symbols (thanks
    to lambdafu\_).
-   *BUG!* It was not possible to pass buffering parameters such as
    `whitespace` to the parser's constructor (thanks to lambdafu\_).
-   Added command-line and parser options to specify the buffering
    treatment of `whitespace` and `nameguard` (lambdafu\_).
-   Several improvements and bug fixes (mostly by lambdafu\_).

## [1.4.0]

-   *BUG!* Sometimes the AST\_ for a closure (`{}`) was not a list.
-   Semantic actions can now be implemented by a delegate.
-   Reset synthetic method count and use decorators to increase
    readability of generated parsers.
-   The **Grako** EBNF\_ grammar and the bootstrap parser now align, so
    the grammar can be used to bootstrap **Grako**.
-   The bootstrap parser was refactored to use semantic delegates.
-   Proved that grammar models can be pickled, unpickled, and reused.
-   Added the *antlr* example with an ANTLR\_-to-**Grako**
    grammar translator.
-   Changed the licensing to simplified BSD\_.

## [1.3.0]

-   *Important memory optimization!* Remove the memoization information
    that a *cut* makes obsolete (thanks to Kota Mizushima).
-   Make sure that *cut* actually applies to the nearest fork.
-   Finish aligning model parsing with generated code parsing.
-   Report all the rules missing in a grammar before aborting.
-   Align the sample *etc/grako.ebnf* grammar to the language parsed by
    the bootstrap parser.
-   Ensure compatibility with Python\_ 2.7.4 and 3.3.1.
-   Update credits.

## [1.2.1]

-   Lazy rendering of template fields.
-   Optimization of *rendering engine*'s `indent()` and `trim()`.
-   Rendering of iterables using a specified separator, indent,
    and format.
-   Basic documentation of the *rendering engine*.
-   Added a cache of compiled regexps to `Buffer`.
-   Align bootstrap parser with generated parser framework.
-   Add *cuts* to bootstrap parser so errors are reported closer to
    their origin.
-   *(minor) BUG!* `FailedCut` exceptions must translate to their nested
    exception so the reported line and column make sense.
-   Prettify the sample **Grako** grammar.
-   Remove or comment-out code for tagged/named rule names (they don't
    work, and their usefulness is doubtful).
-   Spell-check this document with [Vim spell].
-   Lint using [flake8].

## [1.1.0]

-   *BUG!* Need to preserve state when closure iterations
    match partially.
-   Improved performance by also memoizing exception results and
    advancement over whitespace and comments.
-   Work with Unicode while rendering.
-   Improved consistency between the way generated parsers and
    models parse.
-   Added a table of contents to this *README*.
-   Document `parseinfo` and default it to *False*.
-   Mention the use of *context managers*.

## [1.0.0]

-   First public release.

[Cython]: http://cython.org/
[Franz\_G]: https://bitbucket.org/Franz_G
[JSON]: http://www.json.org/
[Sublime Text]: https://www.sublimetext.com
[Vim spell]: http://vimdoc.sourceforge.net/htmldoc/spell.html
[Visitor Pattern]: http://en.wikipedia.org/wiki/Visitor_pattern
[YAML]: https://en.wikipedia.org/wiki/YAML
[colorama]: https://pypi.python.org/pypi/colorama/
[commit log]: https://bitbucket.org/apalala/grako/commits/
[flake8]: https://pypi.python.org/pypi/flake8
[pull request]: https://bitbucket.org/apalala/grako/pull-request/13/
[tox]: https://testrun.org/tox/latest/

[franz\_g]: https://bitbucket.org/Franz_G
[marcus]: http://blog.marcus-brinkmann.de/
[pauls]: https://bitbucket.org/PaulS/
[basel-shishani]: https://bitbucket.org/basel-shishani
[drothlis]: https://bitbucket.org/drothlis/
[gapag]: https://bitbucket.org/gapag/
[gkimbar]: https://bitbucket.org/gkimbar/
[jimon]: https://bitbucket.org/jimon/
[linkdd]: https://bitbucket.org/linkdd/
[nehz]: https://bitbucket.org/nehz/grako
[neumond]: https://bitbucket.org/neumond/
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
