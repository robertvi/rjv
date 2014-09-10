#!/usr/bin/python

'''
fastq decompression

split fastq into three stream: header, bases, quality
compress each separately using bzip2
'''

usage=\
'''
usage: decompfq.py input_file
output filename is to input_file minus trailing .tar
'''

from rjv.fastq import *
from rjv.fileio import *

import sys


decomp = 'bunzip2'
ext = '.bz2'

if len(sys.argv) != 2:
    print usage
    exit()

tarfile = sys.argv[1]

assert tarfile.endswith('.tar')

run('tar -xf [tarfile]')

#chop off .tar
inp = tarfile[:-4]

outh = inp+'.head' + ext
outb = inp+'.base' + ext
outq = inp+'.qual' + ext

remove(outh)
remove(outb)
remove(outq)

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

do_show = True

procs = run(
'''
cat [outh] | [decomp] > [pipeh]&
cat [outb] | [decomp] > [pipeb]&
cat [outq] | [decomp] > [pipeq]&
''')

fhead = open(pipeh,'rb')
fbase = open(pipeb,'rb')
fqual = open(pipeq,'rb')

fout = open(inp+'.test','wb')

for fq in next_fastq(inp):
    header = fhead.readline()
    if header == '': break
    header = header.strip()
    seq = fbase.readline().strip()
    qual = fqual.readline().strip()
    write_fastq(fq,fout)
    
fhead.close()
fbase.close()
fqual.close()
fout.close()

waitfor(procs)

remove(pipeh)
remove(pipeb)
remove(pipeq)

remove(outh)
remove(outb)
remove(outq)
