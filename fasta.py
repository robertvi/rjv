import re,os,shelve

from rjv.defs import _newline

_offset_prefix = '__POS_BY_OFFSET__'
_header_key = '__HEADER_KEY__'

def qget_fasta(fname,seqid):
    '''
    get fasta from an indexed file
    assumes seqid ends in a 0-based integer
    giving the position of the sequence in the file
    (re)build the index if missing or stale
    '''

    if type(seqid) == int:
        offset = seqid
    else:
        match = re.search('[0-9]+$',seqid)
        assert match
        offset = int(match.group())
    
    index = fname+'.quick'
    make_index = False
    
    if not os.path.isfile(index):
        make_index = True
    else:
        itime = os.path.getmtime(index)
        ftime = os.path.getmtime(fname)
        if ftime > itime: make_index = True

    if make_index:
        qindex_fasta(fname)
        
    pos = qfind_fasta(fname,offset)
    f = open(fname,'rb')
    f.seek(pos)
    fa = read_fasta(f)
    f.close()
    return fa
        
def qfind_fasta(fname,offset):
    '''
    get record start position in file
    from index
    '''
    
    f = open(fname+'.quick','rb')
    
    #find length of one index record
    line = f.readline()
    reclen = f.tell()
    
    #calculate position of sequence record
    f.seek(reclen * offset)
    pos = int(f.readline())
    f.close()
    
    return pos

def qindex_fasta(fname):
    '''
    quick index a fasta file
    all sequence ids must end in a number giving their offset in the
    list of sequences
    '''
    
    #find required record length
    size = os.path.getsize(fname)
    maxlen = len(str(size))
    fmt='%0' +str(maxlen) + 'd'
    
    f = open(fname,'rb')
    index = fname+'.quick'
    findex = open(index,'wb')
    
    count = 0
    
    while True:
        posn = f.tell()
        line = f.readline()
        
        if line.startswith('>'):
            #check that sequence id ends in correct number
            seqid = line[1:].split()[0]
            match = re.search('[0-9]+$',seqid)
            assert match, 'seqid does not end in a number'
            offset = int(match.group())
            assert count == offset, 'seqid number %d does not match sequence offset %d'%(offset,count)
            count += 1
            
            #record position of header
            findex.write(fmt%posn + _newline)
        elif line == '':
            #record position of end of file
            findex.write(fmt%f.tell() + _newline)
            break
            
    findex.close()
    f.close()
    
def get_fasta(fname,seqid,start=None,end=None,nodup=True):
    '''
    get fasta from a shelve-indexed file
    (re)build the index if missing or stale
    '''
    
    index = fname+'.shelve'
    make_index = False
    
    if not os.path.isfile(index):
        make_index = True
    else:
        itime = os.path.getmtime(index)
        ftime = os.path.getmtime(fname)
        if ftime > itime: make_index = True

    if make_index:
        index_fasta(fname,nodup)
        
    pos = find_fasta(fname,seqid)
    f = open(fname,'rb')
    f.seek(pos)
    fa = read_fasta(f)
    f.close()
    
    if start:
        if end:
            if start > end: start,end = end,start
            fa['seq'] = fa['seq'][start:end]
        else:
            fa['seq'] = fa['seq'][start:]
    
    return fa
    
def find_fasta(fname,seqid,raiseerror=True):
    '''
    get record position from an indexed fasta file
    look up by seqid or offset
    '''
    
    ind = shelve.open(fname+'.shelve','r')
    
    try:
        if type(seqid) == int:
            pos = ind[_offset_prefix+str(seqid)]
        else:
            pos = ind[seqid]
        ind.close()
        return pos
    except:
        ind.close()
        if raiseerror:
            raise Exception('unknown seqid: %s'%seqid)
        else:
            return None

def header_fasta(fname):
    '''
    get header info from fasta index
    '''
    
    ind = shelve.open(fname+'.shelve','r')
    header = ind[_header_key]
    ind.close()
    return header
    
def index_fasta(fname,nodup=True):
    '''
    store record position and length in file
    keyed by first whitespace token of header line
    '''
    
    ind = shelve.open(fname+'.shelve','n') #n for new, delete any existing
    f = open(fname,'rb')
    seqcount = 0
    basecount = 0
    
    while True:
        pos = f.tell()
        fa = read_fasta(f,storeseq=False)
        if fa == None: break #end of file
        seqid = fa['id']
        
        if nodup:
            #raise error if name is a duplicate
            assert not ind.has_key(seqid), 'duplicated seqid: %s'%seqid
        
        #store position by seqid and offset
        ind[seqid] = pos
        ind[_offset_prefix+str(seqcount)] = pos
        
        seqcount += 1
        basecount += fa['len']
        
    #store header record
    header = {'seqs':seqcount,'bases':basecount}
    ind[_header_key] = header
    
    ind.close()

