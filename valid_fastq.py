#!/usr/bin/python

'''
check single fastq files are valid

valid_fastq.py fname...
'''

import sys

files = sys.argv[1:]

buffsize = 10000
newline = '\n'
maxids = 1000000

fout = sys.stdout

for fname in files:
	uid = {}
	readct = 0
	f = open(fname)

	while True:
		readct += 1
		pos = f.tell()
		buff = f.read(buffsize)
		if buff == '':
			fout.write('%s %d reads ok\n'%(fname,readct))
			fout.flush()
			break #end of file
			
		read = buff.split(newline)
		
		if len(read) < 4:
			fout.write('%s read %d less than four lines available %s\n'%(fname,readct,read[0]))
			fout.flush()
			break
			
		read = read[:4]
		
		readsize = len(newline.join(read) + newline)
		f.seek(pos+readsize)
		
		if not read[0].startswith('@'):
			fout.write('%s read %d header invalid: %s\n'%(fname,readct,read[0]))
			fout.flush()
			break
			
		if not read[2].startswith('+'):
			fout.write('%s read %d second header invalid: %s\n'%(fname,readct,read[2]))
			fout.flush()
			break
			
		if readct < maxids:
			#to avoid running out of memory for large files
			#stop checking read uids after 'maxids'
			if read[0] in uid:
				fout.write('%s read %d duplicate header: %s\n'%(fname,readct,read[0]))
				fout.flush()
				break
		
			uid[read[0]] = True
		
		if len(read[1]) != len(read[3]):
			fout.write('%s read %d seq and qual lengths differ: %d %d\n'%(fname,readct,len(read[1]),len(read[3])))
			fout.flush()
			break
			
		errflag = False
		for x in read[1]:
			if x not in 'ATCGNatcgn':
				fout.write('%s read %d invalid seq character: %s\n'%(fname,readct,x))
				fout.flush()
				errflag = True
				break
				
		if errflag: break
				
		for x in read[3]:
			if not (33 <= ord(x) <= 74):
				fout.write('%s read %d invalid qual character: %s\n'%(fname,readct,x))
				fout.flush()
				errflag = True
				break
		
		if errflag: break
		
	f.close()
