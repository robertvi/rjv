#!/usr/bin/python

'''
count kmers from stdin
save hash to a pickle file

usage: zcat *.fq.gz | countkmers.py [kmersize] > output.pkl
'''

import sys,os

if os.uname()[1] == 'mocedades':
    #running on laptop
    pyth_dir = '/home/rov/rjv_files/python_lib/'
else:
    #assume running on a cluster node
    pyth_dir = '/ibers/ernie/home/rov/python_lib/'
    
sys.path.append(pyth_dir) 

from rjv.fastq import *
from rjv.fileio import *

k = int(sys.argv[1])

ct = {}

for fq in next_fastq(sys.stdin):
    seq = fq['seq']
    l = len(seq)
    
    for pos in xrange(0,l-k):
        kmer = seq[pos:pos+k]
        
        if 'N' in kmer: continue
        
        try:
            ct[kmer] += 1
        except:
            ct[kmer] = 1

save_pickle(ct,sys.stdout)
