#!/usr/bin/env python
# encoding=utf8 ---------------------------------------------------------------
# Project           : Litterate.py
# -----------------------------------------------------------------------------
# Author            : FFunction
# License           : BSD License
# -----------------------------------------------------------------------------
# Creation date     : 02-Mar-2015
# Last modification : 23-Apr-2015
# -----------------------------------------------------------------------------

import re

VERSION = "0.1.1"
LICENSE = "http://ffctn.com/doc/licenses/bsd"


__version__ = VERSION
__doc__     = """
A small litterate-programming tool that extracts and strips text within comment
delimiters and outputs it on stdout.
"""

"""{{{
# Litterate.py
## A multi-language litterate programming tool

```
Version :  0.0.1
URL     :  http://github.com/sebastien/litterate.py
```

`litterate.py` extract documentation embedded in source-code files, allowing
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

In C or JavaScript, they look like this

```
/**
  * <TEXT THAT WILL BE EXTRACTED>
  * ...
*/

```

In Python, they look like this

```
\"\"\"{{{
<TEXT THAT WILL BE EXTRACTED>
\}\}\}\"\"\"
```

The extracted text will then be output to stdout (or to a specific file using
the `-o` command line option). You're then free to process the output
with a tool such as `pandoc` to format it to a more readable format.

A typical workflow would be like that

```
$ litterate.py a.py b.py | pandoc -f markdown -t html README.html
```

}}}"""

# {{{PASTE:COMMAND_LINE}}}
# {{{PASTE:LANGUAGES}}}
# {{{PASTE:COMMANDS}}}
# {{{PASTE:API}}}

# -----------------------------------------------------------------------------
#
# COMMNANDS
#
# -----------------------------------------------------------------------------

# {{{CUT:COMMANDS}}}

"""{{{

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
# {{{CUT:ABOUT\}\}\}
```

The *available commands* are the following:

`CUT:<NAME>`::
	`CUT` will not output any following litterate text until another
	`CUT` command or a corresponding `END` command is encountered.

`END:<NAME>`::
	`END` will end the `CUT`ting of the litterate text. Any litterate
	text after that will be output.

`PASTE:<NAME>`::
	`PASTE`s the `CUT`ted litterate text block. You can `PASTE` before
	a `CUT`, but there always need to be a corresponding `CUT`ted block.

Note that `<NAME>` in the above corresponds to a string that matches
`[A-Z][A-Z0-9_\-]*[A-Z0-9]?`, that is starts with an UPPER CASE letter,
might contain UPPER CASE letters, digits, dashes or underscores and end
with an UPPER CASE letter or digit. That's a bit restrictive, but it makes
it easier to highlight and spot in your source code.
}}}"""

RE_COMMAND_PASTE    = re.compile("\s*(PASTE):([A-Z][A-Z0-9_\-]*[A-Z0-9]?)")
RE_COMMAND_CUT      = re.compile("\s*(CUT):([A-Z][A-Z0-9_\-]*[A-Z0-9]?)")
RE_COMMAND_END      = re.compile("\s*(END):([A-Z][A-Z0-9_\-]*[A-Z0-9]?)")
RE_COMMAND_VERBATIM = re.compile("\s*(VERBATIM):(START|END)")

COMMANDS = {
	"PASTE": RE_COMMAND_PASTE,
	"CUT"  : RE_COMMAND_CUT,
	"END"  : RE_COMMAND_END,
	"VERBATIM" : RE_COMMAND_VERBATIM
}



# -----------------------------------------------------------------------------
#
# LANGUAGES/API
#
# -----------------------------------------------------------------------------

# {{{CUT:API}}}

"""{{{

API
===

You can import `litterate` as a module from Python directly, and use it
to extract litterate text from files/text.

The module defines ready-made language parsers:

- `litterate.C`, `litterate.JavaScript` for C-like languages
- `litterate.Python`, `litterate.Sugar` for Pythonic languages

You can also subclass the `litterate.Language`, in particular:

}}}"""

