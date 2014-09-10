#!/usr/bin/python

'''
convert sam into fastq for file sorted by read name
therefore assumes read pairs are listed on adjacent lines

samtools view [bamfile] | sam2fastq.py [read1] [read2] [read3]
where reads 1 and 2 are paired and read3 is unpaired
'''

import sys

def revcomp(kmer):
    '''
    return reverse complement of the kmer
    only 'ATCGN' are considered legitimate bases
    '''
    
    rev = ''
    
    for ch in kmer:
        if   ch == 'A': rev = 'T' + rev
        elif ch == 'T': rev = 'A' + rev
        elif ch == 'C': rev = 'G' + rev
        elif ch == 'G': rev = 'C' + rev
        elif ch == 'N': rev = 'N' + rev
        else:           raise Exception
        
    return rev
    
def write_rec(f,r):
    if r[3]:
        r[1] = revcomp(r[1])
        r[2] = r[2][::-1]
    
    f.write('@'+r[0]+'\n'+r[1]+'\n+\n'+r[2]+'\n')

fin = sys.stdin

read1 = open(argv[1],"wb")
read2 = open(argv[2],"wb")
read3 = open(argv[3],"wb")

prev = None

while True:
    line = fin.readline()
    if line.startswith('@'): continue
    
    if line == '':
        if prev: write_rec(read3,prev)
        break
        
    tok = line.strip().split('\t')
    
    qname = tok[0]
    seq = tok[9]
    qual = tok[10]
    mate = tok[6]
    rev = int(tok[1]) & 0x10
    if mate == '=': mate = qname
    
    if prev:
        if mate == prev[0]:
            #write read pair
            write_rec(read1,prev)
            write_rec(read2,[qname,seq,qual,rev])
            prev = None
        else:
            #write unpaired read
            write_rec(read3,prev)
            prev = [qname,seq,qual,rev]
    else:
        prev = [qname,seq,qual,rev]
    
