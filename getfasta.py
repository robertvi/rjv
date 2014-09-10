#!/usr/bin/python

'''
get one fasta sequence from a file by its seqid
'''

import sys
sys.path.append('/ibers/ernie/home/rov/python_lib')
    
from rjv.fasta import *

usage=\
'''
usage: getfasta.py <fastafile> <seqid> > <output_file>
'''

if len(sys.argv) != 3:
    print usage
    exit()
    
inp = sys.argv[1]
seqid = sys.argv[2]

fa = get_fasta(inp,seqid)
write_fasta(fa,sys.stdout)
