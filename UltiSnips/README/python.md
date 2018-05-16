# How to get the name of the current file?

        os.path.basename(vim.current.buffer.name)

# How to get the name of the current file, without its extension?

        os.path.splitext(os.path.basename(vim.current.buffer.name))[0]

# How to get the path to the directory `foo/` out of the path `/tmp/foo/bar`?

        os.path.dirname('/tmp/foo/bar')

# How to get the name of the directory of the current file?

        os.path.basename(os.path.dirname(vim.current.buffer.name))
                │                │
                │                └ remove last past path component
                │
                └ get last path component

# What's a python equivalent of `printf('%s %s, 'one', 'two')`?

        '{} {}'.format('one', 'two')

# How to improve the readability of the next code (and avoid the “magic number” effect)?

        def func():
            ...
            if var = 42


Like this:

↣
      def func():
            ...
            ┌ “description”: name which conveys the meaning of `42` inside this function
            │
            desc = 42
            if var = desc
↢


Or shorter:

↣
        def func(desc = 42):
            ...
            if var = desc
↢

# What does `splitext()` do?

It splits a string at the last dot, and returns a list with two items:

        >>> os.path.splitext('foo.bar')
        ('foo', '.bar')

        >>> os.path.splitext('foo.bar.baz')
        ('foo.bar', '.baz')

# I need to extract a substring from some text, but maybe it's not there. How to handle a possible exception?

Use a `try` statement and a `catch` clause:

        try:
            substring = re.search('...(...)...', text).group(1)
        except AttributeError:
            substring = ''

