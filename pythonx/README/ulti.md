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

