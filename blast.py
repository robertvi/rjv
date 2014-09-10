import re,os,subprocess,csv
from rjv.fasta import *
from rjv.fileio import *
#from rjv.seqdb import *

from rjv.defs import _newline

_blastnbin = '/usr/bin/blastn'
_blastxbin = '/usr/bin/blastx'

#partial list of available blast record fields
#omitting those relating to NCBI accession & numbers GI number etc
_blastfields_all = [
'qseqid','qlen','qstart','qend','qframe',
'sseqid','slen','sstart','send','sframe',
'evalue','bitscore','score','length','pident','nident','mismatch','positive','gapopen','gaps','ppos','frames',
'qseq','sseq',
]

_blastfields_noseq = [
'qseqid','qlen','qstart','qend','qframe',
'sseqid','slen','sstart','send','sframe',
'evalue','bitscore','score','length','pident','nident','mismatch','positive','gapopen','gaps','ppos','frames',
]

#conversion function for each field
#NB: may not all be correct
_fieldtype = {
'qseqid':str,'qlen':int,'qstart':int,'qend':int,'qframe':int,
'sseqid':str,'slen':int,'sstart':int,'send':int,'sframe':int,
'evalue':float,'bitscore':float,'score':str,'length':int,'pident':str,'nident':int,'mismatch':int,
'positive':int,'gapopen':int,'gaps':int,'ppos':float,'frames':str,
'qseq':str,
'sseq':str,
}

def mask_hit(fa,hit,query=True,check=True,soft=False):
    '''
    mask the matching part of the sequence using Ns
    or lowercase (soft masking)
    '''
    
    if query:
        start = hit['qstart']
        end = hit['qend']
        
        if check: assert fa['id'] == hit['qseqid']
    else:
        start = hit['sstart']
        end = hit['send']

        if check: assert fa['id'] == hit['sseqid']
        
    if start > end: start,end = end,start
    
    #convert from 1- to 0-based
    #note: end now means one-past-the-end in 0-based
    start -= 1
    
    seqlen = len(fa['seq'])
    assert start >= 0 and start < seqlen
    assert end > 0 and end <= seqlen

    seq1 = fa['seq'][:start]
    if soft:
        seqNNN = fa['seq'][start:end].lower()
    else:
        seqNNN = 'N'*(end-start)
    seq2 = fa['seq'][end:]
    
    fa['seq'] = seq1+seqNNN+seq2

def hit_seq(fa,hit,query=True,check=True):
    '''
    get sequence from the fa corresponding to the blast hit
    '''
    
    if query:
        start = hit['qstart']
        end = hit['qend']
        
        if check: assert fa['id'] == hit['qseqid']
    else:
        start = hit['sstart']
        end = hit['send']

        if check: assert fa['id'] == hit['sseqid']
        
    if start > end: start,end = end,start
    
    #convert from 1- to 0-based
    start -= 1
    
    return fa['seq'][start:end]

def hits_overlap(a,qa,b,qb):
    '''
    return true if blast hits a and b overlap
    qa True means use query position of a
    qb True means use query position of b
    
    does NOT check that sequence ids are the same!
    '''
    
    if qa:
        start1 = a['qstart']
        end1 = a['qend']
    else:
        start1 = a['sstart']
        end1 = a['send']

    if qb:
        start2 = b['qstart']
        end2 = b['qend']
    else:
        start2 = b['sstart']
        end2 = b['send']
    
    if start1 > end1: start1,end1 = end1,start1
    if start2 > end2: start2,end2 = end2,start2
        
    if end1 < start2 or end2 < start1: return False

    return True

