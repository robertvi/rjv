#!/usr/bin/python

'''
count how many markers have changed linkage group
requires a file giving the old and new LG numbers
'''

import sys

usage=\
'''
usage: compare_map_lgs.py csv_file csv_file lg_numbers
'''

if len(sys.argv) != 4:
    print usage
    exit()
    
file1 = sys.argv[1]
file2 = sys.argv[2]
numbs = sys.argv[3]



#load map1 data
f = open(file1,"rb")
for line in f:
    tok = line.strip().split(',')
    marker = tok[0]
    chrm = int(tok[1])
    pos = float(tok[2])
    data1.append([marker,chrm,pos]) #marker, chrom, pos
    leng1[chrm] = max(pos,leng1[chrm]) #record length of each chromosome
f.close()

f = open(file2,"rb")
for line in f:
    tok = line.strip().split(',')
    marker = tok[0]
    chrm = int(tok[1])
    pos = float(tok[2])
    data2.append([marker,chrm,pos]) #marker, chrom, pos
    leng2[chrm] = max(pos,leng2[chrm])
f.close()

