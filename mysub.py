#!/usr/bin/python

'''
run command on the grid in current directory
capture output,error messages and send to stdout, stderr

usage: mysub command [args]
'''

import sys,random,os
from rjv.cheetah import *

if len(sys.argv) == 1:
    print 'usage: mysub.py cmd...'
    exit()

cmd = sys.argv[1:]

outfile = '.myoutfile%06d'%random.randint(0,999999)
errfile = '.myerrfile%06d'%random.randint(0,999999)
jobfile = '.myjobfile%06d'%random.randint(0,999999)

script='#$ -S /bin/sh\n#$ -N mysub\n#$ -cwd\n#$ -o %s\n#$ -e %s\n#$ -l h_vmem=2G\n'
script = script%(outfile,errfile)
script += ' '.join(cmd) + '\n'

f = open(jobfile,'wb')
f.write(script)
f.close()

qsub = 'qsub -sync y %s > /dev/null'%jobfile
os.system(qsub)
cheetah('cat @outfile')
cheetah('cat @errfile 1>&2')
cheetah('rm @jobfile @outfile @errfile')
