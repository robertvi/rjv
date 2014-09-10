'''
functions for reading / writing SAM/BAM files
'''

import os
from rjv.fileio import *

newline = '\n'

#required fields
samspec = \
[
    ('qname',str,'query template name'),
    ('flag',int,'bitfield of flags'),
    ('rname',str,'reference sequence name'),
    ('pos',int,'1-based left most mapping position'),
    ('mapq',int,'mapping quality'),
    ('cigar',str,'cigar string'),
    ('rnext',str,'reference name of the mate/next sequence'),
    ('pnext',int,'position of the mate/next sequence'),
    ('tlen',int,'observed template length'),
    ('seq',str,'segment sequence'),
    ('qual',str,'ascii of phred scaled base quality+33'),
]

#optional fields
fieldtype = \
{
'i':int,
'f':float,
'A':str,
'Z':str,
'H':str,#bytearray in hex format
'B':str,#integer or numeric array
}

def bam2sam(bam,sam):
    '''
    convert bamfile into sam
    '''
    
    assert os.path.exists(bam)
    run('samtools view -h [bam] > [sam]')
    
    
def sam2bam(sam,bam):
    '''
    convert samfile into sam
    '''
    
    assert os.path.exists(sam)
    run('samtools view -Shb [sam] > [bam]')

def sort_bam(inp,outp=None,usebamtools=False):
    '''
    make a sorted version of the bam file
    replace existing file with sorted version
    '''

    assert os.path.exists(inp)
    
    tmpfile = tempfilename()
    
    #run('bamtools sort -in [inp] -out [tmpfile].bam')
    run('samtools sort [inp] [tmpfile]')
    tmpfile += '.bam'
    
    if outp == None:
        #replace unsorted file with sorted one
        remove(inp)
        run('mv [tmpfile] [inp]')
    else:
        #retain unsorted file
        run('mv [tmpfile] [outp]')
    
def index_bam(fname):
    '''
    index the bam file
    '''
    
    assert os.path.exists(fname)
    run('samtools index [fname]')

def filter_bam(inp,script,outp):
    '''
    filter a bam file through a script
    '''

    assert os.path.exists(inp)
    assert os.path.exists(script)

    pipe = tempfilename()
    run('mkfifo [pipe]')
    run('samtools view -h [inp] | [script] > [pipe]&')
    run('samtools view -Sb [pipe] > [outp]')
    remove(pipe)

"""
def write_gff3_record(x,f):
    '''
    write one gff3 record to file
    '''
    line = []
    line.append(x['seqid'])
    line.append(x['source'])
    line.append(x['type'])
    line.append(str(x['start']))
    line.append(str(x['end']))
    line.append(str(x['score']))
    line.append(x['strand'])
    line.append(x['phase'])
    line.append(';'.join(['%s=%s'%(k,v) for (k,v) in x['attributes'].iteritems()]))
        
    f.write('\t'.join(line) + newline)
"""   
   
"""    
def gff3_export(data,fname):
    '''
    write gff3 annotation data to file
    '''
    
    f = open(fname,'wb')
    
    if isinstance(data,dict):
        ldata = data.values()
    else:
        ldata = data
    
    f.write('##gff-version 3' + newline)
    
    for i,x in enumerate(data):
        write_gff3_record(x,f,newline)
    
    f.close()
"""

"""
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
"""

def next_sam(fname):
    '''
    generator to yield next sam record
    from sam file
    '''
    
    f = open(fname,'rb')
    
    while True:
        rec = read_sam_record(f)

        #end of file
        if rec == None: break
        
        yield rec

    f.close()

def next_bam(fname):
    '''
    generator to yield next sam record from bam file
    '''
    
    assert os.path.exists(fname)
    
    pipe = tempfilename()
    run('mkfifo [pipe]')
    run('samtools view [fname] > [pipe]&')
    
    f = open(pipe,'rb')
    
    while True:
        rec = read_sam_record(f)

        #end of file
        if rec == None: break
        
        yield rec

    f.close()
    remove(pipe)

def readheader_sam(fname):
    '''
    return just the header lines from the SAM file
    '''

    lines = []
    
    f = open(fname,'rb')
    
    while True:
        line = f.readline()
        if line == '': return None #end of file
        if line.startswith('#') or line.strip() == '' or line.startswith('@'):
            lines.append(line)
        else:
            break
    
    f.close()
    
    return ''.join(lines)

def read_sam_record(f):
    '''
    skip to and read the next sam record
    '''

    while True:
        line = f.readline()
        if line == '': return None #end of file
        line = line.strip()
        if line.startswith('#') or line == '' or line.startswith('@'):
            continue
        
        tok = line.split('\t')
        
        assert len(tok) >= 11, 'SAM record should have at least 11 tab delimited tokens:%s'%line
    
        rec = {}
        
        #required fields
        for i,spec in enumerate(samspec):
            rec[spec[0]] = spec[1](tok[i])
            
        #optional fields
        for x in tok[11:]:
            #TAG:TYPE:VALUE
            tag,_type,value = x.split(':')
            value = fieldtype[_type](value)
            
            rec[tag] = value
        
        rec['raw'] = line
        
        return rec

"""
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
"""
