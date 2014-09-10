#!/usr/bin/python

'''
merge kmer count files

usage: merge_kmerz.py inp inp... out
'''

import sys

inp = sys.argv[1:-1]
out = sys.argv[-1]

fin = [open(x,'rb') for x in inp]
fout = open(out,"wb")

while True:
    count = 0
    
    for i,f in enumerate(fin):
        val = f.read(1)
        if val == '':
            assert i == 0
            count = None
            break
        count += ord(val)
        
    if count == None: break
    
    if count > 255: count = 255
    
    fout.write(chr(count))
    
for f in fin: f.close()
    
fout.close()
