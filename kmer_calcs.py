'''
functions to do kmer-based calculations
'''

import pandas as pd
import math
from math import factorial as fac
import random
import scipy as sp

def mutate_seq(seq,error_rate):
    '''
    mutate a sequence
    '''
    
    out = ''
    bases = 'ATCG'
    
    for x in seq:
        #prob of mutating a base
        if random.uniform(0.0,1.0) < error_rate:      
            #mutate to random different base
            x = bases[(bases.index(x) + random.randint(1,3))%4]
        
        out += x
        
    return out

def count_samples(inp):
    '''
    count how many kmers were sampled in total
    which is given by sum(ct*freq)
    
    inp is filename for space separated csv
    containing two columns: kmer count, frequency of this count
    ie like a jellyfish histogram dump file
    '''

    #load data from file
    #or take direct from dataframe
    if type(inp) == str:
        #treat inp as filename
        df = pd.read_csv(inp,sep=' ',names=['ct','freq'],index_col=False)
    else:
        #treat inp as dataframe
        df = inp

    total = 0
    for i,x in df.iterrows():
        total += x.ct * x.freq #pandas probably has a smarter way of doing this
        
    return total

def norml(x, mu, std):
    '''
    return probability density for x given mean and standard deviation
    assuming a normal probability distribution
    '''
    x_mu = float(x) - mu
    return math.exp(-x_mu*x_mu / (2.0*std*std)) / (std*math.sqrt(2.0*math.pi))

def single_copy_histogram(genome_size,samples,max_ct):
    '''
    predict kmer frequency histogram
    for a single copy genome of known size
    assuming no sequencing errors
    for a given sample size (number of kmers sampled)
    
    predict histogram up to max_ct
    '''
    
    mu = float(samples) / float(genome_size)
    std = math.sqrt(mu * (1.0 - 1.0 / float(genome_size)))

    ct = range(1,max_ct+1)
    freq = [norml(x,mu,std)*genome_size for x in ct]
    
    return ct,freq

def multi_copy_histogram(sizes,copy_numbers,samples,max_ct):
    '''
    predict kmer frequency histogram
    for a variable copy genome
    assuming no sequencing errors
    for a given sample size (number of kmers sampled)
    
    sizes = size of single copy of each region
    copy_number = how many times region is present relative to single copy sequence
    
    predict histogram up to max_ct
    '''
    
    assert len(sizes) == len(copy_numbers)
    
    genome_size = sum([sizes[i] * copy_numbers[i] for i in xrange(len(sizes))])
    
    #generate a separate gaussian for each region
    ct = range(1,max_ct+1)
    freq = [0] * max_ct
    
    for i in xrange(len(sizes)):
        #avoid division by zero
        if float(sizes[i]) == 0.0: continue
        
        #number of kmers available to be sampled depends only on the size of a single repeat
        isize = sizes[i]                    
        
        #number of samples expected depends on the size of copy number
        isamples = float(samples) * sizes[i] * copy_numbers[i] / genome_size #samples across 
        
        mu = float(isamples) / float(isize)
        std = math.sqrt(mu * (1.0 - 1.0 / float(isize)))
        
        #print isize,isamples,mu,std

        for j,y in enumerate([norml(x,mu,std)*isize for x in ct]):
            freq[j] += y
    
    return ct,freq
    
def multi_copy_with_errors(sizes,copy_numbers,samples,max_ct,kmer_size,error_rate):
    '''
    predict kmer frequency histogram
    for a variable copy genome
    with sequencing errors
    for a given sample size (number of kmers sampled)
    
    sizes = size of single copy of each region
    copy_number = how many times region is present relative to single copy sequence
    
    predict histogram up to max_ct
    '''
    
    assert len(sizes) == len(copy_numbers)
    
    orig_samples = samples
    
    #how many kmers are error-free
    samples = float(samples) * (1.0 - error_rate)**kmer_size
    #print samples
    
    #how many have errors
    #error_kmers = float(orig_samples) - samples
    
    genome_size = sum([sizes[i] * copy_numbers[i] for i in xrange(len(sizes))])
    
    #generate a separate gaussian for each region
    ct = range(1,max_ct+1)
    freq = [0] * max_ct
    
    for i in xrange(len(sizes)):
        #avoid division by zero
        if float(sizes[i]) == 0.0: continue
        
        #number of kmers available to be sampled depends only on the size of a single repeat
        isize = sizes[i]                    
        
        #number of samples expected depends on the size of copy number
        isamples = float(samples) * sizes[i] * copy_numbers[i] / genome_size #samples across 
        
        mu = float(isamples) / float(isize)
        std = math.sqrt(mu * (1.0 - 1.0 / float(isize)))
        
        #print isize,isamples,mu,std

        for j,y in enumerate([norml(x,mu,std)*isize for x in ct]):
            freq[j] += y
    
    return ct,freq
    
def poisson(mean,hits):
    return 0.0
    
