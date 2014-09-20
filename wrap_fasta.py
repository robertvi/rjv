#!/usr/bin/python

'''
convert one-record-per-line fasta
into normal fasta
'''

usage = 'usage: cat input.fa | wrap_fasta.py > output.fa'

import sys

f = sys.stdin

width=70

for line in f:
    line = line.strip()
    
    tok = line.split('\t') #try splitting with tabs
    if len(tok) != 2: tok = line.split(',') #try with comma
    if len(tok) != 2: tok = line.split() #try with spaces
    assert len(tok)
    
    print tok[0]
    
    pos = 0
    
    while True:
        seq = tok[1][pos:pos+width]
        print seq
        pos += width
        if pos >= len(tok[1]): break
