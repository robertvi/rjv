import cPickle,os,random,datetime,sys
import fcntl,re,inspect
from subprocess import Popen as popen

def task_offset():
    '''
    get SGE_TASK_ID if defined
    else return None
    '''
    
    if not 'SGE_TASK_ID' in os.environ:
        return None
    else:
        return int(os.environ['SGE_TASK_ID']) - 1

class fbuffer:
    def _init_(x,_f):
        x.f = _f
        x.data = None
        x.replay = False
        
    def readline(x):
        '''
        return next line in file
        retain it in case a restore is called
        '''
        
        if not x.replay:
            x.data = x.f.readline()
        else:
            x.replay = False
       
        return x.data
        
    def restore(x):
        '''
        next readline yields the buffered line again
        '''
        
        x.replay = True

def write_file(content,fname,append=False,strip=True):
    '''
    write content to file
    '''
    
    if append:
        f = open(fname,'ab')
    else:
        f = open(fname,'wb')
        
    #get local variables from calling function
    _var = inspect.currentframe().f_back.f_locals
    
    #filter to allow access only to basic variable types
    var = {}
    allowed = [str,int,float]
    for k,v in _var.iteritems():
        if type(v) in allowed:
            var[k] = v
            
    #substitute parameter values
    #for key,val in var.iteritems():
    #    _key = '[%s]'%key
    #    if not _key in content: continue
    #    content = content.replace(_key,str(val))
    
    content = sub_vals(content,var)
        
    if strip:
        #remove whitespace
        for i,line in enumerate(content.split('\n')):
            line = line.strip()
            if line == '' and i == 0: continue
            f.write(line+'\n')
    else:
        #retain whitespace
        f.write(content)
        
    f.close()

def run(script,var=None,show=False,run=True,wait=False,check=True):
    '''
    run script using variables
    '''
    
    if var == None:
        #get local variables from calling function
        _var = inspect.currentframe().f_back.f_locals
        
        #filter to allow access only to basic variable types
        var = {}
        allowed = [str,int,float,bool]
        for k,v in _var.iteritems():
            if type(v) in allowed:
                var[k] = v
                
        #get run and show parameters from caller
        if 'do_run' in var: run = var['do_run']
        if 'do_show' in var: show = var['do_show']
    
    procs = []
    
    if check:
        #check that all variables can be assigned
        for cmd in script.split('\n'):
            if cmd.strip() == '': continue #blank line
            
            #look for variable place holders in command
            while True:
                res = re.search(r'\[([a-zA-Z0-9_]+)\]',cmd)
                
                if not res: break #no more place holders found
                
                key = res.group(1)
                
                #check a value is present for this variable
                assert key in var
                
                #remove the placeholder
                cmd = cmd.replace('[%s]'%key,'')
            
    for cmd in script.split('\n'):
        if cmd.strip() == '': continue #blank line
        
        #substitute parameter values
        for key,val in var.iteritems():
            _key = '[%s]'%key
            if not _key in cmd: continue
            cmd = cmd.replace(_key,str(val))
            
        #decide if this command should block
        block = True
        if cmd.endswith('&'):
            block = False
            cmd = cmd[:-1]
        
        #print command
        if show: print cmd
        
        if run:
            p = popen(cmd,shell=True)
            
            if block:
                #wait for this step to complete
                p.wait()
                assert p.returncode == 0
            else:
                #do not wait for this step to complete yet
                procs.append(p)

    #wait for all running processes to complete
    if wait:
        for p in procs: p.wait()
        for p in procs: assert p.returncode == 0
    else:
        return procs
        
def sub_vals(cmd,var):
    '''
    replace place holders with values
    '''
    
    #replace [varname] with value
    _cmd = cmd #so we can modify cmd without invalidating iterator
    for match in re.finditer(r'\[([a-zA-Z0-9_][a-zA-Z0-9_.]*)\]',_cmd):
        key = match.group(1)
        
        #allow config variables to be replaced correctly
        if '.' in key:
            k = key.split('.')
            #assign the value (fails if not present)
            cmd = cmd.replace('[%s]'%key, str(var[k[0]].__dict__[k[1]]))
        else:
            #assign the value (fails if not present)
            cmd = cmd.replace('[%s]'%key, str(var[key]))
        
    #look for escaped [!something] place holders, remove !
    _cmd = cmd #so we can modify cmd without invalidating iterator
    for match in re.finditer(r'\[!([^\]]+)\]',_cmd):
        key = match.group(1)
        
        #assign the value (fails if not present)
        cmd = cmd.replace('[!%s]'%key, '[%s]'%key)
        
    return cmd
        
