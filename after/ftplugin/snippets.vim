" Autocmds {{{1

augroup format_snippets
    au! * <buffer>
    " What does it do?{{{
    " In a snippet file, we reset `'expandtab'`:
    "
    " We do this because:
    "
    "         1. Tabs  have a  special  meaning  for UltiSnips  (“increase  the level
    "            of indentation of the line“)
    "
    "         2. we sometimes  forget to  insert a  Tab inside  a snippet  when it's
    "            needed
    "
    " So whenever you press `Tab` to increase  the indentation of a line, you insert a
    " literal `Tab` character.
    " This is what  we want in a  snippet (snippet...endsnippet), but not  in a python
    " function (global...endglobal), because python expects 4 spaces.
    "
    " To fix this, we execute `:RemoveTabs` on the global block.
    "}}}
    au BufWritePost <buffer> call snippets#remove_tabs_in_global_blocks()
augroup END

" Mappings {{{1

nno  <buffer><nowait><silent>  q  :<c-u>call lg#window#quit()<cr>

" Options "{{{1

setl isk+=#

" We want real tabs  in a snippet file, because they have  a special meaning for
" UltiSnips (“increase the level of indentation of the line“).
setl noet sw=4 ts=4
"         └───────┤
"                 └ alternative: let &l:ts = &l:sw

augroup my_snippets
    au! *            <buffer>
    au  BufWinEnter  <buffer>  setl fdm=marker
                          \ |  setl fdt=fold#text()
                          \ |  setl cocu=nc
                          \ |  setl cole=3
augroup END

" Teardown {{{1

let b:undo_ftplugin =         get(b:, 'undo_ftplugin', '')
                    \ .(empty(get(b:, 'undo_ftplugin', '')) ? '' : '|')
                    \ ."
                    \      setl cocu< cole< et< fdm< fdt< isk< sw< ts<
                    \    | exe 'au!  my_snippets * <buffer>'
                    \    | exe 'au!  format_snippets * <buffer>'
                    \    | exe 'nunmap <buffer> q'
                    \  "

