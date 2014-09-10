#!/usr/bin/python

'''
plot marker position according to position in two different maps
'''

import xlrd,sys,time
from rjv.markers import extract_data
from rjv.excel import *
from rjv.fileio import *
from rjv.rplot import *
from subprocess import *

usage=\
'''
usage: compare_maps.py <excel_file> <sheet> <excel_file> <sheet> <png_file>
'''

if len(sys.argv) != 6:
    print usage
    exit()
    
file1 = sys.argv[1]
sheet1 = sys.argv[2]

file2 = sys.argv[3]
sheet2 = sys.argv[4]

outfile = sys.argv[5]

#tmpfile = tempfilename()
#tmpfile2 = tempfilename()
#outfile = open(tmpfile,'wb')

unmapped = -10.0
newline = '\n'

data1 = get_all_data(file1,sheet1)[1:]
data2 = get_all_data(file2,sheet2)[1:]

#add markers to a dict
markers = {}
for i in range(len(data1)):
    row = data1[i]
    markers[row[0]] = [float(row[2]),unmapped]

for i in range(len(data2)):
    row = data2[i]
    if not row[0] in markers:
        markers[row[0]] = [unmapped,float(row[2])]
    else:
        markers[row[0]][1] = float(row[2])

x = [v[0] for v in markers.itervalues()]
y = [v[1] for v in markers.itervalues()]

plot_xy(x,y,outfile,xlab=file1+'_'+sheet1,ylab=file2+'_'+sheet2)