def predict_errors(n,ct_main,freq_main,kmer_size,error_rate):
    '''
    predict kmer freq for kmers with exactly n errors
    '''
    
    #how many possible error kmers are there
    #k-choose-n combinations of bases can be mutated
    #for each combination there are 3^n combinations of bases to mutate to
    #pos = 3.0**n * sp.misc.comb(kmer_size,n)
    pos = 3.0**n * fac(kmer_size) / (fac(n)*fac(kmer_size-n))
    
    #probability of any one particular error kmer being generated
    #when the kmer is read
    #n bases misread as the particular error base
    #remainder of bases are not misread
    prob = (error_rate/3.0)**n * (1.0 - error_rate)**(kmer_size-n)

    freq = [0.0] * len(ct_main)

    #for every count in the error-free histogram
    for i,ct1 in enumerate(ct_main):
        mean = ct1 * prob
        val1 = freq_main[i] * pos * math.exp(-mean)
        
        #generate error predictions for every count in the error histogram
        for j,ct2 in enumerate(ct_main):
            #poisson for count ct2
            #scaled by val1 'trials'
            #freq[j] += val1 * poisson(mean,ct2)
            
            freq[j] += val1 * mean**ct2 / fac(ct2)
            if ct2 == 170: break #fac(171) is too big to be a float
    
    return freq
    
def multi_copy_with_errors_full(sizes,copy_numbers,samples,max_ct,kmer_size,error_rate,maxerrs):
    '''
    predict kmer frequency histogram
    for a variable copy genome
    with sequencing errors
    for a given sample size (number of kmers sampled)
    
    sizes = size of single copy of each region
    copy_number = how many times region is present relative to single copy sequence
    
    predict histogram up to max_ct including error kmers
    '''
    
    #get predicted ct and freq without errors
    [ct_main,freq_main] = multi_copy_histogram(sizes,copy_numbers,samples,max_ct)
    
    #estimate error kmers for 1 to maxerrs per kmer
    freq_err = [0.0] * max_ct
    for i in xrange(1,maxerrs+1):
        freq = predict_errors(i,ct_main,freq_main,kmer_size,error_rate)
        for j in xrange(max_ct):
            freq_err[j] += freq[j]
        
    #get predicted ct and freq with errors, add to error kmers
    [ct_main,freq_main] = multi_copy_with_errors(sizes,copy_numbers,samples,max_ct,kmer_size,error_rate)
    for j in xrange(max_ct):
        freq_main[j] += freq_err[j]
    
    return ct_main,freq_main

def single_with_errors(genome_size,samples,max_ct,kmer_size,error_rate):
    '''
    predict kmer frequency histogram
    for a single copy genome of known size
    assuming a give per base error rate
    for a given sample size (number of kmers sampled)
    
    predict histogram up to max_ct
    '''
    
    orig_samples = samples
    
    #how many kmers are error-free
    samples = float(samples) * (1.0 - error_rate)**kmer_size
    #print samples
    
    #how many have errors
    error_kmers = float(orig_samples) - samples
    
    mu = float(samples) / float(genome_size)
    std = math.sqrt(mu * (1.0 - 1.0 / float(genome_size)))

    ct = range(1,max_ct+1)
    freq = [norml(x,mu,std)*genome_size for x in ct]
    
    return ct,freq

def estimate_genome_size(inp,min_max=None):
    '''
    expects a dataframe with columns 'ct' and 'freq'
    or else a filename to load a df from
    ct = kmer count
    freq = frequency of this count in the data set
    ct should not be the index
    
    
    min_max = [min,max]
    
    can be loaded from a jellyfish histogram dump file using:
    df = pd.read_csv(fname,sep=' ',names=['ct','freq'],index_col=False)
    
    either provide estimates of ct of first min and max
    or will do its own estimate (using a rather non-robust method)
    
    return [ctmin,ctmax,genome_size]
    '''
    
    #load data from file
    #or take direct from dataframe
    if type(inp) == str:
        #treat inp as filename
        df = pd.read_csv(inp,sep=' ',names=['ct','freq'],index_col=False)
    else:
        #treat inp as dataframe
        df = inp
    
    if min_max == None:
        #find first minimum
        #(assume that rows with zero counts maybe omitted entirely)
        for i in xrange(len(df)-1):
            if df.freq.iloc[i+1] > df.freq.iloc[i]:
                ctmin = df.ct.iloc[i]
                break

        #find first maximum
        for i in xrange(i,len(df)-1):
            if df.freq.iloc[i+1] < df.freq.iloc[i]:
                ctmax = df.ct.iloc[i]
                break
    else:
        ctmin = min_max[0]
        ctmax = min_max[1]

    #discard counts below minimum
    df = df[df.ct >= ctmin]

    total = 0.0
    for i,x in df.iterrows():
        total += float(x.ct) / ctmax * x.freq
    
    return [ctmin,ctmax,int(round(total))]
