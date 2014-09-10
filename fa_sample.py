#!/usr/bin/python

'''
pass a random subset of fasta records
from stdin to stdout

usage: cat *.fa | fa_sample.py <prob> > out
'''

import sys,random

usage = 'usage: cat *.fa | fa_sample.py <prob> > out'

if len(sys.argv) != 2:
    print usage
    exit()

prob = float(sys.argv[1])
fin = sys.stdin
fout = sys.stdout
echo = False

while True:
    line = fin.readline()
    if line == '': break
    
    if line.startswith('>'):
        if random.random() < prob:
            echo = True
        else:
            echo = False
            
    if not echo: continue
    
    try:
        fout.write(line)
    except:
        #broken pipe?
        exit()
