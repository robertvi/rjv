import csv,shelve,os,sys,cPickle,xlrd,re
from rjv.fileio import *

db_file = 'marker_database.pkl'
ril_file = 'ril_names.csv'
newline = '\n'

def extract_data2(fname,sheet,first_marker,first_ril):
    '''
    find the map data in the excel sheet
    return list of ril names
    and grid of marker names and ril genotypes
    uses first marker and ril names to find data
    '''
    
    wb = xlrd.open_workbook(fname)
    sh = wb.sheet_by_name(sheet)
    nrows = sh.nrows
    ncols = sh.ncols
    
    #find cell containing first marker
    r1,c1 = find_cell(sh,first_marker,range(nrows),range(ncols))
    if r1 == None:
        raise Exception('cannot find match to pattern "%s"'%first_marker)
    
    #find first empty cell in marker name col
    r2,c2 = find_cell(sh,r'^$',range(r1,nrows),[c1])
    if r2 == None:
        #if not found assume final row
        c2 = c1
        r2 = nrows
    
    #find cell containing first ril
    r3,c3 = find_cell(sh,first_ril,range(nrows),range(ncols))
    if r3 == None:
        raise Exception('cannot find match to pattern "%s"'%first_ril)
    
    #find the first empty cell in the ril name row
    r4,c4 = find_cell(sh,r'^$',[r3],range(c3,ncols))
    if r4 == None:
        #if not found assume final column
        r4 = r3
        c4 = ncols
    
    #read ril names
    header = [str(sh.cell_value(r3,c)) for c in range(c3,c4)]
    
    #print header
    
    data = []
    
    #read marker names and ril data
    for r in range(r1,r2):
        marker = [str(sh.cell_value(r,c1))]
        row = [str(sh.cell_value(r,c)) for c in range(c3,c4)]
        data.append(marker + row)
        
    return header,data
    
def extract_names2(fname,sheet,first_ril):
    '''
    find the RIL names nad ordering in the excel sheet
    return list of ril names
    uses fi rst ril name to find data
    '''
    
    wb = xlrd.open_workbook(fname)
    sh = wb.sheet_by_name(sheet)
    nrows = sh.nrows
    ncols = sh.ncols
    
    #find cell containing first ril
    r3,c3 = find_cell(sh,first_ril,range(nrows),range(ncols))
    if r3 == None:
        raise Exception('cannot find match to pattern "%s"'%first_ril)
    
    #find the first empty cell in the ril name row
    r4,c4 = find_cell(sh,r'^$',[r3],range(c3,ncols))
    if r4 == None:
        #if not found assume final column
        r4 = r3
        c4 = ncols
    
    #read ril names
    header = [str(sh.cell_value(r3,c)) for c in range(c3,c4)]
    
    return header

def extract_data(fname,sheet):
    '''
    find the map data in the excel sheet
    return list of ril names
    and grid of marker names and ril genotypes
    uses #sample and ^BG to define data locations
    '''
    
    wb = xlrd.open_workbook(fname)
    sh = wb.sheet_by_name(sheet)
    nrows = sh.nrows
    ncols = sh.ncols
    
    #find cell containing '#sample'
    r1,c1 = find_cell(sh,r'#sample',range(nrows),range(ncols))
    if r1 == None:
        raise Exception('cannot find "#sample"')
    
    #find first empty cell in marker name col
    r2,c2 = find_cell(sh,r'^$',range(r1,nrows),[c1])
    if r2 == None:
        #if not found assume final row
        c2 = c1
        r2 = nrows
    
    #find first cell starting with 'BG' in ril name row
    r3,c3 = find_cell(sh,r'^BG',[r1],range(c1,ncols))
    if r3 == None:
        raise Exception('cannot find a RIL name starting with "BG"')
    
    #find the first empty cell in the ril name row
    r4,c4 = find_cell(sh,r'^$',[r3],range(c3,ncols))
    if r4 == None:
        #if not found assume final column
        r4 = r1
        c4 = ncols
    
    #read ril names
    header = [str(sh.cell_value(r1,c)) for c in range(c3,c4)]
    
    data = []
    
    #read marker names and ril data
    for r in range(r1+1,r2):
        marker = [str(sh.cell_value(r,c1))]
        row = [str(sh.cell_value(r,c)) for c in range(c3,c4)]
        data.append(marker + row)
        
    return header,data
    
def find_cell(sh,pattern,rows,cols):
    '''
    find cell containing value
    '''
    
    for r in rows:
        for c in cols:
            if re.search(pattern,str(sh.cell_value(r,c))) != None:
                #print xlrd.colname(c),r+1,pattern
                return r,c
    
    return None,None
    #assert False, "couldn't find "+pattern

