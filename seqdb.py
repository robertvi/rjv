'''
build a database from a set of fasta files listed in
a source_list file

sanitise the sequences and headers

convert headers to: lcl|<dbname>_<seqoffset> <original_header>

store sequences as 80 bases per line
make an index file where all index records have the same
length as the first record

'''

import subprocess,shelve,re
from rjv.fasta import *
from rjv.fileio import *
from socket import gethostname

from rjv.defs import _newline

basedirdict =\
{
    'bert':'/ibers/ernie/home/rov/seq_data/',
    'mocedades':'/home/rov/rjv_files/seq_data/',
}

basedir = basedirdict[gethostname()]
source_file = basedir+'source_list'
database_file = basedir+'db.pickle'
alias_file = basedir+'alias.shelve'

def rebuild_all():
    '''
    rebuild all blast databases
    create new database index
    drop all previous information
    '''
    
    #remove any existing alias and db files
    remove(database_file)
    remove(alias_file)
    
    #load even those records preceeded by a #
    file_list = read_source_list(ignore=False)
    
    sanitize_fastas(file_list)
    
    create_blastdbs(file_list)
    
    create_indexes(file_list)
    
    save_pickle(file_list,database_file)

def add_newdbs():
    '''
    build new blast databases
    add to existing database index
    retain all previous information
    '''
    
    #load only those records where the key is not preceeded by a #
    new_list = read_source_list(ignore=True)
    
    sanitize_fastas(new_list)
    
    create_blastdbs(new_list)
    
    create_indexes(new_list)
    
    orig_list = load_pickle(database_file)
    
    for k,v in new_list.iteritems():
        orig_list[k] = v
    
    save_pickle(orig_list,database_file)

def db_info(db_key):
    '''
    show summary stats of database
    '''
    
    file_dict = load_pickle(database_file)
    
    if not db_key in file_dict:
        print db_key,'not found'
        return
    
    info = file_dict[db_key]
    for key,val in info.iteritems():
        print key,'=',val

def lookup_file(db_key):
    '''
    go from key to fasta file name
    this is also the blast database name
    '''
    
    file_list = load_pickle(database_file)
    
    assert db_key in file_list
    
    #if not db_key in file_list: return None
    
    return file_list[db_key]['file_mod']

def seqdb_info():
    '''
    return dict of database info
    '''
    
    return load_pickle(database_file)

def list_keys():
    '''
    list all blast database keys
    '''
    
    file_list = load_pickle(database_file)
    
    for k in file_list.iterkeys(): print k

"""
def read_index(fname,offset):
    '''
    get record start/end position in file
    from index
    '''
    
    f = open(fname+'.indx','rb')
    
    #find length of one index record
    line = f.readline()
    reclen = f.tell()
    
    #calculate position of sequence record
    f.seek(reclen * offset)
    pos1 = int(f.readline())
    pos2 = int(f.readline())
    f.close()
    
    return [pos1,pos2]
"""

def seqheader(seqid,token=0):
    '''
    convenience function to return a given token of the header
    '''
    
    return seqrecord(seqid,None)['header'].split()[token]

def lookup_alias(db_key,seqalias):
    '''
    lookup a sequence alias
    '''
    
    alias_db = shelve.open(alias_file,'r')
    
    alias = db_key+'::'+seqalias
    assert alias_db.has_key(alias)
    seqoffset = alias_db[alias]
    
    alias_db.close()
    
    return db_key+'_%010d'%seqoffset

