fu snippets#get_autoload_funcname() abort "{{{1
    return expand('%:p') =~# 'autoload\|plugin'
       \ ?     substitute(matchstr(expand('%:p'), '\%(autoload\|plugin\)/\zs.*\ze.vim'), '/', '#', 'g').'#'
       \ :     ''
endfu

fu snippets#get_lg_tag_number() abort "{{{1
    let lines = reverse(getline(1, line('.')-1))
    call filter(lines, {_,v -> v =~# '^\s*\*lg-lib-\%(\d\+\)\*\s*$'})
    return empty(lines)
       \ ?     ''
       \ :     matchstr(lines[0], '^\s*\*lg-lib-\zs\d\+\ze\*\s*$')
endfu

fu snippets#get_plugin_name_in_guard() abort "{{{1
    " Purpose:
    " Try to  guess the name of  the global variable  used (as a guard)  by the
    " plugin we're currently customizing in `~/.vim/after/plugin/foo.vim`.
    let guard_name = getcompletion('g:loaded_*', 'var')
    let guard_name = filter(guard_name, {_,v -> v =~# expand('%:t:r')})
    let guard_name = get(guard_name, 0, '')
    let guard_name = matchstr(guard_name, 'g:loaded_\zs.*')
    return guard_name
endfu

fu snippets#get_plugin_name_in_rtp() abort "{{{1
    " Purpose:
    " Try to  guess the name of  plugin name in the rtp.
    let rtp = split(&rtp, ',')
    let guard_name = filter(rtp, {_,v -> v =~# expand('%:t:r')})
    let guard_name = fnamemodify(get(guard_name, 0, ''), ':h:t')
    return guard_name
endfu

fu snippets#remove_tabs_in_global_blocks() abort "{{{1
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

