'''
functions for plotting data using R
'''

from subprocess import *
from StringIO import *

r_cmd = ['R','--no-save']

newline = '\n'

def plot_xy(x,y,fname):
    '''
    do an xy plot to a png file
    '''
    
    proc = Popen(r_cmd,stdin=PIPE)

    script = [
              'x <- c(' + ','.join(str(x)) + ')',
              'y <- c(' + ','.join(str(y)) + ')',
              'png("%s")'%fname,
              'plot(x,y)',
              'dev.off()',
              'q()',
             ]
             
    proc.stdin.write(newline.join(script) + newline)
    #proc.stdin.close()
