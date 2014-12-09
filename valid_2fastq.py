#!/usr/bin/python

'''
check pair of fastq files are valid

valid_2fastq.py read1 read2 sep=' '

assumes already checked using valid_fastq.py

sep defines the separator between the shared part of the read id and the part saying the read number
eg ' ' for space, or '/' for /1 /2 type numbering
'''

import sys,sets,gzip

def check_read(read,uid,fname,readct,maxids):
    '''
    check read looks valid
    '''

    #check for unique ids
    if readct < maxids:
        #to avoid running out of memory for large files
        #stop checking read uids after 'maxids'
        if read[0] in uid:
            print '%s read %d duplicate header: %s'%(fname,readct,read[0])
            exit(1)

        uid.add(read[0])
        
    #check secondary header is empty or matches main header
    if read[2] != '+':
        if read[0][1:] != read[2][1:]:
            print '%s read %d second header does not match first header: %s %s'%(fname,readct,read[0],read[2])
            exit(1)

    #check quality and sequence have same length
    if len(read[1]) != len(read[3]):
        print '%s read %d seq and qual lengths differ: %d %d'%(fname,readct,len(read[1]),len(read[3]))
        exit(1)
            
    #check seq contains valid characters only
    for x in read[1]:
        if x not in 'ATCGNatcgn':
            print '%s read %d invalid seq character: %s'%(fname,readct,x)
            exit(1)
            
    #check quality contains valid characters only
    for x in read[3]:
        if not (33 <= ord(x) <= 74):
            print '%s read %d invalid qual character: %s'%(fname,readct,x)
            exit(1)

def next_read(f,fname,readct):
    '''
    get next read from possibly corrupted file
    '''

    buffsize = 5000
    newline = '\n'
    pos = f.tell()
    buff = f.read(buffsize)

    #end of file
    if buff == '': return None
        
    read = buff.split(newline)

    if len(read) < 4:
        print str(read)
        print '%s read %d less than four lines available'%(fname,readct)
        exit(1)
        
    read = read[:4]

    readsize = len(newline.join(read) + newline)
    f.seek(pos+readsize)

    return read

maxids = 1000000
uid = sets.Set()
readct = 0
fread1 = sys.argv[1]
fread2 = sys.argv[2]

if len(sys.argv) == 4:
    sep = sys.argv[3]
else:
    #default separator
    sep = ' '

if fread1.endswith('.gz'):
    f1 = gzip.open(fread1)
else:
    f1 = open(fread1)

if fread2.endswith('.gz'):
    f2 = gzip.open(fread2)
else:
    f2 = open(fread2)

while True:
    readct += 1

    #get next read, without assuming well formed data
    read1 = next_read(f1,fread1,readct)
    read2 = next_read(f2,fread2,readct)

    #catch normal end of file
    if read1 == None and read2 == None:
        print '%s %s %d read pairs ok'%(fread1,fread2,readct)
        break
        
    #catch abnormal end of file
    if read1 == None:
        print '%s read %d file ended before the other file'%(fread1,readct)
        exit(1)
        
    if read2 == None:
        print '%s read %d file ended before the other file'%(fread2,readct)
        exit(1)
        
    check_read(read1,uid,fread1,readct,maxids)
    check_read(read2,uid,fread2,readct,maxids)
        
    uid1 = read1[0].split(sep)
    uid2 = read2[0].split(sep)

    if uid1[0] != uid2[0]:
        print '%s %s read %d read ids do not match %s %s'%(fread1,fread2,readct,uid1[0],uid2[0])
        exit(1)

f1.close()
f2.close()
