#!/usr/bin/python

'''
check pair of fastq files are valid

valid_2fastq.py read1 read2 sep=' '

assumes already checked using valid_fastq.py

sep defines the separator between the shared part of the read id and the part saying the read number
eg ' ' for space, or '/' for /1 /2 type numbering
'''

import sys

fread1 = sys.argv[1]
fread2 = sys.argv[2]

if len(sys.argv) == 4:
	sep = sys.argv[3]
else:
	#default separator
	sep = ' '

fout = sys.stdout

readct = 0
f1 = open(fread1)
f2 = open(fread2)

while True:
	readct += 1
	
	read1 = [f1.readline() for i in xrange(4)]
	read2 = [f2.readline() for i in xrange(4)]
	
	if read1[0] == '' or read2[0] == '':
		if read1[0] != read2[0]:
			fout.write('%s %s read %d one file ended before the other one\n'%(fread1,fread2,readct))
			fout.flush()
		else:
			fout.write('%s %s %d reads ok\n'%(fread1,fread2,readct))
			fout.flush()
		break

	uid1 = read1[0].split(sep)
	uid2 = read2[0].split(sep)
	
	if uid1[0] != uid2[0]:
		fout.write('%s %s read %d read ids do not match %s %s\n'%(fread1,fread2,readct,uid1[0],uid2[0]))
		fout.flush()
		break
	
f1.close()
f2.close()
