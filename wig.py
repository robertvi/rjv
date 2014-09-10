from rjv.defs import _newline

def write_wig(wig,f):
    '''
    save wig header and data
    '''
    
    f.write(wig['header'] + _newline)
    
    for x in wig['data']:
        f.write(str(x) + _newline)

def read_wig(f):
    '''
    read next wig track record
    file must be at start of record or end of file
    '''
    
    line = f.readline()
    if line == '': return None #end of file
    
    assert line.startswith('fixedStep'), 'expecting wig track header: %s'%line
    
    header = line.strip()
    
    data = []
    while True:
        pos = f.tell()
        line = f.readline()
        if line == '' or line.startswith('fixedStep'):
            f.seek(pos)
            break
        
        line = line.strip()
        if line == '': continue #blank line
        
        try:
            val = int(line)
        except:
            val = float(line)
        
        data.append(val)
        
    wig = {}
    wig['header'] = header
    wig['seqid'] = header.split()[1].split('=')[1]
    wig['data'] = data
        
    return wig
    
def next_wig(fname):
    '''
    generator to yield next wig track
    '''
    
    f = open(fname,'rb')
    
    while True:
        wig = read_wig(f)

        #end of file
        if wig == None: break
        
        yield wig

    f.close()
    
def load_wig(fname):
    '''
    load all wig tracks
    each sequence record has: header, seqid, data
    '''
    
    return [x for x in next_wig(fname)]

