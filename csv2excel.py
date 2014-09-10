#!/usr/bin/python

'''
combine a set of csv files into a single excel spreadsheet
with one csv file per sheet using xlwt
'''

import xlwt,sys,csv,os
from rjv.misc import string2number

usage=\
'''
usage: csv2excel.py <csv_file>... > <excel_file>
'''

if len(sys.argv) == 1:
    print usage
    exit()
    
inpfiles = sys.argv[1:]
outfile = sys.stdout

workbook = xlwt.Workbook()

for inpfile in inpfiles:
    f = open(inpfile,'rb')
    data = [row for row in csv.reader(f)]
    f.close()
    
    sheetname = os.path.basename(inpfile).split('.')[0]
    sheet = workbook.add_sheet(sheetname)
    
    for r,row in enumerate(data):
        for c,value in enumerate(row):
            
            sheet.write(r,c,string2number(value))

workbook.save(outfile)
    
