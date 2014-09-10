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
upload an excel file (.xls format) and a config file

usage: runmstmap.py <conf_file>

see the example config file for details

note that using the remove_hets option does not remove the Hs
from the resulting output file, it only hides them from mstmap
'''

if len(sys.argv) < 2:
    print usage
    exit()

#read master config file
conf = read_conf(sys.argv[1])

#read data from excel file
header,data = extract_data2(conf['excel_file'],
                            conf['sheet_name'],
                            conf['first_marker'],
                            conf['first_individual'])

#write data out as mstmap file
export2mstmap(header,data,conf,tmpconf)

os.system('rm %s 2> /dev/null'%tmpmap)

result = os.system('mstmap %s %s 2> err > out'%(tmpconf,tmpmap))

if result != 0:
    print 'an mstmap error occurred'
    exit()
    
if not os.path.isfile(tmpmap):
    print 'mstmap failed to produce an output file'
    exit()
    
map2excel(conf,tmpmap,header,data)
    