def marker_init():
    '''
    create a new empty database file if one does not already exist
    '''
    
    markers = {}
    save_pickle(markers,db_file)
    
def marker_from_csvs(fnames,modify=False):
    '''
    load from multiple csv files
    '''
    for x in fnames: marker_from_csv(x,modify)

def marker_from_excel2(fname,sheet,first_marker,first_ril):
    '''
    load data from an excel file
    '''
    
    header,data = extract_data2(fname,sheet,first_marker,first_ril)
    data = [['Marker'] + header] + data
    
    add_data2(data)

def marker_from_excel(fname,sheets):
    '''
    load data from an excel file
    '''
    
    for sh in sheets:
        print 'sheet:',sh
        header,data = extract_data(fname,sh)
        data = [['#sample'] + header] + data
        
        add_data(data)

def map2csv(inpfile):
    '''
    convert mstmap output into csv format map file
    including the ril genotype data
    '''
    
    #load markers
    markers = load_pickle(db_file)

    #read in ril ordering
    with open(ril_file,'rb') as f: rils = csv.reader(f).next()
    rils = rils[1:] #skip marker column

    #open mst map file
    fin = open(inpfile,'rb')

    #format: data[group][row] = [marker_name,position]
    data = []

    #load data from mstmap map file
    while True:
        line = fin.readline()
        
        #end of file
        if line == '': break
        
        line = line.strip()
        
        #ignore comments and blank lines
        if line.startswith(';') or line == '': continue
        
        if line.startswith('group lg'):
            #start new linkage group
            data.append([])
            continue
            
        toks = line.split('\t')
        data[-1].append([toks[0].strip(),float(toks[1].strip())])

    fin.close()

    #sort linkage groups by size
    data.sort(key=lambda x:x[-1][1],reverse=True)

    fout = sys.stdout

    headers = ['#sample','chrom','site'] + rils
    #headers = ['#sample','cM'] + rils #omitting linkage group
    fout.write(','.join(headers) + newline)

    #for each linkage group
    for i,grp in enumerate(data):
        
        #for each marker
        for j,row in enumerate(grp):
            mark = row[0]
            rec = markers[mark]
            
            #marker name, linkage group and map position
            outrow = [mark,str(i+1),str(row[1])]
            #outrow = [mark,str(row[1])] #omit linkage group
            
            #ril genotypes
            for x in rils:
                if x not in rec:
                    outrow.append('-')
                else:
                    outrow.append(rec[x])
            
            fout.write( ','.join(outrow) + newline)

    fout.close()

    #print data

def map2csv2(inpfile,rilnamez):
    '''
    convert mstmap output into csv format map file
    including the ril genotype data
    get rilname file from commandline
    '''
    
    #load markers
    markers = load_pickle(db_file)

    #read in ril ordering
    with open(rilnamez,'rb') as f: rils = csv.reader(f).next()
    rils = rils[1:] #skip marker column

    #open mst map file
    fin = open(inpfile,'rb')

    #format: data[group][row] = [marker_name,position]
    data = []

    #load data from mstmap map file
    while True:
        line = fin.readline()
        
        #end of file
        if line == '': break
        
        line = line.strip()
        
        #ignore comments and blank lines
        if line.startswith(';') or line == '': continue
        
        if line.startswith('group lg'):
            #start new linkage group
            data.append([])
            continue
            
        toks = line.split('\t')
        data[-1].append([toks[0].strip(),float(toks[1].strip())])

    fin.close()

    #sort linkage groups by size
    data.sort(key=lambda x:x[-1][1],reverse=True)

    fout = sys.stdout

    headers = ['#sample','chrom','site'] + rils
    #headers = ['#sample','cM'] + rils #omitting linkage group
    fout.write(','.join(headers) + newline)

    #for each linkage group
    for i,grp in enumerate(data):
        
        #for each marker
        for j,row in enumerate(grp):
            mark = row[0]
            rec = markers[mark]
            
            #marker name, linkage group and map position
            outrow = [mark,str(i+1),str(row[1])]
            #outrow = [mark,str(row[1])] #omit linkage group
            
            #ril genotypes
            for x in rils:
                if x not in rec:
                    outrow.append('-')
                else:
                    outrow.append(rec[x])
            
            fout.write( ','.join(outrow) + newline)

    fout.close()

    #print data
    
