import sys
import os
import re

try:
	from simplejson import json
except ImportError:
	import json

from twisted.python.filepath import FilePath


def showError(msg):
	import Tkinter
	import tkMessageBox

	root = Tkinter.Tk()
	root.withdraw()

	tkMessageBox.showerror("QuickDired error", msg) 


UNC_PREFIX = u"\\\\?\\"

def absPathToUncPath(p):
	r"""
	See http://msdn.microsoft.com/en-us/library/aa365247%28v=vs.85%29.aspx#maxpath
	"""
	return UNC_PREFIX + p


def upgradeFilepath(f):
	r"""
	@param f: a L{FilePath} to upgrade.
	@return: a possibly-upgraded L{FilePath}.
	"""
	if not f.path.startswith(UNC_PREFIX):
		return FilePath(absPathToUncPath(f.path))
	return f


def tryInt(s):
	try:
		return int(s)
	except:
		return s


def filenameKey(s):
	return tuple(tryInt(c) for c in re.split('([0-9]+)', s))


def sortNicely(l):
	return sorted(l, key=filenameKey)


def utf8(s):
	return s.encode('utf-8')


def getNamesFromContent(s):
	return [name.decode("utf-8") for name in s.rstrip("\n").split("\n")]


def shouldInclude(name):
	return name not in set([
		u".quickdired.oldnames",
		u".quickdired.newnames",
		u".quickdired.options",
	])


def withoutBase(root, fp):
	return fp.path.replace(root.path, u"", 1).lstrip(u"/\\")


def getListing(root, deep):
	if not deep:
		return sortNicely(filter(shouldInclude, os.listdir(root.path)))
	else:
		return sortNicely(map(
			lambda fp: withoutBase(root, fp),
			filter(
				# --deep does not support renaming directories
				lambda fp: not fp.isdir() and shouldInclude(fp.basename()),
				root.walk()
			)))


def writeListingOrRename(deep): # Note: deep may be changed below
	f = upgradeFilepath(FilePath(os.getcwdu()))

	oldNamesFile = f.child(u".quickdired.oldnames")
	newNamesFile = f.child(u".quickdired.newnames")
	optionsFile = f.child(u".quickdired.options")

	if oldNamesFile.isfile() and newNamesFile.isfile() and optionsFile.isfile():
		# If both files exist, rename the files in current dir
		oldNames = getNamesFromContent(oldNamesFile.getContent())
		newNames = getNamesFromContent(newNamesFile.getContent())
		options = json.loads(optionsFile.getContent())
		if options['deep']:
			# Even if no --deep, assume deep if .options says deep: true
			deep = True

		listingNames = getListing(f, deep)

		if set(oldNames) != set(listingNames):
			print "old names = ", oldNames
			print "cur names = ", listingNames
			showError("Files in directory do not match .oldnames")
			return
		if len(oldNames) != len(newNames):
			showError(".newnames lists %r names while .oldnames lists %r names" % (len(newNames), len(oldNames)))
			return

		for i, o in enumerate(oldNames):
			os.rename(o, newNames[i])
		
		optionsFile.remove()
		oldNamesFile.remove()
		newNamesFile.remove()
	else:
		listingNames = getListing(f, deep)

		# Create the .oldnames and .newnames files, which the
		# user should edit, and then re-run quickdired.
		oldNamesFile.setContent("\n".join(map(utf8, listingNames)) + "\n")
		newNamesFile.setContent("\n".join(map(utf8, listingNames)) + "\n")
		optionsFile.setContent(json.dumps({"deep": deep}, indent=2))

		# Associate .newnames with whatever text editor you want
		os.startfile(u".quickdired.newnames")


def main():
	try:
		deep = sys.argv[1] == '--deep'
	except IndexError:
		deep = False
	writeListingOrRename(deep)


if __name__ == '__main__':
	main()
