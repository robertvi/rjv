#!/usr/bin/python

'''
convert csv format genetic map with marker data
into tassel's polymorphism format
'''

import sys
from rjv import mycsv

if len(sys.argv) < 2:
    print 'usage: map2tassel.py input > output'
    exit()

out = sys.stdout

conv =\
{
    'A':'A:A',
    'B':'B:B',
    'H':'A:B',
    '-':'?:?',
}

data = mycsv.load_csv(sys.argv[1])
data = mycsv.transpose_table(data)

header = data[0]
header[0] = '<Marker>'

out.write('\t'.join(header) + '\n')

#ignore the lg and pos data
data = data[3:]
for row in data:
    row = [row[0]] + [conv[x] for x in row[1:]]
    out.write('\t'.join(row) + '\n')

