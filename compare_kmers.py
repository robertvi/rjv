#!/usr/bin/python

'''
compare kmer positions between two fasta files
usage: compare_kmers kmersize fasta1 fasta2 > output.coords
'''

from rjv.fasta import *
from rjv.kmer import *
import sys

kmersize = int(sys.argv[1])
inp1 = sys.argv[2]
inp2 = sys.argv[3]

kmer_posn = {}

#index position of all kmers
posn = 0
for fa in next_fasta(inp1):
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

posn = 0
for fa in next_fasta(inp2):
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
			print x,posn+i
	
	posn += len(fa['seq'])
