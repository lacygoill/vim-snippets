vim9script

# How to hide leading spaces which are highlighted (in blue by default)?{{{
#
#     hi! link snipLeadingSpaces Normal
#}}}
# Why should I *not* do it?{{{
#
# Most of our lines should be indented with  tabs, so that when a tab trigger is
# expanded, our  buffer-local options  related to indenting  (like 'shiftwidth')
# are taken into account.
#
# So, we should be informed whenever a  line is indented with spaces, because it
# may mean that we need to replace them with tabs.
#}}}

# TO_DO and FIX_ME are not highlighted if they're directly followed by a colon.{{{
# This is because of:
#
#     syntax iskeyword @,48-57,_,192-255,-,:
#                                          ^
#
# This setting comes from `$VIMRUNTIME/syntax/sh.vim`.
# `~/.vim/pack/minpac/opt/ultisnips/syntax/snippets.vim` loads  the `sh` syntax,
# to correctly highlight a shell interpolation.
#
#     syntax include @Shell syntax/sh.vim
#
# We remove it to join TO_DO and FIX_ME with the colon, like everywhere else.
# BUT: it may break the syntax highlighting inside a shell interpolation.
# I think I value the latter less than the former: I won't use a lot of shell
# interpolation.
#}}}
syntax iskeyword @,48-57,_,192-255,-

