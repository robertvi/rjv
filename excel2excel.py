#!/usr/bin/python

'''
apply style changes to an excel file

# aqua 0x31
# black 0x08
# blue 0x0C
# blue_gray 0x36
# bright_green 0x0B
# brown 0x3C
# coral 0x1D
# cyan_ega 0x0F
# dark_blue 0x12
# dark_blue_ega 0x12
# dark_green 0x3A
# dark_green_ega 0x11
# dark_purple 0x1C
# dark_red 0x10
# dark_red_ega 0x10
# dark_teal 0x38
# dark_yellow 0x13
# gold 0x33
# gray_ega 0x17
# gray25 0x16
# gray40 0x37
# gray50 0x17
# gray80 0x3F
# green 0x11
# ice_blue 0x1F
# indigo 0x3E
# ivory 0x1A
# lavender 0x2E
# light_blue 0x30
# light_green 0x2A
# light_orange 0x34
# light_turquoise 0x29
# light_yellow 0x2B
# lime 0x32
# magenta_ega 0x0E
# ocean_blue 0x1E
# olive_ega 0x13
# olive_green 0x3B
# orange 0x35
# pale_blue 0x2C
# periwinkle 0x18
# pink 0x0E
# plum 0x3D
# purple_ega 0x14
# red 0x0A
# rose 0x2D
# sea_green 0x39
# silver_ega 0x16
# sky_blue 0x28
# tan 0x2F
# teal 0x15
# teal_ega 0x15
# turquoise 0x0F
# violet 0x14
# white 0x09
# yellow 0x0D 
'''

import xlwt,xlrd,sys,csv,os
from rjv.misc import string2number
from rjv.excel import get_all_data

usage=\
'''
usage: excel2excel.py <excel_file> > <excel_file>
'''



if len(sys.argv) == 1:
    print usage
    exit()
    
inpfile = sys.argv[1]
outfile = sys.stdout

inp_wb = xlrd.open_workbook(inpfile)
sheets = inp_wb.sheet_names() #list of sheetnames

del inp_wb #no close method?!

out_wb = xlwt.Workbook()

#fore-colour actually seems to set the background colour of the cell
styleA = xlwt.easyxf('pattern:pattern solid, fore-colour yellow')
styleB = xlwt.easyxf('pattern:pattern solid, fore-colour cyan_ega')
styleH = xlwt.easyxf('pattern:pattern solid, fore-colour green')
styleM = xlwt.easyxf('pattern:pattern solid, fore-colour red')
#styleA = xlwt.easyxf('pattern:pattern solid, fore-colour green')
#styleB = xlwt.easyxf('pattern:pattern solid, fore-colour red')
#styleH = xlwt.easyxf('pattern:pattern solid, fore-colour blue')
#styleDEF = xlwt.easyxf('pattern:pattern solid, fore-colour blue')

for shname in sheets:
    out_sh = out_wb.add_sheet(shname)
    data = get_all_data(inpfile,sheet=shname)
    
    for r,row in enumerate(data):
        for c,value in enumerate(row):

            if value == 'A':
                out_sh.write(r,c,string2number(value),style=styleA)
            elif value == 'B':
                out_sh.write(r,c,string2number(value),style=styleB)
            elif value == 'H':
                out_sh.write(r,c,string2number(value),style=styleH)
            elif value == '-':
                out_sh.write(r,c,string2number(value),style=styleM)
            else:
                out_sh.write(r,c,string2number(value))

out_wb.save(outfile)
    
