#!/usr/bin/python

'''
add/update/delete marker database
this is the second version of the marker database
uses pickle instead of shelve

marker record has these fields:
db[marker] = {ril:genotype [,ril:genotype]}

csv format (comma separated, double quote delimited)
header: "marker",      <ril_name>     [,<ril_name>...]
data:   <marker_name>, <ril_genotype> [,<ril_genotype>...]
'''

import sys

from rjv.markers import *

#=========parameters

usage=\
'''
init
addexcel <excel_file> <sheet> [<sheet>...]
addexcel2 <excel_file> <sheet> <first_marker> <first_ril>
exportmstmap <mstconf> [<ril_set>] > <out_file>
exportmstmap2 <mstconf> <excel_file> <sheet> > <out_file>
exportmstmap_nohets <mstconf> [<ril_set>|ALL] > <out_file>
exportprincomp <excel_file> <sheet> > <out_file>
map2csv <mapfile> > <out_file>
add <csv_file>...
modify <csv_file>...
export [<ril_order> [<marker_order>]] > <out_file>
'''

#=========script

if len(sys.argv) == 1:
    print usage
    sys.exit()

command = sys.argv[1]

if command == 'init':
    marker_init()

elif command == 'addexcel':
    marker_from_excel(sys.argv[2],sys.argv[3:])
    
elif command == 'addexcel2':
    assert(len(sys.argv) == 6)
    marker_from_excel2(sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5])
    
elif command == 'add':
    marker_from_csvs(sys.argv[2:])
    
elif command == 'modify':
    marker_from_csvs(sys.argv[2:],modify=True)
    
elif command == 'export':
    if len(sys.argv) == 3:
        #export with custom ril ordering
        marker_export(sys.argv[2])
    elif len(sys.argv) == 4:
        #export with custom ril and marker ordering
        marker_export(sys.argv[2],sys.argv[3])
    else:
        #export with default ril ordering
        marker_export()

elif command == 'exportmstmap':
    if len(sys.argv) == 4:
        #export with custom ril set
        mstmap_export(sys.argv[2],sys.argv[3])
    else:
        #export with default ril set
        mstmap_export(sys.argv[2])

elif command == 'exportmstmap2':
    #export with ril ordering from excel file
    mstmap_export2(sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5])

elif command == 'exportprincomp':
    #export with ril ordering from excel file
    princomp_export(sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5])
    
elif command == 'exportmstmap2_nohets':
    #export with ril ordering from excel file
    mstmap_export2(sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],hets=False)

elif command == 'exportmstmap_nohets':
    #convert hets into unknowns
    if len(sys.argv) == 4:
        #export with custom ril set
        mstmap_export(sys.argv[2],sys.argv[3],hets=False)
    else:
        #export with default ril set
        mstmap_export(sys.argv[2],hets=False)

elif command == 'map2csv':
    #convert mstmap output into csv map file including marker genotypes
    map2csv(sys.argv[2])

elif command == 'map2csv2':
    #convert mstmap output into csv map file including marker genotypes
    #use rilfile in csv format
    map2csv2(sys.argv[2],sys.argv[3])

elif command == 'map2csv3':
    #convert mstmap output into csv map file including marker genotypes
    #get ril ordering from excel sheet
    map2csv3(sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5])

else:
    print usage
    
