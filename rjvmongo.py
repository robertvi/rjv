_rowlist = []

def batch_insert(coll,nextrow=None,batch=1000):
    'insert docs in batches'
    global _rowlist

    if nextrow != None: _rowlist.append(nextrow)

    if len(_rowlist) >= batch or nextrow == None:
        
        if len(_rowlist) > 0:
            coll.insert_many(_rowlist)
            
        _rowlist = []

def mongo_password(fname='/home/vicker/passwords/mongo_vicker'):
    'get the password from a file'
    f = open(fname)
    password = f.read().strip()
    f.close()
    return password
