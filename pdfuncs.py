'''
read in csv file using pandas with sensible defaults for names and index
'''

import pandas

def pdread(fname,sep,names):
    '''
    read in csv file using pandas with sensible defaults for names and index
    '''

    #must provide column names
    df = pandas.read_csv(fname,sep=sep,names=names,header=None,index_col=False)
    
    #index starting from 1 not 0
    df.index += 1
    
    return df
