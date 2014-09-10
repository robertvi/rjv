#!/usr/bin/python

'''
file synchronisation 
'''
usage=\
'''
usage: file_sync.py local_root remote_root
'''

import sys,glob,re
from rjv.fileio import *

exclude =\
[
    r'\./logs/*',
]

def collect_data(root,exclude,file_dict={}):
    '''
    use find to collect filename, mtime, permission and size data
    '''
    
    os.chdir(root)
    
    first = False
    if len(file_dict) == 0: first = True
    tmpfile = '/home/rov/rjv_files/tmp/' + tmpfname()
    #name mtime permission size 
    #run2('find . -printf "%p %T+ %M %s\n" > [tmpfile]') 
    run2('find . -printf "%p %T+ %s\n" > [tmpfile]') 

    f = open(tmpfile,'rb')
    for line in f:
        tok = line.split()
        
        fname = tok[0]
        
        flag = False
        for x in exclude:
            if re.search(x,fname):
                flag = True
                break
        
        if flag: continue

        if first:
            file_dict[fname] = [tok[1:],None]
        else:
            if not fname in file_dict:
                file_dict[fname] = [None,tok[1:]]
            else:
                file_dict[fname][1] = tok[1:]
    f.close()
    
    return file_dict

if len(sys.argv) < 3:
    print usage
    exit()

root1 = sys.argv[1]
root2 = sys.argv[2]

file_dict = collect_data(root1,exclude)
file_dict = collect_data(root2,exclude,file_dict)

print '=================================='
for k,v in file_dict.iteritems():
    if v[0] == v[1]: continue
    print k
    
    if v[0] == None:
        line = [str(i) for i in v[1]]
        print '    ROOT1:  NO FILE'
        print '    ROOT2: ', ' '.join(line)
        print '----------------------------------'
        continue
        
    if v[1] == None:
        line = [str(i) for i in v[0]]
        print '    ROOT1: ', ' '.join(line)
        print '    ROOT2:  NO FILE'
        print '----------------------------------'
        continue
    
    line1 = [str(i) for i in v[0]]
    line2 = [str(i) for i in v[1]]
    print '    ROOT1: ', ' '.join(line1)
    print '    ROOT2: ', ' '.join(line2)
            
    print '----------------------------------'
