# Misc

To  store your  python helper  functions, you  can use  any sub-directory  named
`pythonx` inside a directory of the runtimepath.

For more info, see `:h pythonx-directory`.

---

UltiSnips doesn't take into account a change in a function of a custom module,
until you restart Vim.

---

A function in a custom module can't access the `snip` and `vim` objects.
If you need them for a given function, do one of the 2 following things:

 - from your custom module, outside any function, import `vim`
 - from the snippet where you call your function, pass `vim` and/or `snip` as arguments

Note that it seems  you can't import `snip`. So, the only way  for a function to
access it, relies on you passing it as an argument.

---

Contrary to an interpolation, in which UltiSnips automatically pre-import the modules:

 - os
 - random
 - re
 - string
 - vim

… no module is pre-imported in a custom python module.

If you need one of them in one of your helper function, import it at the beginning
of the file.

---

When you need to debug some code and capture the value of a variable, try this:

    vim.command('let g:debug = ' + '"' + str(your_variable) + '"')

`str()` must be invoked to cast `your_variable` into a string.
Contrary to  Vim's `string()`, if  `your_variable` is already a  string, `str()`
won't add quotes inside it, which is why, here, you need to concatenate 2 '"'.
A double invocation won't have any effect:

    str(str(your_variable))
    ✘

    '"' + str(your_variable) + '"'
    ✔
