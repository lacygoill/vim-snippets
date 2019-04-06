## What's the first argument expected  by `complete()`?

The weight of the text up to the word you want to complete + 1.

Why `+1`?
Probably because `0` is reserved for an error.
From `:h complete()`:

>     Use col('.') for an empty string.
>     "col('.') - 1" will replace one character by a match.

## How to get a list of the snippets whose tab trigger is matched by the word before the cursor?

Use `UltiSnips#SnippetsInCurrentScope()`.

It will give you a dictionary whose:

   - keys  are the  tab triggers of  the  snippets available  in the
     current buffer, and which are matched by the word before the cursor

   - values are the description of the snippets

Usage example:

        ino  <silent>  <c-x><c-x>  <c-r>=<sid>complete_snippets()<cr>
        fu! s:complete_snippets() abort
            let word = len(strpart(getline('.'), 0, col('.')-1))
            call complete(
            \             col('.') - len(word),
            \             keys(UltiSnips#SnippetsInCurrentScope()))
            return ''
        endfu

        \             len(matchstr(getline('.'), '^.*\ze\<.\{-1,}\%'.col('.').'c'))+1,



`UltiSnips#SnippetsInCurrentScope()` returns a Vim  dictionary with the snippets
whose trigger:

   - matches the current word, if the function was passed no argument
   - anything,                 if the function was passed the argument 1

What's the output of the function without argument?

What's the output of the function with `1` as argument?
The same as without argument, except the restriction “the word before the cursor
must match the tab trigger” is removed.
IOW, all snippets are listed.

Example of value:

        { 'qnd':        'Quick aNd Dirty settings',
        \ 'bug_report': 'filing bug report for (Neo)Vim',
        \ 'spoiler':    'hide long code'}

        {'qnd': 'Quick aNd Dirty settings', 'bug_report': 'filing bug report for (Neo)Vim', 'spoiler': 'hide long code'}

##
# UltiSnips#SnippetsInCurrentScope()

If you need all snippets information for the current buffer, you can simply pass
1  (which means  all) as  first  argument of  this  function, and  use a  global
variable `g:current_ulti_dict_info` to get the result (see example below).

This  function does  not add  any new  functionality to  ultisnips directly  but
allows third party plugins to integrate the current available snippets.
For example, all completion plugins that integrate UltiSnips use this function.

Usage example:

        fu! Expand_possible_shorter_snippet()
            "only one candidate...
            if len(UltiSnips#SnippetsInCurrentScope()) == 1
                let curr_key = keys(UltiSnips#SnippetsInCurrentScope())[0]
                norm! diw
                exe 'norm! a'.curr_key.' '
                return 1
            endif
            return 0
        endfu
        ino <silent>  <c-l>  <c-r>=Expand_possible_shorter_snippet() == 0 ? '' : UltiSnips#ExpandSnippet()<cr>

This  code installs  a  `C-l` mapping  which completes  a  possible partial  tab
trigger, and automatically expands it.

---

One last example:

        fu! GetAllSnippets()
            call UltiSnips#SnippetsInCurrentScope(1)
            let list = []
            for [key, info] in items(g:current_ulti_dict_info)
                let parts = split(info.location, ':')
                call add(list, {
                \ 'key':         key,
                \ 'path':        parts[0],
                \ 'linenr':      parts[1],
                \ 'description': info.description,
                \ })
            endfor
            return list
        endfu

Here,  we define  a custom  function to  extract all  snippets available  in the
current buffer.

#
#
#
# Snippets
## How to create an alias `bar` for the snippet `foo`?

Create a  snippet `bar` which  inserts the text  `foo`, and use  a `post_expand`
statement to automatically invoke `UltiSnips#ExpandSnippet()`.

        snippet foo "" bm
        hello world
        endsnippet

        post_expand "vim.eval('feedkeys(\"\<c-r>=UltiSnips#ExpandSnippet()\<cr>\", \"in\")')"
        snippet bar "" bm
        foo
        endsnippet

---

Note that you could also use a `post_jump` statement:

        post_jump "vim.eval('feedkeys(\"\<c-r>=UltiSnips#ExpandSnippet()\<cr>\", \"in\")')"
        snippet bar "" bm
        foo
        endsnippet

## How to create the aliases `foobar`, `foobaz`, and `fooqux` for the snippet `foo`?

        snippet "foo(bar|baz|qux)" "" r
        hello world
        endsnippet

## How to expand a snippet from another one, programmatically?

Use the same technique as for creating an alias.
With one caveat:
don't  give   the  `b`  option   to  the   second  snippet  (the   one  expanded
programmatically), unless you know for sure  that its tab trigger will always be
at the beginning of a line, even inside other snippets.

                       ┌ don't add `b`:
                       │
                       │     `foo` will be used AFTER the beginning of the line
                       │     in the next snippet
                       │
        snippet foo "" m
        beautiful
        endsnippet

        post_expand "vim.eval('feedkeys(\"\<c-r>=UltiSnips#ExpandSnippet()\<cr>\", \"in\")')"
        snippet bar "" bm
        hello foo$1 world
        endsnippet

            →    bar + Tab  =  hello beautiful world

---

Note that if  use a `post_jump` statement,  you'll need to check  the tabstop to
avoid triggering an undesired expansion whenever you jump to a tabstop:

        snippet foo "" m
        beautiful
        endsnippet

        post_jump "if snip.tabstop == 1: vim.eval('feedkeys(\"\<c-r>=UltiSnips#ExpandSnippet()\<cr>\", \"in\")')"
        snippet bar "" bm
        hello foo$1 world$2
        endsnippet

Even then,  it's better to use  a `post_expand` statement, because  you may jump
several times  to the tabstop whose  purpose is to expand  another snippet, and,
while the first time it will do  what you want, there could be another undesired
expansion the next time:

        snippet foo "" m
        beautiful foo
        endsnippet

        post_jump "if snip.tabstop == 1: vim.eval('feedkeys(\"\<c-r>=UltiSnips#ExpandSnippet()\<cr>\", \"in\")')"
        snippet bar "" bm
        hello foo$1 world$2
        endsnippet

## How to create a new snippet programmatically?

Use `UltiSnips#AddSnippetWithPriority()`.

The signature of this function is:

        UltiSnips#AddSnippetWithPriority(trigger, value, description, options, filetype, priority)

Example:

        call UltiSnips#AddSnippetWithPriority('foo', "hello\nworld", 'test', 'bm', 'all', 1)

## What's an anonymous snippet?

A snippet  whose body is  defined outside a  snippet file (python  function, Vim
mapping, ...), expanded and immediately discarded (i.e.
not added to the global list of snippets).

## How to expand an anonymous snippet in VimL?

Invoke `UltiSnips#Anon()`.

This function can expand an anonymous snippet.
Its signature is:

        UltiSnips#Anon(value, [trigger, description, options])

If you  pass a trigger  and options as arguments,  the snippet will  be expanded
only if the word before the cursor matches the trigger, and if the options allow
the expansion.
The description  is not  used, since  the snippet  is discarded  as soon  as the
snippet is  expanded, but  is probably  necessary to pass  the options  in third
position.

Usage example:

        ino <silent>  !!  !!<c-r>=UltiSnips#Anon('hello $1 world $2', '!!')<cr>

This expands the snippet whenever two bangs are typed.

## How to expand an anonymous snippet in python?

Invoke the `snip.expand_anon()` method:

        snip.expand_anon(my_snippet)
                         │
                         └ variable in which you've saved the body of our anonymous snippet

## When should I use an autotriggered snippet vs an anonymous snippet?

If  you   need  some  advanced   features  (like  `context`   and  `post_expand`
statements),  and if  you  care  about readability,  then  use an  autotriggered
snippet.

If you  don't need the snippet  permanently, only in a  particular circumstance,
then use an anonymous snippet.

#
# Interpolation
## What's the scope of a variable in a python interpolation?

The whole snippet.

## Can I pass a variable from a python interpolation block to another?

Yes.

        snippet foo "" bm
        `!p var = 'hello'`
        `!p snip.rv = var`
        endsnippet

---

Note that the order matters, so you can't write that:

        snippet foo "" bm
        `!p snip.rv = var`
        `!p var = 'hello'`
        endsnippet

#
# Statements
## What are the four statements which can invoke python code (besides an in-snippet interpolation)?

   - context
   - pre_expand
   - post_expand
   - post_jump

## When is the python code invoked by a `pre_expand` statement executed?

Right after the trigger condition is matched, but before the snippet is actually
expanded.

## When is the python code invoked by a `post_expand` statement executed?

Right after  the snippet is expanded,  the interpolations have been  applied for
the first time, and the cursor has jumped to the first tabstop.

## When is the python code invoked by a `post_jump` statement executed?

Right after you jump to the next/prev tabstop.

## Can I modify the buffer from a `pre_expand` statement without the cursor position being wrong after the expansion?

Yes, you can.

From `pre_expand`:

        Snippet expansion position will be automatically adjusted.

#
# Variables
## How to read/modify the lines of the current buffer in a python function/expression?

Use the `snip.buffer` variable.

It's an alias for `vim.current.window.buffer` and `vim.current.buffer`.
Both seem to be the same object.

## How to get the full path to the current file, without VimL?

        vim.current.buffer.name

It's an alias for:

        vim.current.window.buffer.name

From a context statement, you could also use:

        snip.buffer.name

## How to refer to the last visually-selected text (in `context`/`pre_expand` statement, interpolation, in-snippet)?

    ┌───────────────┬─────────────────────┐
    │ context       │ snip.visual_text    │
    ├───────────────┼─────────────────────┤
    │ pre_expand    │ snip.visual_content │
    ├───────────────┼─────────────────────┤
    │ interpolation │ snip.v.text         │
    ├───────────────┼─────────────────────┤
    │ in-snippet    │ ${VISUAL}           │
    └───────────────┴─────────────────────┘

## How to refer to the last visual mode?

    ┌───────────────┬──────────────────┐
    │ context       │ snip.visual_mode │
    ├───────────────┼──────────────────┤
    │ interpolation │ snip.v.mode      │
    └───────────────┴──────────────────┘

## What are the three variables which can be used in a `post_jump` statement?

    ┌─────────────────────────────────┬─────────────────────────────────────────┐
    │ snip.jump_direction             │ 1: forwards, -1: backwards              │
    ├─────────────────────────────────┼─────────────────────────────────────────┤
    │ snip.tabstop                    │ number of tabstop jumped unto           │
    ├─────────────────────────────────┼─────────────────────────────────────────┤
    │ snip.tabstops                   │ list of tabstops objects                │
    └─────────────────────────────────┴─────────────────────────────────────────┘

## What are the three properties of the `snip.tabstops` variable?

    ┌─────────────────────────────────┬─────────────────────────────────────────┐
    │ snip.tabstops[123].current_text │ text inside the 123th tabstop           │
    ├─────────────────────────────────┼─────────────────────────────────────────┤
    │ snip.tabstops[123].start        │ (line, column) of its starting position │
    ├─────────────────────────────────┼─────────────────────────────────────────┤
    │ snip.tabstops[123].end          │ (line, column) of its ending position   │
    └─────────────────────────────────┴─────────────────────────────────────────┘

## From which statement(s)/interpolation can I use `snip.snippet_start` and `snip.snippet_end`?

Only from a `post_expand` and `post_jump` statement.

You can use them from an interpolation, but they don't give the expected result:
they seem to give the position of the tab trigger.

##
# Methods
## What does `snip.cursor.set(12,34)` do?

It positions the cursor on the 12th line and the 34th column.

## From which statement(s)/interpolation can I use `snip.cursor.set(12,34)`?

Only from a `pre_expand` or `post_jump` statement.

## When is `snip.cursor.set()` necessary?

If your code  needs to modify the  line where the trigger was  matched, then you
will have to invoke `snip.cursor.set(x,y)` with the desired cursor position.

#
#
#
# Predefined Variables / Methods
## Universal

    vim.current.buffer
    vim.current.window.buffer
    vim.current.window.cursor


    snip.window    (interpolation ✘)    (alias for `vim.current.window`)

          FIXME:
          What's its purpose?


    snip.line      (interpolation ✘)
    snip.column    (")
    snip.cursor    (")

            Position of the cursor.
            All 3 variables are 0-indexed.

            `snip.cursor`  behaves  like   `vim.current.window.cursor`  but  the
            coordinates  are  indexed  from  zero, and  the  object  comes  with
            additional methods:

                    * preserve()        - special method for executing pre/post/jump actions

                    * set(line,column)  - sets cursor to specified line and column

                    * to_vim_cursor()
                                        - returns cursor position, but the coordinates being
                                          indexed from 1;
                                          suitable to be assigned to `vim.current.window.cursor`

                    It seems  to be  useful, for example,  when you  capture the
                    position  of the  cursor in  a function  with `snip.cursor`,
                    then  you  want  to  restore  it  in  another  function  via
                    `vim.current.window.cursor`:

                    https://github.com/reconquest/snippets/blob/b5d86da79604e7d341d26de1f3366b3f1373f7c5/python.snippets#L49

                    Btw, I don't know how he can pass an argument to `snip.cursor.to_vim_cursor()`.
                    On my machine, it raises an error. The function doesn't accept any argument.


                                               NOTE:

            None of the variables / methods exist in an interpolation.
            However, you  can still  use `vim.current.window.cursor`  instead of
            `snip.cursor`.


                                               NOTE:

            Although, you  can call  `snip.cursor.set(x,y)` from  all statements
            (but not in an interpolation), it has an effect only from `pre_expand`
            and `post_jump`.


    snip.context

            Result of context condition.

            You can (ab)use this variable  to pass an arbitrary information from
            a statement to another:

                    https://github.com/reconquest/snippets/blob/b5d86da79604e7d341d26de1f3366b3f1373f7c5/python.snippets#L33-L38

            Here, the author passes an information from `pre_expand` to `post_jump`.
            They use `pre_expand` to “enrich” `snip.context`.
            To do so, they move it inside a dictionary:

                    - one of its value is the original `snip.context`
                    - another          is `snip.cursor`
                    - another          is `snip.visual_content`
                    - another          is an arbitrary info

            They then use `post_jump` to analyze this enriched `snip.context`.

## context

By default, a snippet is used to expand  the text before the cursor only if it's
matched by the tab trigger (keyword, regex).
And a tab trigger can be expanded with only one snippet.

You  can  give more  “intelligence”  to  a  snippet  and work  around  those
limitations, by passing it the `e` option.

It will allow you to:

   - make the snippet take into consideration more than just the text
     before the cursor

   - expand a tab trigger with more than 1 snippet

To do so, the snippet should be defined using one of those syntaxes:

                                ┌ any python expression
                                │
                                │ If it evaluates to `True`,
                                │ then UltiSnips will use this snippet.
                                │
    snippet tab_trigger "desc" "expr" e


    context "expr"
    snippet tab_trigger "desc" e
                        │      │
                        │      └ you can add more options
                        │
                        └ Contrary to `desc`, which can be surrounded with
                          any character absent from the description,
                          `expr` MUST be wrapped inside double quotes.


Python code invoked from a `context` statement can use the variables:

    ┌────────────────────────────────────┬────────────────────────────────────────────────────┐
    │ snip.visual_mode                   │ v  V  ^V                                           │
    ├────────────────────────────────────┼────────────────────────────────────────────────────┤
    │ snip.visual_text                   │ last visually-selected text                        │
    ├────────────────────────────────────┼────────────────────────────────────────────────────┤
    │ snip.last_placeholder              │ last active placeholder from previous snippet      │
    │ snip.last_placeholder.current_text │ text in the placeholder on the moment of selection │
    │ snip.last_placeholder.start        │ placeholder start on the moment of selection       │
    │ snip.last_placeholder.end          │ placeholder end on the moment of selection         │
    └────────────────────────────────────┴────────────────────────────────────────────────────┘

    The last 3 properties may not exist.
    You need  to test  whether `snip.last_placeholder`  is different  than None,
    before trying to use them:

            if snip.last_placeholder:
                var = snip.last_placeholder.current_text

### Examples

    snippet r "" "re.match('^\s+if err ', snip.buffer[snip.line-1])" be
    return err
    endsnippet

            Will be expanded into 'return err'  only if the previous line begins
            with 'if err'.


    snippet i "" "re.match('^\s+[^=]*err\s*:?=', snip.buffer[snip.line-1])" be
    if err != nil {
        $1
    }
    endsnippet

    snippet i "" b
    if $1 {
        $2
    }
    endsnippet

            Will be  expanded with the 1st  snippet if the previous  line begins
            with sth like 'err :='. Otherwise the 2nd snippet will be used.

            It works  because context snippets are  PRIORITIZED over non-context
            ones. It  allows to  use  non-context snippets  as  fallback, if  no
            context was matched.


    global !p
    import my_utils
    endglobal

    snippet , "" "my_utils.is_return_argument(snip)" ie
    , `!p
    if my_utils.is_in_err_condition():
        snip.rv = "err"
    else:
        snip.rv = "nil"
    `
    endsnippet

            Will be expanded only if the cursor is located in the return statement.
            Will be expanded either into 'err'  or 'nil' depending on which 'if'
            statement it's located in.

            `is_return_argument()`  and `is_in_err_condition()`  are  part of  a
            custom python module which is called `my_utils`.

            The evaluation of:

                    my_utils.is_return_argument(snip)

            … is available in the `snip.context` variable inside the snippet.

                                     NOTE:

            By  moving the  python expression  into  a named  function inside  a
            module, and  by importing the  latter from  a global block,  you can
            re-use the expression in other snippets in the same file.


    snippet + "" "re.match('\s*(.*?)\s*:?=', snip.buffer[snip.line-1])" ie
    `!p snip.rv = snip.context.group(1)` += $1
    endsnippet

            That snippet  will be  expanded into  'var1 +='  after a  line which
            begins with 'var1 :='.


                                         ┌ automatically
                                         │
    snippet = "" "snip.last_placeholder" Ae
    `!p snip.rv = snip.context.current_text` == 0
    endsnippet

            Will be expanded only if you  press `=` while a tabstop is currently
            selected in  another snippet. The latter  will be replaced  with the
            original tabstop value followed by ' == 0'.

            This  shows  how you  can  capture  the  placeholder text  from  the
            previous snippet.


                                     NOTE:

            How can you be sure that the snippet will be expanded only while a tabstop
            is currently selected in another snippet?

            Because the expression is  `snip.last_placeholder`. Thus, it will be
            true iff  this variable exists. That  is iff a tabstop  is currently
            selected in another snippet.


                                     NOTE:

            For this to work, you need to choose a single-character tab trigger.
            Also, the expression `snip.last_placeholder` is not precise enough.
            Currently,  it will  be expanded  when you  press `=`,  while you're
            selecting a tabstop of ANY snippet.
            It should be expanded only in the snippet for which it was intended.
            You'll need to add a condition.
            Ex:

                    snip.last_placeholder and snip.last_placeholder.current_text == 'else'

                            only if the current tabstop contains the text 'else'

                    snip.last_placeholder and re.match(r'^\s*for\b', snip.buffer[snip.line])

                            only if the previous line begins with the keyword `for`


                                     NOTE:

            By default, the `snip` object has no `current_text` property.
            And yet this code works and refers to `snip.context.current_text`.
            How does it work?

            In a context snippet, the evaluation of the expression is assigned
            to `snip.context`. Here, the expression is `snip.last_placeholder`.
            So, when the interpolation is applied:

                    snip.context = snip.last_placeholder

            ... which means:

                    snip.context.current_text = snip.last_placeholder.current_text


                                     NOTE:

            More  generally, a  single-character tab  trigger combined  with the
            options `Ae` allows you to include a snippet inside a snippet.

            And the inner snippet can itself contain tabstops:

                    snippet test
                    ${1:foo} ${2:bar}
                    endsnippet

                    snippet + "" "snip.last_placeholder" Ae
                    ${1:baz} ${2:qux}
                    endsnippet

            The process can be repeated as many times as you want.
            With one minor issue:
            the 1st time you try to expand a snippet from another snippet, it will work.
            The next times, it won't work from the 1st tabstop.

            You can get around this issue, by moving to the next tabstop and coming back:

                    test
                    →
                    foo bar
                    └─┤
                      └ 1st tabstop of the 1st snippet is selected

                        ┌ tab trigger of inner snippet
                        │
                    foo + bar
                    →
                    baz qux bar

                        ┌ go to 2nd inner tabstop (Tab),
                        │ then come back (S-Tab),
                        │ and expand a 3rd inner snippet (+)
                        │
                        ├─────────┐
                    baz Tab S-Tab + qux bar
                    →
                    baz qux qux bar


    global !p
    def my_cond1(snip):
        return snip.line % 2 == 0 and snip.column == 1
    def my_cond2(snip):
        return snip.line % 2 == 1 and snip.column == 1
    endglobal

    context "my_cond1(snip)"
    snippet xy "" e
    context1
    endsnippet

    context "my_cond2(snip)"
    snippet xy "" e
    context2
    endsnippet

    snippet xy ""
    non-context
    endsnippet

            xy            context1
            xy        →   context2
                xy            non-context

            You can  have several snippets  using the  same tab trigger  and the
            option `e`.

            UltiSnips will  test each  of them,  and use the  one for  which the
            expression is true.

            If the expression of several of them is true, they will be listed to
            let the user choose one.

            If none of them  has a true expression, and a  snippet uses the same
            tab trigger without `e`, the latter will be used as a fallback.

            These rules allow you to expand a tab trigger in as many ways as you
            want, depending on the contents of the buffer.

## interpolation

An interpolation may be applied several times, because of dependencies between
different text-objects.
The 1st time, it's applied after `pre_expand` but before `post_expand`.

In a python interpolation, you can use the variables:

        ┌───────────────┬──────────────────────────────────────────┐
        │ snip.basename │ current filename, with extension removed │
        ├───────────────┼──────────────────────────────────────────┤
        │ snip.fn       │ current filename                         │
        ├───────────────┼──────────────────────────────────────────┤
        │ snip.ft       │ current filetype                         │
        ├───────────────┼──────────────────────────────────────────┤
        │ path          │ complete path to the current file        │
        ├───────────────┼──────────────────────────────────────────┤
        │ t             │ The values of the placeholders:          │
        │               │                                          │
        │               │         t[1] is the text of ${1}, etc.   │
        └───────────────┴──────────────────────────────────────────┘

The 'snip' object provides a few methods:

    snip.rv = "foo\n"
    snip.rv += snip.mkline("bar\n")

            Assuming the level of indentation of the line (where the interpolation
            is applied) is 4, it returns:

                foo
                bar

            OTOH:

                    snip.rv = "foo\n"
                    snip.rv += snip.mkline("bar\n")

            … would have returned:

                foo
            bar

            IOW, `snip.mkline()` allows to copy the level of indentation of the previous line.
            The latter can be changed via:

                    - snip.shift()
                    - snip.unshift()
                    - snip.reset_indent()


    snip += line

            Equivalent to:
            snip.rv += '\n' + snip.mkline(line)


    snip.shift(123)
    snip >> 123

            Increases the default  indentation level used by `mkline()` by the
            number of spaces defined by 'shiftwidth', 123 times.

    snip.unshift(123)
    snip << 123

            Decreases the  default indentation level  used by `mkline()`  by the
            number of spaces defined by 'shiftwidth', 123 times.

    snip.reset_indent()

            Resets the indentation level to its initial value.


    snip.rv = "i1\n"
    snip.rv += snip.mkline("i1\n")
    snip.shift(1)
    snip.rv += snip.mkline("i2\n")
    snip.unshift(2)
    snip.rv += snip.mkline("i0\n")
    snip.shift(3)
    snip.rv += snip.mkline("i3")`

            Returns:

                i1
                i1
                    i2
            i0
                        i3


    snip.opt(var, default)

            Returns the value of `var` (can be a variable or an option).
            If it doesn't exist, returns `default`.

The 'snip' object provides some properties as well:

    snip.rv

            'rv' is  the return  value, the  text that  will replace  the python
            block  in the  snippet definition. It  is initialized  to the  empty
            string.

    snip.c

            The  text  currently  in  the python  block's  position  within  the
            snippet.  It  is set  to empty  string as  soon as  interpolation is
            completed.

            Thus:

                    if snip.c != ''
            or
                    if not snip.c

            ... makes sure that the interpolation is only done once.
            You can read this last statement as:

                    “if the tabstop has not yet a current value”

            Usage example:

                    snippet uuid "UUID" b
                    `!p
                    import uuid
                    if not snip.c:
                        snip.rv = uuid.uuid4().hex
                    `
                    endsnippet

            Without `if not snip.c`, you'll get the error:

                    'The snippets content did not converge: Check for Cyclic '

            Since there can be dependencies between text objects, UltiSnips runs
            each of them several times  (until they no longer change). Which can
            be  an issue  for random  strings, because  their value  will always
            change, and thus never “converge”.

                    https://github.com/SirVer/ultisnips/issues/375#issuecomment-55115227

            `if not snip.c` can be used to prevent “cyclic” dependencies:

                    One text  object (A)  depends on  another (B),  which itself
                    depends on (A).   When UltiSnips will evaluate  (A), it will
                    affect (B), which will affect (A)…

    snip.p

            Last  selected  placeholder. Will  contain placeholder  object  with
            following properties:

            ┌─────────────────────┬────────────────────────────────────────────────────┐
            │ snip.p.current_text │ text in the placeholder on the moment of selection │
            ├─────────────────────┼────────────────────────────────────────────────────┤
            │ snip.p.start        │ placeholder start on the moment of selection       │
            ├─────────────────────┼────────────────────────────────────────────────────┤
            │ snip.p.end          │ placeholder end on the moment of selection         │
            └─────────────────────┴────────────────────────────────────────────────────┘

    snip.v

            Info about the `${VISUAL}` placeholder. The property has two attributes:

                    - snip.v.mode   v  V  ^V
                    - snip.v.text   text that was selected

#
#
#
## Interpolation

    `date`
    `!v strftime('%c')`
    `!p python code`

            Interpolation d'une commande shell ou d'une expression Vim.

            Les backticks encadrent la commande / expression interpolée.
            `!v` indique que ce qui suit est une expression Vim.
            `!p` "                           du code python.


    snippet wpm "average speed" b
    I typed ${1:750} words in ${2:30} minutes; my speed is `!p
    snip.rv = float(t[1]) / float(t[2])
    ` words per minute
    endsnippet

            Si on écrit  un bloc de code  python, après le `!p`,  on peut écrire
            chaque instruction sur une ligne dédiée, pour + de lisibilité.

            De  plus, UltiSnips  configure  automatiquement  certains objets  et
            variables python, valables au sein du bloc de code:

                    - snip.rv    = variable 'return value';
                                   sa valeur sera interpolée au sein du document

                    - t          = liste dont les éléments contiennent le texte
                                   inséré dans les différents tabstops;
                                   ex:    t[1] = $1, t[2] = $2

            Ici, `float()` est une fonction python, et non Vim.


                                               NOTE:

            Quelle différence entre `!p` et `#!/usr/bin/python`?
            Qd une interpolation débute par un  shebang, la sortie du script est
            insérée dans le buffer.
            Mais `!p` est différent.
            Avec `!p`, UltiSnips  ignore la sortie de  l'expression python qu'on
            écrit.
            Il ne fait que l'évaluer.
            Pour  insérer  sa  sortie  dans  le buffer,  il  faut  l'affecter  à
            `snip.rv`.


                                               NOTE:

            Si on modifie la valeur d'un  tabstop en mode normal via la commande
            `r`, l'interpolation est mise à jour.
            Ça  peut donner  l'impression  de travailler  avec  un tableur  (pgm
            manipulant des feuilles de calcul).

## Substitution

On  peut  réinsérer  automatiquement  un  tabstop où  l'on  veut,  on  parle  de
“mirroring“.
On peut également effectuer une substitution au sein du tabstop miroir.


    snippet fmatter
    ---
    title: ${1:my placeholder}
    ---
    # $1
    $0
    endsnippet

            Le 1er tabstop ($1) est répété 2 fois.
            Cela implique que lorsqu'on lui donne  une valeur, le même texte est
            inséré automatiquement une 2e fois, là où se trouve sa 2e occurrence
            (ici: `# $1`).

            On dit que le tabstop est “mirrored“ (reflété).


    snippet t "A simple HTML tag" bm
    <${1:div}>
    </${1/(\w+).*/$1/}>
    endsnippet

            On applique une transformation sur le miroir.
            Il s'agit de la substitution:    :s/(\w+).*/$1/

            Le $1 au  sein de la substitution ne correspond  pas au 1er tabstop,
            mais à la 1e sous-expression capturée dans le pattern (\w+).
            L'expression régulière est gérée par python et non par Vim.


                                               NOTE:

            La chaîne de remplacement peut contenir des variables `$i`, qui font
            référence au sous-expressions capturées dans le pattern.
            Ici, `$1` fait référence au 1er mot capturé dans le 1er tabstop.

            `$0` est spéciale: elle fait référence à l'ensemble du match (équivaut à `&` ou `\0` dans Vim).


    snippet cond
    ${1:some_text}
    ${1/(a)|.*/(?1:foo:bar)/}
    endsnippet

            Le miroir subit une substitution conditionnelle, qui:

                    1. cherche et capture le pattern `a`:

                    2. pour le remplacer par:    (?1:foo:bar)

            Ça  signifie  que si  le  texte  inséré  dans le  tabstop  d'origine
            commence par  un `a`,  il sera  remplacé par  `foo` dans  le miroir,
            autrement il sera totalement (`|.*`) remplacé par `bar`.


            Section de l'aide pertinente:  :h Ultisnips-replacement-string


                                               NOTE:

            Le token `?1` permet de tester si le groupe 1 a capturé qch ou pas.
            Le  token  `()`  permet  de  demander  à  Ultisnips  de  traiter  le
            remplacement comme une expression à évaluer.
            Similaire à `\=` pour la commande `:s` dans Vim.


    ${1/(a)|(b)|.*/(?1:foo)(?2:bar)/}

            Ici, la substitution:

                    1. cherche le pattern:       (a)|(b)|.*
                       en capturant `a` ou `b` si le caractère est trouvé

                    2. pour le remplacer par:    (?1:foo)(?2:bar)

            Ce qui  signifie que si  le texte  inséré dans le  tabstop d'origine
            commence par un:

                    - `a`, le miroir commencera par `foo`
                    - `b`, "                        `bar`
                    - ni `a`, ni `b`, le miroir sera vide


                                               NOTE:

            On   remarque   au   passage   qu'il  semble   que   python   ajoute
            automatiquement l'ancre `^` au début du pattern.

                                               NOTE:

            On   pourrait   omettre  la   dernière   branche   `|.*`;  le   code
            fonctionnerait pratiquement à l'identique.
            À ceci près que le texte  inséré dans le tabstop d'origine ne serait
            pas supprimé  dans le miroir  lorsqu'il ne  commence pas par  `a` ou
            `b`.


    ${1/(a)|(b)|.*/(?1:foo:bar)(?2:baz:qux)/}

            Si le texte inséré dans le tabstop d'origine commence par un:

                    - `a`, le miroir commencera par `fooqux`
                    - `b`, "                        `barbaz`
                    - ni `a`, ni `b`, le miroir commencera par `barqux`

            Illustre qu'un miroir peut être aussi intelligent qu'on veut; i.e.
            être capable d'effectuer autant  de substitutions que nécessaire, et
            choisir  la  bonne  en  fonction d'une  caractéristique  du  tabstop
            d'origine.

## Misc

When  you  write some  python  code  (function/interpolation),  you can  add  an
arbitrary key  to `snip`, but it  will be removed as  soon as the code  has been
processed.

OTOH, `snip` persists during the whole  expansion of a snippet.
Some of its keys are also persistent: `context` is one of them.
So, if you assign some data to the `context` key of `snip`, in some python code,
it will be accessible to the next one.

You can use this to pass arbitrary information from a statement to another.

Finally, if you create a new variable:

   - in a python function, it will be local to the function:

       NOT accessible to the next processed function

   - in a python interpolation, it will be local to the snippet:

       ACCESSIBLE to the next interpolation

---

Don't confuse the method `re.match()` with the object `match`.

`re.match()` allows you to compare a string with a regex.
`match` is automatically created by UltiSnips when you use the `r` option to
create a snippet whose tab trigger is a regex.

It contains the match and all captured groups resulting from the comparison
between the regex of the tab trigger and the text which was in front of the
cursor when Tab was pressed.

---

To retrieve a capturing group, use the `group()` method:

        match.group(123)
        snip.context.group(123)

                123th  captured group,  in the  regex matched  against the  text
                before the cursor; the regex being used in:

                - the tab trigger       (with the `r` option)
                - the expression field  (with the `e` option)

---

What's the difference between:

        $0
          ${VISUAL}
        $0${VISUAL}
       ${0:${VISUAL}}

`${VISUAL}` is only a PLACEHOLDER automatically  replaced by the contents of the
last  visual selection. It  is NOT  a tabstop:  by default,  UltiSnips does  not
select it, and therefore does not position the cursor somewhere near it.

OTOH, `$0` IS a tabstop.
And as all tabstops, it can have a placeholder.
You can leverage this to select the contents of `${VISUAL}` by writing it as the
placeholder of `$0`.
Or any other tabstop.

---

NEVER use a use Vim command to modify the buffer.
UltiSnips would not be able to track changes in buffer from actions.
It would raise an error.
Instead, modify a line of the buffer via `snip.buffer`.

---

You can't use a line continuation in a VimL interpolation.

---

Inside a snippet, you can invoke a python function in 2 ways:

   - as a simple routine:                          `!p           func()`
   - for its output to be inserted in the buffer:  `!p snip.rv = func()`

---

There's no need to invoke a Vim function with `vim.command()`.
Use `vim.eval()` instead. It's less verbose:

        vim.command('call Func()')
        vim.eval('Func()')

`vim.command()` should be reserved to Ex commands (!= `:call`):

        vim.command('12,34delete')

---

In a python interpolation, the modules:

   - os
   - random
   - re
   - string
   - vim

... are pre-imported.
Other modules can be imported using the python 'import' command:

    `!p
    import uuid
    ...
    `

They are NOT automatically imported in your custom modules `~/.vim/pythonx/*.py`.
You must do it yourself.

## Configuration

    :echo has('python')
    :echo has('python3')

            Tester si Vim a été compilé avec python 2.x ou 3.x


    :py  import sys; print(sys.version)
    :py3 import sys; print(sys.version)

            Déterminer la version de l'interpréteur python 2.x / 3.x contre laquelle Vim a été compilé.


   let g:UltiSnipsUsePythonVersion = 2
   let g:UltiSnipsUsePythonVersion = 3

            Demander à Vim d'utiliser python 2.x ou 3.x

            Cette configuration est généralement inutile, car UltiSnips devrait détecter automatiquement
            quelle version de l'interpréteur python a été compilé dans Vim.
            Toutefois, ça peut être nécessaire si cette détection échoue.


UltiSnips permet de développer un tab trigger en snippet.


Qd UltiSnips doit développer un tab trigger et qu'il cherche le fichier dans lequel il est défini,
il regarde dans un certain nb de dossiers.

Ces derniers sont définis par les variables `g:UltiSnipsSnippetsDir` et `g:UltiSnipsSnippetDirectories`.
Quelle différence entre les 2 ?

La 1e variable:

   - N'est pas définie par défaut

   - Attend comme valeur une chaîne contenant un chemin absolu vers un dossier.
     Le dernier composant du chemin ne doit pas être 'snippets'. En effet, qd
     UltiSnips entre dans un dossier portant le nom 'snippets', il considère que
     les fichiers qui s'y trouvent utilisent le format SnipMate (différent du
     format UltiSnips).

   - Est utile pour configurer le chemin vers notre dossier de snippets privé.
     Ex:

           let g:UltiSnipsSnippetsDir = '~/.vim/UltiSnips/'

   - Est le 1er dossier dans lequel UltiSnips cherche le fichier de snippets
     à éditer qd on tape :USE


La 2e variable:

   - Vaut ['UltiSnips'] par défaut.

   - Attend comme valeur une liste de chemins relatifs ou absolus. Si le chemin
     est relatif, UltiSnips cherchera à compléter le chemin via tous les
     dossiers du &rtp.

   - Est utile pour pouvoir utiliser immédiatement des snippets tiers, tq:

           https://github.com/honza/vim-snippets

   - Si on lui affecte un seul élément correspondant à un chemin absolu, alors
     UltiSnips ne cherchera pas de snippets dans `&rtp` ce qui peut améliorer
     les performances.

---

Note that I can't use `g:UltiSnipsSnippetsDir` atm.
No matter how I assign it a value, the snippets in there are not used.
It may be due to an issue:
<https://github.com/SirVer/ultisnips/issues/711>

See also this comment: <https://github.com/SirVer/ultisnips/issues/711#issuecomment-227159748>

Also, note the absence of an `s` at the end of `Snippet` in one of the variable, but not in the other:

                      v
    g:UltiSnipsSnippetsDir
    g:UltiSnipsSnippetDirectories
                     ^
                     no 's' at the end

Also, avoid using `~` at the start of a path; it may not be expanded.
Prefer `$HOME`.

---

À l'intérieur de ces dossiers, le nom d'un fichier de snippets doit suivre un certain schéma parmi
plusieurs possibles. Tous dépendent du type de fichiers courant.
Pex, si le buffer courant est de type vim, UltiSnips cherchera dans un fichier nommé:

   - vim.snippets

   - vim_foo.snippets
   - vim/foo
   - vim/foo.snippets

   - all.snippets
   - all/foo.snippets

UltiSnips considère `all` comme une sorte de type de fichiers universel.
`all.snippets` est utile pour définir des snippets indépendant du type de fichiers,
comme pex l'insertion d'une date.


    :UltiSnipsEdit
    :USE (custom)

            Édite le fichier de snippets correspondant au type de fichier du buffer courant.

            Dans un 1er temps, UltiSnips cherche dans le dossier `g:UltiSnipsSnippetsDir`, puis
            s'il ne trouve rien, il cherche dans les dossiers `g:UltiSnipsSnippetDirectories`.


   :UltiSnipsAddFiletypes rails.ruby
                          │     │
                          │     └── … doit provoquer l'activation des snippets ruby
                          └── l'activation des snippets rails …

            Demande à ce que les snippets ruby soient chargés qd on édite un buffer rails.

            À taper dans un buffer rails, ou à écrire dans un filetype plugin rails.
            On pourrait également taper/écrire:

                    :UltiSnipsAddFiletypes ruby.programming

            L'ordre de priorité des snippets (en cas de conflit) serait alors:

                    rails > ruby > programming > all


    ┌────────────────────────────────┬───────────────────┬─────────────────┬─────────────────────────────────┐
    │ variable                       │ valeur par défaut │ valeur actuelle │ effet                           │
    ├────────────────────────────────┼───────────────────┼─────────────────┼─────────────────────────────────┤
    │ g:UltiSnipsExpandTrigger       │ Tab               │                 │ développer un tab trigger       │
    │                                │                   │                 │                                 │
    │ g:UltiSnipsListSnippets        │ C-Tab             │ C-Tab           │ lister les snippets disponibles │
    │                                │                   │                 │                                 │
    │ g:UltiSnipsJumpForwardTrigger  │ C-j               │ S-F18           │ sauter vers le prochain tabstop │
    │                                │                   │                 │                                 │
    │ g:UltiSnipsJumpBackwardTrigger │ C-k               │ S-F19           │ "              précédent "      │
    └────────────────────────────────┴───────────────────┴─────────────────┴─────────────────────────────────┘


                                               NOTE:

            Il faut configurer ces variables avant l'appel de fin à une fonction du plugin manager.
            Pour vim-plug, il s'agit de la ligne:

                    call plug#end()


                                               NOTE:

            Les mappings de saut (C-j et C-k par défaut) ne sont installés que pendant le développement
            d'un snippet, et détruits immédiatement après pour ne pas interférer avec des mappings utilisateurs.


    UltiSnips#JumpForwards()
    UltiSnips#JumpBackwards()

    UltiSnips#ExpandSnippet()
    UltiSnips#ExpandSnippetOrJump()

            Il s'agit  de 4 fonctions  publics dont on  peut se servir  pour des
            configurations avancées.

            Les  2 premières  fonctions  servent  à sauter  vers  le prochain  /
            précédent tabstop.
            Les 2 dernières demandent le développement d'un tab trigger.


                                               NOTE:

            Quelle différence entre les 2 fonctions de développement ?

            ┌───────────────────────┬──────────────────────────────────────────────────────────┐
            │ ExpandSnippetOrJump() │ à utiliser si on a choisi la même touche pour développer │
            │                       │ et sauver vers l'avant:                                  │
            │                       │                                                          │
            │                       │ g:UltiSnipsExpandTrigger = g:UltiSnipsJumpForwardTrigger │
            ├───────────────────────┼──────────────────────────────────────────────────────────┤
            │ ExpandSnippet()       │ à utiliser si on a choisi des touches différentes        │
            └───────────────────────┴──────────────────────────────────────────────────────────┘


                                               NOTE:

            Si on a choisi la même touche pour développer et sauter vers l'avant, pex Tab,
            UltiSnips installe 2 mappings globaux:

                    i  <Tab>       * <C-R>=UltiSnips#ExpandSnippetOrJump()<cr>
                    s  <Tab>       * <Esc>:call UltiSnips#ExpandSnippetOrJump()<cr>

            … et 2 mappings locaux au buffer:

                    i  <S-Tab>     *@<C-R>=UltiSnips#JumpBackwards()<cr>
                    s  <S-Tab>     *@<Esc>:call UltiSnips#JumpBackwards()<cr>

            Les  locaux sont  installés  dès qu'un  tab  trigger est  développé,
            et   supprimés   dès   que   le  développement   est   terminé   (:h
            UltiSnips-triggers):

                    UltiSnips will only map the jump triggers while a snippet is
                    active to interfere as little as possible with other mappings.


                                               NOTE:

            Ces 4 fonctions produisent un code de retour chacun stocké dans une variable globale,
            dont la valeur code un succès ou un échec:

                    g:ulti_expand_res            0: fail, 1: success
                    g:ulti_expand_or_jump_res    0: fail, 1: expand, 2: jump
                    g:ulti_jump_forwards_res     0: fail, 1: success
                    g:ulti_jump_backwards_res    0: fail, 1: success

## Syntaxe basique

Dans un fichier où des snippets sont définis, on peut faire commencer une ligne par un mot-clé pour
exécuter une directive. Parmi ces mots-clés, on trouve:

   - extends
   - priority
   - clearsnippets
   - snippet
   - endsnippet

   - context
   - pre_expand
   - post_expand
   - post_jump


    extends perl, ruby

            UltiSnips active tous les snippets liés aux types de fichiers dont le nom suit.
            Pex ici:    perl, ruby

            On peut utiliser  autant de directives `extends` qu'on  veut, et les
            placer où on veut.


    priority 42

            Les snippets définis après cette ligne ont une priorité de 42.
            Sans cette directive, par défaut, les snippets ont une priorité de 0.

            En cas de conflit, càd si un tab trigger est utilisé dans 2 snippets
            différents, celui ayant la plus haute priorité gagne.


    snippet tab_trigger "description" options

            Syntaxe de base pour déclarer un snippet.
            La description et les options sont optionnelles.


                                               NOTE:

            Si le  tab trigger contient  un espace,  il faut l'encadrer  avec un
            caractère qui n'apparaît pas en son sein, comme des guillemets.
            Ex:

                    snippet "tab trigger"

            Si on veut en plus qu'il  contienne des guillemets, on peut utiliser
            le point d'exclamation:

                    snippet !"tab trigger"!

            Qd plusieurs snippets  ont le même tab trigger et  la même priorité,
            UltiSnips affiche la liste des  snippets possibles, chacun avec leur
            description.
            C'est à ce moment-là que la description est utile.
            Elle permet à l'utilisateur de choisir le bon.

            Exception:
            En cas  de conflit entre  2 snippets, l'un d'eux  utilisant l'option
            `e` mais  pas l'autre,  celui qui utilise  `e` a  automatiquement la
            priorité.
            Ça permet  de définir un  snippet “fallback” qd la  condition testée
            par l'expression du snippet utilisant `e` échoue.


                                               NOTE:

            Pour  augmenter  le niveau  d'indentation  d'une  ligne au  sein  du
            snippet, il faut la préfixer avec un caractère littéral.
            Qd  le  snippet  sera  développé,   le  caractère  tab  sera  inséra
            littéralement  ou remplacé  par  des espaces  suivant  la valeur  de
            'expandtab'.

            Dans un snippet, on peut voir le caractère tab comme l'appui sur la touche tab.


                                               NOTE:

            ┌────────┬──────────────────────────────────────────────────────────────────────┐
            │ option │ signification                                                        │
            ├────────┼──────────────────────────────────────────────────────────────────────┤
            │ b      │ beginning of line                                                    │
            │        │                                                                      │
            │        │ ne développer le tab trigger que s'il se trouve au début d'une ligne │
            ├────────┼──────────────────────────────────────────────────────────────────────┤
            │ e      │ expression                                                           │
            │        │                                                                      │
            │        │ le snippet n'est développé que si l'expression est vraie             │
            ├────────┼──────────────────────────────────────────────────────────────────────┤
            │ i      │ in-word                                                              │
            │        │                                                                      │
            │        │ autoriser le développement du snippet, même si le tab trigger        │
            │        │ est au milieu d'un mot                                               │
            │        │                                                                      │
            │        │ par défaut, un snippet n'est développé que si le tab trigger         │
            │        │ est en début de ligne ou précédé de whitespace                       │
            ├────────┼──────────────────────────────────────────────────────────────────────┤
            │ m      │ trim                                                                 │
            │        │                                                                      │
            │        │ les trailing whitespace de toutes les lignes du snippet              │
            ├────────┼──────────────────────────────────────────────────────────────────────┤
            │ r      │ regex                                                                │
            │        │                                                                      │
            │        │ interpréter le tab trigger comme une regex python                    │
            └────────┴──────────────────────────────────────────────────────────────────────┘

            Pour des infos concernant les options dispo:

                    :h UltiSnips-snippet-options


    snippet tab_trigger
    \`texte entouré de backticks\`
    endsnippet

            Le  caractère backtick  ayant  un sens  spécial  pour UltiSnips,  si
            on  veut  en insérer  un  littéralement  dans  un snippet,  il  faut
            l'échapper.


    snippet fmatter
    ---
    title: $1
    date: $2
    tags: $3
    ---
    $0
    endsnippet

            $1, $2, $3 et $0 correspondent à des tabstops.

            On peut naviguer entre les tabstops via les raccourcis définis par:

                    g:UltiSnipsJumpForwardTrigger
            et
                    g:UltiSnipsJumpBackwardTrigger

            Le  tabstop $0  est spécial,  car qd  on arrive  sur lui,  UltiSnips
            considère  que  le développement  du  tab  trigger et  l'édition  du
            snippet sont terminés.
            Déplacer  le  curseur en-dehors  du  snippet  termine également  son
            développement.

            Dès lors, on ne peut plus naviguer entre les autres tabstops.

            Tant qu'on reste au-sein du  snippet, les raccourcis fonctionnent en
            mode insertion et sélection.


    title: ${1:my placeholder}

            On définit un placeholder pour le tabstop:

                    $1    →    ${1:my placeholder}

            Ici il  s'agit d'une simple  chaîne de caractères, mais  on pourrait
            aussi utiliser:

                    - une interpolation d'une commande shell/VimL/python… entre des backticks. Ex:

                            ${1:`date`}

                    - autre tabstop

            Qd  notre   curseur  est  positionné   sur  un  tabstop   doté  d'un
            placeholder,  ce  dernier est  sélectionné  visuellement,  et on  se
            trouve en mode 'select'.
            Ainsi,  n'importe quel  caractère tapé  remplace automatiquement  le
            placeholder, et on peut continuer  à insérer des caractères ensuite,
            car on est alors en mode 'insertion'.


    snippet a
    <a href="$1"${2: class="${3:link}"}>
        $0
    </a>
    endsnippet

            Le 2e placeholder:

                    class="…"

            … contient lui-même un tabstop:

                    ${3:link}

            Imbriquer 2  tabstops permet  d'exprimer une relation  de dépendance
            entre eux: l'un est une partie de l'autre.

            Ici,  si  on  supprime  l'attribut, la  valeur  est  automatiquement
            supprimée.
            Ce qui  est souhaitable, car  on ne  pourrait pas avoir  un attribut
            (`class`) HTML sans valeur, ni l'inverse, une valeur sans attribut.


                                               NOTE:

            Le placeholder `link` du 3e tabstop est important.
            Sans  lui,  si   on  supprime  le  2e  tabstop,  le   3e  n'est  pas
            automatiquement supprimé.
            Plus généralement, un tabstop est automatiquement supprimé ssi:

                - il est inclus dans le placeholder d'un autre tabstop
                - il est suivi d'un texte qcq à l'intérieur du placeholder

                    snippet a
                    foo ${1:bar $2}($3)
                    endsnippet

                        a Tab
                            →  foo bar()
                                   └─┤
                                     └ sélectionné

                        C-h
                            → foo |()
                                  ^
                                  curseur

                        Tab
                            → foo |()
                                  ✘ le 2e tabstop n'a pas été automatiquement supprimé
                                    raison pour laquelle le curseur reste sur place

                    snippet a
                    foo ${1:bar $2 baz}($3)
                    endsnippet

                        a Tab
                            →  foo bar()
                            →  foo bar  baz()
                                   └──────┤
                                          └ sélectionné

                        C-h
                            → foo |()
                                  ^
                                  curseur

                        Tab
                            → foo (|)
                                   ✔


    snippet date
    ${2:${1:`date +%d`}.`date +%m`}.`date +%Y`
    endsnippet

            Autre exemple, où un placeholder contient lui-même un tabstop.

            Décomposition de l'imbrication:

                    ${2:${1:`date +%d`}.`date +%m`}
                        │   │          │
                        │   │          └── ce n'est pas un opérateur de concaténation (juste un point)
                        │   └── début du placeholder du 1er tabstop:    `date +%d`
                        └── début du placeholder du 2e tabstop:         ${1:…}.`date +%m`

            Cette déclaration exprime que le jour dépend du mois.
            Ainsi, si on supprime le mois, le jour sera lui-aussi automatiquement supprimé.

            On aurait pu aussi écrire:

                    ${1:`date +%d`}.${2:`date +%m`}

            … mais dans ce cas, il n'y a plus de relations de dépendance.


    snippet "chap?t?e?r?" "Latex chapter" r
    chapter
    \section{chapter}
       $0
    \end{chapter}
    endsnippet

            Dans cet exemple, le tab trigger prend la forme d'une expression régulière python:

                    "chap?t?e?r?"

            Une  expression régulière  doit être  encadrée avec  des quotes,  ou n'importe  quel
            caractère absent de l'expression.

            Ici, elle équivaut à `\vcha%[pter]>`.
            On peut donc développer plusieurs tab triggers ayant un même préfixe en un même snippet.

            Si le snippet contient du code python, celui-ci peut accéder au texte matché par la regex
            via la variable locale `match`.


    snippet if "test" bm
    if ${1:condition}
        ${0:${VISUAL:MyCmd}}
    endif
    endsnippet

            Ce snippet permet d'entourer une commande Ex, avec un bloc `if`.

            Pour ce faire, il faut:

                    1. sélectionner la commande Ex

                    2. appuyer sur Tab pour qu'UltiSnips capture la sélection
                       et nous fasse passer en mode insertion

                    3. insérer `if` et ré-appuyer sur Tab pour développer ce snippet

            Le snippet utilise le placeholder spécial `${VISUAL}`.
            Ce dernier est donné en valeur par défaut au tabstop final 0.

            Il reçoit lui-même en valeur par défaut `MyCmd`.
            Ainsi qd on appuiera sur Tab, `${VISUAL}` sera développé en:

                    - `MyCmd` depuis le mode insertion
                    - la dernière sélection visuelle depuis le mode visuel


                                               NOTE:

            Sans valeur par  défaut, le placeholder fonctionne  toujours même qd
            on appuie sur  Tab en mode insertion: il est  alors développé en une
            chaîne vide.

            Les accolades au sein du placeholder sont obligatoires.
            En  leur absence,  UltiSnips  interpréterait  `${VISUAL}` comme  une
            simple chaîne littérale.


                                               NOTE:

            Si  on  veut  apporter  une modification  à  la  dernière  sélection
            visuelle, il faut  passer par une interpolation  python, et utiliser
            `snip.v.text` au lieu de `${VISUAL}`.

            Par exemple, pour  supprimer le 1er caractère  `x` qu'elle contient,
            on écrira:

                    `!p snip.rv = snip.v.text.strip('x')`

#
##
##
# Issues
## I have a very long line in my snippet.  It's hard to read, and it breaks syntax highligting!

Use a VimL interpolation whose return value is an empty string.
It won't add anything to the snippet, but you can break it on several lines:

        some very long line

        ⇒

        some very `!v ''
        `long line

## `\U` doesn't work in the replacement field of a substitution in a mirror!

Use `\E`, even if you don't need it.

    snippet th "Text Header" bm
    .TH $1 ${1/.*/\U$0\E/}
    endsnippet

##
#
#
# TODO

Document the `append()` method of the `snip.buffer` object.

It's not documented in the help.
It's just used in a single example:

                                                        vvvvvvvvvv
    pre_expand "del snip.buffer[snip.line]; snip.buffer.append(''); snip.cursor.set(len(snip.buffer)-1, 0)"
    snippet x
    def $1():
            ${2:${VISUAL}}
    endsnippet

---

Learn how to use `pyrasite` to debug python code used in a snippet:

    https://www.reddit.com/r/vim/comments/am8dc9/writing_python_plugins_i_wish_i_had_known_about/
    https://github.com/lmacken/pyrasite

---

Read these PRs:

    pre/post-expand and post-jump actions

            https://github.com/SirVer/ultisnips/pull/507

    Autotrigger

            https://github.com/SirVer/ultisnips/pull/539

And this issue:

    Markdown table snippet breaks on various dimensions

            https://github.com/SirVer/ultisnips/issues/877

And this one:

            https://vi.stackexchange.com/questions/11240/ultisnips-optional-line

---

Watch all gifs from `vim-pythonx` and `vim-snippets`.
Re-read all your snippets (fix/improve).
Re-read this file.
Understand 3 advanced examples:

        https://github.com/SirVer/ultisnips/tree/master/doc/examples/autojump-if-empty
        https://github.com/SirVer/ultisnips/tree/master/doc/examples/snippets-aliasing
        https://github.com/SirVer/ultisnips/tree/master/doc/examples/tabstop-generation

Read documentation.


The following events:

    UltiSnipsEnterFirstSnippet
    UltiSnipsExitLastSnippet

... are NOT fired  when the snippet is  automatically expanded (like with  `fu` in a
vim file).
At least, it seems so.
Make some tests.
Document the results.
It may be a bug.
Report it.

---

https://github.com/reconquest/vim-pythonx/ (1163 sloc, after removing `tests` and all `__init__.py` files)
https://github.com/reconquest/vim-pythonx/issues/11

        Python library

https://github.com/reconquest/snippets

        Snippets

https://github.com/SirVer/ultisnips/pull/507

        PR: pre/post-expand and post-jump actions

https://github.com/seletskiy/dotfiles/blob/8e04f6a47fa1509be96094e5c8923f4b49b22775/.vim/UltiSnips/go.snippets#L11-23

        Interesting snippet.

                “It   covers  all   three   cases   using  one   single-character
                trigger. You don't need to remember three different snippets.”

---

Create   snippets  for   `context`,  `pre_expand`,   `post_expand`,  `post_jump`
statements and for interpolations.
Your goal  should be to  teach them everything  you know about  those statements
(which variables/methods can be used).
This way, no more: “what the fuck was  the name of the variable to refer to last
visual text”?

---

Document the `w` option.
Answer the question:

> By default,  a tab  trigger is  only expanded if  it's a  whole word,  so what
> difference does `w` make?

Answer:
By default, the tab trigger must be preceded by a whitespace.
With `w`, any character outside `'isk'` will do.

---

Every  time  you've  noted  that  something doesn't  work  in  an  interpolation
(inaccessible variable, method), check whether  you can bypass the limitation by
creating a simple helper function.
That's what is done here:

        https://github.com/SirVer/ultisnips/blob/master/doc/examples/snippets-aliasing/README.md

... to access `vim.current.window.buffer` and `vim.current.window.cursor` inside
an interpolation.

Update:
In  fact, there's  no  need  of a  helper  function, `vim.current.window`  works
directly from an interpolation.

---

Add sth like this  for Neovim; it could make neovim  faster (especially if you
use UltiSnips):

    let g:loaded_python_provider = 1
    let g:python_host_skip_check=1
    let g:python_host_prog = '/usr/bin/python'
    let g:python3_host_skip_check=1
    let g:python3_host_prog = '/usr/bin/python3'

Also, disable automatic expansion of snippets with this:

    augroup ultisnips_no_auto_expansion
        au!
        au VimEnter * au! UltiSnips_AutoTrigger
    augroup END

It has a significant impact in Neovim.
MWE:

    1000i some text
        → several seconds with the autocmd
          1 or 2 without

Also, read this:
https://github.com/neovim/neovim/issues/5702
https://github.com/neovim/neovim/issues/7063

