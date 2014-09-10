#!/usr/bin/python

'''
print only those sequence whose header matched the regex

usage: cat input.fa | fa_filter.py <regex> > out.fa
'''

import sys,re

usage = 'usage: cat input.fa | fa_filter.py <regex> > out.fa'

if len(sys.argv) != 2:
    print usage
    exit()

regex = sys.argv[1]

fin = sys.stdin
fout = sys.stdout
echo = False

while True:
    line = fin.readline()
    if line == '': break #eof
    
    if line.startswith('>'):
        match = re.search(line[1:],regex)
        if mathc != None:
            echo = True
        else:
            echo = False
            
    if not echo: continue
    
    try:
        fout.write(line)
    except:
        #broken pipe?
        exit()
