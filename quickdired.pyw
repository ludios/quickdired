import os
import re

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
	return name not in set([".quickdired.oldnames", ".quickdired.newnames"])


def main():
	f = upgradeFilepath(FilePath(os.getcwdu()))
	listingNames = sortNicely(filter(shouldInclude, os.listdir(f.path)))

	oldNamesFile = f.child(".quickdired.oldnames")
	newNamesFile = f.child(".quickdired.newnames")

	if oldNamesFile.isfile() and newNamesFile.isfile():
		# If both files exist, rename the files in current dir
		oldNames = getNamesFromContent(oldNamesFile.getContent())
		newNames = getNamesFromContent(newNamesFile.getContent())
		
		if set(oldNames) != set(listingNames):
			showError("Files in directory do not match .oldnames")
			return
		if len(oldNames) != len(newNames):
			showError(".newnames lists %r names while .oldnames lists %r names" % (len(newNames), len(oldNames)))
			return

		for i, o in enumerate(oldNames):
			os.rename(o, newNames[i])
		
		oldNamesFile.remove()
		newNamesFile.remove()
	else:
		# Create the .oldnames and .newnames files, which the
		# user should edit, and then re-run quickdired.
		oldNamesFile.setContent("\n".join(map(utf8, listingNames)) + "\n")
		newNamesFile.setContent("\n".join(map(utf8, listingNames)) + "\n")


if __name__ == '__main__':
	main()
