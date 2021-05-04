# coding=utf-8
# The previous line  allows us to use unicode characters  in comments (like …){{{
# without python raising an exception.
#
# https://stackoverflow.com/a/10589674/9110115
# https://stackoverflow.com/a/729016/9110115
#
# The `-*-` prefix/suffix are not necessary, unless you use Emacs.
#}}}

# We import  the same modules  that UltiSnips  automatically import in  a python
# interpolation.
import os
import random
import re
import string
import vim

# TODO:
# understand all the new functions

# TODO:
# Split this file into several ones, once it becomes too big.
# For the layout, take inspiration from there:
#
# https://github.com/reconquest/vim-pythonx
# https://github.com/reconquest/snippets

def advance_jumper(snip): #{{{1
    return _make_jumper_jump(snip, 'forwards')

def capture_visual_content(snip): #{{{1
    snip.context = {
        'original': snip.context,
        'visual': snip.visual_content,
    }

def clean_first_placeholder(snip): #{{{1
# This function will clean up first placeholder when this is empty.

    # Jumper is a helper for performing jumps in UltiSnips.
    make_jumper(snip)

    # If we've  emptied the 1st tabstop, we need  to remove the parentheses
    # which are now useless, because they don't contain anything.

    # WARNING: It's not completely reliable.{{{
    #
    # It assumes that the 1st tabstop is:
    #
    #    - on a single line
    #    - on the same line as the 2nd one
    #
    # It will erase the wrong text if the 2 tabstops are on different lines.
    # IOW, this function must be adapted to the snippet for which you call it.
    #
    # More generally, an ad hoc substitution, which the following code tries
    # to perform, is tricky.
    #}}}
    # Here's how it works:{{{
    #
    #     line = snip.buffer[snip.cursor[0]]
    #
    #             copy the text on the current line
    #
    #     line[:snip.tabstops[1].start[1]-2] + \
    #     line[snip.tabstops[1].end[1]+1:]
    #
    #             remove the parentheses inside the copy
    #
    #     snip.buffer[snip.cursor[0]] = \
    #     …
    #
    #             replace the current line with the modified copy
    #}}}

    if snip.tabstop == 2 and not get_jumper_text(snip):
    #                        ├───────────────────────┘
    #                        └ Don't remove anything
    #                          if the 1st tabstop hasn't been emptied.
    #                          Alternative:
    #                              snip.tabstops[1].current_text == ''
    #
        line = snip.buffer[snip.cursor[0]]
        # remove parentheses
        # Why `-2`?{{{
        #
        # We want  to remove  the parentheses,  but also  the space  just before
        # them.
        #}}}
        # Why `snip.tabstops[1].start[1]-2`?{{{
        #
        # We want to extract the characters from  the 1st on the line, up to the
        # space before the 1st tabstop.
        # The index of the 1st character of the 1st tabstop can be expressed via
        # `snip.tabstops[1].start[1]`:
        #
        #     snip.tabstops[1].start[1]
        #                   │  │     │
        #                   │  │     └ column position (0 would be the line position)
        #                   │  └ 1st character (`end` would be the last)
        #                   └ 1st tabstop
        #
        # But  here, the  tabstop is  empty, so  this variable  matches the  1st
        # character after the tabstop.
        # So, the index of the opening parentheses right before the tabstop is:
        #
        #     snip.tabstops[1].start[1] - 1
        #
        # And the one of the space before the tabstop is:
        #
        #     snip.tabstops[1].start[1] - 2
        #
        # Besides in python, when we slice a string:
        #
        #     $ python
        #     s = 'hello world'
        #     s[3:8]
        #         → lo wo
        #
        # The first index matches the one of the 1st character we want.
        # The 2nd   index matches the one of the 1st character we DON'T want.
        # IOW, they are resp. inclusive and EXCLUSIVE.
        #
        # So, we must use:
        #
        #     snip.tabstops[1].start[1] - 2
        #
        # Because, it's  the index of  the space which  is the 1st  character we
        # don't want.
        #}}}
        snip.buffer[snip.cursor[0]] = \
                line[:snip.tabstops[1].start[1]-2] + \
                line[snip.tabstops[1].end[1]+1:]
        # position cursor (move it 3 characters back)
        # Why `-3`?{{{
        #
        # We must go back 1 character to the left to make up for:
        #
        #    1. the closing parenthesis
        #    2. the opening parenthesis
        #    3. the space
        #}}}
        snip.cursor.set(
            snip.cursor[0],
            snip.cursor[1] - 3,
        )

