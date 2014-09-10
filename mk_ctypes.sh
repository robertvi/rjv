#!/bin/sh
FNAME='test_ctypes'

#static library
#gcc -c ${FNAME}.c -o ${FNAME}.o
#ar rcs lib${FNAME}.a ${FNAME}.o

#shared library
#gcc -c -fPIC ${FNAME}.c -o ${FNAME}.o
#gcc -shared -Wl,-soname,lib${FNAME}.so.1 -o lib${FNAME}.so.1.0.1  ${FNAME}.o

#shared library 2
gcc -c -fPIC ${FNAME}.c -o ${FNAME}.o
gcc -shared -o ${FNAME}.so ${FNAME}.o
