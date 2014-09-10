#!/usr/bin/python

'''
zip two fastq files together
to give interleaved reads
take the first white-space token of each id
ensure these are the same for both reads
append /1 and /2 to the ends

usage: zip_fastqs.py input1 input2 > output
'''

import sys
sys.path.append('/ibers/ernie/groups/quoats/python_lib')
from rjv.fastq import *

fname1 = sys.argv[1]
fname2 = sys.argv[2]

gen1 = next_fastq(fname1)
gen2 = next_fastq(fname2)

while True:
    try:
        fq1 = gen1.next()
    except:
        break
    
    fq2 = gen2.next()

    id1 = fq1['header'].split()[0]
    id2 = fq2['header'].split()[0]

    assert id1 == id2

    fq1['header'] = id1+'/1'
    fq2['header'] = id1+'/2'
    
    write_fastq(fq1,sys.stdout)
    write_fastq(fq2,sys.stdout)