def complete(base, matches): #{{{1
    # remove possible empty candidate
    matches = [m for m in matches if m != '']
    #          ├────────────────┘ ├────────┘
    #          │                  └ filtering
    #          └ list comprehension (python construct)

    # if the text to complete is not empty
    if base:
        # filter the list, removing the matches which don't start like the text to complete
        matches = [m[len(base):] for m in matches if m.startswith(base)]
        #           ├──────────┘ ├──────────────┘ ├───────────────────┘{{{
        #           │            │                └ but keep only the ones which start with `base`
        #           │            │                  (filtering)
        #           │            │
        #           │            └ make `c` iterate over the values stored in `matches`
        #           │
        #           └ expression which will be evaluated with a range of values for `m`;
        #             the set of all the evaluations will populate the list `matches`
        #             (list comprehension)
        #}}}

    if not matches:
        return ''
    # if there's only 1 candidate left, return it directly
    elif len(matches) == 1:
        return matches[0]
    # if there are more, return all of them (with some formatting)
    else:
        return '[' + ' | '.join(matches) + ']'

def create_table(snip): #{{{1
    # get the dimension of the table (how many rows x how many columns)

    #                            ┌ remove leading/trailing whitespace
    #                            │      ┌ remove the first 2 characters (`tb`)
    #                            │      │    ┌ split the rest every `x` do it only once
    #                            ├─────┐├──┐ ├───────────┐
    dim = snip.buffer[snip.line].strip()[2:].split('x', 1)
    rows = int(dim[0])
    cols = int(dim[1])

    # create anonymous snippet with expected content and number of tabstops
    anon_snip_title = ' | '.join(['$' + str(col) for col in range(1, cols+1)]) + '\n'
    anon_snip_delimiter = '--|' * (cols-1) + "--\n"

    anon_snip_body = ''
    for row in range(1, rows+1):
        anon_snip_body += ' | '.join(['$' + str(row*cols+col) for col in range(1, cols+1)]) + '\n'

    anon_snip_table = anon_snip_title + anon_snip_delimiter + anon_snip_body

    # erase current line
    snip.buffer[snip.line] = ''

    # expand anonymous snippet
    snip.expand_anon(anon_snip_table)

def get_jumper_position(snip): #{{{1
    if not snip.context or 'jumper' not in snip.context:
        return None

    return snip.context['jumper']['snip'].tabstop

def get_jumper_text(snip): #{{{1
    if not snip.context or 'jumper' not in snip.context:
        return None

    pos = get_jumper_position(snip)

    if pos not in snip.context['jumper']['snip'].tabstops:
        return None

    return snip.context['jumper']['snip'].tabstops[pos].current_text
    #      ├────────────────────────────┘
    #      └ FIXME: Why all of this?
    #        Why not just `snip.tabstops[pos].current_text`?

def jump_to_second_when_first_is_empty(snip): #{{{1
    if get_jumper_position(snip) == 1:
        if not get_jumper_text(snip):
            advance_jumper(snip)

def make_context(snip): #{{{1
    # FIXME:
    # What's the purpose?
    # See 1st line in `_make_jumper_jump()`.
    # I think this function is useful to make sure `snip.context`
    # exists.
    # Otherwise `'jumper' not in snip.context` would raise an error.
    # Same thing for:
    #
    #     snip.context.update(...)
    return {'__dummy': None}

