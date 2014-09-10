'''
functions relating to csv type files
containing data in generic tabular form
'''

def save_csv(data,fname,sep=','):
    '''
    save data to generic tabular format
    '''
    
    f = open(fname,"wb")

    for row in data:
        f.write(sep.join([str(x) for x in row]) + '\n')
        
    f.close()

def load_csv(fname,sep=',',strip_data=True):
    '''
    load in data into a list of lists
    return header lines separately
    '''

    f = open(fname,"rb")
    data = [line.strip().split(sep) for line in f]
    f.close()
    
    #remove whitespace from data
    if strip_data:
        for row in data:
            for i,x in enumerate(row):
                row[i] = x.strip()
        
    #return data without a header
    return data

def reorder_columns(data,order,missing=-1,reverse=False):
    '''
    reorder columns according to given heading order
    '''
    
    order_dict = {}
    for i,x in enumerate(order): order_dict[x] = i

    data = transpose_table(data)
    
    #append correct ordering
    for row in data:
        if row[0] in order_dict:
            row.append(order_dict[row[0]])
        else:
            row.append(missing)

    data.sort(key=lambda x:x[-1],reverse=reverse)
    
    #remove ordering value
    for row in data: del row[-1]

    return transpose_table(data)

def sort_columns(data,func):
    '''
    sort table columns using func
    '''
    
    data = transpose_table(data)
    data.sort(key=func)
    return transpose_table(data)

def transpose_table(data):
    '''
    transpose the list of lists
    '''
    
    return map(list,zip(*data))
