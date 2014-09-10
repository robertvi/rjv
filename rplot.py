'''
functions for plotting data using R
'''

from subprocess import *
from StringIO import *
from rjv.fileio import tempfilename

r_cmd = ['R','--no-save']

newline = '\n'

def plot_xy_buggy(x,y,fname,xlab='x',ylab='y'):
    '''
    do an xy plot to a png file
    this version does not wait for the subprocess to complete
    before returning!
    this version does not require creation of a temporary file
    '''
    
    x = [str(val) for val in x]
    y = [str(val) for val in y]
    
    script = [
              'x <- c(' + ','.join(x) + ')',
              'y <- c(' + ','.join(y) + ')',
              #'png("%s")'%fname,
              'pdf("%s")'%fname,
              'plot(x,y,xlab="%s",ylab="%s")'%(xlab,ylab),
              'dev.off()',
              'q()',
             ]

    f = open('/dev/null','wb')
    proc = Popen(r_cmd,stdin=PIPE,stdout=f,stderr=STDOUT)
    proc.stdin.write(newline.join(script) + newline)
    proc.stdin.close()
    f.close()

def plot_xy(x,y,fname,xlab='x',ylab='y'):
    '''
    do an xy plot to a png file
    this version creates a temporary file containing the R commands
    and data
    but reliably waits for the subprocess to finish before returning
    '''
    
    x = [str(val) for val in x]
    y = [str(val) for val in y]
    
    script = [
              'x <- c(' + ','.join(x) + ')',
              'y <- c(' + ','.join(y) + ')',
              #'png("%s")'%fname,
              'pdf("%s")'%fname,
              'plot(x,y,xlab="%s",ylab="%s")'%(xlab,ylab),
              'dev.off()',
              'q()',
             ]

    tmpname = tempfilename()
    f = open(tmpname,'wb')
    f.write(newline.join(script) + newline)
    f.close()
    
    f = open(tmpname,'rb')
    fnull = open('/dev/null','wb')
    call(r_cmd,stdin=f,stdout=fnull,stderr=STDOUT)
    f.close()
    fnull.close()
