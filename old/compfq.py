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

#comp = 'bzip2'
#ext = '.bz2'
comp = 'zp c3'
ext = '.zpaq'

if len(sys.argv) != 2:
    print usage
    exit()

inp = sys.argv[1]

outh = inp+'.head'
outb = inp+'.base'
outq = inp+'.qual'
tarfile = inp+'.tar'

tmph = tmpfname()
tmpb = tmpfname()
tmpq = tmpfname()

fhead = open(tmph,'wb')
fbase = open(tmpb,'wb')
fqual = open(tmpq,'wb')

for fq in next_fastq(inp):
    fhead.write(fq['header'] + '\n')
    fbase.write(fq['seq'] + '\n')
    fqual.write(fq['qual'] + '\n')
    
fhead.close()
fbase.close()
fqual.close()

procs = run(
'''
[comp] [outh] [tmph] &
[comp] [outb] [tmpb] &
[comp] [outq] [tmpq] &
''')

waitfor(procs)

remove(tmph)
remove(tmpb)
remove(tmpq)

outh += ext
outb += ext
outq += ext

run('tar -cf [tarfile] [outh] [outb] [outq]')

remove(outh)
remove(outb)
remove(outq)
