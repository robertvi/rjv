#!/usr/bin/python

'''
count base pairs in fastq file(s)
usage: countfqbases.py file1...
'''

import sys

from rjv.fastq import *

total = 0
for fname in sys.argv[1:]:
    ct = 0
    for fq in next_fastq(fname):
        ct += len(fq['seq'])
    print fname,ct
    total += ct
    
print 'total',total