def make_jumper(snip): #{{{1
    if snip.tabstop != 1:
        return

    # `update()` is a method of the standard library.
    # It allows to merge 2 dictionaries (like `extend()` in VimL).
    snip.context.update({'jumper': {'enabled': True, 'snip': snip}})
    # ├────────┘        ├─────────────────────────────────────────┘
    # │                 └ 2nd dictionary
    # └ 1st dictionary

def _make_jumper_jump(snip, direction): #{{{1
    if not snip.context or 'jumper' not in snip.context:
        return False

    jumper = snip.context['jumper']
    if not jumper['enabled']:
        return False

    jumper['enabled'] = False

    vim.eval('feedkeys("\<c-r>=UltiSnips#Jump'
             + direction.title()
             + '()\<cr>")')

    return True

def my_index(a_list, pattern): #{{{1
    pat = re.compile(pattern)
    for i, s in enumerate(a_list):
        if pat.search(s):
            return i
    return -1

def plugin_guard(snip): #{{{1
    path_to_file = vim.current.buffer.name
    path_to_dir = os.path.dirname(path_to_file)
    # get the name of the current file without its extension (`splitext()`)
    basename = os.path.splitext(os.path.basename(path_to_file))[0]

    finish = '\n' + vim.eval("repeat(' ', &l:sw)") + 'finish'

    # What's the alternative to the `try` statement?{{{
    # An expression using a ternary operator `a if condition else b`:
    #
    #     ┌ Match
    #     │
    #     m = re.search('autoload/(.*)\.vim', path_to_file)
    #     relative_path = m.group(1) if m else ''
    #                                   │
    #                                   └ will evaluate to False if there's no match
    #}}}
    # Why using the `try` statement is better?{{{
    #
    # EAFP: it's Easier to Ask for Forgiveness than Permission.
    # https://docs.python.org/3/glossary.html#term-eafp
    #}}}
    try:
        relative_path = re.search('autoload/(.*)\.vim', path_to_file).group(1)
    except AttributeError:
        relative_path = ''

    if snip.line != 0:
        # guard to prevent infinite:
        #
        #    - loop (`break`)
        #    - recursive call of a function (`return`)
        #
        # TODO: add a tabstop and make the snippet complete it,{{{
        # so that we can choose between `break` and `return`.
        # I tried to replace this line:
        #
        #     + '\nbreak | return'
        #
        # with:
        #
        #     + "\n$1`!p snip.rv = complete(t[1], ['break', 'return'])`"
        #
        # But it raises an error, because `complete()` is not recognized.
        # The code doesn't contain any syntax  error, so I think the issue comes
        # from the fact that the snippet is anonymous.
        #}}}
        anon_snip_body = (
              'if g > 999'
            + '\nbreak | return'
            + '\ng += 1'
            + '\n$0'
        )

    elif '/autoload/slow_call' in path_to_dir:
        rtp_name = vim.eval('snippets#getPluginNameInGuard()')
        anon_snip_body = (
            "if stridx(&rtp, '${1:" + rtp_name + "}') == -1"
            + finish
            + '\nendif'
            + '\n$0'
        )

    # This block deals with a file such as ~/.vim/plugin/foo.vim.{{{
    #
    # It shouldnt'be sourced if:
    #
    #    - the plugin has already been sourced
    #    - the plugin has been temporarily disabled
    #}}}
    elif '/.vim/plugin' in path_to_dir:
        guard_name = vim.eval('snippets#getPluginNameInGuard()')
        rtp_name = vim.eval('snippets#getPluginNameInRtp()')

        anon_snip_body = (
              "if exists('${2:g:loaded_${1:" + basename + "}}')"
            + " || stridx(&rtp, '${3:" + rtp_name + "}') == -1"
            + finish
            + '\nendif'
            + '\n$0'
        )

    # Why the slash before 'autoload'?{{{
    #
    # It can be useful to avoid an ambiguity.
    # For example between `ftplugin` and `plugin`.
    #}}}
    # Why not a slash after 'autoload'?{{{
    #
    # `dirname()` has removed the ending slash from the path.
    #}}}
    # TODO: When can we omit the `+` operator?{{{
    #
    # We can after and before a string.
    # But we can't after nor before a variable containing a string.
    # So, here,  we could remove  most `+` except  the ones around  the variable
    # `finish`.
    # Are there other cases where we cannot?
    # What are the rules regarding the omission of operators?
    #}}}
    elif '/plugin' in path_to_dir or '/autoload' in path_to_dir:
            anon_snip_body = (
                'vim9script noclear'
                + "\n\nif exists('loaded') | finish | endif"
                + '\nvar loaded = true'
                + '\n\n$0'
            )

    elif '/ftplugin' in path_to_dir:
        anon_snip_body = (
            "if exists('b:did_ftplugin')"
            + finish
            + '\nendif'
            + '\n\n$0'
            + '\nlet b:did_ftplugin = v:true'
        )

    elif '/syntax' in path_to_dir:
        anon_snip_body = (
            "if exists('b:current_syntax')"
            + finish
            + '\nendif'
            + '\n\n$0'
            + "\n\nlet b:current_syntax = '$1'"
        )

    elif '/indent' in path_to_dir:
        anon_snip_body = (
            "if exists('b:did_indent')"
            + finish
            + '\nendif'
            + '\n\n$0'
            + "\n\nlet b:did_indent = v:true"
        )

    else:
        # Why `preserve()`?{{{
        #
        # If we're not  in a known type  of plugin, the tab  trigger (here 'gd')
        # should not be expanded.
        # But without `preserve()`, it would be automatically removed.
        #}}}
        snip.cursor.preserve()
        return

    snip.buffer[snip.line] = ''
    snip.expand_anon(anon_snip_body)

