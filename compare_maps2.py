#!/usr/bin/python

'''
plot marker position according to position in two different maps
'''

import rpy2.robjects as robjects
import sys

usage=\
'''
usage: compare_maps2.py csv_file csv_file outfile
'''

if len(sys.argv) != 4:
    print usage
    exit()
    
rr = robjects.r
    
file1 = sys.argv[1]
file2 = sys.argv[2]
outfile = sys.argv[3]

unmapped = -10.0
newline = '\n'

#load map1 data
data1 = []
leng1 = [0]*200
f = open(file1,"rb")
f.readline()
for line in f:
    tok = line.strip().split(',')
    marker = tok[0]
    chrm = int(tok[1])
    pos = float(tok[2])
    data1.append([marker,chrm,pos]) #marker, chrom, pos
    leng1[chrm] = max(pos,leng1[chrm]) #record length of each chromosome
f.close()

data2 = []
leng2 = [0]*200
f = open(file2,"rb")
f.readline()
for line in f:
    tok = line.strip().split(',')
    marker = tok[0]
    chrm = int(tok[1])
    pos = float(tok[2])
    data2.append([marker,chrm,pos]) #marker, chrom, pos
    leng2[chrm] = max(pos,leng2[chrm])
f.close()

#find cumulative length of chromosomes
#retain dummy length of zero for chromosome zero
for i in xrange(len(leng1)):
    if i == 0: continue
    leng1[i] += leng1[i-1]

for i in xrange(len(leng2)):
    if i == 0: continue
    leng2[i] += leng2[i-1]
    
for i in xrange(len(data1)):
    pos = data1[i][2]
    chrm = data1[i][1]
    newpos = pos + leng1[chrm-1]
    data1[i].append(newpos)

for i in xrange(len(data2)):
    pos = data2[i][2]
    chrm = data2[i][1]
    newpos = pos + leng2[chrm-1]
    data2[i].append(newpos)
    
marker = {}

for x in data1: marker[x[0]] = [x[3],unmapped]
for x in data2:
    if x[0] in marker: marker[x[0]][1] = x[3]
    else:              marker[x[0]] = [unmapped,x[3]]

xval = [str(x[0]) for x in marker.itervalues()]
yval = [str(x[1]) for x in marker.itervalues()]

#print xval
#print yval

rr('x <- c(' + ','.join(xval) + ')')
rr('y <- c(' + ','.join(yval) + ')')
#'png("%s")'%fname,
rr('pdf("%s")'%outfile)

#plot marker positions
rr('plot(x,y,pch = ".",xlab="%s", ylab="%s")'%(file1,file2))

#plot chromosome boundaries
for i in xrange(len(leng1)):
    if i == 0: continue
    xpos = leng1[i]
    ymin = 0.0
    ymax = leng2[-1]
    rr('a <- c(%f,%f)'%(xpos,xpos))
    rr('b <- c(%f,%f)'%(ymin,ymax))
    rr('lines(a,b)')

for i in xrange(len(leng2)):
    if i == 0: continue
    ypos = leng2[i]
    xmin = 0.0
    xmax = leng1[-1]
    rr('a <- c(%f,%f)'%(xmin,xmax))
    rr('b <- c(%f,%f)'%(ypos,ypos))
    rr('lines(a,b)')
    
rr('dev.off()')

