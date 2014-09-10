#!/usr/bin/python

'''
unison this directory with the same directory on bertscratch
'''

import os

scratch = '/home/rov/rjv_files/bert_scratch/'
local = '/home/rov/rjv_files/projects/'

cwd = os.getcwd()

basename = os.path.basename(cwd)

root1 = local + basename
root2 = scratch + basename

print root1
print root2

assert root1 == cwd
assert os.path.exists(root2)

os.system('unison %s %s'%(root1,root2))
