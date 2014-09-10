'''
functions for reading / writing GFF files
'''

from rjv.defs import _newline

#def write_gff3_record(x,f):
def write_gff(gff,f):
    '''
    write one gff record to file
    '''
    line = [
        gff['seqid'],
        gff['source'],
        gff['type'],
        gff['start'],
        gff['end'],
        gff['score'],
        gff['strand'],
        gff['phase'],
        ';'.join(['%s=%s'%(k,v) for (k,v) in gff['attributes'].iteritems()]),
    ]
    
    f.write('\t'.join( [ str(x) for x in line ] ) + _newline)
    
def gff3_export(data,fname):
    '''
    write gff3 annotation data to file
    '''
    
    f = open(fname,'wb')
    
    if isinstance(data,dict):
        ldata = data.values()
    else:
        ldata = data
    
    f.write('##gff-version 3' + _newline)
    
    for i,x in enumerate(data):
        write_gff3_record(x,f,_newline)
    
    f.close()

def gff3_import(fname,as_dict=False):
    '''
    import gff3 data as a list or dict
    '''
    
    f = open(fname,'rb')
    
    data = []
    
    for line in f:
        line = line.strip()
        if line.startswith('#') or line == '': continue #skip comments
        
        toks = line.split('\t')
        
        assert len(toks) == 9, 'line must have 9 tab-delimited tokens'
            
        x = {}
        data.append(x)
        
        x['seqid']      = toks[0]
        x['source']     = toks[1]
        x['type']       = toks[2]
        x['start']      = int(toks[3])
        x['end']        = int(toks[4])
        x['score']      = float(toks[5])
        x['strand']     = toks[6]
        x['phase']      = toks[7]
        x['attributes'] = dict(x.split('=') for x in toks[8].split(';'))

    f.close()
    
    if as_dict:
        data = dict((x['attributes']['ID'],x) for x in data)
    
    return data

def next_gff(fname):
    '''
    generator to yield next gff
    '''
    
    f = open(fname,'rb')
    
    while True:
        rec = read_gff(f)

        #end of file
        if rec == None: break
        
        yield rec

    f.close()

#def read_gff3_record(f):
def read_gff(f):
    '''
    read the next gff3 record
    '''

    while True:
        line = f.readline()
        if line == '': return None #end of file
        line = line.strip()
        if line.startswith('#') or line == '': continue
        
        toks = line.split('\t')
        
        assert len(toks) == 9, 'gff3 record should have 9 tab delimited tokens:%s'%line
    
        x = {}
        
        x['seqid']      = toks[0]
        x['source']     = toks[1]
        x['type']       = toks[2]
        x['start']      = int(toks[3])
        x['end']        = int(toks[4])
        try:
            x['score']      = float(toks[5])
        except:
            x['score']      = '.'
        x['strand']     = toks[6]
        x['phase']      = toks[7]
        
        try:
            x['attributes'] = dict(y.split('=') for y in toks[8].split(';'))
        except:
            #failed to get attributes, try to retrieve the first one at least
            tmp = toks[8].split(';')[0].split('=')
            x['attributes'] = {tmp[0]:tmp[1]}
            #print 'recovered only first attribute:',x['attributes']
        
        return x

def make_gff(seqid,src,_type,start,end,_id,name,score=0.0,strand='+',phase='.'):
    '''
    convenience function to make a gff record
    '''
    
    x = {}
    
    x['seqid']      = seqid
    x['source']     = src
    x['type']       = _type
    x['start']      = start
    x['end']        = end
    x['score']      = score
    x['strand']     = strand
    x['phase']      = phase
    x['attributes'] = {'ID':_id,'Name':name}
    
    return x
