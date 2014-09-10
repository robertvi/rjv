from rjv.kmer import *
from rjv.fastq import *
from rjv.fileio import *
import random

def alt_count_kmers(fname,kmersize):
    ct = {}

    for fq in next_fastq(fname):
        for kmer in next_kmer(fq['seq'],14):
            if 'N' in kmer: continue
            rev = revcomp(kmer)
            try:
                ct[kmer] += 1
                ct[rev] += 1
            except:
                ct[kmer] = 1
                ct[rev] = 1

    return ct

def test_next_kmer():
    seq = 'ATCGATCG'
    gen = next_kmer(seq,4)
    assert gen.next() == 'ATCG'
    assert gen.next() == 'TCGA'
    assert gen.next() == 'CGAT'
    assert gen.next() == 'GATC'
    assert gen.next() == 'ATCG'

    try:
        gen.next()
        assert False
    except:
        assert True

def test_query_kmer():
    #count kmers using python
    alt_counts = alt_count_kmers('outns',14)
    
    #load kmerz counts
    counts = load_kmer_counts('outns_count14',14)
    
    for fq in next_fastq('outns'):
        for kmer in next_kmer(fq['seq'],14):
            count = query_kmer(kmer,counts,14)
            
            if 'N' in kmer:
                assert count == None
                assert kmer not in alt_counts
            else:
                assert count == alt_counts[kmer]
                assert count != 0
                assert count != None

def test_kmer2integer():
    assert kmer2integer("AAAAAAAAAA") == 0
    assert kmer2integer("TTTTTTTTTT") == 0
    assert kmer2integer("AAAAAAAAAC") == 1
    assert kmer2integer("GTTTTTTTTT") == 1
    assert kmer2integer("AAAAAAAAAG") == 2
    assert kmer2integer("CTTTTTTTTT") == 2
    assert kmer2integer("AAAAAAAAAT") == 3
    assert kmer2integer("ATTTTTTTTT") == 3
    assert kmer2integer("GAAAAAAAAA") == 524288
    assert kmer2integer("TTTTTTTTTC") == 524288

    assert kmer2integer("AAAAAAAAAAAAAAAA") == 0
    assert kmer2integer("TTTTTTTTTTTTTTTT") == 0
    assert kmer2integer("AAAAAAAAAAAAAAAC") == 1
    assert kmer2integer("GTTTTTTTTTTTTTTT") == 1
    assert kmer2integer("AAAAAAAAAAAAAAAG") == 2
    assert kmer2integer("CTTTTTTTTTTTTTTT") == 2
    assert kmer2integer("AAAAAAAAAAAAAAAT") == 3
    assert kmer2integer("ATTTTTTTTTTTTTTT") == 3
    assert kmer2integer("AAAAAAAAAAAAAACA") == 4
    assert kmer2integer("TGTTTTTTTTTTTTTT") == 4
    assert kmer2integer("AAAAAAAAAAAAAAGA") == 8
    assert kmer2integer("TCTTTTTTTTTTTTTT") == 8
    assert kmer2integer("AAAAAAAAAAAAAATA") == 12
    assert kmer2integer("TATTTTTTTTTTTTTT") == 12
    
    assert kmer2integer("GTTACGTCGATGCTAG") == 1917683393

def test_all():
    '''
    count kmers from a fastq file
    query kmers from the same file
    all queries should return invalid or >= 1
    '''
    
    kmersize=16
    inpfile='ril002-01-R3.q20.fq'

    outfile='kmerz%d'%kmersize
    run2('cat [inpfile] | kmerz [kmersize] [outfile]')
    counts = load_kmer_counts(outfile,kmersize)

    for fq in next_fastq(inpfile):
        for kmer in next_kmer(fq['seq'],kmersize):
            count = query_kmer(kmer,counts,kmersize)
            assert (count == None and 'N' in kmer) or count >= 1

def test_revcomp():
    assert revcomp('AAAA') == 'TTTT'
    assert revcomp('TTTT') == 'AAAA'
    assert revcomp('CCCC') == 'GGGG'
    assert revcomp('GGGG') == 'CCCC'
    assert revcomp('ATCG') == 'CGAT'
    assert revcomp('CGAT') == 'ATCG'
    
    bases = 'ATCG'
    
    for i in xrange(1000):
        l = random.randint(1,20)
        
        kmer = ''.join([random.choice(bases) for x in xrange(l)])
        
        assert revcomp(revcomp(kmer)) == kmer
