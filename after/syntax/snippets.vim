" don't color in blue a leading space inside a snippet
hi! link snipLeadingSpaces Normal

" TO_DO and FIX_ME are not highlighted if they're directly followed by a colon.{{{
" This is because of:
"
"     syntax iskeyword @,48-57,_,192-255,-,:
"                                          ^
"
" This setting comes from `$VIMRUNTIME/syntax/sh.vim`.
" `~/.vim/plugged/ultisnips/syntax/snippets.vim`  loads  the   `sh`  syntax,  to
" correctly highlight a shell interpolation.
"
"     syntax include @Shell syntax/sh.vim
"
" We remove it to join TO_DO and FIX_ME with the colon, like everywhere else.
" BUT: it may break the syntax highlighting inside a shell interpolation.
" I think I value the latter less than the former: I won't use a lot of shell
" interpolation.
"}}}
syntax iskeyword @,48-57,_,192-255,-

"                                 ┌ get rid of it once we've concealed comment leaders
"                               ┌─┤
syn match snippetsFoldMarkers  /#\?\s*{{{\d*\s*\ze\n/  conceal cchar=❭  containedin=snipComment
syn match snippetsFoldMarkers  /#\?\s*}}}\d*\s*\ze\n/  conceal cchar=❬  containedin=snipComment