class Language(object):

	LINE_BASED    = False
	# {{{
	# `Language.RE_START:regexp`::
	# 	The regular expression that is used to match start delimiters
	# }}}
	RE_START      = None
	# {{{
	# `Language.RE_END:regexp`::
	# 	The regular expression that is used to match end delimiters
	# }}}
	RE_END        = None
	# {{{
	# `Language.RE_STRIP:regexp`::
	# 	The regular expression that is used to strip pieces such as leading
	#   `#` characters.
	# }}}
	RE_STRIP      = None
	# {{{
	# `Language.ESCAPE=[(old:String,new:String)]`
	#	A list of `old` strings to be replaced by `new` strings, which is
	#	a very basic way of dealing with excaping delimiters.
	# }}}
	ESCAPE        = [None, None]

	def __init__( self, options=None ):
		self.newlines = options and options.newlines or True
		self.strip    = options and options.strip    or True

	def command( self, text ):
		"""Returns a couple `(command:String, argument:String)` if the
		given text corresponds to a Litterate command."""
		for name, regexp in COMMANDS.items():
			m = regexp.match(text)
			if m: return m.group(1), m.group(2)
		return None

	# {{{
	# `Language.extract( self, text:String )`::
	#	The main algorithm that extracts the litterate text blocks from the
	#	source files.
	# }}}

	def extract( self, text, start=None, end=None, strip=None, escape=None, lineBased=None ):
		"""Extracts litterate string from the given text, using
		the given `start`, `end` and `strip` regular expressions.

		- `start` is used to match the start of a litterate text
		- `end` is used to match the end of a litterate text
		- `strip` is used to match any leading text to be stripped from
		  a litterate text line.

		"""
		# {{{```}}}
		# {{{VERBATIM:START}}}
		start     = start  or self.RE_START
		end       = end    or self.RE_END
		strip     = strip  or self.RE_STRIP
		escape    = escape or self.ESCAPE
		lineBased = self.LINE_BASED if lineBased is None else lineBased
		assert start, "Language.extract: no start regexp given"
		assert end,   "Language.extract: no end   regexp given"
		block  = []
		blocks = {"MAIN":block}
		last_end = -1
		verbatim = None
		for i, s in enumerate(start.finditer(text)):
			e = end.search(text, s.end())
			# If we did not find an end, or that we found a start before the last
			# end, then we continue.
			if not e or s.end() < last_end: continue
			t        = text[s.end():e.start()]
			if self.LINE_BASED:
				# For line-based languages, we string on a line basis
				r = []
				for line in t.split("\n"):
					m = strip.match(line)
					if m: r.append(line[m.end():])
					else: r.append(line)
				t = "\n".join(r)
			else:
				# For non-line-based languages, we strip the expressions directly
				t        = "".join((_ for _ in strip.split(t) if _ is not None))
			for old, new in escape: t = t.replace(old, new)
			command = self.command(t)
			# {{{TODO:It should still be possible to insert litterate text here}}}
			if not command:
				if verbatim:
					block.append(text[max(verbatim,last_end):s.start()])
				# If we have the strip option, we absorb the leading newline
				if self.strip and i == 0 and len(block) == 0 and t[0] == "\n": t = t[1:]
				# If we have the newlines options, and the block is not empty, ends with a string,
				# which is not the empty string, then we add it.
				if self.newlines and i > 0 and len(block) > 0 and type(block[-1]) in (str, unicode) and not block[-1][-1] == "\n": block.append("\n")
				block.append(t)
			elif command[0] == "CUT":
				block = blocks.setdefault(command[1], [])
			elif command[0] == "END":
				block = blocks["MAIN"]
			elif command[0] == "PASTE":
				block.append(command)
			elif command[0] == "VERBATIM":
				if command[1] == "START":
					verbatim = e.end()
				else:
					# TODO: We should de-indent for Pythonic languages
					block.append(text[max(verbatim,last_end):s.start()])
					verbatim = None
			else:
				raise Exception("Unsupported command: " + t)
			last_end = e.end()
		for _ in self._output(blocks["MAIN"], blocks):
			yield _
		# {{{VERBATIM:END}}}
		# {{{```}}}

	def _output( self, block, blocks ):
		last      = len(block)
		last_line = None
		for i, line in enumerate(block):
			if type(line) in (str, unicode):
				yield line
			elif line[0] == "PASTE":
				for _ in self._output( blocks[line[1]], blocks):
					yield _

# -----------------------------------------------------------------------------
#
# SPECIFIC LANGUAGES
#
# -----------------------------------------------------------------------------

# {{{CUT:LANGUAGES}}}
"""{{{

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

}}}"""
class C(Language):
	RE_START      = re.compile("/\*\*")
	RE_END        = re.compile("\*/")
	RE_STRIP      = re.compile("[ \t]*\*[ \t]?")
	ESCAPE        = (("\\*\\/", "*/"),)

class JavaScript(C):
	pass

"""{{{
Python
------

The recognized extensions are `.py`. Litterate texts
start with `{{{` and end with `\}\}\}`. Any line starting with `|` (leading and
trailng spaces) will be stripped.

Example:

```
# {{{CUT:ABOUT\}\}\}

\"\"\"{{{
Input data is acquired through _iterators_. Iterators wrap an input source
(the default input is a `FileInput`) and a `move` callback that updates the
iterator's offset. The iterator will build a buffer of the acquired input
and maintain a pointer for the current offset within the data acquired from
the input stream.
\}\}\}\"\"\"


if True:
	\"\"\"{{{
#	| You can get an iterator on a file by doing:
#	|
#	| ```c
#	| Iterator* iterator = Iterator_Open("example.txt");
#	| ```
 	\}\}\}\"\"\"
```
}}}"""

