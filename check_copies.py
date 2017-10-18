#!/usr/bin/python

#
# compare source and destination directories
#

import sys,os,glob

#https://stackoverflow.com/questions/1392413/calculating-a-directory-size-using-python
def get_size(start_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

#https://stackoverflow.com/questions/800197/how-to-get-all-of-the-immediate-subdirectories-in-python
def get_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir) if os.path.isdir(os.path.join(a_dir, name))]

src_list = \
[
#    '/home/miseq_data/2013/ANALYSIS',
#    '/home/miseq_data/2014/ANALYSIS',
#    '/home/miseq_data/2015/ANALYSIS',
#    '/home/miseq_data/2016/ANALYSIS',
#    '/home/miseq_data/2017/ANALYSIS',
#    '/home/miseq_data/2013/RAW',
#    '/home/miseq_data/2014/RAW',
#    '/home/miseq_data/2015/RAW',
#    '/home/miseq_data/2016/RAW',
#    '/home/miseq_data/2017/RAW',
#    '/home/miseq_data/.tmp_nas_data/miseq_data/miseq_data/ANALYSIS/2016',
#    '/home/miseq_data/.tmp_nas_data/miseq_data/miseq_data/RAW/2016',
    '/home/miseq_data/.tmp_nas_data/miseq_data/miseq_data/Archive',
]

dst_list = \
[
#    '/data/seq_data/miseq/2013/ANALYSIS',
#    '/data/seq_data/miseq/2014/ANALYSIS',
#    '/data/seq_data/miseq/2015/ANALYSIS',
#    '/data/seq_data/miseq/2016/ANALYSIS',
#    '/data/seq_data/miseq/2017/ANALYSIS',
#    '/data/seq_data/miseq/2013/RAW',
#    '/data/seq_data/miseq/2014/RAW',
#    '/data/seq_data/miseq/2015/RAW',
#    '/data/seq_data/miseq/2016/RAW',
#    '/data/seq_data/miseq/2017/RAW',
#    '/data/seq_data/miseq/misc',
    '/data/seq_data/miseq/archive',
]


src = {}
for item in src_list:
    for sub in get_subdirectories(item):
        size = get_size(os.path.join(item,sub))
        #print item,sub,size
        if not sub in src: src[sub] = []
        src[sub].append([item,size])


dst = {}
for item in dst_list:
    for sub in get_subdirectories(item):
        size = get_size(os.path.join(item,sub))
        #print item,sub,size
        if not sub in dst: dst[sub] = []
        dst[sub].append([item,size])

for sub in src:
    for item,size in src[sub]:
        print sub,item,size,
        if sub in dst:
            for ditem,dsize in dst[sub]:
                if dsize==size:
                    print ' -->',ditem,
        print
