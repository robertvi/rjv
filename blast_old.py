import re,os,subprocess,csv
from rjv.fasta import *
from rjv.fileio import *

source_file = '/home/rov/rjv_files/seq_data/database/source_list'
database_file = '/home/rov/rjv_files/seq_data/database/db.pickle'
blastnbin = '/usr/bin/blastn'
blastdbcmdbin = '/usr/bin/blastdbcmd'
newline = '\n'

#list of all available blast record fields
blastfields = [
'qseqid',
'qlen',
'qstart',
'qend',
'qframe',

'sseqid',
'slen',
'sstart',
'send',
'sframe',

'evalue',
'bitscore',
'score',
'length',
'pident',
'nident',
'mismatch',
'positive',
'gapopen',
'gaps',
'ppos',
'frames',
'btop',

'qseq',
'sseq',
]

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
        rec = blastdb_rec(seqid)
        
        #write to file in fasta format
        write_fasta_rec(rec,f)
    f.close()


def list_keys():
    '''
    list all blast database keys
    '''
    
    file_list = load_pickle(database_file)
    
    for k in file_list.iterkeys(): print k
    
    #print file_list
    
def blastdb_rec(seqid,start=1,end=None):
    '''
    return a fasta record of the requested sequence
    '''

    seq = blastdb_seq(seqid,start,end)
    
    if seqid.startswith('gi|'): header = seqid
    else:                       header = 'lcl|'+seqid
    
    return {'header':header,'seq':seq}
    
def hit2fasta(seqid,fname):
    '''
    save a single blast hit to a fasta file
    '''

    seq = blastdb_seq(seqid)
    header = 'lcl|'+seqid
    
    rec = {'header':header,'seq':seq}
    
    f = open(fname,'wb')
    write_fasta_rec(rec,f)
    f.close()
    
def blastdb_seq(seqid,start=1,end=None):
    '''
    use blastdbcmd to extract just the sequence from a blast database
    '''
    
    dbkey = seqid[:-11]
    dbname = lookup_name(dbkey)
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

def blastn(query,subject,outfile,threads=4,ops='',incl_seq=False):
    '''
    run blast locally
    query - name of fasta file containing query sequences
    subject - name of blast database containing subject sequences
    outfile - name of output file
    threads - how many threads to use during search
    ops - extra blast options
    incl_seq - if true, include sequence in output
    '''

    #get name of blast database from the database id
    dbname = lookup_name(subject)
    
    if incl_seq == False:
        #exclude sequence data from blast output
        outfmt = ' '.join(blastfields[:-2])
    else:
        #include sequence data from blast output
        outfmt = ' '.join(blastfields)
    
    cmd = [
           blastnbin,
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
    
def blastn_stdout(query,subject,threads=4,ops=''):
    '''
    run blast locally
    show results to stdout
    '''

    dbname = lookup_name(subject)
    
    cmd = [
           blastnbin,
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

def save_blast(data,fname):
    '''
    write all blast records to file
    '''
    
    f = open(fname,'wb')
    for x in data: write_blast(x,f)
    f.close()

def write_blast(rec,f):
    '''
    write blast hit to file
    write record in order defined by blastfields
    use record size to determine whether sequence data is included
    '''
    
    line = []
    
    if len(rec) == len(blastfields):
        #record includes sequence data
        headers = blastfields
    else:
        #record excludes sequence data
        headers = blastfields[:-2]
    
    for field in headers: line.append(str(rec[field]))
    f.write( ','.join(line) + newline)

def next_blast(fname):
    '''
    generator to yield blast hits
    '''
    
    #iterator through the results file
    f = open(fname,'rb')
    
    for hit in csv.reader(f):
        #use number of tokens on line to determine if seq data is included
        if len(hit) == len(blastfields):
            #record includes sequence data
            headers = blastfields
        else:
            #record excludes sequence data
            headers = blastfields[:-2]

        rec = {headers[i]:x for i,x in enumerate(hit)}
        yield rec
    f.close()

def load_blast(fname):
    '''
    load all results from blast tabular file
    '''
    
    return [ hit for hit in next_blast(fname) ]

def rebuild_all():
    '''
    rebuild all blast databases
    create new database index
    drop all previous information
    '''
    
    #load even those records preceeded by a #
    file_list = read_source_list(ignore=False)
    
    sanitize_fastas(file_list)
    
    create_blastdbs(file_list)
    
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
    
    orig_list = load_pickle(database_file)
    
    for k,v in new_list.iteritems():
        orig_list[k] = v
    
    save_pickle(orig_list,database_file)
    
def create_blastdbs(file_list):
    '''
    for each file in the list
    create a blast db using blast+
    '''
    
    for rec in file_list.itervalues():
        blastplusdb(rec['modfile'])
        rec['blastdb'] = rec['modfile']
    
def blastplusdb(seqfile):
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
    cmd = 'makeblastdb -in %s -dbtype nucl -parse_seqids'%seqfile

    if subprocess.call(cmd.split()) != 0:
        raise Exception('makeblastdb error')
    
def sanitize_fastas(file_list):
    '''
    apply modification to sequences / headers
    save as new fasta file
    '''
    
    #for each fasta file
    for key,rec in file_list.iteritems():
        print rec['file']
        rec['modfile'] = rec['file'] + '_mod.fa'
        f = open(rec['modfile'],'wb')
        
        #for each sequence
        seqs=0
        bases=0
        for seq in next_fasta(rec['file']):
            #modify header to lcl|<dbid>_<seqid> <original_header>
            seq['header'] = 'lcl|'+key+'_%010d'%(seqs+1)+' '+seq['header']
            
            #ensure upper case sequence free of masking
            if not 'retaincase' in rec: seq['seq'] = seq['seq'].upper()
            
            write_fasta_rec(seq,f,width=80)
            
            seqs += 1
            bases += len(seq['seq'])
            
        f.close()
        
        rec['seqs'] = seqs
        rec['bases'] = bases
    
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
            
            #avoid duplicates
            assert key not in file_list
            
            #do not store commented keys if ignore flag is set
            if oldrec and ignore: continue
            
            file_list[key] = rec
            print key
            continue
            
        #store additional information in the record
        toks = line.split()
        
        if len(toks) == 1:
            #store single token
            rec[toks[0]] = True
        else:
            #store key value pair
            rec[toks[0]] = line[len(toks[0]):].strip()
    
    f.close()
    
    return file_list
    
