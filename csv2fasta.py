#!/usr/bin/python

'''
convert csv output into fasta
assumes last column of each line is the sequence
the other cols are to go in the header
'''

import sys
sys.path.append('/ibers/ernie/home/rov/python_lib')
from rjv.fasta import *

for line in sys.stdin:
    tok = line.strip().split(',')
    fa = {}
    fa['header'] = ' '.join(tok[:-1])
    fa['seq'] = tok[-1]
    write_fasta(fa,sys.stdout)
