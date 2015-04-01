#!/usr/bin/env python
# encoding=utf8 ---------------------------------------------------------------
# Project           : Litterate.py
# -----------------------------------------------------------------------------
# Author            : FFunction
# License           : BSD License
# -----------------------------------------------------------------------------
# Creation date     : 02-Mar-2015
# Last modification : 01-Apr-2015
# -----------------------------------------------------------------------------

VERSION = "0.0.0"
LICENSE = "http://ffctn.com/doc/licenses/bsd"

# EOF - vim: ts=4 sw=4 noet

import re

__version__ = "0.0.0"
__doc__ = """
A small litterate-programming tool that extracts and strips text within comment
delimiters and outputs it on stdout.
"""

"""{{{
#  Litterate.py
## A multi-language litterate programming tool

```
Version :  ${VERSION}
URL     :  http://github.com/sebastien/litterate.py
```

`Litterate.py` helps you keep your code/API documentation along with the source
file. It is intended for small-sized projects where you would prefer to avoid
having the documentation and the code separate.

How does it work?
-----------------

`Litterate.py` will look for specific delimiters in your source code and
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
}}}\"\"\"

```

The extracted text will then be output to stdout (or to a specific file using
the `-o` command line option). This lets you choose any specific format for
the text -- I personnaly use Markdown, but you could use ReST or even XML.

A typical workflow would be like that

```
$ litterate.py a.py b.py | pandoc -f markdown -t html README.html
```

}}}"""


# {{{PASTE:LANGUAGES}}}

# -----------------------------------------------------------------------------
#
# COMMNANDS
#
# -----------------------------------------------------------------------------

"""{{{
Commands
--------

One of the typical problem you'll encounter when adding documentation in your
source code is that the source ordering of elements (functions, classes, etc)
might not be ideal from an explanation/documentation perspective. In other
words, you might want some sections of your litterate text to be re-ordered
on the output.

To do that, `litterate.py` provides you with a few useful commands, which
need to be the only content of a litterate text to be interpreted.

For instance:

```
/**
  * CUT:ABOUT
*/
```

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

RE_COMMAND_PASTE = re.compile("(PASTE):([A-Z][A-Z0-9_\-]*[A-Z0-9]?)")
RE_COMMAND_CUT   = re.compile("(CUT):([A-Z][A-Z0-9_\-]*[A-Z0-9]?)")
RE_COMMAND_END   = re.compile("(END):([A-Z][A-Z0-9_\-]*[A-Z0-9]?)")
COMMANDS = {
	"PASTE": RE_COMMAND_PASTE,
	"CUT"  : RE_COMMAND_CUT,
	"END"  : RE_COMMAND_END,
}


# {{{PASTE:COMMAND_LINE}}}
# {{{PASTE:API}}}

# -----------------------------------------------------------------------------
#
# LANGUAGES
#
# -----------------------------------------------------------------------------

# {{{CUT:API}}}

"""{{{
API
---

The language class defines how "litterate" strings are extracted from the
source file.

}}}"""

class Language(object):

	RE_START = None
	RE_END   = None
	RE_STRIP = None

	def command( self, text ):
		"""Returns a couple `(command:String, argument:String)` if the
		given text corresponds to a Litterate command."""
		for name, regexp in COMMANDS.items():
			m = regexp.match(text)
			if m: return m.group(1), m.group(2)
		return None

	def extract( self, text, start=None, end=None, strip=None ):
		"""Extracts litterate string from the given text, using
		the given `start`, `end` and `strip` regular expressions.

		- `start` is used to match the start of a litterate text
		- `end` is used to match the end of a litterate text
		- `strip` is used to match any leading text to be stripped from
		  a litterate text line.

		"""
		start  = start or self.RE_START
		end    = end   or self.RE_END
		strip  = strip or self.RE_STRIP
		block  = []
		blocks = {"MAIN":block}
		for s in start.finditer(text):
			e = end.search(text, s.end())
			if not e: continue
			t = text[s.end():e.start()]
			t = "".join(strip.split(t))
			command = self.command(t)
			if not command:
				block.append(t)
			elif command[0] == "CUT":
				block = blocks.setdefault(command[1], [])
			elif command[0] == "END":
				block = blocks["MAIN"]
			elif command[0] == "PASTE":
				block.append(command)
			else:
				raise Exception("Unsupported command: " + t)
		for _ in self._output(blocks["MAIN"], blocks):
			yield _

	def _output( self, block, blocks ):
		for line in block:
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

C, C++ & JavaScript
===================

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
	RE_START = re.compile("/\*\*")
	RE_END   = re.compile("\*/")
	RE_STRIP = re.compile("[ \t]*\*[ \t]?")

class C(Language):
	pass

class JavaScript(C):
	pass

"""{{{

Python
=============

The recognized extensions are `.py`. Litterate texts
start with `{{{` and end with `}}}`. Any line starting with `|` (leading and
trailng spaces) will be stripped.

Example:

```
# {{{CUT:ABOUT}}}

\"\"\"{{{
Input data is acquired through _iterators_. Iterators wrap an input source
(the default input is a `FileInput`) and a `move` callback that updates the
iterator's offset. The iterator will build a buffer of the acquired input
and maintain a pointer for the current offset within the data acquired from
the input stream.
}}}\"\"\"


if True:
	\"\"\"{{{
	| You can get an iterator on a file by doing:

	| ```c
	| Iterator* iterator = Iterator_Open("example.txt");
	| ```
	}}}\"\"\"

```

}}}"""
class Python(Language):
	RE_START = re.compile("{{{")
	RE_STRIP = re.compile("\s*#\s*|[ \t]\|[ \t]?")
	RE_END   = re.compile("\s*\#?\s*}}}")

"""{{{

Sugar
=====

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
	# ```c
	# Iterator* iterator = Iterator_Open("example.txt");
	# ```
	# }}}
end
```

}}}"""

class Sugar(Python):
	pass

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
def getLanguage( filename ):
	ext = filename.rsplit(".", 1)[-1]
	for pattern, parser in LANGUAGES.items():
		if re.match(pattern, ext):
			return parser()
	return None

# -----------------------------------------------------------------------------
#
# MAIN
#
# -----------------------------------------------------------------------------

if __name__ == "__main__":

	# {{{CUT:COMMAND_LINE}}}
	"""{{{
	| Command-line tool
	| -----------------
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

	| }}}"""
	import sys, argparse
	out  = sys.stdout
	# Parses the arguments
	parser = argparse.ArgumentParser(
		description="Extracts selected text from source code to create documentation files."
	)
	parser.add_argument("files", metavar="FILE", type=str, nargs="+", help="Source files to be processed. Stdin is denoted by `-`")
	parser.add_argument("-l", "--language", dest="language", action="store", help="Enforces the given language for the input file. If empty, lists the available languages")
	parser.add_argument("-o", "--output", dest="output", action="store", help="Specifies an input file, stdout is denoted by -")
	args = parser.parse_args()
	output = None
	if args.output:
		output = file(p)
	out = output or out
	# Executes the main program
	if not args.files or args.files == ["-"]:

		out.write(extract(sys.stdin.read(), start, end, strip))
	else:
		for p in args:
			language = args.language or getLanguage(p)
			assert language, "No language registered for file: {0}. Supported extensions are {1}".format(p, ", ".join(LANGUAGES.keys()))
			with file(p) as f:
				for line in language.extract(f.read()):
					out.write(line)
	if output: output.close()
# EOF
