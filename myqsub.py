#!/usr/bin/python

'''
wrapper for qsub, script file must be the last argument
store the job id of a job when it is submitted
and a copy of the script file
'''

usage = 'usage:myqsub.py <normal qsub arguments> <qsubscript>'

import sys,os,random,time,sqlite3,datetime
from rjv.sql import *
from rjv.sge import *

if len(sys.argv) == 1:
    print usage
    exit()
   
prefix = 'myqsub.'
datadir = '/home/vicker/qsub_sqlite/'
dbfile = datadir + 'qsub_records.db'
tmpout = datadir + 'tmp/' + str(random.random())[-6:] + '.' + ('%.9f'%time.time()).split('.')[1] + '.stdout'
script = sys.argv[-1]

#get time and cwd
dt_string = str(datetime.datetime.now())
epoch_string = float(time.time())
cwd_string = str(os.getcwd())

#run qsub, capture stdout
os.system('qsub ' + ' '.join(sys.argv[1:]) + ' > ' + tmpout)

#get job number from the file
f = open(tmpout)
data = f.read()
f.close()
jobid = int(data.strip().split()[2])

#make copy of script file
cpyscript = datadir + 'scripts/' + prefix + str(jobid) + '.script'
if os.path.exists(cpyscript):
    print 'script file already exists: ' + cpyscript
    exit(1)
os.system('cp '+script+' '+cpyscript)


#open database
db = sqlite3.connect(dbfile)
cur = db.cursor()

cur.execute('select jobid from jobs where jobid=%d'%jobid)
res = cur.fetchall()

if len(res) != 0:
    print "jobid %d already present in database"%jobid
    exit()

