import xlrd,re,xlwt

conf_keys =\
[
#mstmap parameters
'population_type',
'population_name',
'distance_function',
'cut_off_p_value',
'no_map_dist',
'no_map_size',
'missing_threshold',
'estimation_before_clustering',
'detect_bad_data',
'objective_function',

#other parameters
'genotype_symbols',
'excel_file',
'sheet_name',
'first_marker',
'first_individual',
'remove_hets',
'sort_by_size',
'output_file',
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

def map2excel(conf,inpfile,rils,scores):
    '''
    convert mstmap output into csv format map file
    including the ril genotype data
    get rilname file from commandline
    '''
    
    #convert ril scores into dict keyed by marker name
    scores_dict = {}
    for row in scores:
        scores_dict[row[0]] = row[1:]
    
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

    #sort linkage groups by cM size
    if conf['sort_by_size'].lower() == 'true':
        data.sort(key=lambda x:x[-1][1],reverse=True)

    workbook = xlwt.Workbook()

    sheetname = 'Sheet1'
    sheet = workbook.add_sheet(sheetname)
    
    styleA = xlwt.easyxf('pattern:pattern solid, fore-colour yellow')
    styleB = xlwt.easyxf('pattern:pattern solid, fore-colour cyan_ega')
    styleH = xlwt.easyxf('pattern:pattern solid, fore-colour green')
    #styleU = xlwt.easyxf('pattern:pattern solid, fore-colour red')

    headers = ['marker','chrom','site'] + rils

    for c,x in enumerate(headers): sheet.write(0,c,x)
        
    ptA = conf['genotype_symbols'][0] #A parent A
    ptB = conf['genotype_symbols'][1] #B parent B
    het = conf['genotype_symbols'][2] #H heterozygote
    unk = conf['genotype_symbols'][3] #- unknown
        
    #for each linkage group
    r = 0
    for i,grp in enumerate(data):
        
        #for each marker
        for j,row in enumerate(grp):
            r += 1
            #marker name, linkage group and map position
            outrow = [row[0],str(i+1),str(row[1])] + scores_dict[row[0]]
            for c,value in enumerate(outrow):
                if c < 3:
                    #uncoloured
                    sheet.write(r,c,string2number(value))
                    continue
                    
                #colour genotype symbols
                if value == ptA:
                    sheet.write(r,c,string2number(value),style=styleA)
                elif value == ptB:
                    sheet.write(r,c,string2number(value),style=styleB)
                elif value == het:
                    sheet.write(r,c,string2number(value),style=styleH)
                else:
                    sheet.write(r,c,string2number(value))

    workbook.save(conf['output_file'])

def map2excel_rqtl(conf,inpfile,rils,scores):
    '''
    convert mstmap output into csv format map file
    including the ril genotype data
    get rilname file from commandline
    '''
    
    #convert ril scores into dict keyed by marker name
    scores_dict = {}
    for row in scores:
        scores_dict[row[0]] = row[1:]
    
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

    #sort linkage groups by cM size
    if conf['sort_by_size'].lower() == 'true':
        data.sort(key=lambda x:x[-1][1],reverse=True)

    workbook = xlwt.Workbook()

    sheetname = 'Sheet1'
    sheet = workbook.add_sheet(sheetname)
    
    styleA = xlwt.easyxf('pattern:pattern solid, fore-colour yellow')
    styleB = xlwt.easyxf('pattern:pattern solid, fore-colour cyan_ega')
    styleH = xlwt.easyxf('pattern:pattern solid, fore-colour green')
    #styleU = xlwt.easyxf('pattern:pattern solid, fore-colour red')

    headers = ['marker','chrom','site'] + rils

    for c,x in enumerate(headers): sheet.write(0,c,x)
        
    ptA = 'AA' #A parent A
    ptB = 'BB' #B parent B
    het = 'AB' #H heterozygote
    unk = '-' #- unknown
        
    #for each linkage group
    r = 0
    for i,grp in enumerate(data):
        
        #for each marker
        for j,row in enumerate(grp):
            r += 1
            #marker name, linkage group and map position
            outrow = [row[0],str(i+1),str(row[1])] + scores_dict[row[0]]
            for c,value in enumerate(outrow):
                if c < 3:
                    #uncoloured
                    sheet.write(r,c,string2number(value))
                    continue
                    
                #colour genotype symbols
                if value == ptA:
                    sheet.write(r,c,string2number(value),style=styleA)
                elif value == ptB:
                    sheet.write(r,c,string2number(value),style=styleB)
                elif value == het:
                    sheet.write(r,c,string2number(value),style=styleH)
                else:
                    sheet.write(r,c,string2number(value))

    workbook.save(conf['output_file'])

def export2mstmap(rils,data,conf,outfile):
    '''
    process data ready for mstmap
    do not validate ril names
    if marker names are duplicated but ril data is the same, ignore them
    otherwise report error
    
    record type:
    markers[mark] = {ril_name:genotype, [ril_name:genotype]}
    '''

    n_markers = len(data)
    n_rils = len(rils)

    f = open(outfile,'wb')
    
    #write mstmap conf
    for k in conf_keys[:10]: f.write('%-030s %s\n'%(k,conf[k]))
    f.write('%-030s %s\n'%('number_of_loci',str(n_markers)))
    f.write('%-030s %s\n'%('number_of_individual',str(n_rils)))
    f.write('\n')

    #write ril names
    f.write('locus_name\t' + '\t'.join(rils) + '\n')

    error_flag = False
    
    ptA = conf['genotype_symbols'][0] #A parent A
    ptB = conf['genotype_symbols'][1] #B parent B
    het = conf['genotype_symbols'][2] #H heterozygote
    unk = conf['genotype_symbols'][3] #- unknown

    #write data
    for row in data:
        #marker name
        row[0] = row[0].strip()
        
        #ignore markers prepended with '#'
        #if mark.startswith('#'): continue
        
        #remove mapmaker asterisk if prepended to marker name
        if row[0].startswith('*'): row[0] = row[0][1:]
        
        #verify data present for each ril heading
        if len(row) != len(rils)+1:
            error_flag = True
            print 'marker '+row[0]+' incorrect number of RIL genotype scores'
            
        #write marker name
        f.write(row[0])    
        
        for i,x in enumerate(row):
            if i == 0: continue #skip marker name
            
            #remove flanking white space, ensure upper case
            row[i] = row[i].strip().upper()
            
            #validate genotype codes
            #if row[i] not in 'ABH-' or row[i] == '':
            if row[i] not in conf['genotype_symbols'] or row[i] == '':
                print 'marker',row[0],'RIL',rils[i-1],\
                      'invalid RIL code "%s"'%row[i],\
                      'converted to "%s" (unknown)'%unk
                row[i] = unk
                #error_flag = True

            #output processed version of genotype symbol
            if row[i] == het:
                symb = 'X'
                if conf['remove_hets'].lower() == 'true': symb = '-'
            elif row[i] == ptA:
                symb = 'A'
            elif row[i] == ptB:
                symb = 'B'
            else:
                symb = '-'

            f.write('\t'+symb)

        #write marker name and ril genotype scores
        f.write('\n')
      
    f.close()
    
    if error_flag:
        raise Exception('error(s) found in data, quiting')

def export2mstmap_rqtl(rils,data,conf,outfile):
    '''
    process data ready for mstmap
    this version handles data exported from r qtl
    '''

    n_markers = len(data)
    n_rils = len(rils)

    f = open(outfile,'wb')
    
    #write mstmap conf
    for k in conf_keys[:10]: f.write('%-030s %s\n'%(k,conf[k]))
    f.write('%-030s %s\n'%('number_of_loci',str(n_markers)))
    f.write('%-030s %s\n'%('number_of_individual',str(n_rils)))
    f.write('\n')

    #write ril names
    f.write('locus_name\t' + '\t'.join(rils) + '\n')

    error_flag = False
    
    ptA = 'AA' #A parent A
    ptB = 'BB' #B parent B
    het = 'AB' #H heterozygote
    unk = '-' #- unknown

    #write data
    for row in data:
        #marker name
        row[0] = row[0].strip()
        
        #ignore markers prepended with '#'
        #if mark.startswith('#'): continue
        
        #remove mapmaker asterisk if prepended to marker name
        if row[0].startswith('*'): row[0] = row[0][1:]
        
        #verify data present for each ril heading
        if len(row) != len(rils)+1:
            error_flag = True
            print 'marker '+row[0]+' incorrect number of RIL genotype scores'
            
        #write marker name
        f.write(row[0])    
        
        for i,x in enumerate(row):
            if i == 0: continue #skip marker name
            
            #remove flanking white space, ensure upper case
            row[i] = row[i].strip().upper()
            
            #validate genotype codes
            #if row[i] not in 'ABH-' or row[i] == '':
            if row[i] not in [ptA,ptB,het,unk] or row[i] == '':
                print 'marker',row[0],'RIL',rils[i-1],\
                      'invalid RIL code "%s"'%row[i],\
                      'converted to "%s" (unknown)'%unk
                row[i] = unk
                #error_flag = True

            #output processed version of genotype symbol
            if row[i] == het:
                symb = 'X'
                if conf['remove_hets'].lower() == 'true': symb = '-'
            elif row[i] == ptA:
                symb = 'A'
            elif row[i] == ptB:
                symb = 'B'
            else:
                symb = '-'

            f.write('\t'+symb)

        #write marker name and ril genotype scores
        f.write('\n')
      
    f.close()
    
    if error_flag:
        raise Exception('error(s) found in data, quiting')

def read_conf(fname):
    '''
    read in conf file
    return as dictionary
    try to allow filenames to contain spaces
    '''
    
    f = open(fname,'rb')
    
    conf = {k:None for k in conf_keys}
    
    for line in f:
        line = line.strip()
        
        if line == '': continue
        if line.startswith('#'): continue
        
        key = line.split()[0]
        if not key in conf:
            raise Exception('unknown configuration option:'+key+' in file:'+fname)
            
        value = line[len(key):].strip()#retain internal whitespace
        conf[key] = value
    
    flag = False
    for k in conf_keys:
        if conf[k] == None:
            flag = True
            print 'missing configuration option:'+k
            
    if flag:
        raise Exception('failed to load all configuration options from file:'+fname)
        
    f.close()
    
    return conf

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
        
        row = []
        for c in range(c3,c4):
            val = sh.cell_value(r,c)
            if type(val) == float: val = '%.0f'%val
            else:                  val = str(val)
            row.append(val)
                
        #row = [str(sh.cell_value(r,c)) for c in range(c3,c4)]
        data.append(marker + row)
        
    return header,data

def find_cell(sh,pattern,rows,cols):
    '''
    find first cell containing value
    scan by row starting from top left
    '''
    
    for r in rows:
        for c in cols:
            if re.search(pattern,str(sh.cell_value(r,c))) != None:
                #print xlrd.colname(c),r+1,pattern
                return r,c
    
    return None,None
    #assert False, "couldn't find "+pattern
