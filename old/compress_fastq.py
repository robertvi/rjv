#!/usr/bin/python

'''
fastq compression

split fastq into three stream: header, bases, quality
compress each separately using bzip2
'''

usage=\
'''
usage: compfq.py input_file
output is to input_file.tar
'''

from rjv.fastq import *
from rjv.fileio import *

import sys


comp = 'bzip2'
ext = '.bz2'

if len(sys.argv) != 2:
    print usage
    exit()

inp = sys.argv[1]

outh = inp+'.head' + ext
outb = inp+'.base' + ext
outq = inp+'.qual' + ext
tarfile = inp+'.tar'

pipebase = 'pipe'+tmpfname()+'%d'
pipeh = pipebase%1
pipeb = pipebase%2
pipeq = pipebase%3

remove(pipeh)
remove(pipeb)
remove(pipeq)

run('mkfifo [pipeh]')
run('mkfifo [pipeb]')
run('mkfifo [pipeq]')

procs = run(
'''
cat [pipeh] | [comp] > [outh]&
cat [pipeb] | [comp] > [outb]&
cat [pipeq] | [comp] > [outq]&
''')

fhead = open(pipeh,'wb')
fbase = open(pipeb,'wb')
fqual = open(pipeq,'wb')

for fq in next_fastq(inp):
    fhead.write(fq['header'] + '\n')
    fbase.write(fq['seq'] + '\n')
    fqual.write(fq['qual'] + '\n')
    
fhead.close()
fbase.close()
fqual.close()

waitfor(procs)

remove(pipeh)
remove(pipeb)
remove(pipeq)

run('tar -cf [tarfile] [outh] [outb] [outq]')

remove(outh)
remove(outb)
remove(outq)
