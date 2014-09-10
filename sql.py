import sqlite3,os

def insert_row(cur,table,row):
    '''
    insert row into table
    guess data types from row elements
    use None for NULL value
    '''
    
    cmd = "insert into %s values ("%table
    
    for x in row:
        if x == None:
            cmd += 'NULL,'
        elif type(x) == int:
            cmd += '%d,'%x
        elif type(x) == float:
            cmd += '%e,'%x
        else:
            assert type(x) == str
            cmd += "'%s',"%x
            
    cmd = cmd[:-1] + ');'#remove last comma
    
    cur.execute(cmd)

def create_table(cur,table,spec):
    '''
    create table with the given fields
    text is default type
    name/scaf/bp integer/cm real/type
    '''
    
    cur.execute("drop table if exists %s;"%table)
    
    tok = spec.strip().split('/')
    
    for i,x in enumerate(tok):
        y = x.strip().split()
        field = y[0]
        
        if len(y) == 1:
            _type = 'text'
        else:
            assert len(y) == 2
            _type = y[1]
    
        if i == 0:
            cur.execute("create table %s (%s %s);"%(table,field,_type))
        else:
            cur.execute("alter table %s add column %s %s;"%(table,field,_type))

def sql_connect(fname):
    '''
    create new database file, or open existing file
    '''
    
    return sqlite3.connect(fname)

def gff2sql(con,fname,name=None,match=None):
    '''
    con is existing database handle
    
    load in gff3 records
    '''

    #get filename extension
    table = os.path.basename(fname)
    ext = table.split('.')[-1]
    assert ext in ['gff','gff3']
    
    #gff3 main columns are tab delimited
    sep = '\t'
    
    #derive table name from filename
    #or used supplied name
    if name == None:
        table = ''.join(table.split('.')[:-1])
    else:
        table = name
        
    #create table with 'id' as primary key
    #(ie as an alias for rowid)
    cur = con.cursor()
    cur.execute("create table %s (id integer primary key);"%table)

    f = open(fname,'rb')
    
    #create columns for gff3 format data

    cols =\
    [
        'seqid:text',
        'source:text',
        'type:text',
        'start:integer',
        'end:integer',
        'score:real',
        'strand:text',
        'phase:integer',
        'GFFID:text',#ID is already used as the key
        'Name:text',
        'Parent:text',
        'Attr:text',
    ]

    for x in cols:
        cmd = "alter table %s add column %s %s;"%(table,x.split(':')[0],x.split(':')[1])
        #print cmd
        cur.execute(cmd)
            
    #for each row
    null = '.'
    for i,x in enumerate(f):
        if x.startswith('#'): continue #skip comment
        x = x.strip().split(sep)
        values = ["%d"%i] #id
        
        #only use lines with matching type field
        if match != None:
            if x[2] != match:
                continue
        
        values =\
        [
            "%d"%i, #0id
            x[0],#1seqid
            x[1],#2source
            x[2],#3type
            x[3],#4start
            x[4],#5end
            x[5],#6score
            x[6],#7strand
            x[7],#8phase
            '.',#9ID
            '.',#10Name
            '.',#11Parent
            '.',#12any other attr as key=val[;key=val...]
        ]
        
        attr = {}
        for y in x[8].split(';'):
            z = y.split('=')
            attr[z[0]] = z[1]
    
        if 'ID' in attr:
            values[9] = attr['ID']
            del attr['ID']
        if 'Name' in attr:
            values[10] = attr['Name']
            del attr['Name']
        if 'Parent' in attr:
            values[11] = attr['Parent']
            del attr['Parent']
        
        if len(attr) > 0:
            value[12] = ';'.join(['%s=%s'%(k,v) for k,v in attr.iteritems()])
        
        for j,y in enumerate(values):
            #convert '.' into NULL
            if y == null:
                values[j] = 'NULL'
            #enclose text in single quotes
            elif j > 0 and cols[j-1].split(':')[1] == 'text':
                values[j] = "'%s'"%values[j]
                
            assert ',' not in values[j]
                
        values = ','.join(values)
        #print values
        cmd = "insert into %s values (%s);"%(table,values)
        #print cmd
        cur.execute(cmd)
        
    #con.commit()
    
    return con

def blast2sql(con,fname,name=None):
    '''
    load in blast+ outfmt=6 type tsv file
    '''
    
    blastheader = "queryid,subjectid,pident.r,length.i,mismatches.i,gapopens.i,qstart.i,qend.i,sstart.i,send.i,evalue.r,bitscore.r"

    return csv2sql(con,fname,name,blastheader)

def csv2sql(con,fname,name=None,header=None,null='-'):
    '''
    con is existing database handle
    load csv/tsv into sqlite table
    must be .csv with , delimiter
    or .tsv with tab delimiter
    first row must be column names unless provided as argument
    column name ending with .i, .r => int/real
    default type is text
    
    header argument containing tabs will be split by tabs
    else will be split by commas
    '''

    #get filename extension
    table = os.path.basename(fname)
    ext = table.split('.')[-1]
    assert ext in ['csv','tsv']
    
    #infer column delimiting character from ext
    if ext == 'csv': sep = ','
    else :           sep = '\t'
    
    #derive table name from filename
    if name == None:
        table = ''.join(table.split('.')[:-1])
    else:
        table = name
        
    #create table with 'id' as primary key
    #(ie as an alias for rowid)
    cur = con.cursor()
    cur.execute("create table %s (id integer primary key);"%table)

    f = open(fname,'rb')
    
    #if no header provided by caller assume file has a header line
    if header == None:
        header = f.readline().strip()
        header = header.split(sep)
    else:
        #header provided as argument
        if '\t' in header:
            header = header.split('\t') #use tab as sep if tabs found
        else:
            header = header.split(',')#else assume commas
    
    cols = len(header)
    types = []
    for x in header:
        _type = 'text'
        if x.endswith('.i'):
            x = x[:-2]
            _type = 'integer'
        elif x.endswith('.r'):
            x = x[:-2]
            _type = 'real'
        types.append(_type)

        cmd = "alter table %s add column %s %s;"%(table,x,_type)
        #print cmd
        try:
            cur.execute(cmd)
        except:
            print cmd
            exit()
            
    #for each row
    for i,x in enumerate(f):
        x = x.strip().split(sep)
        values = ["%d"%i] #id
        for j,y in enumerate(types):
            # check for NULL
            if x[j] == null:
                values.append('NULL')
            elif y == 'text':
                values.append("'%s'"%x[j])
            else:
                values.append("%s"%x[j])
        values = ','.join(values)
        #print values
        cmd = "insert into %s values (%s);"%(table,values)
        #print cmd
        try:
            cur.execute(cmd)
        except:
            print cmd
            exit()
        
    #con.commit()
    
    return con
