# What's the purpose of this directory?

From `:h pythonx`:

> If you want to use a module, you can put it in the `{rtp}/pythonx` directory.
> See `|pythonx-directory|`.

So, it can be used to store custom python modules, in which you define functions
that you will invoke from your snippets.

# If I modify a function, does Vim catch the change immediately?

No, you have to restart the session.

# Does UltiSnips pre-import some modules in the scope of a custom python module?

No.

If you need a particular module in one of your helper function, import it at the
beginning of the file.

# How to access the `snip` object from a function?

You must pass it as an argument from the snippet definition:

                          `snip` is passed to `func()` as an argument
                          v
        post_expand "func(snip)"
        snippet foo "" bm
        endsnippet

# How to capture the value of a variable in `g:debug`?

        vim.command('let g:debug = ' + '"' + str(your_variable) + '"')

`str()` must be invoked to cast `your_variable` into a string.

Contrary to  Vim's `string()`, if  `your_variable` is already a  string, `str()`
won't add quotes inside it.
A double invocation won't have any effect:

        str(str(your_variable))
        ✘

Which is why, here, you need to concatenate two double quotes.

        '"' + str(your_variable) + '"'
        ✔

# Is it possible to prevent UltiSnips from consuming the tab trigger?

Only  if you  use a  `pre_expand`  statement, and  from the  expression/function
invoked by the latter, you invoke one of these:

        • snip.cursor.preserve()

        • snip.expand_anon()

# How to remove the tab trigger if UltiSnips didn't do it?   (assuming it's alone on the line)

        snip.buffer[snip.line] = ''

##
# Issues
## How to deal with “line under the cursor was modified, but "snip.cursor" variable is not set”?

This issue arises when  you modify the line of the  tab trigger, without setting
the new position of the cursor.

Invoke one of these:

        snip.cursor.preserve()
        snip.cursor.set(snip.cursor[0], snip.cursor[1])

---

MWE:

        global !p
        def func(snip):
            if 'foobar' in vim.current.buffer.name:
                anon_snip_body = 'hello world'
            else:
                snip.cursor.preserve()
                return

            snip.buffer[snip.line] = ''
            snip.expand_anon(anon_snip_body)
        endglobal

        pre_expand "func(snip)"
        snippet ab "" Abm
        endsnippet

This snippet expands the tab trigger `ab` into `hello world` iff the path to the
current file contains the word `foobar`.

## I try to compare the output of `vim.eval('VimL expr')` to a number, but it fails!

The output of `vim.eval()` is a string not a number.

You need to convert it into a number using the `int()` function:

           ✘
           v
        if vim.eval('VimL expr') == 123:

           ✔
           v
        if int(vim.eval('VimL expr')) == 123:

