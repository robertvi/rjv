#!/usr/bin/python

'''
compare kmer positions between two fasta files
usage: plot_compare_kmers kmersize fasta1 fasta2 output.png
'''

#set matplotlib to use a backend suitable for headless operation
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from rjv.fasta import *
from rjv.kmer import *
import sys

if len(sys.argv) < 5:
    print 'usage: plot_compare_kmers kmersize fasta1 fasta2 output.png'
    exit(0)

kmersize = int(sys.argv[1])
inp1 = sys.argv[2]
inp2 = sys.argv[3]
out = sys.argv[4]

kmer_posn = {}

inp1_sizes = []
inp2_sizes = []

#index position of all kmers
posn = 0
for fa in next_fasta(inp1):
    inp1_sizes.append(len(fa['seq']))
    for i,kmer in enumerate(next_kmer(fa['seq'],kmersize)):
        
        try:
            #create reverse complement of the kmer
            rev = revcomp(kmer)
        except:
            #invalid base found
            continue
            
        #convert to canonical kmer
        if rev < kmer: kmer = rev
        
        if not kmer in kmer_posn: kmer_posn[kmer] = []
        kmer_posn[kmer].append(posn+i)

    posn += len(fa['seq'])

xx = []
yy = []

posn = 0
for fa in next_fasta(inp2):
    inp2_sizes.append(len(fa['seq']))
    for i,kmer in enumerate(next_kmer(fa['seq'],kmersize)):
        
        try:
            #create reverse complement of the kmer
            rev = revcomp(kmer)
        except:
            #invalid base found
            continue
            
        #convert to canonical kmer
        if rev < kmer: kmer = rev
        
        if not kmer in kmer_posn: continue
        for x in kmer_posn[kmer]:
            xx.append(x)
            yy.append(posn+i)

    posn += len(fa['seq'])

plt.plot(xx,yy,'ro',alpha=0.5,markersize=0.1)

posn = 0
for x in inp1_sizes[:-1]:
    posn += x
    plt.axvline(x=posn)

posn = 0
for x in inp2_sizes[:-1]:
    posn += x
    plt.axhline(y=posn)

plt.savefig(out, dpi=300, bbox_inches='tight')
