#!/usr/bin/python

'''
read n lines from a position in the file defined
by proportion of total size
to avoid having to read through a massive file before
obtaining lines near the end
'''

import sys
from rjv.fileio import read_posn

if len(sys.argv) == 3:
    #read_posn.py <file> <posn>
    read_posn(sys.argv[1],float(sys.argv[2]))
elif len(sys.argv) == 4:
    #read_posn.py <file> <posn> <lines>
    read_posn(sys.argv[1],float(sys.argv[2]),int(sys.argv[3]))
else:
    print 'usage: read_posn.py <file> <proportion> [<lines>]'
