'''
functions for manipulating vcf files
'''

_nl = '\n'

headings = ['#CHROM','POS','ID','REF','ALT','QUAL','FILTER','INFO','FORMAT']
headings2 = ['chrom','pos','id','ref','alt','qual','filter','info','format']

spec = \
[
('chrom',str),
('pos',int),
('id',str),
('ref',str),
('alt',str),
('qual',str),
('filter',str),
('info',str),
#('format',str),
]

def read_vcf_record(f):
    '''
    skip to and read next vcf record
    '''
    
    while True:
        line = f.readline()
        if line == '': return None #end of file
        line = line.strip()
        if line.startswith('#') or line == '': #blank line or header lines
            continue
        
        tok = line.split('\t')
        
        assert len(tok) >= 9, 'expecting at least 9 tab delimited tokens:%s'%line
    
        rec = {}
        
        #required fields
        for i,sp in enumerate(spec):
            rec[sp[0]] = sp[1](tok[i])
            
        #format field
        _format = tok[8].split(':')
        
        genotype = []
        for x in tok[9:]:
            items = x.split(':')
            n = len(items)
            assert len(_format) == n
            y = {_format[i]:items[i] for i in xrange(n)}
            genotype.append(y)
            
        #list of genotype calls
        rec['genotype'] = genotype
        
        #raw vcf record data
        rec['raw'] = line
        
        return rec

def next_vcf(fname):
    '''
    generator to yield next vcf record
    '''
    
    f = open(fname,'rb')
    
    while True:
        rec = read_vcf_record(f)

        #end of file
        if rec == None: break
        
        yield rec

    f.close()


def save_vcf(data,sample_ids,fname):
    '''
    save sorted vcfs
    '''
    
    f = open(fname,'wb')
    
    write_vcf_header(sample_ids,f)
    
    #data.sort(key = lambda x:x['pos'])
    
    for x in data: write_vcf_rec(x,f)
    
    f.close()

def write_vcf_header(sample_ids,f):
    '''
    write vcf file header
    '''
    
    f.write('##fileformat=VCFv4.1' + _nl)

    head = []
    head += headings

    if type(sample_ids) == list:
        head += sample_ids
    else:
        head.append(sample_ids)
        
    f.write('\t'.join(head) + _nl)

def write_vcf_rec(rec,f):
    '''
    write vcf record to file
    where rec has the same fields as headings2 plus a field 'samples'
    containing a list of sample data
    '''

    f.write(str(rec['chrom']) + '\t')
    f.write(str(rec['pos']) + '\t')
    f.write('.' + '\t') #id
    f.write(rec['ref'] + '\t')
    f.write(rec['alt'] + '\t')
    f.write(str(rec['qual']) + '\t') #qual
    f.write('.' + '\t') #filter
    f.write('.' + '\t') #info
    f.write('.' + '\t') #format
    f.write('.' + '\t') #sample
    
    f.write(_nl)
