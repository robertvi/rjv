#!/usr/bin/python

'''
split fasta into chunks based on record counting
i.e. does not require seeking within the file
'''

import os,sys
if os.uname()[1] != 'mocedades':
    sys.path.append('/ibers/ernie/home/rov/python_lib')
    
from rjv.fasta import *

usage=\
'''
usage: splitfasta.py <fastafile[.gz]> <chunks> <offset> > <outputfile>

eg splitfasta.py mycontigs.fa 10 0
gives every tenth record from the file starting with the first record

eg splitfasta.py mycontigs.fa.gz 20 1
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

ct=-1
for fa in next_fasta(inpname):
    ct += 1
    if ct%chunks != offset: continue
    
    write_fasta(fa,fout)
    
    #fout.write('>' + fa['header'] + newline)
    #fout.write(fa['seq'] + newline)
