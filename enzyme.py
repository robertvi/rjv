#!/usr/bin/python

'''
scan sequences for restiction enzyme sites
output hits as GFF annotation file
'''

from rjv.gff import *
from rjv.fasta import *
import re,sys

usage=\
'''
usage: ./enzyme.py input.fa pattern_file > output_file.gff

where pattern file is:
<label> && <forward strand regexp> && <reverse strand regexp>

use --none-- if there is no reverse strand regexp
'''

if len(sys.argv) == 1:
    print usage
    exit()

f = open(sys.argv[2],'rb')
reg = []
for line in f:
    reg.append([x.strip() for x in line.split('&&')])
f.close()

ct=0
sys.stdout.write('##gff-version 3' + newline)

for rec in next_fasta(sys.argv[1]):
    name = rec['header'].split()[0]
    for expr in reg:
        #search for matches on the forward strand
        for match in re.finditer(expr[1], rec['seq']):
            ct += 1
            x = make_gff(name,'python', 'enzyme binding',
                         match.start()+1, match.end(),
                         ct, expr[0], strand='+')
            write_gff3_record(x,sys.stdout)
                
        if expr[2] == '--none--': continue
        
        #search for matches on the reverse strand
        for match in re.finditer(expr[2], rec['seq']):
            ct += 1
            x = make_gff(name,'python', 'enzyme binding',
                         match.start()+1, match.end(),
                         ct, expr[0], strand='-')
            write_gff3_record(x,sys.stdout)
