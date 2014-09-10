#!/usr/bin/python

'''
output random sequence(s) as fasta
'''

usage=\
'usage: randseq.py header seqlen [bases="ATCG"] > output.fa'


import rjv.misc as misc
from rjv.fasta import *

import sys

if len(sys.argv) < 3:
    print usage
    exit()

fa = {}

fa['header'] = sys.argv[1]
seqlen = int(sys.argv[2])

if len(sys.argv) == 4:
    bases = sys.argv[3]
else:
    bases = 'ATCG'
    
f = sys.stdout

fa['seq'] = misc.random_seq(seqlen,bases)

write_fasta(fa,f)