"""
def next_blast2gff(fname,headers=_blastfields_all,annotate_subject=True,score='evalue'):
    '''
    generator to yield blast hits as gff records
    '''
    
    #iterator through the results file
    f = open(fname,'rb')
    
    ct=-1
    
    for hit in csv.reader(f):
        ct += 1
        
        #check number of fields agrees
        assert len(hit) == len(headers)

        rec = {}
        for i,x in enumerate(hit):
            key = headers[i]
            func = _fieldtype[key] if key in _fieldtype else str
            val = func(x)
            rec[key] = val
            
        gff = {}
        
        s1 = rec["sstart"]
        s2 = rec["send"]
        q1 = rec["qstart"]
        q2 = rec["qend"]
        
        if annotate_subject:
            #annotate the subject with the query hit
            gff['seqid'] = rec['sseqid']
            
            if s1 > s2:
                #start must be <= end
                #note:sequences are now reversed!
                s1,s2 = s2,s1
                q1,q2 = q2,q1
            
            gff['start'] = int(s1)
            gff['end']   = int(s2)
            
            #label using query name
            _id = rec['qseqid'] +':'+ str(ct)
            gff['attributes'] = {'ID':_id,'Name':_id}
            
        else:
            #annotate the query sequence with the subject hit
            gff['seqid'] = rec['qseqid']
            
            if q1 > q2:
                #start must be <= end
                #note:sequences are now reversed!
                s1,s2 = s2,s1
                q1,q2 = q2,q1
            
            gff['start'] = int(q1)
            gff['end']   = int(q2)
        
            #label using subject name
            _id = rec['sseqid'] +':'+ str(ct)
            gff['attributes'] = {'ID':_id,'Name':_id}
            
        gff['source'] = 'blast'
        gff['type'] = 'match' #type: from SOFA sequence ontology
        gff['score'] = float(rec[score]) #defaults to evalue
        gff['phase'] = '.' #CDS only
        
        
        if (s1 < s2) == (q1 < q2): gff['strand'] = '+' #strand
        else:                      gff['strand'] = '-'
        
        yield gff
        
    f.close()
"""

def blast2gff(rec,query=True,uid=None,score='evalue',_type='match',_source='blast'):
    '''
    convert a blast hit into a gff annotation
    annotations are against subject sequence or query sequence
    depending on annotate_subject flag
    '''
    
    gff = {}
    
    s1 = rec["sstart"]
    s2 = rec["send"]
    q1 = rec["qstart"]
    q2 = rec["qend"]
    
    if query:
        #annotate the query sequence with the subject hit
        gff['seqid'] = rec['qseqid']
        
        if q1 > q2:
            #start must be <= end
            #note:sequences are now reversed!
            s1,s2 = s2,s1
            q1,q2 = q2,q1
        
        gff['start'] = int(q1)
        gff['end']   = int(q2)
    
        #label using subject name
        _id = rec['sseqid']
        if uid: _id += ':'+ str(uid)
        gff['attributes'] = {'ID':_id,'Name':_id}
    else:
        #annotate the subject with the query hit
        gff['seqid'] = rec['sseqid']
        
        if s1 > s2:
            #start must be <= end for a gff
            #note:sequences are now reversed!
            s1,s2 = s2,s1
            q1,q2 = q2,q1
        
        gff['start'] = int(s1)
        gff['end']   = int(s2)
        
        #label using query name
        _id = rec['qseqid']
        if uid: _id += ':'+ str(uid)
        gff['attributes'] = {'ID':_id,'Name':_id}
        
    gff['source'] = _source
    gff['type'] = _type #type: from SOFA sequence ontology
    
    if score in rec:
        gff['score'] = float(rec[score]) #defaults to evalue
    else:
        gff['score'] = '.'
        
    gff['phase'] = '.'
    
    if (s1 < s2) == (q1 < q2): gff['strand'] = '+' #strand
    else:                      gff['strand'] = '-'
    
    return gff

