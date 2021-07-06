vim9script noclear

def snippets#getAutoloadFuncname(): string #{{{1
    return expand('%:p') =~ 'autoload\|plugin'
        ?     expand('%:p')
            ->matchstr('\%(autoload\|plugin\)/\zs.*\ze.vim')
            ->substitute('/', '#', 'g') .. '#'
        :     ''
enddef

def snippets#getLgTagNumber(): string #{{{1
    var lines: list<string> = getline(1, line('.') - 1)
        ->reverse()
        ->filter((_, v: string): bool => v =~ '^\s*\*lg-lib-\%(\d\+\)\*\s*$')
    return empty(lines)
        ?     ''
        :     lines[0]->matchstr('^\s*\*lg-lib-\zs\d\+\ze\*\s*$')
enddef

def snippets#getPluginNameInGuard(): string #{{{1
# Purpose:
# Try to guess the  name of the global variable used (as a  guard) by the plugin
# we're currently customizing in `~/.vim/plugin/foo.vim`.
    return getcompletion('g:loaded_*', 'var')
        ->filter((_, v: string): bool => v =~ expand('%:t:r'))
        ->get(0, '')
        ->matchstr('g:loaded_\zs.*')
enddef

def snippets#getPluginNameInRtp(): string #{{{1
# Purpose:
# Try to  guess the name of  plugin name in the runtimepath.
    return split(&runtimepath, ',')
        ->filter((_, v: string): bool => v =~ expand('%:t:r'))
        ->get(0, '')
        ->fnamemodify(':t')
enddef

def snippets#removeTabsInGlobalBlocks() #{{{1
    var pos: list<number> = getcurpos()
    var start: string = ':1/^\Cglobal !p$/'
    var end: string = '/^\Cendglobal$/'
    # Don't replace `4` with `&l:shiftwidth`.
    # Python expects you indent your code with exactly 4 spaces.
    Rep = (m: list<string>): string => repeat(' ', m[0]->strcharlen() * 4)
    var substitution: string = 'substitute/^\t\+/\=Rep()/'
    execute 'silent! keepjumps keeppatterns '
        .. start .. ';' .. end .. 'global/^/' .. substitution
    setpos('.', pos)
enddef

var Rep: func

def snippets#undoFtplugin() #{{{1
    set expandtab<
    set iskeyword<
    set shiftwidth<
    set tabstop<
    autocmd! FormatSnippets * <buffer>
    nunmap <buffer> q
enddef

