#!/usr/bin/python

'''
convert the sam file 'flags' field in human readable form

read input lines from stdin, treat 2nd token as a samfile bitfield
convert into letter codes:

0x0001	p	the read is paired in sequencing
0x0002	P	the read is mapped in a proper pair
0x0004	u	the query sequence itself is unmapped
0x0008	U	the mate is unmapped
0x0010	r	strand of the query (1 for reverse)
0x0020	R	strand of the mate
0x0040	1	the read is the first read in a pair
0x0080	2	the read is the second read in a pair
0x0100	s	the alignment is not primary
0x0200	f	the read fails platform/vendor quality checks
0x0400	d	the read is either a PCR or an optical duplicate

'''

import sys

codes=\
[
(0x0001,'p','paired'),
(0x0002,'P','proper-paired'),
(0x0004,'u','unmapped'),
(0x0008,'U','mate-unmapped'),
(0x0010,'r','reverse-strand'),
(0x0020,'R','mate-reverse-strand'),
(0x0040,'1','1st-of-pair'),
(0x0080,'2','2nd-of-pair'),
(0x0100,'s','not-primary'),
(0x0200,'f','fails-QC'),
(0x0400,'d','PCR-or-optical-duplicate'),
]

newline = '\n'

fin = sys.stdin
fout = sys.stdout

while True:
    line = fin.readline()
    if line == '': break #eof
    
    tok = line.split()
    
    try:
        flags = int(tok[1])
        newflags = ''
        for x in codes:
            if x[0] & flags: newflags += x[1]
        if newflags == '': newflags = '-'
        tok[1] = newflags
    except:
        pass
        
    try:
        fout.write('\t'.join(tok) + newline)
    except:
        break #probably receiving program closed stream

fin.close()
fout.close()
