#!/usr/bin/python

'''
lander waterman calculations
'''

from math import *

#haploid genome length (bp)
G = 3.8e9

#length of insert (bp)
L = 101

#reads
N = 116e6 + 125e6

#overlap required to form contig (bp)
#kmer minus one?
T = 22



alpha = N / G #prob per base of starting a new read
theta = T / L
c = L * N / G #redundancy of coverage
sigma = 1.0 - theta

contigs = N * exp(-c * sigma)
contig_len = L * ( (exp(c*sigma)-1) / c + 1.0 - sigma )

print contigs, contig_len
