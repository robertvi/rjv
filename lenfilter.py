#!/usr/bin/python

'''
filter fastas by sequence length


'''

from rjv.fasta import *
import sys

usage=\
'''
lenfilter.py inp.fa minlen maxlen > out.fa
'''

if len(sys.argv) < 4:
    print usage
    exit()

fout = sys.stdout
inpname = sys.argv[1]
minlen = int(sys.argv[2])
maxlen = int(sys.argv[3])

for fa in next_fasta(inpname):
    if len(fa['seq']) >= minlen and len(fa['seq']) <= maxlen:
        write_fasta(fa,fout)
