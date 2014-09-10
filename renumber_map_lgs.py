#!/usr/bin/python

'''
count how many markers have changed linkage group
requires a file giving the old and new LG numbers
'''

import sys

usage=\
'''
usage: renumber_map_lgs.py inp_csv_file out_csv_file
edit the script to set the renumbering scheme
'''

if len(sys.argv) != 3:
    print usage
    exit()
    
inp = sys.argv[1]
out = sys.argv[2]

#map defining renumbering of input map to output map
conv=\
{
    1:7,
    2:2,
    3:1
    4:5,
    5:3,
    6:4,
    7:6,
}

#load map1 data
f = open(inp,"rb")
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

