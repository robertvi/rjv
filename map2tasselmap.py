#!/usr/bin/python

'''
convert csv format genetic map with marker data
into tassel's genetic map format
'''

import sys
from rjv import mycsv

if len(sys.argv) < 2:
    print 'usage: map2tasselmap.py input > output'
    exit()

out = sys.stdout

data = mycsv.load_csv(sys.argv[1])[1:]

out.write('<Map>\n')

#output only marker, lg and pos
for row in data:
    out.write('\t'.join(row[:3]) + '\n')