def map2csv3(inpfile,excelfile,sheet,first_name):
    '''
    convert mstmap output into csv format map file
    including the ril genotype data
    get ril ordering from excel file
    '''
    
    #load markers
    markers = load_pickle(db_file)

    #read in ril ordering
    rils = extract_names2(excelfile,sheet,first_name)

    #open mst map file
    fin = open(inpfile,'rb')

    #format: data[group][row] = [marker_name,position]
    data = []

    #load data from mstmap map file
    while True:
        line = fin.readline()
        
        #end of file
        if line == '': break
        
        line = line.strip()
        
        #ignore comments and blank lines
        if line.startswith(';') or line == '': continue
        
        if line.startswith('group lg'):
            #start new linkage group
            data.append([])
            continue
            
        toks = line.split('\t')
        data[-1].append([toks[0].strip(),float(toks[1].strip())])

    fin.close()

    #sort linkage groups by size
    data.sort(key=lambda x:x[-1][1],reverse=True)

    fout = sys.stdout

    headers = ['#sample','chrom','site'] + rils
    #headers = ['#sample','cM'] + rils #omitting linkage group
    fout.write(','.join(headers) + newline)

    #for each linkage group
    for i,grp in enumerate(data):
        
        #for each marker
        for j,row in enumerate(grp):
            mark = row[0]
            rec = markers[mark]
            
            #marker name, linkage group and map position
            outrow = [mark,str(i+1),str(row[1])]
            #outrow = [mark,str(row[1])] #omit linkage group
            
            #ril genotypes
            for x in rils:
                if x not in rec:
                    outrow.append('-')
                else:
                    outrow.append(rec[x])
            
            fout.write( ','.join(outrow) + newline)

    fout.close()

    #print data
    
def marker_export(rilfile=None,markerfile=None):
    '''
    dump to csv file using ril ordering from ril_file
    '''
    
    #load existing markers
    markers = load_pickle(db_file)
    
    #read in requested ril ordering
    if rilfile == None: rilfile = ril_file #default ordering
    with open(rilfile,'rb') as f: rils = csv.reader(f).next()
    rils = rils[1:] #skip marker column
    
    #read in requested marker ordering
    if markerfile == None:
        mark_list = markers.keys()#default, database ordering of all markers
    else:
        #only markers listed in the marker file
        with open(markerfile,'rb') as f: mark_list = [ x[0].strip() for x in csv.reader(f) ]
        mark_list = mark_list[1:] #skip headers
    
    #open outfile
    f = sys.stdout
    
    #dump headings
    f.write('marker,' + ','.join(rils) + newline)
    
    #dump marker data in requested order
    for mark in mark_list:
        row = [mark]
        
        #create blank record for missing markers
        if not mark in markers:
            rec = {}
        else:
            rec = markers[mark]
        
        for k in rils:
            if not k in rec: row.append('-')
            else:            row.append(rec[k])
            
        f.write(','.join(row) + newline)
    
    f.close()

def mstmap_export(mstconf,rilfile=None,hets=True):
    '''
    dump to mstmap format file using ril ordering from ril_file
    '''
    
    #load existing markers
    markers = load_pickle(db_file)
    
    #read in requested ril ordering
    if rilfile == None: rilfile = ril_file #default RILs
    with open(rilfile,'rb') as f: rils = csv.reader(f).next()
    rils = rils[1:] #skip marker column
    
    #open outfile
    f = sys.stdout
    
    #dump mstmap configuration
    fp = open(mstconf,'rb')
    f.write(fp.read())
    fp.close()
    
    #write MSTMap headers
    f.write('number_of_loci               ' + str(len(markers)) + newline)
    f.write('number_of_individual         ' + str(len(rils)) + newline)
    f.write(newline)

    #dump headings
    f.write('locus_name\t' + '\t'.join(rils) + newline)
    
    #dump marker data for requested RILs
    for mark in markers.iterkeys():
        row = [mark]
        rec = markers[mark]
        
        for k in rils:
            if not k in rec:
                row.append('-')
            elif rec[k] == 'H':
                if hets:
                    row.append('X') #use mstmap's convention for displaying hets
                else:
                    row.append('-') #convert hets to unknowns
            else:
                row.append(rec[k])
            
        f.write('\t'.join(row) + newline)
    
    f.close()
    
