# coding=utf-8
# The previous line  allows us to use unicode characters  in comments (like …){{{
# without python raising an exception.
#
#     https://stackoverflow.com/a/10589674/9110115
#     https://stackoverflow.com/a/729016/9110115
#
# The `-*-` prefix/suffix are not necessary, unless you use Emacs.
#}}}

# We import  the same modules  that UltiSnips  automatically import in  a python
# interpolation.
import os, random, re, string, vim

# TODO:
# understand all the new functions

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
    #     • on a single line
    #     • on the same line as the 2nd one
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

    #                                                ┌  Don't remove anything
    #                                                │  if the 1st tabstop hasn't been emptied.
    #                                                │  Alternative:
    #                                                │      snip.tabstops[1].current_text == ''
    #                        ┌───────────────────────┤
    if snip.tabstop == 2 and not get_jumper_text(snip):
    #
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
        #     1. the closing parenthesis
        #     2. the opening parenthesis
        #     3. the space
        #}}}
        snip.cursor.set(
                snip.cursor[0],
                snip.cursor[1] - 3,
        )

def complete(base, candidates): #{{{1
    # remove possible empty candidate
    candidates = [c for c in candidates if c != '']
    #             └───────────────────┤ └────────┤
    #                                 │          └ filtering
    #                                 └ list comprehension (python construct)

    # if the text to complete is not empty
    if base:
        # filter the  list, removing the  candidates which don't start  like the
        # text to complete
        candidates = [ c[len(base):] for c in candidates if c.startswith(base) ]
        #              └───────────┤ └─────────────────┤ └───────────────────┤{{{
        #                          │                   │                     └ but keep only the ones
        #                          │                   │                       which start with `base`
        #                          │                   │                       (filtering)
        #                          │                   │
        #                          │                   └ make `c` iterate over the values stored in `candidates`
        #                          │
        #                          └ expression which will be evaluated with a range of values for `c`;
        #                            the set of all the evaluations will populate the list `candidates`
        #                            (list comprehension)
        #}}}

    if not candidates:
        return ''
    # if there's only 1 candidate left, return it directly
    elif len(candidates) == 1:
        return candidates[0]
    # if there are more, return all of them (with some formatting)
    else:
        return '[' + '|'.join(candidates) + ']'

def create_table(snip): #{{{1
    # get the dimension of the table (how many rows x how many columns)

    #                                   ┌ remove leading/trailing whitespace
    #                                   │
    #                                   │   ┌ remove the first 2 characters (`tb`)
    #                                   │   │
    #                                   │   │            ┌ split the rest every `x`
    #                                   │   │            │ do it only once
    #                             ┌─────┤┌──┤ ┌──────────┤
    dim  = snip.buffer[snip.line].strip()[2:].split('x',1)
    rows = int(dim[0])
    cols = int(dim[1])

    # create anonymous snippet with expected content and number of tabstops
    anon_snip_title     = ' | '.join(['$' + str(col) for col in range(1,cols+1)]) + "\n"
    anon_snip_delimiter = '--|' * (cols-1) + "--\n"

    anon_snip_body = ''
    for row in range(1,rows+1):
        anon_snip_body += ' | '.join(['$' + str(row*cols+col) for col in range(1,cols+1)]) + "\n"
        #                                                                                    │
        #                         not necessary, but we use double quotes to stay consistent ┘
        #                         with how strings are parsed in other languages

    anon_snip_table = anon_snip_title + anon_snip_delimiter + anon_snip_body

    # erase current line
    snip.buffer[snip.line] = ''

    anon_snip_table = '$1'
    # expand anonymous snippet
    snip.expand_anon(anon_snip_table)

def forkv_comma(snip): #{{{1
    snip.buffer[snip.line] = 'for [k,v] in items(a_dict)'

def forkv_items(snip): #{{{1
    try:
        if snip.tabstops[2].current_text == 'items(':
            vim.eval('timer_start(0, {-> feedkeys("\<c-g>6lo6l\<c-g>", "in")})')
    except KeyError:
        pass

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
    #      └────────────────────────────┤
    #                                   └ FIXME: why all of this?
    #                                     why not just `snip.tabstops[pos].current_text`?

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
    #     snip.context.update(…)
    return {'__dummy': None}

def make_jumper(snip): #{{{1
    if snip.tabstop != 1:
        return

    # `update()` is a method of the standard library.
    # It allows to merge 2 dictionaries (like `extend()` in VimL).
    snip.context.update({'jumper': {'enabled': True, 'snip': snip}})
    # └────────┤        └─────────────────────────────────────────┤
    #          │                                                  └ 2nd dictionary
    #          └ 1st dictionary

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

    # Why the slash before 'autoload'?{{{
    #
    # It can be useful to avoid an ambiguity.
    # For example between `ftplugin` and `plugin`.
    #}}}
    # Why not a slash after 'autoload'?{{{
    #
    # `dirname()` has removed the ending slash from the path.
    #}}}
    if '/autoload' in path_to_dir:
        anon_snip_body = ("if exists('${2:g:autoloaded_${1:"
            + relative_path.replace('/', '#')
            + "}}')"
            + finish
            + '\nendif'
            + '\nlet $2 = 1'
            + '\n$0')

    elif '/plugin' in path_to_dir:
        anon_snip_body = ("if exists('${2:g:loaded_${1:"
            + basename
            + "}}')"
            + finish
            + '\nendif'
            + '\nlet $2 = 1'
            + '\n$0')

    elif '/ftplugin' in path_to_dir:
        anon_snip_body = ("if exists('b:did_ftplugin')"
            + finish
            + '\nendif'
            + '\nlet b:did_ftplugin = 1'
            + '\n\n$0')

    elif '/syntax' in path_to_dir:
        anon_snip_body = ("if exists('b:current_syntax')"
            + finish
            + '\nendif'
            + '\n\n$0'
            + "\n\nlet b:current_syntax = '$1'")

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
    # There's no need to trim any line if we've expanded the snippet from normal
    # mode. Besides, it would remove the indentation in front of `$0` in the `fu`
    # snippet, forcing us to press Tab an extra time to indent the line before
    # beginning writing the 1st line of the function.
    #}}}
    if not snip.context['visual']:
        return
    #                                                    ┌ address of first line in snippet{{{
    #                                                    │ the tuple `snip.snippet_start` contains 2 numbers:
    #                                                    │
    #                                                    │     (line, column)
    #                                                    │
    #                                                    │                   ┌ address of last line in snippet
    #                                ┌───────────────────┤ ┌─────────────────┤}}}
    for i,l in enumerate(snip.buffer[snip.snippet_start[0]:snip.snippet_end[0]]):
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
    # From `:h Ultisnips-buffer-proxy`:
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
            # To avoid error when we expand the snippet from normal mode:
            #
            #     RuntimeError: line under the cursor was modified,
            #     but "snip.cursor" variable is not set;
            #     either set set "snip.cursor" to new cursor position,
            #     or do not modify cursor line
            #
            # Alternative: snip.cursor.set(i, 0)
            #}}}
            snip.cursor.preserve()
