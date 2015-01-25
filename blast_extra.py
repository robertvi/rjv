#!/usr/bin/python

'''
augment blast hits to include lengths of query and subject sequences
and proportionate lengths of alignments

note: percentages will be wrong if one sequence is nucleotide and the other protein
'''

from rjv.fasta import *
from rjv.blast6 import *
import sys,csv

if len(sys.argv) != 4:
    print 'usage: blast_extra.py blast_hits query_seqs subject_seqs > output_file'
    exit(0)

hits = [ hit for hit in next_hit(sys.argv[1]) ]

querys = { fa['id']:fa['seq'] for fa in next_fasta(sys.argv[2]) }

subjects = { fa['id']:fa['seq'] for fa in next_fasta(sys.argv[3]) }

for hit in hits:
    #find length of both sequences
    hit['qlen'] = len(querys[hit['query']])
    hit['slen'] = len(subjects[hit['subject']])

    #calculate alignment length as proportion of total length
    hit['qpcalign'] = float(hit['alen']) / hit['qlen'] * 100.0
    hit['spcalign'] = float(hit['alen']) / hit['slen'] * 100.0
    
    #calculate percentage identity over total length
    hit['qpident'] = hit['pident'] * hit['qpcalign'] / 100.0
    hit['spident'] = hit['pident'] * hit['spcalign'] / 100.0

    keys = ['query','subject','pident','alen',
            'mismatch','gaps','qstart','qend',
            'sstart','send','evalue','bscore',
            'qlen','slen','qpcalign','spcalign','qpident','spident']

    print '\t'.join([str(hit[x]) for x in keys])
