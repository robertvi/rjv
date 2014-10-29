#!/usr/bin/python

'''
usage: prev n

return the nth line from the bottom of a sorted list from stdin
'''

import sys

data = sys.stdin.readlines()

try:
	sys.stdout.write(data[-int(sys.argv[1])])
except:
	sys.stderr.write('unable to find a item to print\n')
	exit(1)