def run2(cmd):
    '''
    run a command using variables from the calling function
    simplified version
    '''
    
    #get local variables from calling function
    _var = inspect.currentframe().f_back.f_locals
    
    #filter to allow access only to basic variable types
    var = {}
    allowed = [str,int,float,bool]
    for k,v in _var.iteritems():
        if type(v) in allowed or str(type(v)) == "<type 'instance'>":
            var[k] = v
            
    del _var
            
    #get run and show parameters from caller
    if 'do_run' in var:
        run = var['do_run']
    else:
        run = True
        
    if 'do_show' in var:
        show = var['do_show']
    else:
        show = False
    
    #look for variable place holders in command
    cmd = sub_vals(cmd,var)
        
    #print command
    if show: print cmd
    
    #decide if this command should block
    block = True
    if cmd.endswith('&'):
        block = False
        cmd = cmd[:-1]
    
    if not run: return None
    
    p = popen(cmd,shell=True)
    
    if block:
        #wait for this step to complete
        p.wait()
        assert p.returncode == 0
        return p.returncode
    else:
        #do not wait for this step to complete yet
        return p
        
def waitfor(procs):
    '''
    wait for all processes to complete
    '''
    
    for p in procs: p.wait()
    for p in procs: assert p.returncode == 0
    
def nonblock(f):
    '''
    make file non blocking
    '''
    
    # make stdin a non-blocking file
    fd = f.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

def read_posn(fname,prop,n=1):
    '''
    jump to a position defined as a proportion of the file size
    print the next n complete lines
    '''
    
    f = open(fname,'rb')
    f.seek(0,2)
    posn = float(f.tell()) * float(prop)
    f.seek(int(posn))
    f.readline()
    
    for i in range(n):
        line = f.readline()
        if line == '': break
        print line
        
    f.close()
    
def tempfilename(tmpdir='/home/rov/rjv_files/tmp/',ext=''):
    '''
    return the name of a temporary file
    '''
    fname =  'tmp%06d'%random.randint(0,999999)
    fname += datetime.datetime.now().strftime("%Y.%m.%d.%H.%M.%S.%f")[:-3]
    fname += ext
    
    return tmpdir + fname

def tmpfname():
    '''
    return the name of a temporary file
    '''
    
    fname =  'tmp.'
    fname += datetime.datetime.now().strftime("%Y.%m.%d.%H.%M.%S.%f")
    fname += '.%06d'%random.randint(0,999999)
    
    return fname

def remove(fname):
    '''
    remove file
    do not complain if it doesn't exist
    
    observes do_run and do_show of calling function
    will not run the command if do_run == False
    will print the command if do_show == True
    '''

    do_run = True
    do_show = False
    
    #get local variables from calling function
    var = inspect.currentframe().f_back.f_locals
    
    #get run and show parameters from caller
    if 'do_run' in var:
        do_run = var['do_run']
        assert type(do_run) == bool
        
    if 'do_show' in var:
        do_show = var['do_show']
        assert type(do_show) == bool
        
    del var
    
    if os.path.exists(fname):
        if do_show: print 'rm %s'%fname
        if do_run:  os.unlink(fname)

def concat(src,dst):
    '''
    append src file to end of dst file
    avoid loading all into memory at once
    '''
    
    f1 = open(dst,'ab')
    f2 = open(src,'rb')
    
    while True:
        data = f2.read(10000)
        if data == '': break
        f1.write(data)
        
    f2.close()
    f1.close()

def load_pickle(fname):
    '''
    load variable from pickle file
    '''
    if fname.endswith('.gz'):
        #uncompress with gzip
        f = gzip.open(fname,'rb')
    else:
        #read directly
        f = open(fname,'rb')
        
    data = cPickle.load(f)
    f.close()
    
    return data

def save_pickle(data,fname):
    '''
    save variable to pickle file
    '''
    
    if fname == sys.stdout:
        f = sys.stdout
    elif fname.endswith('.gz'):
        #compress with gzip
        f = gzip.open(fname,'wb')
    else:
        #save uncompressed
        f = open(fname,'wb')
        
    cPickle.dump(data,f)
    f.close()
