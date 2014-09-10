#!/usr/bin/python

from rjv.fileio import *
from ctypes import *

fname = 'test_ctypes'

run2('gcc -c -fPIC [fname].c -o [fname].o')
run2('gcc -shared -o [fname].so [fname].o')
clib = CDLL('./%s.so'%fname)

val = clib.cfunc(123)

print val
