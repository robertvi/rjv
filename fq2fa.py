#!/usr/bin/python

'''
convert fastq to fasta
assumes every four lines start with sequence line
and then have 3 ignoreable lines
'''

import sys

if len(sys.argv) != 3:
    print 'usage: fq2fa.py inputfile outputfile\n - means stdin/out'
    exit()

if sys.argv[1] == '-':
    fin = sys.stdin
else:
    fin = open(sys.argv[1],'rb')
    
if sys.argv[2] == '-':
    fout = sys.stdout
else:
    fout = open(sys.argv[2],'wb')

while True:
    #description line
    line = fin.readline()
    if line == '': break
    assert line.startswith('@')
    fout.write('>' + line[1:])
    
    #sequence line
    line = fin.readline()
    assert line != ''
    
    try:
        fout.write(line)
    except:
        exit()
    
    #skip next two lines
    line = fin.readline()
    assert line != ''
    line = fin.readline()
    assert line != ''
    
fin.close()
fout.close()

