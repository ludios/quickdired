#!/usr/bin/env python3

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(
	name="quickdired",
	version="2.0.0",
	description="Rename files by generating a file listing and applying changes after edits",
	url="https://github.com/ludios/quickdired",
	author="Ivan Kozik",
	author_email="ivan@ludios.org",
	classifiers=[
		"Programming Language :: Python :: 3",
		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: End Users/Desktop",
		"License :: OSI Approved :: MIT License",
	],
	scripts=["quickdired"],
)