def mstmap_export2(mstconf,excelfile,sheet,first_ril,hets=True):
    '''
    dump to mstmap format file using ril ordering from excel sheet
    '''
    
    #load existing markers
    markers = load_pickle(db_file)
    
    #read in requested ril ordering
    rils = extract_names2(excelfile,sheet,first_ril)
    
    #open outfile
    f = sys.stdout
    
    #dump mstmap configuration
    fp = open(mstconf,'rb')
    f.write(fp.read())
    fp.close()
    
    #write MSTMap headers
    f.write('number_of_loci               ' + str(len(markers)) + newline)
    f.write('number_of_individual         ' + str(len(rils)) + newline)
    f.write(newline)

    #dump headings
    f.write('locus_name\t' + '\t'.join(rils) + newline)
    
    #dump marker data for requested RILs
    for mark in markers.iterkeys():
        row = [mark]
        rec = markers[mark]
        
        for k in rils:
            if not k in rec:
                row.append('-')
            elif rec[k] == 'H':
                if hets:
                    row.append('X') #use mstmap's convention for displaying hets
                else:
                    row.append('-') #convert hets to unknowns
            else:
                row.append(rec[k])
            
        f.write('\t'.join(row) + newline)
    
    f.close()
    
def princomp_export(excelfile,sheet,first_marker,first_ril):
    '''
    convert sheet into format loadable by R
    '''
    
    conv = {'A':-1, 'B':1, 'H':0, '-':0}
    
    #read in requested ril ordering
    header,data = extract_data2(excelfile,sheet,first_marker,first_ril)
    header = ['Marker'] + header
    
    #open outfile
    f = sys.stdout
    
    f.write('\t'.join(header) + '\n')
    
    for row in data:
        for i,x in enumerate(row):
            if x in conv: row[i] = str(conv[x])
            
        f.write('\t'.join(row) + '\n')
    
    f.close()
    
def marker_from_csv(fname,modify=False):
    '''
    add markers from csv file
    validate ril names
    if marker names are duplicated but ril data is the same, ignore them
    otherwise report error
    
    record type:
    markers[mark] = {ril_name:genotype, [ril_name:genotype]}
    '''
    
    #load csv data
    with open(fname,'rb') as f: data = [row for row in csv.reader(f)]
    
    add_data(data,modify)

def add_data(data,modify=False):
    '''
    add markers from csv file
    validate ril names
    if marker names are duplicated but ril data is the same, ignore them
    otherwise report error
    
    record type:
    markers[mark] = {ril_name:genotype, [ril_name:genotype]}
    '''
    
    #split into ril names and marker data
    rils = data[0][1:]
    data = data[1:]
    
    #load ordered list of valid ril names
    with open(ril_file,'rb') as f: valid_rils = csv.reader(f).next()
    valid_rils = valid_rils[1:] #skip marker column
    valid_rils = [x.strip() for x in valid_rils]
    
    ril_dict = {}
    error_flag = False
    
    #check each ril name found in the file headers
    rils = [x.strip() for x in rils]
    for x in rils:
        if x in ril_dict:
            #duplicated ril name found in headers
            error_flag = True
            print 'duplicated RIL name "%s"'%x
            
        if x not in valid_rils:
            #ril name is not listed as valid
            error_flag = True
            print 'invalid RIL name "%s"'%x
            
        #record all ril names encountered so far
        ril_dict[x] = True
        
    if error_flag:
        print 'aborting'
        return

    #load existing markers
    markers = load_pickle(db_file)
    
    ct_new = 0
    ct_existing = len(markers)
    ct_duplicate = 0
    ct_conflict = 0
    ct_modified = 0
    ct_deleted = 0
    
    for row in data:
        #marker name
        mark = row[0].strip()
        
        #delete ignore markers prepended with '#DEL'
        #if mark.startswith('#DEL'):
        #    mark = mark[4:].strip()
        #    if mark in markers: del markers[mark]
        #    ct_deleted += 1
        #    continue
        
        #ignore markers prepended with '#'
        if mark.startswith('#'): continue
        
        #remove mapmaker asterisk if prepended to marker name
        if mark.startswith('*'): mark = mark[1:]
        
        #ril data
        row = row[1:]
        
        #verify data present for each ril heading
        if len(row) != len(rils):
            print 'marker',mark,'incorrect number of RIL columns'
            error_flag = True
            
        for i,x in enumerate(row):
            #remove flanking white space, ensure upper case
            row[i] = row[i].strip().upper()
            
            #validate genotype codes
            if row[i] not in 'ABH-' or row[i] == '':
                print 'marker',mark,'RIL',rils[i],\
                      'invalid RIL code "%s" converted to -'%row[i]
                row[i] = '-'
                #error_flag = True

        #create new marker record
        rec1 = {}
        for i,x in enumerate(row):
            #do not explicitly record unknown genotypes
            if x == '-' and modify == False: continue
            
            #record all known genotypes, keyed by ril name
            #record '-' if we are fixing existing records
            rec1[rils[i]] = x
        
        #check for duplicated markers
        if mark in markers:
            rec2 = markers[mark]
            
            if modify:
                #apply changes to existing record
                mod = False
                for k,v in rec1.iteritems():
                    if v == '-':
                        if k in rec2:
                            del rec2[k]
                            mod = True
                    elif k not in rec2 or rec2[k] != v:
                        mod = True
                        rec2[k] = v
            
                if mod: ct_modified += 1
            
            elif rec1 != rec2:
                print 'duplicated marker with differing ril data: %s'%mark
                
                #compare conflicting records
                for k in valid_rils:
                    x1 = rec1[k] if k in rec1 else '-'
                    x2 = rec2[k] if k in rec2 else '-'
                    if x1 != x2: print k,x2,'<==>',x1
                    
                ct_conflict += 1
                error_flag = True
            else:
                #print 'duplicated marker with identical ril data: %s'%mark
                ct_duplicate += 1
        else:
            markers[mark] = rec1
            ct_new += 1
            
    print 'existing: %d,  new: %d,  duplicate: %d, conflict: %d, deleted: %d, modified: %d'\
          %(ct_existing,ct_new,ct_duplicate,ct_conflict,ct_deleted,ct_modified)
    
    if error_flag:
        print 'aborting'
        return
        
    save_pickle(markers,db_file)