def trim_ws(snip): #{{{1
    # no need  to use the  `^` anchor, because  we're going to  invoke `match()`
    # which, contrary to  `search()`, always searches from the  beginning of the
    # string
    ws = re.compile('\s+$')

    # Why?{{{
    #
    # There's no need to trim any line if we've expanded the snippet from insert
    # mode.
    # Besides, it  would remove  the indentation  in front of  `$0` in  the `fu`
    # snippet.
    #}}}
    if not snip.context['visual']:
        return
    #                                ┌ address of first line in snippet{{{
    #                                │ the tuple `snip.snippet_start` contains 2 numbers:
    #                                │
    #                                │     (line, column)
    #                                │                     ┌ address of last line in snippet
    #                                ├───────────────────┐ ├─────────────────┐
    #}}}
    for i, l in enumerate(snip.buffer[snip.snippet_start[0]:snip.snippet_end[0]]):
    #   └─┤    └───────┤{{{
    #     │            │
    #     │            └ iterate over some lines of the buffer
    #     │
    #     └ i = index of item in the list
    #       l = item in the list (buffer line)
    #}}}
    # snip.buffer = lines in buffer{{{
    #
    # When you want to modify the buffer, use this variable.
    # From `:h UltiSnips-buffer-proxy`:
    #
    #     Note:   special  variable   called   'snip.buffer'   should  be   used
    #     for  all   buffer  modifications. Not  'vim.current.buffer'   and  not
    #     'vim.command("...")', because in that case  UltiSnips will not be able
    #     to track changes in buffer from actions.
    #}}}
        # check  whether  each  line  in  the  snippet  matches  an  empty  line
        # containing whitespace
        if ws.match(l):
            # if so, remove the whitespace
            snip.buffer[snip.snippet_start[0]+i] = ''
            # Why?{{{
            #
            # To avoid error when we expand the snippet from visual mode:
            #
            #     RuntimeError: line under the cursor was modified,
            #     but "snip.cursor" variable is not set;
            #     either set set "snip.cursor" to new cursor position,
            #     or do not modify cursor line
            #
            # Alternative: snip.cursor.set(i, 0)
            #}}}
            snip.cursor.preserve()

