#!/usr/bin/python

'''
convert a csv file into a colour coded xls
used for colouring genotypes in a map file

usage: cat inpfile.csv | colour_csv.py outfile.xls A=yellow B=cyan_ega H=green ...
'''

import xlrd,re,xlwt,sys

colours=\
[
    'aqua',
    'black',
    'blue',
    'blue_gray',
    'bright_green',
    'brown',
    'coral',
    'cyan_ega',
    'dark_blue',
    'dark_blue_ega',
    'dark_green',
    'dark_green_ega',
    'dark_purple',
    'dark_red',
    'dark_red_ega',
    'dark_teal',
    'dark_yellow',
    'gold',
    'gray_ega',
    'gray25',
    'gray40',
    'gray50',
    'gray80',
    'green',
    'ice_blue',
    'indigo',
    'ivory',
    'lavender',
    'light_blue',
    'light_green',
    'light_orange',
    'light_turquoise',
    'light_yellow',
    'lime',
    'magenta_ega',
    'ocean_blue',
    'olive_ega',
    'olive_green',
    'orange',
    'pale_blue',
    'periwinkle',
    'pink',
    'plum',
    'purple_ega',
    'red',
    'rose',
    'sea_green',
    'silver_ega',
    'sky_blue',
    'tan',
    'teal',
    'teal_ega',
    'turquoise',
    'violet',
    'white',
    'yellow',
]

def string2number(value):
    '''
    try to convert to a float or int
    '''
    
    try:
        return int(value)
    except:
        pass
        
    try:
        return float(value)
    except:
        pass
        
    return value

if len(sys.argv) < 2:
    for i in colours: print i
    print 'usage: cat inpfile.csv | colour_csv.py outfile.xls pat1=col1 pat2=col2...'
    exit()

f = sys.stdin

workbook = xlwt.Workbook()
sheetname = 'Sheet1'
sheet = workbook.add_sheet(sheetname)

outfile = sys.argv[1]
symbols = sys.argv[2:]

symdict = {}

for x in symbols:
    x = x.split('=')
    assert x[1] in colours
    symdict[x[0]] = xlwt.easyxf('pattern:pattern solid, fore-colour %s'%x[1])

r=0
for line in f:
    tok = line.strip().split(',')
    c=0

    for x in tok:
        value = string2number(x)
        if x in symdict:
            sheet.write(r,c,value,symdict[x])
        else:
            sheet.write(r,c,value)

        c+=1
        
    r+=1
workbook.save(outfile)
