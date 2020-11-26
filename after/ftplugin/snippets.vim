" Autocmds {{{1

augroup format_snippets
    au! * <buffer>
    " What does it do?{{{
    " In a snippet file, we reset `'expandtab'`:
    "
    " We do this because:
    "
    "   1. Tabs have  a special  meaning for UltiSnips  (“increase the  level of
    "   indentation of the line“)
    "
    "   2. we sometimes forget to insert a Tab inside a snippet when it's needed
    "
    " So whenever  you press `Tab`  to increase the  indentation of a  line, you
    " insert a literal `Tab` character.
    " This is what  we want in a snippet (snippet...endsnippet),  but *not* in a
    " python function (global...endglobal), because:
    "
    "   - PEP8 recommends spaces
    "
    "   - we could easily end up mixing tabs and spaces, when we copy paste some
    "   code, which would raise an error:
    "
    "         IndentationError: unexpected indent
    "
    " To fix this, we execute `:RemoveTabs` on the global block.
    "}}}
    au BufWritePost <buffer> call snippets#remove_tabs_in_global_blocks()
augroup END

" Mappings {{{1

nmap <buffer><nowait> q <plug>(my_quit)

" Options "{{{1

setl isk+=#

" We want real tabs  in a snippet file, because they have  a special meaning for
" UltiSnips (“increase the level of indentation of the line“).
setl noet sw=4 ts=4
"         ├───────┘
"         └ alternative: let &l:ts = &l:sw

" Teardown {{{1

let b:undo_ftplugin = get(b:, 'undo_ftplugin', 'exe')
    \ .. '| call snippets#undo_ftplugin()'

