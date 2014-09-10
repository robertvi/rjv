#!/usr/bin/python

'''
run MSTmap on map data in an excel file
'''

from rjv.mstmap import *

import sys,os

#sys.tracebacklimit = 0
tmpconf = 'tmp_mstmap_conf'
tmpmap = 'tmp_mstmap_output'

usage = \
'''
prepare data from a csv file for input to MSTmap

usage: runmstmap_csv.py <conf_file>

see the example config file for details

note that using the remove_hets option does not remove the Hs
from the resulting output file, it only hides them from mstmap
'''

if len(sys.argv) < 2:
    print usage
    exit()

#read master config file
conf = read_conf(sys.argv[1])

#read in map data in R  QTL export format
csv_file = conf['excel_file']
f = open(csv_file,"rb")
rils = f.readline()
rils = rils.strip().split(',')[3:]
data = []
for line in f:
    tok = line.strip().split(',')
    data.append([tok[0]] + tok[3:])

export2mstmap_rqtl(rils,data,conf,tmpconf)

result = os.system('mstmap %s %s 2> err > out'%(tmpconf,tmpmap))

if result != 0:
    print 'an mstmap error occurred'
    exit()
    
if not os.path.isfile(tmpmap):
    print 'mstmap failed to produce an output file'
    exit()
    
map2excel_rqtl(conf,tmpmap,rils,data)
    