def blast2fasta(blastfile,fastafile,subject=True):
    '''
    for each unique hit in the blastfile
    lookup the full sequence and save to the fasta file
    
    extract the database key from the sequence id
    
    if subject == False, lookup the query sequence instead
    '''
    
    f = open(fastafile,'wb')
    id_dict = {}
    
    if subject: seqkey = 'sseqid'
    else:       seqkey = 'qseqid'
    
    for hit in next_blast(blastfile):
        seqid = hit[seqkey]
        
        #skip duplicate hits
        if seqid in id_dict:
            continue
        else:
            id_dict[seqid] = True
                
        #extract the database key from the seqid
        #dbkey = seqid[:-11]
        
        #lookup the sequence record
        #rec = blastdb_rec(dbkey,seqid)
        #rec = blastdb_rec(seqid)
        rec = seqrecord(seqid)
        
        #write to file in fasta format
        write_fasta_rec(rec,f)
    f.close()


def hit2fasta(seqid,fname):
    '''
    save a single blast hit to a fasta file
    '''

    rec = seqrecord(seqid)
    f = open(fname,'wb')
    write_fasta_rec(rec,f)
    f.close()
    
def blastx(query,subject,outfile=None,threads=4,ops='',fields=_blastfields_all):
    '''
    run blastx locally
    query - name of fasta file containing query sequences
    subject - name of blast database containing subject sequences
    outfile - name of output file
    threads - how many threads to use during search
    ops - extra blast options
    incl_seq - if true, include sequence in output
    '''

    tmpfile = False
    
    if outfile == None:
        outfile = tempfilename()
        tmpfile = True

    #get name of blast database from the database id
    dbname = lookup_file(subject)
    
    #which data to include from blast output
    outfmt = ' '.join(fields)
    
    cmd = [
           _blastxbin,
           '-num_threads',str(threads),
           '-parse_deflines',
           '-query',query,
           '-db',dbname,
           '-out',outfile,
           '-outfmt','"10 %s"'%outfmt,
           ops,
          ]

    cmdstr = ' '.join(cmd)
    
    result = subprocess.call(cmdstr,shell=True)
    
    assert result == 0, 'error for command: %s'%cmd
    
    #return results directly if a tmp file was used
    if tmpfile:
        hits = load_blast(outfile)
        os.unlink(outfile)
        return hits
    else:
        return None
    
def blastn(query,subject,outfile=None,threads=4,ops='',fields=_blastfields_all):
    '''
    run blast locally
    query - name of fasta file containing query sequences
    subject - name of blast database containing subject sequences
    outfile - name of output file
    threads - how many threads to use during search
    ops - extra blast options
    incl_seq - if true, include sequence in output
    '''

    tmpfile = False
    
    if outfile == None:
        outfile = tempfilename()
        tmpfile = True

    #get name of blast database from the database id
    dbname = lookup_file(subject)
    
    outfmt = ' '.join(fields)
    
    cmd = [
           _blastnbin,
           '-num_threads',str(threads),
           '-parse_deflines',
           '-query',query,
           '-db',dbname,
           '-out',outfile,
           '-outfmt','"10 %s"'%outfmt,
           ops,
          ]

    cmdstr = ' '.join(cmd)
    
    result = subprocess.call(cmdstr,shell=True)
    
    assert result == 0, 'error for command: %s'%cmd
    
    #return results directly if a tmp file was used
    if tmpfile:
        hits = load_blast(outfile)
        os.unlink(outfile)
        return hits
    else:
        return None
    
def blastn_stdout(query,subject,threads=4,ops=''):
    '''
    run blast locally
    show results to stdout
    '''

    dbname = lookup_name(subject)
    
    cmd = [
           _blastnbin,
           '-num_threads',str(threads),
           '-parse_deflines',
           '-query',query,
           '-db',dbname,
           ops,
          ]

    cmdstr = ' '.join(cmd)
    
    result = subprocess.call(cmdstr,shell=True)
    
    assert result == 0, 'error for command: %s'%cmd

def blast_filter(fname,code,params={}):
    '''
    filter blast hits based on python expression
    '''
    
    comp = compile(code,'dummyfilename','eval')
    
    tmpfile = fname+'_filter_tmp_'
    f = open(tmpfile,'wb')
    
    for i,x in enumerate(next_blast(fname)):
        params['x'] = x
        params['i'] = i
        if not eval(comp,params): continue
        write_blast(x,f)
    
    f.close()
    os.unlink(fname)
    os.rename(tmpfile,fname)

