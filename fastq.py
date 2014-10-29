import os,gzip,random,sys


def write_fastq(fq,f):
    '''
    write fastq record
    '''
    
    f.write('@' + fq['header'] + '\n')
    f.write(fq['seq'] + '\n')
    f.write('+\n')
    f.write(fq['qual'] + '\n')

def random_fastq(fname):
    '''
    return a (more or less) random record
    '''
    
    size = os.stat(fname).st_size
    
    while True:
        f = open(fname,'rb')
        f.seek(random.randint(0,size))
        find_record(f)
        
        fq = read_fastq(f)
        
        if fq != None:
            return fq

def read_fastq(f):
    '''
    read next fastq record
    file must be at start of record or end of file
    returns record or None
    '''
    
    header = f.readline()
    if header == '': return None #eof
    assert header[0] == '@'
    header = header[1:].strip()
    
    seq = f.readline()
    assert seq != ''
    seq = seq.strip()
    
    redundant = f.readline()
    assert redundant[0] == '+'
    
    qual = f.readline()
    assert qual != ''
    qual = qual.strip()

    rec = {}
    rec['header'] = header
    rec['seq'] = seq
    rec['qual'] = qual
    return rec

def next_fastq(fname):
    '''
    generator to yield next fastq sequence
    '''
    
    if fname == sys.stdin:
        f = sys.stdin
    elif fname.endswith('.gz'):
        #from subprocess import Popen, PIPE
        #f = Popen(['zcat', fname], stdout=PIPE).stdout #not significantly faster
        f = gzip.open(fname,'rb')
    else:
        f = open(fname,'rb')
    
    while True:
        rec = read_fastq(f)

        #end of file
        if rec == None: break
        
        yield rec

    f.close()

def next_fastqs(fname1,fname2):
    '''
    iterate through a pair of matched fastqs
    '''
    
    gen1 = next_fastq(fname1)
    gen2 = next_fastq(fname2)

    while True:
        try:
            fq1 = gen1.next()
        except:
            break
        
        fq2 = gen2.next()
        yield fq1,fq2
        
def next_fastq_split(fname,offset,chunks):
    '''
    generator to yield next fastq sequence from a file
    split records into groups
    eg offset=0, chunks=10 means yield first of every ten records
    
    seeking in a gzip file and determining the original file size
    are not straightforward, therefore I'm not using my original
    design for file spliting which involved seeking to a point in the
    file and returning consecutive records
    '''

    if fname.endswith('.gz'):
        f = gzip.open(fname,'rb')
    else:
        f = open(fname,'rb')

    ct = -1
    while True:
        ct += 1
        rec = read_fastq(f)

        #end of file
        if rec == None: break
        
        if ct%chunks == offset:
            yield rec

    f.close()
    

def find_record(f):
    '''
    find first complete record starting at current position
    '''

    f.readline()
    
    while True:
        posn = f.tell()
        header = f.readline()
        posn2 = f.tell()
        seq = f.readline()
        redundant = f.readline()
        qual = f.readline()
        
        if qual == '': break #eof, leave file at end
        
        if header[0] == '@' and redundant[0] == '+':
            f.seek(posn)
            break

        f.seek(posn2)

def load_fastq(fname):
    '''
    load all fastq records into a list
    each sequence record has: header, seq, qual
    '''
    
    return [x for x in next_fastq(fname)]

