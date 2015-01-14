#!/usr/bin/python

'''
delete existing database file!
then inits qsub database
'''

import os,sqlite3
from rjv.sql import *

fields =\
[
    'jobid integer',
    'name',
    'status',
    'exit_code',
    'fail_code',
    'mem real',
    'memlimit real',
    'time real',
    'timelimit',
    'slots integer',
    'cwd',
    'startdate',
    'startsecs real',
]

datadir = '/home/vicker/qsub_sqlite/'
dbfile = datadir + 'qsub_records.db'

os.system('rm '+dbfile)

db = sqlite3.connect(dbfile)
cur = db.cursor()
create_table(cur,'jobs','/'.join(fields))
cur.execute('create unique index jobid_ix on jobs ( jobid );')
db.commit()
db.close()
