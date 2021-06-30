vim9script

# Autocmds {{{1

augroup FormatSnippets
    autocmd! * <buffer>
    # What does it do?{{{
    # In a snippet file, we reset `'expandtab'`:
    #
    # We do this because:
    #
    #   1. Tabs have  a special  meaning for UltiSnips  (“increase the  level of
    #   indentation of the line“)
    #
    #   2. we sometimes forget to insert a Tab inside a snippet when it's needed
    #
    # So whenever  you press `Tab`  to increase the  indentation of a  line, you
    # insert a literal `Tab` character.
    # This is what  we want in a snippet (snippet...endsnippet),  but *not* in a
    # python function (global...endglobal), because:
    #
    #   - PEP8 recommends spaces
    #
    #   - we could easily end up mixing tabs and spaces, when we copy paste some
    #   code, which would raise an error:
    #
    #         IndentationError: unexpected indent
    #
    # To fix this, we execute `:RemoveTabs` on the global block.
    #}}}
    autocmd BufWritePost <buffer> snippets#removeTabsInGlobalBlocks()
augroup END

# Mappings {{{1

nmap <buffer><nowait> q <Plug>(my_quit)

# Options {{{1

setlocal iskeyword+=#

# We want real tabs  in a snippet file, because they have  a special meaning for
# UltiSnips (“increase the level of indentation of the line“).
&l:expandtab = false
&l:shiftwidth = 4
&l:tabstop = &l:shiftwidth

# Teardown {{{1

b:undo_ftplugin = get(b:, 'undo_ftplugin', 'execute')
    .. '| call snippets#undoFtplugin()'

