#!/usr/bin/python

'''
filter fastas by sequence length


'''

from rjv.fasta import *
import sys

usage=\
'''
namefilter.py inp.fa > out.fa
'''

if len(sys.argv) < 2:
    print usage
    exit

fout = sys.stdout
inpname = sys.argv[1]

for rec in next_fasta(inpname):
    rec['header'] = rec['header'][4:]
    write_fasta_rec(rec,fout)
