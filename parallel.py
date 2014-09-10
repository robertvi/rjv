from subprocess import Popen

from rjv.fileio import *

def splitter(splitter,runner,chunks,tmpbase,outfile=None,append=False):
    '''
    parallelise a command by splitting up its input using pipes
    
    example splitter command:
    'splitfasta.py scaffolds.fa [chunks] [offset] > [pipe]'
    
    example runner command
    'blastn -query [pipe] -subject mydb.fa > [output]'
    
    example tmpbase
    '../tmp/%s_%d' must have %s followed by %d
    
    output ends up in files called tmpbase%('output',offset)
    or in outfile
    '''

    procs = []
    for offset in xrange(chunks):
        #create pipe
        pipe = tmpbase%('pipe',offset)
        remove(pipe)
        Popen('mkfifo %s'%pipe,shell=True).wait()

        #launch the splitter command
        cmd = splitter.replace('[chunks]',str(chunks))
        cmd = cmd.replace('[offset]',str(offset))
        cmd = cmd.replace('[pipe]',pipe)
        Popen(cmd,shell=True)
        
        #launch the runner command
        outp = tmpbase%('output',offset)
        cmd = runner.replace('[pipe]',pipe)
        cmd = cmd.replace('[output]',outp)
        p = Popen(cmd,shell=True)
        procs.append(p)

    #wait for all runners to complete
    for p in procs: p.wait()
    
    for offset in xrange(chunks):
        #remove pipes
        remove(tmpbase%('pipe',offset))
    
    #do not aggreagte results
    if not outfile: return
    
    #remove any existing results file
    if not append: remove(outfile)
    
    #aggregate results files
    for offset in xrange(chunks):
        outp = tmpbase%('output',offset)
        Popen('cat %s >> %s'%(outp,outfile),shell=True).wait()
        remove(outp)
    
