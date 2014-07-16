" Vim syntax file
" Language:         EBNF
" Maintainer:       Hans Fugal
" Last Change:      $Date: 2003/01/28 14:42:09 $
" Version:          $Id: ebnf.vim,v 1.1 2003/01/28 14:42:09 fugalh Exp $
" With thanks to Michael Brailsford for the BNF syntax file.

" Quit when a syntax file was already loaded
if version < 600
  syntax clear
elseif exists("b:current_syntax")
  finish
endif

syn match ebnfInclude />[A-Za-z0-9_-]\+/  skipwhite skipempty
syn match ebnfMetaIdentifier /[A-Za-z0-9_-]\+/ skipwhite skipempty nextgroup=ebnfSeparator
syn match ebnfName /@:\|@+:\|@\|[A-Za-z0-9_-]\+:/ skipwhite skipempty

syn match ebnfParamsStart "::" nextgroup=ebnfParams skipwhite skipempty
syn match ebnfParams /[A-Za-z0-9_-]\+/ contained skipwhite skipempty nextgroup=ebnfSeparator

syn match ebnfSeparator "=" contained nextgroup=ebnfProduction skipwhite skipempty
syn region ebnfProduction start=/\zs[^\.;]/ end=/[\.;]/me=e-1 contained contains=ebnfSpecial,ebnfDelimiter,ebnfTerminal,ebnfSpecialSequence,ebnfPattern,ebnfComment,ebnfName,ebnfInclude nextgroup=ebnfEndProduction skipwhite skipempty
syn match ebnfDelimiter #[\-\*]\|>>\|[&~,(|)\]}\[{!]\|\(\*)\)\|\((\*\)\|\(:)\)\|\((:\)# contained
syn match ebnfSpecial /[\*+]/ contained
syn region ebnfPattern matchgroup=Delimiter start=/\// end=/\// contained
syn region ebnfSpecialSequence matchgroup=Delimiter start=/?/ end=/?/ contained
syn match ebnfEndProduction /[\.;]/ contained
syn region ebnfTerminal matchgroup=delimiter start=/"/ end=/"/ contained
syn region ebnfTerminal matchgroup=delimiter start=/'/ end=/'/ contained

syn region ebnfComment start="(\*" end="\*)" contains=ebnfTodo
syn keyword ebnfTodo		FIXME NOTE NOTES TODO XXX contained


hi link ebnfComment Comment
hi link ebnfMetaIdentifier Identifier
hi link ebnfSeparator ebnfDelimiter
hi link ebnfEndProduction ebnfDelimiter
hi link ebnfDelimiter Delimiter
hi link ebnfDelimiter Delimiter
hi link ebnfSpecial Keyword
hi link ebnfSpecialSequence Statement
hi link ebnfPattern Statement
hi link ebnfTerminal String
hi link ebnfName Keyword
hi link ebnfInclude Include
hi link ebnfParamsStart ebnfParams
hi link ebnfParams Type
hi link ebnfTodo Todo
