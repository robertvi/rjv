#!/usr/bin/python

'''
split fastq into chunks based on record counting
'''

import os,sys
from rjv.fastq import *

usage=\
'''
usage: splitfastq2.py <fastqfile> <chunks>

eg splitfastq2.py myreads.fq 10
gives myreads-000.fq,... myreads-009.fq
'''

if len(sys.argv) != 3:
    print usage
    exit()
    
inpname = sys.argv[1]
chunks = int(sys.argv[2])
base = os.path.basename(inpname)
base = ''.join(base.split('.')[:-1])

if inpname.endswith('.fq'): base += '-%03d.fq'
else:                       base += '-%03d.fastq'

f = [open(base%i,'wb') for i in xrange(chunks)]

for i,fa in enumerate(next_fastq(inpname)):
    write_fastq(fa,f[i%chunks])

for x in f: x.close()