def save_blast(data,fname,fields=_blastfields_all):
    '''
    write all blast records to file
    '''
    
    f = open(fname,'wb')
    
    #write header
    writeheader_blast(f,fields)
    
    for x in data: write_blast(x,f,fields)
    f.close()

def write_blast(hit,f,fields=_blastfields_all):
    '''
    write blast hit to file
    write record in order defined by fields
    '''
    
    #assert len(hit) == len(fields)
    line = []
    
    #use number of tokens on line to determine if seq data is included
    line = [ str(hit[field]) for field in fields ]
    f.write( ','.join(line) + _newline)
    
def writeheader_blast(f,fields=_blastfields_all):
    '''
    write blast fields header to file
    '''

    f.write('#'+','.join(fields) + _newline)

def saveheader_blast(fname,fields=_blastfields_all):
    '''
    write blast fields header to file
    '''

    f = open(fname,'wb')
    f.write('#'+','.join(fields) + _newline)
    f.close()

class blastpeeker:
    def __init__(self,fname,fields=_blastfields_all):
        self.f = open(fname,'rb')
        self.fields = fields
        self.prevpos = None
        
    def nxt(self):
        '''
        return next blast hit
        with ability to 'put it back' later
        '''
        
        self.prevpos = self.f.tell()
        return self.read()
        
    def replace(self):
        '''
        replace file position at start of previous record
        '''
        
        assert self.prevpos != None
        self.f.seek(self.prevpos)
        
    def close(self):
        '''
        close file
        not done in read in case a replace is required
        after the last record
        '''
        
        self.f.close()
        
    def read(self):
        '''
        read in the next blast record from tabular blast file
        return None if end of file
        '''
        
        while True:
            line = self.f.readline()
            if line == '':
                return None #end of file
            line = line.strip()
            if line == '': continue #blank line
            
            tok = line.split(',')
            if tok[0].startswith('#'): #header line
                #get fields from header, override fields argument
                tok[0] = tok[0][1:]
                self.fields = tok
                continue
                
            assert len(tok) == len(self.fields)

            rec = {}
            for i,x in enumerate(tok):
                key = self.fields[i]
                func = _fieldtype[key] if key in _fieldtype else str
                val = func(x)
                rec[key] = val
                
            return rec

def next_blast(fname,fields=_blastfields_all):
    '''
    generator to yield blast hits
    '''
    
    #iterator through the results file
    f = open(fname,'rb')
    
    for hit in csv.reader(f):
        if len(hit) > 0 and hit[0].startswith('#'):
            #get fields from header, override fields argument
            hit[0] = hit[0][1:]
            fields = hit
            continue
            
        assert len(hit) == len(fields)

        rec = {}
        for i,x in enumerate(hit):
            key = fields[i]
            func = _fieldtype[key] if key in _fieldtype else str
            val = func(x)
            rec[key] = val
        
        yield rec
        
    f.close()

def next_blast_fast(fname,fields=_blastfields_all):
    '''
    generator to yield blast hits
    leave all data as string format
    do not convert into ints and floats
    ignore any file header
    '''
    
    #iterator through the results file
    f = open(fname,'rb')
    
    for hit in csv.reader(f):
        #use number of tokens on line to determine if seq data is included
        assert len(hit) == len(fields)

        rec = dict((fields[i],x) for (i,x) in enumerate(hit)) #py2.6
        #rec = { fields[i]:x for i,x in enumerate(hit) } #py2.7 only
        yield rec
        
    f.close()
    
def next_blast_fast2(fname):
    '''
    generator to yield blast hits
    return hit as a list not a dict
    '''
    
    #iterator through the results file
    f = open(fname,'rb')
    
    for hit in csv.reader(f):  yield hit
        
    f.close()
    
def load_blast(fname):
    '''
    load all results from blast tabular file
    '''
    
    return [ hit for hit in next_blast(fname) ]
