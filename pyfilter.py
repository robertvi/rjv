#!/usr/bin/python

'''
line based filtering using python
usage: cat inpfile | pyfilter.py 'expression' > outfile
'''

import sys,re,time,math

if len(sys.argv) < 2:
    print """usage: cat inpfile | pyfilter.py "'%.3e'%(float(tok[0]))" > outfile"""
    exit()

expr = sys.argv[1]

for line in sys.stdin:
    csv = line.strip().split(',')
    tsv = line.strip().split('\t')
    ssv = line.strip().split()
    
    print eval(expr)
