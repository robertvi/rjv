import inspect,re

def get_local_vars(tvar):
    '''
    extract only simple local variables from the frame
    '''

    dic = {}
    allowed = [str,int,float,bool]

    for k,v in tvar.iteritems():
        if type(k) != str: continue
        if not type(v) in allowed: continue 
        dic[k] = v
        
    del tvar
    return dic

def substitute_values(data,dic):
    '''
    substitute values for place holders
    '''

    #replace {key} with value
    for key in dic.iterkeys():
        if not '{%s}'%key in data: continue
        data = data.replace('{%s}'%key, str(dic[key]))

    #check all placeholders were replaced
    for m in re.finditer('{.*}',data):
        print m.group(0), 'not matched'
        raise Exception

    return data

def fmt(s):
    '''
    fill out place holders
    '''
    
    dic = get_local_vars(inspect.currentframe().f_back.f_locals)
    return substitute_values(s,dic)
