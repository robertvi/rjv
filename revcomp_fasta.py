#!/usr/bin/python

'''
reverse complement a fasta
'''

from rjv.fasta import *
from rjv.kmer import *
import sys

for fa in next_fasta(sys.argv[1]):
    fa['seq'] = revcomp_n(fa['seq'])
    write_fasta(fa,sys.stdout)
    
