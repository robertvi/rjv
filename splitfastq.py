#!/usr/bin/python

'''
split fastq into chunks based on record counting
i.e. does not require seeking within the file
'''

import os,sys
if os.uname()[1] != 'mocedades':
    sys.path.append('/ibers/ernie/home/rov/python_lib')

from rjv.fastq import *

usage=\
'''
usage: splitfastq.py <fastqfile[.gz]> <chunks> <offset> > <outputfile>

eg splitfastq.py myreads.fq 10 0
gives every tenth record from the file starting with the first record

eg splitfastq.py myreads.fq 20 1
gives every 20th record from the file starting with the second record
'''

if len(sys.argv) != 4:
    print usage
    exit()
    
inpname = sys.argv[1]
chunks = int(sys.argv[2])
offset = int(sys.argv[3])

fout = sys.stdout
newline = '\n'

#for rec in next_fastq_split(inpname,offset,chunks):
ct = 0
for fq in next_fastq(inpname):
    if ct % chunks == offset:
        fout.write('@' + fq['header'] + newline)
        fout.write(fq['seq'] + newline)
        fout.write('+' + newline)
        fout.write(fq['qual'] + newline)

    ct += 1 