def add_data2(data,modify=False):
    '''
    add markers from csv file
    do not validate ril names
    if marker names are duplicated but ril data is the same, ignore them
    otherwise report error
    
    record type:
    markers[mark] = {ril_name:genotype, [ril_name:genotype]}
    '''
    
    #split into ril names and marker data
    rils = data[0][1:]
    data = data[1:]
    
    #load existing markers
    markers = load_pickle(db_file)
    
    ct_new = 0
    ct_existing = len(markers)
    ct_duplicate = 0
    ct_conflict = 0
    ct_modified = 0
    ct_deleted = 0
    
    error_flag = False
    
    for row in data:
        #marker name
        mark = row[0].strip()
        
        #ignore markers prepended with '#'
        if mark.startswith('#'): continue
        
        #remove mapmaker asterisk if prepended to marker name
        if mark.startswith('*'): mark = mark[1:]
        
        #ril data
        row = row[1:]
        
        #verify data present for each ril heading
        if len(row) != len(rils):
            print 'marker',mark,'incorrect number of RIL columns'
            error_flag = True
            
        for i,x in enumerate(row):
            #remove flanking white space, ensure upper case
            row[i] = row[i].strip().upper()
            
            #validate genotype codes
            if row[i] not in 'ABH-' or row[i] == '':
                print 'marker',mark,'RIL',rils[i],\
                      'invalid RIL code "%s" converted to -'%row[i]
                row[i] = '-'
                #error_flag = True

        #create new marker record
        rec1 = {}
        for i,x in enumerate(row):
            #do not explicitly record unknown genotypes
            if x == '-' and modify == False: continue
            
            #record all known genotypes, keyed by ril name
            #record '-' if we are fixing existing records
            rec1[rils[i]] = x
        
        #check for duplicated markers
        if mark in markers:
            rec2 = markers[mark]
            
            if modify:
                #apply changes to existing record
                mod = False
                for k,v in rec1.iteritems():
                    if v == '-':
                        if k in rec2:
                            del rec2[k]
                            mod = True
                    elif k not in rec2 or rec2[k] != v:
                        mod = True
                        rec2[k] = v
            
                if mod: ct_modified += 1
            
            elif rec1 != rec2:
                print 'duplicated marker with differing ril data: %s'%mark
                
                #compare conflicting records
                for k in valid_rils:
                    x1 = rec1[k] if k in rec1 else '-'
                    x2 = rec2[k] if k in rec2 else '-'
                    if x1 != x2: print k,x2,'<==>',x1
                    
                ct_conflict += 1
                error_flag = True
            else:
                #print 'duplicated marker with identical ril data: %s'%mark
                ct_duplicate += 1
        else:
            markers[mark] = rec1
            ct_new += 1
            
    print 'existing: %d,  new: %d,  duplicate: %d, conflict: %d, deleted: %d, modified: %d'\
          %(ct_existing,ct_new,ct_duplicate,ct_conflict,ct_deleted,ct_modified)
    
    if error_flag:
        print 'aborting'
        return
        
    save_pickle(markers,db_file)
