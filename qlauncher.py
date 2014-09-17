#!/usr/bin/python

'''
launch a qsub job for each line in a set of files

usage: qlauncher.py [--delay=timedelay(sec)[default=1.0]] scriptfile listfile1 [listfile2...]

overview:
(1) create a template job script with special placeholder, eg "@{fastqfile}"
(2) run qlauncher telling it the script file and a file listing the values for the placeholder
(3) qlauncher fills out the script for each line in the list file, then calls qsub

eg:
script.sh:
-----------------------------------------
#$ [normal sun grid engine parameters here]
gunzip --stdout @{inpfile} > @{outfile}
-----------------------------------------

inpfile:
-----------------------------------------
file1.fa.gz
file2.fa.gz
-----------------------------------------

outfile:
-----------------------------------------
file1.fa
file2.fa
-----------------------------------------

qlauncher command:
$ qlauncher.py script.sh inpfile outfile

runs qsub for scripts containing:
gunzip --stdout file1.fa.gz > file1.fa
gunzip --stdout file2.fa.gz > file2.fa
'''

import sys,os,random,time

#temporary script filename
tmpfile = './.tmp%06d'%random.randint(0,999999)

#default delay between qsub commands
delay = 1.0

if len(sys.argv) < 2:
    print 'usage:qlauncher.py [--delay=timedelay(sec)] scriptfile listfile1 [listfile2...]'
    exit()
    
if sys.argv[1].startswith('--delay='):
    delay = float(sys.argv[1].split('=')[1])
    sys.argv[1:] = sys.argv[2:]

#read in script template
fscr = open(sys.argv[1])
script = fscr.read()
fscr.close()

#open all list files
filez = sys.argv[2:]
f = [open(x) for x in filez]

#launch one job per line in the listfiles
while True:
    #read in next line from each file
    values = [x.readline() for x in f]
    
    #quit if any file end reached
    if '' in values: break
    
    #remove new lines etc
    values = [x.strip() for x in values]
    
    #fill out the script templates
    filledscript = script
    
    #make dictionary of key value pairs
    keyval = {os.path.basename(x):values[i] for i,x in enumerate(filez)}

    #replace @{key} with value
    for key in keyval.iterkeys():
        filledscript = filledscript.replace('@{%s}'%key, keyval[key])
    
    fout = open(tmpfile,'wb')
    fout.write(filledscript)
    fout.close()
    
    time.sleep(delay)
    
    os.system('qsub %s'%tmpfile)

#remove temporary script file
os.system('rm %s'%tmpfile)

#close all list files
for x in f: x.close()
