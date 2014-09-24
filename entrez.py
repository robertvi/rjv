'''
functions to make NCBI queries using the entrez system

see here:
Entrez Programming Utilities Help [Internet].
E-utilities Quick Start
http://www.ncbi.nlm.nih.gov/books/NBK25500/

'''

import urllib,xmltodict,re,json

def try_append(mainlist,obj,keylist):
    '''
    try to append a (nested) keyed value
    append 'NO_DATA' if failed
    '''
    
    x = obj
    
    for y in keylist:
        try:
            x = x[y]
        except:
            mainlist.append('NO_DATA')
            return
    x = json.dumps(x)
    x = x.replace('"','')
    x = x.replace("'",'')
    mainlist.append(x)

def next_uid_file(fname,pat):
    '''
    return unique matching ids from a file, string or list of strings
    eg pat='SRA: (SRS[0-9]{4,10})'
    '''
    
    seen = {}

    f = open(fname)
    for line in f:
        for match in re.finditer(pat, line):
            if match == None: continue
            uid = match.group(1) #pattern must be contained in parentheses ()
            if not uid in seen:
                seen[uid] = True
                yield uid
    f.close()

def next_uid_string(src,pat):
    '''
    return unique matching ids from a string or list of strings
    eg pat='SRA: (SRS[0-9]{4,10})'
    '''
    
    seen = {}

    if type(src) == str: src = [src]

    for line in src:
        for match in re.finditer(pat, line):
            if match == None: continue
            uid = match.group(1) #pattern must be contained in parentheses ()
            if not uid in seen:
                seen[uid] = True
                yield uid

def esearch(term,db='sra',retmax=100000,retmode='xml',usehistory='y'):
    '''
    search an ncbi database, return a results handle
    
    to get a list of databases:
    http://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi
    
    retmode = json | xml
    
    usehistory=y stores the results on ncbi for later use
    
    db=sra&retmax=100000&term=
    '''
    
    url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?'
    url += 'db='+str(db)
    url += '&term='+urllib.quote_plus(str(term))
    url += '&retmax='+str(retmax)
    url += '&usehistory='+str(usehistory)
    url += '&retmode='+str(retmode)
    
    #print url
    
    f = urllib.urlopen(url)
    data = f.read()
    f.close()
    
    return xmltodict.parse(data)
    
def esummary(res,db='sra',retmax=10000):
    '''
    retrieve summaries for a list of search hits
    '''

    res = res['eSearchResult']

    url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?'
    url += 'db='+str(db)
    url += '&query_key='+str(res['QueryKey'])
    url += '&WebEnv='+str(res['WebEnv'])
    
    f = urllib.urlopen(url)
    data = f.read()
    f.close()
    
    return xmltodict.parse(data)
