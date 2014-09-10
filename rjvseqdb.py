#!/usr/bin/python

'''
convert a series of fasta files into blast databases
modify headers using custom code for each file
store a record of each blast database under a short identifier in a master database file
'''

usage = '''
commands:
init - read source_list and rebuild all blast databases
add - read source_list and build only new blast databases
list - list database keys
info <dbkey> - show info about the database
###export <seq_reg_exp> [<seq_reg_exp>] - dump matching sequences to stdout
get {seqid:<seqid> | db:<db> id:<id>} [start:<start>] [end:<end>]
eg get db:rice id:23 start:1 end:100
eg get seqid:rice_0000023 start:1 end:100
positions are 1-based, end is inclusive

mark existing entries:
==> #key
to make the add command skip them
'''

import sys

from rjv.seqdb import *
from rjv.fasta import *

if len(sys.argv) == 1:
    print usage
    exit()

if sys.argv[1] == 'init':
    rebuild_all()
    
elif sys.argv[1] == 'add':
    add_newdbs()
    
elif sys.argv[1] == 'list':
    list_keys()
    
elif sys.argv[1] == 'info':
    db_info(sys.argv[2])
    
elif sys.argv[1] == 'get':
    #default is to return all of sequence
    args = {'start':1,'end':None}
    
    #get command line args
    for x in sys.argv[2:]: args[x.split(':')[0]] = x.split(':')[1]
    
    #build seqid from db and alias
    if 'db' and 'alias' in args:
        args['seqid'] = lookup_alias(args['db'],args['alias'])
        
    #build seqid from db and id
    if 'db' and 'id' in args:
        args['seqid'] = args['db']+'_%010d'%int(args['id'])
    
    args['start'] = int(args['start'])
    if args['end'] != None: args['end'] = int(args['end'])
        
    rec = seqrecord(args['seqid'],args['start'],args['end'])
    
    write_fasta_rec(rec,sys.stdout)

    