class Python(Language):
	LINE_BASED = True
	RE_START   = re.compile("\{\{\{")
	RE_STRIP   = re.compile("^\s*[\|#]\s?")
	RE_END     = re.compile("\s*\#?\s*}}"  "}")
	ESCAPE     = (
		("\\}\\}\\}", "}" "}}"),
		('\\"\\"\\"', '"""')
	)

"""{{{

Sugar
-----

The recognized extensions are `.sjs` and `.spy`. Litterate texts
start with `{{{` and end with `\}\}\}`. Any line starting with `|` (leading and
trailng spaces) will be stripped.

Example:

```
# {{{CUT:ABOUT\}\}\}

# {{{
# Input data is acquired through _iterators_. Iterators wrap an input source
# (the default input is a `FileInput`) and a `move` callback that updates the
# iterator's offset. The iterator will build a buffer of the acquired input
# and maintain a pointer for the current offset within the data acquired from
# the input stream.
# \}\}\}

if True
	# {{{
	# You can get an iterator on a file by doing:
	#
	# ```c
	# Iterator* iterator = Iterator_Open("example.txt");
	# ```
	# \}\}\}
end
```

}}}"""

class Sugar(Python):
	pass

"""{{{

A note about escaping
---------------------

Your source code might contain the delimiters as part of regular code, most
likely within strings. If this is the case you should try to write them diffently,
either by using escape symbols (such as `\`) or by breaking the string in bits (
in Python you could do `"{{" "{"` which would return a string equivalent to
the start delimiter).

If you'd like to represent a delimiter within a litterate text, you only have
to worry about the end delimiter. The convention is to write the delimiter
with each character prefixed by a `\`.

}}}"""

# {{{END:LANGUAGES}}}

# -----------------------------------------------------------------------------
#
# FUNCTIONS
#
# -----------------------------------------------------------------------------

LANGUAGES = {
	"c|cpp|h" : C,
	"js"      : JavaScript,
	"py"      : Python,
	"sjs|spy" : Sugar
}

"""{{{
litterate.getLanguage(filename:String)::
	Returns the `Language` instance that corresponds to the given extension.
}}}
"""
def getLanguage( filename, args ):
	ext = filename.rsplit(".", 1)[-1]
	for pattern, parser in LANGUAGES.items():
		if re.match(pattern, ext):
			return parser(args)
	return None

# -----------------------------------------------------------------------------
#
# MAIN
#
# -----------------------------------------------------------------------------

if __name__ == "__main__":
	import sys, argparse
	def fail( message ):
		sys.stderr.write("[!] ")
		sys.stderr.write(message)
		sys.stderr.write("\n")
		sys.stderr.flush()
		return sys.exit(-1)
	# {{{CUT:COMMAND_LINE}}}
	"""{{{
	|
	| Command-line tool
	| =================
	|
	| `litterate.py` can be executed as a command-line tool.
	|
	| `litterate.py [OPTIONS] FILE...`
	|
	| `FILE` is optional (by default, stdin will be used). You can use `-` to
	| explicitely read data from stding.
	|
	| It takes the following options:
	|
	| - `-l=LANG` `--language=LANG`, where `LANG` is any of `c`, `js` or `sugar`.
	|   If you don't give a language, it will output the list of supported languages.
	|
	| - `-o=PATH` will output the resulting text to the given file. By default,
	|   the extracted text is printed on stdout.
	|
	| - `-n, `--newlines` will ensure that the blocks are always separated by
	|   newlines (default is ON)
	|
	| - `-s, `--strip` will strip leading and trailing spaces/newlines
	|   from the output (default is ON)
	| }}}"""
	out  = sys.stdout
	# Parses the arguments
	parser = argparse.ArgumentParser(
		description="Extracts selected text from source code to create documentation files."
	)
	parser.add_argument("files", metavar="FILE", type=str, nargs="*", help="Source files to be processed. Stdin is denoted by `-`")
	parser.add_argument("-l", "--language", dest="language", action="store", help="Enforces the given language for the input file. If empty, lists the available languages")
	parser.add_argument("-o", "--output",   dest="output",   action="store", help="Specifies an input file, stdout is denoted by -")
	parser.add_argument("-n", "--newlines", dest="newlines", action="store_true", default=True, help="Ensures that blocks are separated by newlines")
	parser.add_argument("-s", "--strip",    dest="strip",    action="store_true", default=True, help="Strips leading and trailing newlines")
	args = parser.parse_args()
	output = None
	if args.output:
		output = file(args.output, "w")
	out = output or out
	# Executes the main program
	if not args.files or args.files == ["-"]:
		if not args.language:
			fail("A language (-l, --language) must be specified when using stdin. Try -lc")
		out.write(getLanguage(args.language, args).extract(sys.stdin.read()))
	else:
		for p in args.files:
			language = args.language or getLanguage(p, args)
			assert language, "No language registered for file: {0}. Supported extensions are {1}".format(p, ", ".join(LANGUAGES.keys()))
			with file(p) as f:
				for line in language.extract(f.read()):
					out.write(line)
	if output: output.close()

# EOF - vim: ts=4 sw=4 noet
