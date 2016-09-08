# Litterate.py
# A multi-language litterate programming tool

```
Version :  0.1.2
URL     :  http://github.com/sebastien/litterate.py
```

`litterate.py` extracts documentation embedded in source-code files, allowing
to have both project documentation and source code in the same file.

It is intended for small-sized projects where you would prefer to avoid
having the documentation and the code separate.

It can also be used as a litterate programming tool where you have the source
code presented alongside explanations.

How does it work?
=================

`litterate.py` will look for specific delimiters in your source files and
extract the content content between these delimiters. The delimiters depend
on the language you're using.

In C-style languages (Java, JavaScript), it looks like this

```
/**
  * TEXT THAT WILL BE EXTRACTED
  * ‥
*/

```

In shell-like or Python-like languages:

```
{{{
TEXT THAT WILL BE EXTRACTED
‥
}}}
```

In Python:

```
"""{{{
TEXT THAT WILL BE EXTRACTED
}}}"""

{{{
TEXT THAT WILL BE EXTRACTED
}}}
```

In indentation:

The extracted text will then be output to stdout (or to a specific file using
the `-o` command line option). You're then free to process the output
with a tool such as `pandoc` to format it to a more readable format.

A typical workflow would be like that

```
$ litterate.py a.py b.py | pandoc -f markdown -t html README.html
```

Command-line tool
=================

`litterate.py` can be executed as a command-line tool.

`litterate.py [OPTIONS] FILE...`

`FILE` is optional (by default, stdin will be used). You can use `-` to
explicitely read data from stding.

It takes the following options:

- `-l=LANG` `--language=LANG`, where `LANG` is any of `c`, `js` or `sugar`.
  If you don't give a language, it will output the list of supported languages.

- `-o=PATH` will output the resulting text to the given file. By default,
  the extracted text is printed on stdout.

- `-n, `--newlines` will ensure that the blocks are always separated by
  newlines (default is ON)

- `-s, `--strip` will strip leading and trailing spaces/newlines
  from the output (default is ON)


Supported Languages
===================

C, C++ & JavaScript
-------------------

The recognized extensions are `.c`, `.cpp`, `.h` and `.js`. Litterate texts
start with `/**` and end with `*/`. Any line starting with `*` (leading and
trailng spaces) will be stripped.

Example:

```
/**
 * Input data is acquired through _iterators_. Iterators wrap an input source
 * (the default input is a `FileInput`) and a `move` callback that updates the
 * iterator's offset. The iterator will build a buffer of the acquired input
 * and maintain a pointer for the current offset within the data acquired from
 * the input stream.
 *
 * You can get an iterator on a file by doing:
 *
 * ```c
 * Iterator* iterator = Iterator_Open("example.txt");
 * ```
 *
*/
```

Python
------

The recognized extensions are `.py`. Litterate texts
start with `{{{` and end with `}}}`. Any line starting with `|` (leading and
trailing spaces) will be stripped.

The following block of text will be processed as part of the documentation:

```python
"""{{{CUT:ABOUT\

Input data is acquired through _iterators_. Iterators wrap an input source
(the default input is a `FileInput`) and a `move` callback that updates the
iterator's offset. The iterator will build a buffer of the acquired input
and maintain a pointer for the current offset within the data acquired from
the input stream.
}}}"""

if True:
The following will be appended to the documentation as well
	"""{{{
	| You can get an iterator on a file by doing:
	|
	| ```c
	| Iterator* iterator = Iterator_Open("example.txt");
	| ```
}}}
"""
```


Sugar
-----

The recognized extensions are `.sjs` and `.spy`. Litterate texts
start with `{{{` and end with `}}}`. Any line starting with `|` (leading and
trailng spaces) will be stripped.

Example:

```
# {{{CUT:ABOUT}}}

# {{{
# Input data is acquired through _iterators_. Iterators wrap an input source
# (the default input is a `FileInput`) and a `move` callback that updates the
# iterator's offset. The iterator will build a buffer of the acquired input
# and maintain a pointer for the current offset within the data acquired from
# the input stream.
# }}}

if True
	# {{{
	# You can get an iterator on a file by doing:
	#
	# \```c
	# Iterator* iterator = Iterator_Open("example.txt");
	# \```
	# }}}
end
```


A note about escaping
---------------------

Your source code might contain the delimiters as part of regular code, most
likely within strings. If this is the case you should try to write them diffently,
either by using escape symbols (such as ``) or by breaking the string in bits (
in Python you could do `"{{" "{"` which would return a string equivalent to
the start delimiter).

If you'd like to represent a delimiter within a litterate text, you only have
to worry about the end delimiter. The convention is to write the delimiter
with each character prefixed by a ``.

Commands
========

One of the typical problem you'll encounter when adding documentation in your
source code is that the source ordering of elements (functions, classes, etc)
might not be ideal from an explanation/documentation perspective. In other
words, you might want some sections of your litterate text to be re-ordered
on the output.

To do that, `litterate.py` provides you with a few useful commands, which
need to be the only content of a litterate text to be interpreted.

For instance, in C/JavaScript:

```
/**
  * CUT:ABOUT
*/
```

or in Python/Sugar:

```
{{{CUT:ABOUT}}}
```

The *available commands* are the following:

<dl>
<dt>`CUT:<NAME>`</dt>
<dd>
`CUT` will not output any following litterate text until another
`CUT` command or a corresponding `END` command is encountered.
</dd>

<dt>`END:<NAME>`</dt>
<dd>
`END` will end the `CUT`ting of the litterate text. Any litterate
text after that will be output.
</dd>

<dt>`PASTE:<NAME>`</dt>
<dd>
`PASTE`s the `CUT`ted litterate text block. You can `PASTE` before
a `CUT`, but there always need to be a corresponding `CUT`ted block.
</dd>
</dl>

Note that `<NAME>` in the above corresponds to a string that matches
`[A-Z][A-Z0-9_-]*[A-Z0-9]?`, that is starts with an UPPER CASE letter,
might contain UPPER CASE letters, digits, dashes or underscores and end
with an UPPER CASE letter or digit. That's a bit restrictive, but it makes
it easier to highlight and spot in your source code.

API
===

You can import `litterate` as a module from Python directly, and use it
to extract litterate text from files/text.

The module defines ready-made language parsers:

- `litterate.C`, `litterate.JavaScript` for C-like languages
- `litterate.Python`, `litterate.Sugar` for Pythonic languages

You can also subclass the `litterate.Language`, in particular:

`Language.RE_START:regexp`
:
	The regular expression that is used to match start delimiters

`Language.RE_END:regexp`
 :
	The regular expression that is used to match end delimiters

`Language.RE_STRIP:regexp`
:
	The regular expression that is used to strip pieces such as leading
  `#` characters.

`Language.ESCAPE=[(old:String,new:String)]`
:
A list of `old` strings to be replaced by `new` strings, which is
a very basic way of dealing with excaping delimiters.

`Language.extract( self, text:String )`
:
The main algorithm that extracts the litterate text blocks from the
source files.