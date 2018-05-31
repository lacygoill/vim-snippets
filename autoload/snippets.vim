fu! snippets#get_autoload_funcname() abort "{{{1
    return expand('%:p') =~# 'autoload\|plugin'
       \ ?     substitute(matchstr(expand('%:p'), '\%(autoload\|plugin\)/\zs.*\ze.vim'), '/', '#', 'g').'#'
       \ :     ''
endfu

fu! snippets#get_lg_tag_number() abort "{{{1
    let lines = reverse(getline(1, line('.')-1))
    call filter(lines, {i,v -> v =~# '^\s*\*lg-lib-\%(\d\+\)\*\s*$'})
    return empty(lines)
       \ ?     ''
       \ :     matchstr(lines[0], '^\s*\*lg-lib-\zs\d\+\ze\*\s*$')
endfu

fu! snippets#get_plugin_name() abort "{{{1
    let plugin_name = getcompletion('g:loaded_*', 'var')
    let plugin_name = filter(plugin_name, {i,v -> v =~# expand('%:t:r')})
    let plugin_name = get(plugin_name, 0, '')
    let plugin_name = matchstr(plugin_name, 'g:loaded_\zs.*')
    return plugin_name
endfu

fu! snippets#remove_tabs_in_global_blocks() abort "{{{1
    let pos = getcurpos()
    let start = '1/^\Cglobal !p$/'
    let end = '/^\Cendglobal$/'
    let substitution = 's/^\t\+/\=repeat(" ", len(submatch(0)) * 4)/'
    "                                                            │
    " Don't replace `4` with `&l:sw`.{{{
    " Python expects you indent your code with exactly 4 spaces.
    "}}}
    sil! exe 'keepj keepp '.start.';'.end.'g/^/'.substitution
    call setpos('.', pos)
endfu

