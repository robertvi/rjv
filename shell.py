from subprocess import Popen as popen
import re
import inspect

def run(script,var=None,show=False,run=True,wait=True,check=True):
    '''
    run script using variables
    '''
    
    if var == None:
        #get local variables from calling function
        _var = inspect.currentframe().f_back.f_locals
        
        #filter to allow access only to basic variable types
        var = {}
        allowed = [str,int,float]
        for k,v in _var.iteritems():
            if type(v) in allowed:
                var[k] = v
    
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
            
            if block: p.wait() #wait for this step to complete
            else:     procs.append(p) #do not wait for this step to complete yet

    #wait for all running processes to complete
    if wait:
        for p in procs:
            p.wait()