def seqrecord(seqid,start=1,end=None):
    '''
    get sequence from indexed fasta
    seqid must be of the form dbkey_%010d(seqoffset)
    see lookup alias for alternative function
    
    start and end position are 1 based
    the end is the last base to include
    not the first base to exclude
    
    end=None => until the end
    start=None => do not load sequence
    '''
    
    db_key = seqid[:-11]
    fname = lookup_file(db_key)
    
    seqoffset = int(seqid[-10:])
    pos = read_index(fname,seqoffset)
    
    f = open(fname,'rb')
    
    #read header
    f.seek(pos[0])
    header = f.readline()[1:].strip()
    _id = header.split()[0][4:]
    
    #if end == None replace with length of sequence
    seqstart = f.tell()
    seqlengthfile = pos[1] - seqstart
    
    #each (partial) line in the file is 81 bytes
    #but contributes only 80 bases (plus _newline)
    linelen = 81
    seqlengthbp = seqlengthfile - ((seqlengthfile-1)//linelen + 1)
    
    rec = {}
    rec['header'] = header
    rec['id'] = _id
    rec['len'] = seqlengthbp
    rec['seq'] = None
    
    if start == None:
        f.close()
        return rec
        
    if end == None: end = seqlengthbp

    assert start >= 1 and start <= seqlengthbp
    assert end >= start and end <= seqlengthbp
        
    #calculate file position of start and end
    startfile = seqstart + (start-1) + ((start-1)//(linelen-1))
    endfile   = seqstart + end       + ((end-1)//(linelen-1))
    
    #read sequence
    f.seek(startfile)
    seq = f.read(endfile-startfile).replace(_newline,'')
    f.close()
    
    return {'id':_id,'header':header,'seq':seq,'len':seqlengthbp}
    
"""    
def create_index(fname):
    '''
    index a fasta file
    '''
    
    f = open(fname,'rb')
    
    index = fname+'.indx'
    findex = open(index,'wb')
    
    fmt='%016d'
    
    while True:
        posn = f.tell()
        line = f.readline()
        
        if line.startswith('>'):
            #record position of header
            findex.write(fmt%posn + _newline)
        elif line == '':
            #record end of file
            findex.write(fmt%f.tell() + _newline)
            break
            
    findex.close()
    f.close()
"""

def create_indexes(file_list):
    '''
    for each file in the list
    create a fasta index
    '''
    
    for rec in file_list.itervalues():
        create_index(rec['file_mod'])

    
def create_blastdbs(file_list):
    '''
    for each file in the list
    create a blast db using blast+
    '''
    
    for rec in file_list.itervalues():
        blastplusdb(rec['file_mod'],rec['type'])
    
def blastplusdb(seqfile,dbtype='nucl'):
    '''
    setup local blastplus database 
    reuse an existing database if it's younger than the fasta file
    this version does not parse the sequence ids therefore cannot
    be used to retrieve sub(sequences) using blastdbcmd
    '''
    
    assert os.path.isfile(seqfile)
    
    #see if a database by that name already exists
    f = os.path.isfile
    if f(seqfile+'.nhr') and f(seqfile+'.nin') and f(seqfile+'.nsq'):
        #see if the fasta file is older than the dbfile
        if os.path.getmtime(seqfile) < os.path.getmtime(seqfile+'.nhr'):
            print 'reusing existing database files'
            return
            
    print 'making blast database from %s'%(seqfile)
    #cmd = 'makeblastdb -in %s -dbtype nucl -parse_seqids'%seqfile
    cmd = 'makeblastdb -in %s -dbtype %s -parse_seqids'%(seqfile,dbtype)
    #cmd = 'makeblastdb -in %s -parse_seqids'%seqfile

    if subprocess.call(cmd.split()) != 0:
        raise Exception('makeblastdb error')
    
def sanitize_fastas(file_list):
    '''
    apply modification to sequences / headers
    save as new fasta file
    '''
    
    #open alias file
    alias_shlv = shelve.open(alias_file)
    
    #for each fasta file
    for key,rec in file_list.iteritems():
        lens = []
        rec['file_mod'] = rec['file'] + '_mod.fa'
        print rec['file_mod']
        f = open(rec['file_mod'],'wb')
        
        #prepare any alias extraction code
        if 'alias' in rec:
            code = compile(rec['alias'],'dummy','eval')
        
        #for each sequence
        seqs=0
        bases=0
        for seq in next_fasta(rec['file']):
            new_id = key+'_%010d'%seqs
            
            if 'alias' in rec:
                #extract alias from original header
                seqalias = eval(code,{'header':seq['header'],'re':re})
                alias = key + '::' + seqalias
                #print alias
                
                #store alias
                alias_shlv[alias] = seqs
            
            #modify header to lcl|<dbid>_<seqid> <original_header>
            seq['header'] = 'lcl|'+new_id+' '+seq['header']
            
            #ensure upper case sequence free of masking
            if not 'retaincase' in rec: seq['seq'] = seq['seq'].upper()
            
            write_fasta_rec(seq,f,width=80)
            
            seqs += 1
            seqlen = len(seq['seq'])
            bases += seqlen
            lens.append(seqlen)
            
        f.close()
        
        #calc N50
        lens.sort()
        base_2 = bases / 2
        curr_bases = 0
        n50 = None
        for i in lens:
            curr_bases += i
            if curr_bases >= base_2:
                n50 = i
                break
        
        assert n50 != None
        
        rec['N50'] = n50
        rec['seqs'] = seqs
        rec['bases'] = bases
        
    alias_shlv.close()
    
def read_source_list(ignore):
    '''
    read in source list file as dict
    '''
    
    f = open(source_file,'rb')
    
    file_list = {}
    
    while True:
        line = f.readline()
        if line == '': break #eof
        if line.startswith('#'): continue #comment
        line = line.strip()
        if line == '': continue #blank line
        
        oldrec = False
        
        if line.startswith('==>'):
            #start new record
            key = line.split()[1]
            
            if key.startswith('#'):
                key = key[1:]
                oldrec = True
            
            rec = {}
            rec['type'] = 'nucl' #default: assume nucl (not prot)
            
            #avoid duplicates
            assert key not in file_list
            
            #do not store commented keys if ignore flag is set
            if oldrec and ignore: continue
            
            file_list[key] = rec
            print key
            continue
            
        #store additional information in the record
        key = line.split()[0].strip()
        keylen = len(key)
        
        if key == 'file':
            #file names are relative to basedir
            rec[key] = basedir + line[keylen:].strip()
        else:
            #store key value pair
            rec[key] = line[keylen:].strip()
    
    f.close()
    
    return file_list
    
def blastdb_seq(seqid,start=1,end=None):
    '''
    use blastdbcmd to extract just the sequence from a blast database
    '''
    
    blastdbcmdbin = '/usr/bin/blastdbcmd'
    dbkey = seqid[:-11]
    dbname = lookup_file(dbkey)
    #tmpfile = '.tmpfile12341234.'
    
    rangestr = str(start) + '-'
    if end != None: rangestr += str(end)
    
    cmd = [
           blastdbcmdbin,
           '-db',dbname,
           '-dbtype','nucl',
           '-entry',"'%s'"%seqid,
           '-outfmt','%s',
           '-range',rangestr
          ]

    cmdstr = ' '.join(cmd)
    child = subprocess.Popen(cmdstr, shell=True, stdout=subprocess.PIPE)
    stdout = child.communicate()[0].strip()
    
    assert child.returncode == 0, 'error for command: %s'%cmdstr
    
    return stdout
