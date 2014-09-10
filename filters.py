def pyfilter(data,_filter,params={},ordered=False):
    '''
    filter the data set using an arbitrary expression
    which must evaluate to true or false
    for lists the current record and offset are available as 'x' and 'i'
    for dicts the current record and key are available as 'x' and 'k'
    '''
    if type(data) == list:
        python_filter_list(data,_filter,params,ordered)
    elif type(data) == dict:
        python_filter_dict(data,_filter,params)
    else:
        raise Exception('unhandled data type')

#filter a list based on any python expression
def python_filter_list(data,_filter,params={},ordered=False):
    #compile the filter code
    code = compile(_filter,'dummyfilename','eval')
    
    orig = len(data) #original records
    
    i = 0
    while i < len(data):
        x = data[i]
        
        #make the current record and offset available inside eval
        params['x'] = x
        params['i'] = i
        
        #execute the filter, should evaluate to a boolean
        result = eval(code,params)
    
        if type(result) != bool:
            raise Exception('filter should evaluate to a bool')
            
        #test if record is to be retained or deleted
        if result == False:
            #delete but retain list ordering
            if ordered == True:
                del data[i]
            #delete efficiently but loose list ordering
            else:
                data[i] = data[-1]
                del data[-1]
        #retain record
        else:
            i = i + 1
        
    print 'matched %d/%d records using: %s'%(len(data),orig,_filter)

#filter a dict based on any python expression
def python_filter_dict(data,_filter,params={}):
    #compile the filter code
    code = compile(_filter,'dummyfilename','eval')
    
    #count number of records removed
    orig = len(data)
    #del_keys = []
    
    items = data.items()
    for k,x in items:
        #make the current record and key available inside eval
        params['x'] = x
        params['k'] = k
        
        #execute the filter, should evaluate to a boolean
        result = eval(code,params)
    
        if type(result) != bool:
            #print type(result)
            raise Exception('filter should evaluate to a bool: %s'%filter)
            
        #test if record is to be retained or deleted
        if result == False:
            del data[k]
            #del_keys.append(key)

    #delete records not matching filter            
    #for key in del_keys:
    #    del data[key]
        
    print 'matched %d/%d records using: %s' \
          %(len(data),orig,filter)

#modify the data in place using a python exec
def pymodify(data,modcode,params={}):
    if type(data) == list:
        python_modify_list(data,modcode,params)
    elif type(data) == dict:
        python_modify_dict(data,modcode,params)
    else:
        raise Exception('unhandled data type')

#modify dict keys and/or records inplace
def python_modify_dict(data,modcode,params={},duplicate_check=True,detect_changes=True):
    #compile the modification code
    code = compile(modcode,'dummyfilename','exec')
    
    #count key and record modifications
    ct_k = 0
    ct_x = 0
    
    #iterate dict using an explicit list of the original keys
    #so we can add and delete from the dict while 'iterating' it
    for k in data.keys():
        #make the current record available inside exec
        params['x'] = data[k]
        
        #make the current key available inside exec
        params['k'] = k
        params['r'] = reg_exp_func
        
        #execute the code on the current record
        exec code in params
    
        if detect_changes:
            #use a hash of the string representation of the record
            #before and after to detect changes
            if hash(repr(data[k])) != hash(repr(params['x'])):
                ct_x += 1
                
        #if the key did not change, assign the (possibly modified)
        #record back to the original key
        if params['k'] == k:
            data[k] = params['x']
            continue
        
        ct_k += 1

        #get the new key
        new_key = params['k']
            
        #check for duplication of an existing key
        if duplicate_check and new_key in data:
            raise Exception('new key %s already exists'%str(new_key))
            
        #store the record under the new key
        data[new_key] = params['x']
            
        #delete the original key
        del data[k]
            
    if detect_changes:
        print 'applied "%s" to %d records, ' \
              '%d keys and %d records changed'%(modcode,len(data),ct_k,ct_x)
    else:
        print 'applied "%s" to %d records, %d keys changed'%(modcode,len(data),ct)
            
#modify records inplace
def python_modify_list(data,modcode,params={},detect_changes=True):
    #compile the filter code
    code = compile(modcode,'dummyfilename','exec')
    
    #count modified records
    ct = 0
    
    for i,x in enumerate(data):
        #make the current record and offset available inside exec
        params['x'] = x
        params['i'] = i
        params['r'] = reg_exp_func
        
        #execute the code on the current record
        exec code in params
    
        if detect_changes:
            #use a hash of the string representation of the record
            #before and after to detect changes
            #if hash(repr(data[i])) != hash(repr(params['x'])):
            if repr(data[i]) != repr(params['x']):
                ct += 1

        #store the modified record back in the list
        data[i] = params['x']
        
    if detect_changes:
        print 'modified %d/%d records using %s'%(ct,len(data),modcode)
    else:
        print 'applied "%s" to %d records'%(modcode,len(data))


#convert list-of-records to dict-of-lists-of-records
#this method does not loose records sharing the same key
#ordering in the original list is preserved in the sublists
#'multidict' by analogy with multimap/multiset in C++ STL
#each dict key yields a list of one or more records
#therefore duplicated keys from the original list
#generate a list of records under that key in the
#multidict
def list2multidict(data,keyfield):
    data2 = {}
    
    for i in data:
        #get the key value from the record
        key = i[keyfield]

        #if this is a new key, create a new record list
        if not key in data2: data2[key] = []
            
        #append the record to the list preserving order
        data2[key].append(i)
            
    print 'list (%d) to multidict (%d) keyed by %s' %(len(data),len(data2),keyfield)
    
    return data2
