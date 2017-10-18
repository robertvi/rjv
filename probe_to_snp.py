#!/usr/bin/python

#
# convert probeset ids to snp ids in a csv
# usage: cat inpfile | probe2snp.py > outfile
#

import sys
import os

p2s = {}

f1 = '/home/vicker/octoploid_mapping/axiom_chip_info/IStraw90.r1.ps2snp_map.ps.fixed'
f2 = '/home/vicker/rjv_mnt/cluster/octoploid_mapping/axiom_chip_info/IStraw90.r1.ps2snp_map.ps.fixed'

if os.path.isfile(f1):
    f = open(f1)
else:
    f = open(f2)
    
f.readline() #skip header
for line in f:
    tok = line.strip().split()
    pid = tok[0]
    sid = tok[1]
    p2s[pid] = sid
f.close()

for line in sys.stdin:
    if line.startswith('AX-'):
        pid = line[:11]
        sid = p2s[pid]
        line = sid + line[11:]
        sys.stdout.write(line)
    elif line.startswith('PHR-') or line.startswith('NMH-') or line.startswith('MHR-'):
        pid = 'AX-' + line[4:12]
        sid = p2s[pid]
        line = sid + line[12:]
        sys.stdout.write(line)
    elif line.startswith('PHR') or line.startswith('NMH'):
        pid = 'AX'+line[5:14]
        sid = p2s[pid]
        line = sid + line[14:]
        sys.stdout.write(line)
    else:
        sys.stdout.write(line)

f.close()
