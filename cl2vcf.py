#/usr/bin/python

#
# convert crosslink loc files into a vcf
#

import sys

if len(sys.argv) < 2 or sys.argv[2] in ['--help','-h','-?','/?']:
    print "usage: cl2vcf.py [--samples <sampnamefile>] [--phased] <locfile...>  > output.vcf"
    print "optional sample file: one sample name per line"
    print "locfiles: as per crosslink, single space separated columns, markerid markertype phase genotype..."
    print "          two characters per genotype"
    exit()

#optional list of sample names
samples = None
phased = False

ops = sys.argv[1:]

while ops[0].startswith('--'):
    if ops[0] == '--samples':
        f = open(ops[1])
        samples = [x.strip() for x in f]
        f.close()
        ops = ops[2:]
    if ops[0] == '--phased':
        phased = True
        ops = ops[1:]

flist = ops

print '##fileformat=VCFv4.2'
print '##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">'
print '#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t',

wrote_header = False

for fname in flist:
    f = open()
    for line in f:
        tok = line.strip().split()

        if wrote_header == False:
            if samples == None: samples = ['samp%03d'%x for x in xrange(len(tok)-3)] #dummy sample names
            print '\t'.join(samples)
            wrote_header = True

        uid = tok[0]
        calls =
    f.close(fname)