def clean_fasta(fa,content='nucl'):
    '''
    santise fasta sequence
    remove whitespace
    convert to upper case
    check for any invalid characters
    '''
    
    #remove any internal white space
    fa['seq'] = fa['seq'].replace(' ','')
    fa['seq'] = fa['seq'].replace('\t','')
    fa['seq'] = fa['seq'].replace('\n','')
    fa['seq'] = fa['seq'].replace('\r','')
    fa['seq'] = fa['seq'].replace('\f','')
    fa['seq'] = fa['seq'].replace('\v','')

    #fa['seq'] = re.sub(r'\s','',fa['seq'])#seems a bit slower
    
    #convert to upper case
    fa['seq'] = fa['seq'].upper()
    
    #check for invalid characters
    if content == 'nucl':
        invalid = '[^ACGTUMRWSYKVHDBXN]'
    else:
        invalid = '[^ABCDEFGHIKLMNPQRSTVWXYZ*]'
    
    match = re.search(invalid,fa['seq'])
    
    if match:
        raise Exception('invalid character in sequence "%s" : "%s"'%(fa['header'],match.group()))
    
    return fa
    
def fasta_mod_header(fname,pattern,replace):
    '''
    modify fasta headers using re.sub
    '''
    
    tmpfile = fname + 'mod_header.tmp'
    
    f1 = open(fname,'rb')
    f2 = open(tmpfile,'wb')
    
    while True:
        line = f1.readline()
        if line == '': break
        line = line.strip()
        
        if line.startswith('>'):
            line = re.sub(pattern,replace,line)
            
        f2.write(line + _newline)
        
    f2.close()
    f1.close()
    
    os.unlink(fname)
    os.rename(tmpfile,fname)

def save_fasta(data,fname):
    '''
    save list of fasta records
    '''
    
    f = open(fname,'wb')
    for rec in data: write_fasta_rec(rec,f)
    f.close()

def append_fasta(fa,f,width=80):
    '''
    save fasta header and sequence
    break into columns of requested width
    append to file if it exists else create
    '''
    
    #if f is a filename open the file for append
    flag = False
    if type(f) == str:
        f = open(f,'a')
        flag = True
    
    f.write('>' + fa['header'] + _newline)
    
    pos = 0
    while True:
        f.write(fa['seq'][pos:pos+width] + _newline)
        pos += width
        if pos >= len(fa['seq']): break
        
    if flag:
        f.close()

def write_fasta(fa,f,width=80):
    '''
    save fasta header and sequence
    break into columns of requested width
    
    append to file if open already
    else overwrite any existing file if filename given
    '''
    
    #if f is a filename open the file for overwriting
    flag = False
    if type(f) == str:
        f = open(f,'wb')
        flag = True
    
    f.write('>' + fa['header'] + _newline)
    
    pos = 0
    while True:
        f.write(fa['seq'][pos:pos+width] + _newline)
        pos += width
        if pos >= len(fa['seq']): break
        
    if flag:
        f.close()

def read_fasta(f,storeseq=True):
    '''
    read next fasta record
    file must be at start of record or end of file
    does not santise or check for valid bases / residues etc
    guesses seqid is first whitespace-token of header
    '''
    
    line = f.readline()
    if line == '': return None #end of file
    assert line.startswith('>'), 'expecting fasta header: %s'%line
    header = line[1:].strip()
    
    seqlen = 0
    seqlines = []
    while True:
        pos = f.tell()
        line = f.readline()
        if line == '' or line.startswith('>'):
            f.seek(pos)
            break
            
        if storeseq:
            seqlines.append(line.strip())
        else:
            seqlen += len(line.strip())
        
    rec = {}
    rec['header'] = header
    rec['id'] = header.split()[0]
    if storeseq:
        rec['seq'] = ''.join(seqlines)
        rec['len'] = len(rec['seq'])
    else:
        rec['seq'] = None
        rec['len'] = seqlen
        
    return rec
    
def next_fasta(fname,storeseq=True):
    '''
    generator to yield next fasta sequence
    '''
    
    f = open(fname,'rb')
    
    while True:
        rec = read_fasta(f,storeseq)

        #end of file
        if rec == None: break
        
        yield rec

    f.close()
    
def next_fasta_split(fname,offset,chunks,storeseq=True):
    '''
    generator to yield next fasta sequence from a file
    split records into groups
    eg offset=0, chunks=10 means yield first of every ten records
    '''

    if fname.endswith('.gz'):
        f = gzip.open(fname,'rb')
    else:
        f = open(fname,'rb')

    ct = -1
    while True:
        ct += 1
        rec = read_fasta(f,storeseq)

        #end of file
        if rec == None: break
        
        if ct%chunks == offset:
            yield rec

    f.close()

def load_fasta_dict(fname,storeseq=True):
    '''
    load fasta as a dictionary keyed by first token of header
    remove lcl| prefix from key if present
    '''
    
    data_list = load_fasta(fname,storeseq)
    
    data = {}
    
    for x in data_list:
        key = x['header'].split()[0]
        if key.startswith('lcl|'): key = key[4:]
        data[key] = x
        
    return data

def load_fasta(fname,storeseq=True):
    '''
    load all fasta records into a list
    each sequence record has: header, id, seq, len
    (because sometimes we want to sequence length without storing the sequence)
    '''
    
    return [x for x in next_fasta(fname,storeseq)]

