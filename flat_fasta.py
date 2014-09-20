#!/usr/bin/python

'''
flatten fasta into one record per line
'''

usage = 'usage: cat input.fa | flat_fasta.py > output.fa'

import sys

f = sys.stdin

rec = None
sep = '\t' #separator between header and sequence

for line in f:
    if line.startswith('>'):
        if rec != None: print ''.join(rec)
        rec = [line.strip() + sep]
    else:
        rec.append( line.strip() )
    
if rec != None: print ''.join(rec)
