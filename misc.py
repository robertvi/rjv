import math,random,subprocess

#def log_message(message):
#    '''
#    append data to file
#    '''
#    
#    f = open(log_file,'ab')
#    f.write(message + '\n')
#    f.close()

def random_seq(length,bases='ATCG'):
    '''
    return random sequence string
    '''
    
    n = len(bases)
    
    seq = ''
    
    for i in xrange(length):
        seq += bases[random.randint(0,n-1)]
    
    return seq

def string2number(value):
    '''
    try to convert to a float or int
    '''
    
    try:
        return int(value)
    except:
        pass
        
    try:
        return float(value)
    except:
        pass
        
    return value

def numeric_histo2(data,bins=20,minval=None,maxval=None):
    #find min and max val if not already provided
    if minval == None: minval = min([min(x) for x in data])
    if maxval == None: maxval = max([max(x) for x in data])

    n_sets = len(data)
    rng = float(maxval - minval + 1)
    histo = [ ] #histo[data_set][bin]
    
    #assign each data point to bins
    for i,x in enumerate(data):#x = data set [i]
        z = [0] * bins
        histo.append(z)
    
        for y in x:#data value y
            bin = float(y-minval) / rng * float(bins)
            if bin >= bins: bin = bins-1
            z[int(math.floor(bin))] += 1
        
    #make the labels
    binwidth = rng / bins
    label = [int(binwidth * i + minval) for i in xrange(bins+1)]
    
    #find the string width of the max frequency and label
    maxlabel = max([len(str(x)) for x in label])
    maxwidth = max([max([len(str(y)) for y in x]) for x in histo])+1
        
    #plot the histogram    
    print 'BP>='.center(maxlabel) + ' ' + \
          ''.join([('%d'%i).center(maxwidth) for i in xrange(n_sets)])
    for i in xrange(bins):
        s = str(label[i]).rjust(maxlabel) + ':'
        
        for j in xrange(n_sets):
            s = s + ('' if not histo[j][i] else str(histo[j][i])).rjust(maxwidth)
            
        print s
        
    print str(label[-1]).rjust(maxlabel)