def undo_ftplugin(snip): #{{{1
    path_to_file = vim.current.buffer.name
    path_to_dir = os.path.dirname(path_to_file)

    if '/ftplugin' in path_to_dir:
        # If there are autocmds, do *not* delete their augroup.{{{
        #
        # Even if  the autocmds for the  current buffer are no  longer relevant,
        # and should be removed, that doesn't mean that the augroup is empty.
        # There  could still  be other  buffers  with the  same filetype,  using
        # autocmds in this augroup.
        # }}}
        # FIXME: When you  expand this snippet,  if you remove the  `setl` line,{{{
        # make sure to remove the first bar on the next line.
        # Otherwise, the value of `b:undo_ftplugin` may begin with a bar:
        #
        #     | some commands
        #
        # The empty command before the bar might have unexpected effect.
        # MWE:
        #     :|echo 'hello'
        #         → prints current line, then echo 'hello'
        #
        # Update:
        # We could use this:
        #
        #     `!p snip.rv = ' ' if t[1] == '' else '|'`
        #
        # But what if we remove `:setl ...` and `:unlet! ...`.
        # And what if we remove `:setl ...`, and `:unlet! ...`, and `:exe 'au! ...'`.
        # ...}}}

        anon_snip_body = (
            '" Teardown {{' + '{1'
            '\n'
            "\nlet b:undo_ftplugin = get(b:, 'undo_ftplugin', 'exe')"
            "\n    \ ..\""
            "\n    \ | ${1:setl ${2:option}<}${3:"
            "\n    \ | unlet! b:${4:variable}}${5:"
            "\n    \ | exe 'au! ${6:group_name} * <buffer>'}${7:"
            "\n    \ | exe '${8:n}unmap <buffer> ${9:lhs}'}${10:"
            "\n    \ | exe '${11:c}una <buffer> ${12:lhs}'}${13:"
            "\n    \ | delc ${14:Cmd}}"
            "\n    \\ \""
            '\n$0'
        )

    elif '/indent' in path_to_dir:
        anon_snip_body = (
            '" Teardown {{' + '{1'
            + '\n'
            + "\nlet b:undo_indent = get(b:, 'undo_indent', 'exe')"
            + "\n    \ ..'| setl ${1:indk}<'"
            + '\n$0'
        )

    else:
        snip.cursor.preserve()
        return

    snip.buffer[snip.line] = ''
    snip.expand_anon(anon_snip_body)

def why(snip): #{{{1
    cml = vim.eval("getline(1) == 'vim9script' && searchpair('^\C\s*fu\%[nction]\>', '', '^\C\s*\<endf\%[unction]\>$', 'nW') <= 0 || searchpair('^\C\s*def\>', '', '^\C\s*\<enddef\>$', 'nW') > 0 ? '#' : split(&l:cms, '%s')->get(0, '')->matchstr('\S\+')")
    cml_r = vim.eval("split(&l:cms, '%s')->get(1, '')->matchstr('\S\+')")
    indent = vim.eval("getline('.')->matchstr('^\s*')")
    if cml_r == '':
        # Why don't you add a space before the fold markers?{{{
        #
        # The default `zf` command in visual mode doesn't add any space.
        # Let's try to be consistent.
        #}}}
        anon_snip_body = (
            indent + cml + ' Why ${1}?{{' + '{'
            + '\n' + indent + cml
            + '\n' + indent + cml + ' ${2:Because.}'
            + '\n' + indent + cml + '}}' + '}'
            )
    else:
        anon_snip_body = (
            indent + cml + ' Why ${1}?' + cml_r + cml + '{{' + '{' + cml_r
            + '\n'
            + '\n' + indent + cml + ' ${2:Because.} ' + cml_r
            + '\n'
            + '\n' + indent + cml + ' ' + cml_r + cml + '}}' + '}' + cml_r
            )
    snip.buffer[snip.line] = ''
    snip.expand_anon(anon_snip_body)

