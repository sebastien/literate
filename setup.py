#!/usr/bin/env python
# Encoding: utf-8
# See: <http://docs.python.org/distutils/introduction.html>
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

VERSION = eval(filter(lambda _:_.startswith("VERSION"),
    file("src/litterate.py").readlines())[0].split("=")[1])

setup(
	name             = "litterate",
	version          = VERSION,
	description      = "Extracts text and documentation embedded in source code",
	author           = "Sébastien Pierre",
	author_email     = "sebastien.pierre@gmail.com",
	url              = "http://github.com/sebastien/litterate",
	download_url     = "https://github.com/sebastien/litterate/tarball/%s" % (VERSION),
	keywords         = ["documentation", "programming", "tools", "litterate", "markup"],
	package_dir      = {"":"src"},
	py_modules       = ["litterate"],
	license          = "License :: OSI Approved :: BSD License",
	classifiers      = [
		"Programming Language :: Python :: 3",
		"Development Status :: 3 - Alpha",
		"Natural Language :: English",
		"Environment :: Console",
		"Intended Audience :: Developers",
		"Operating System :: OS Independent",
		"Topic :: Utilities"
	],
)
# EOF - vim: ts=4 sw=4 noet
