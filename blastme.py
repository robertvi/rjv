#!/usr/bin/python

'''
wrapper for blastn
'''

from rjv.fileio import *
from rjv.blast import _blastfields_all as fields

import sys

usage=\
'''
wrapper for blastn
blastme.py query.fa subject.fa > output.csv
'''

if len(sys.argv) < 3:
    print usage
    exit()

blast = 'blastn'


ops = '-evalue 1e-20' # -num_threads 4'
outfmt = '-outfmt "10 ' +  ' '.join(fields) + '"'

query = sys.argv[1]
subject = sys.argv[2]

sys.stdout.write( '#' + ','.join(fields) + '\n')
sys.stdout.flush()

run('[blast] -query [query] -subject [subject] [ops] [outfmt]')
