#!/usr/bin/python

'''
usage: prevfile n

return the nth file from the end of an mtime sorted listing
'''

import os,glob,sys

files = filter(os.path.isfile, glob.glob("*"))
files.sort(key=lambda x: os.path.getmtime(x),reverse=True)

try:
	print files[int(sys.argv[1])]
except:
	sys.stderr.write('unable to find a filename to print\n')
	exit(1)
