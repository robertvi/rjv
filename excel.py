import re,cPickle,sys
from xlrd import open_workbook
from rjv.misc import string2number

def get_all_data(fname,sheet='Sheet1',conv2numb=False):
    '''
    return all data as a list of lists
    '''
    
    wb = open_workbook(fname)
    sh = wb.sheet_by_name(sheet)
    nrows = sh.nrows
    ncols = sh.ncols
    
    data = []
    
    for r in range(nrows):
        row = []
        data.append(row)
        
        for c in range(ncols):
            val = str(sh.cell_value(r,c))
            if conv2numb: val = string2number(val)
            row.append(val)
    
    return data

def get_excel_data_all(filename,sheetname='Sheet1'):
    '''
    read in data from each row until a blank cell is found
    '''
    
    wb = open_workbook(filename)
    sh = wb.sheet_by_name(sheetname)
    
    data = []
    
    x = 0
    
    while True:
        row = []
        y = 0
        
        while True:
            val = sh.cell_value(x,y)
            if val == '': break
            row.append(val)
            y += 1
        
        data.append(row)
        x += 1
        
    return data
    
def get_excel_data(filename,sheetname,cols,rows):
    '''
    get blocks of data from a (non XML) excel  file
    cols: A,B,F-AA
    rows: 1,4,6-10
    return as consolidated list of rows
    '''
    
    wb = open_workbook(filename)
    sh = wb.sheet_by_name(sheetname)
    cols = excel_col_list(cols)
    rows = excel_row_list(rows)
    
    data = []
    
    for x in rows:
        row = []
        data.append(row)
        
        for y in cols:
            row.append(sh.cell_value(x,y))

    return data
    
def excel_row(s):
    '''
    convert from string excel row number 
    to offset
    '''
    
    return int(s) - 1

def excel_row_list(s):
    '''
    convert from string of row ranges to list of row offsets
    eg '1,2,7-10'
    '''
    
    row_list = []
    
    #split by commas
    for x in s.split(','):
        #split by hyphen
        y = x.split('-')
        if len(y) == 1:
            row_list.append(excel_row(y[0]))
        else:
            assert len(y) == 2, 'invalid row range: %s'%s
            a = excel_row(y[0])
            b = excel_row(y[1])
            for z in range(a,b+1): row_list.append(z)
    
    return row_list
    
def excel_col(s):
    '''
    convert from excel column letter code to python col offset (where A=0, B=1 etc)
    '''
    
    #extract the column, format expected: A1 or ZZ123456
    result = re.search('^([A-Z]+)[0-9]*$',s)
    
    if result == None:
        raise Exception('which excel column did you mean? %s'%s)
    
    col_str = result.group(1)
    col = 0
    
    while True:
        col = col * 26 + int(ord(col_str[0]) - ord('A') + 1)
        
        if len(col_str) == 1: break
        
        col_str = col_str[1:]
        
    return col-1

def excel_col_list(s):
    '''
    convert from string of column ranges to list of column offsets
    eg 'A,B-F,AA-ZZ'
    '''
    
    col_list = []
    
    #split by commas
    for x in s.split(','):
        #split by hyphen
        y = x.split('-')
        if len(y) == 1:
            col_list.append(excel_col(y[0]))
        else:
            assert len(y) == 2, 'invalid column range: %s'%s
            a = excel_col(y[0])
            b = excel_col(y[1])
            for z in range(a,b+1): col_list.append(z)
    
    return col_list
