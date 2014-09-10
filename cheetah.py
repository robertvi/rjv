import inspect,sys
from subprocess import Popen as popen
sys.path.append('/ibers/ernie/home/rov/python_lib/Cheetah-2.4.4-py2.6-linux-x86_64.egg')
from Cheetah.Template import Template

def cheetah(template,run=True,block=True):
    '''
    run shell command after substituting variables from calling function
    using cheetah template engine
    uses @ as the variable start token to make writing
    shell commands easier
    '''
    
    #get local variables from calling function
    var = inspect.currentframe().f_back.f_locals

    #change the 'variable start token' to something more shell-friendly
    template = '#compiler-settings\ncheetahVarStartToken = @\n#end compiler-settings'\
             + template

    cmd = str(Template(template, searchList=[var]))
    
    if run == False:
        #don't run just print the command
        print cmd
        return 0
        
    #run command in a subshell
    p = popen(cmd,shell=True)
    
    if block == True:
        #wait for the command to complete
        p.wait()
        assert p.returncode == 0
        return p.returncode
        
    #do not wait for the command to complete
    return p


def cheetah_file(template,f=None):
    '''
    write script to file after substituting variables from calling function
    using cheetah template engine
    uses @ as the variable start token to make writing
    shell commands easier
    '''
    
    #get local variables from calling function
    var = inspect.currentframe().f_back.f_locals

    #change the variable start token to something more shell-friendly
    template = '#compiler-settings\ncheetahVarStartToken = @\n#end compiler-settings'\
             + template

    cmd = str(Template(template, searchList=[var]))
    
    if f == None:
        #return as string
        return cmd
        
    elif type(f) == str:
        #open file, write, close file
        with open(f,'wb') as fout: fout.write(cmd)
        
    else:
        #append to already open file
        f.write(cmd)
        
