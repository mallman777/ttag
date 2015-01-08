import ctypes
import numpy.ctypeslib
import numpy as np
import time

class myStruct(ctypes.Structure):
    _fields_ = [("times", ctypes.POINTER(ctypes.c_long)),
                ("chans", ctypes.POINTER(ctypes.c_short)),
                ("size", ctypes.c_int)]

lib = numpy.ctypeslib.load_library("testlib", ".")

lib.myadder.restype = ctypes.c_int
lib.myadder.argtypes = [ctypes.c_int, ctypes.c_int]
lib.myFun.restype = ctypes.POINTER(myStruct)
lib.myFun.argtypes = [ctypes.c_int]
lib.arrSum.restypes = ctypes.c_int
lib.arrSum.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int]

x = 6
y = 6

m = lib.myFun(20)

print dir(m.contents)
print m.contents._fields_
print m.contents.size
print m.contents.times[0:m.contents.size]
print m.contents.chans[0:m.contents.size]

if False:
    SIZE = int(1000000)
    z = np.ones(SIZE, dtype = np.int32)

    to = time.time()
    ans1 = np.sum(z)
    tf = time.time()
    runTimeNP = tf-to

    to = time.time()
    ans2 = lib.arrSum(z.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),SIZE) 
    tf = time.time()
    runTimeLIB = tf-to

    ans3 = 0
    to = time.time()
    for i in range(SIZE):
        ans3 += z[i]
    tf = time.time()
    runTimeLoop = tf-to
    
    print ans1, ans2, ans3
    print "runTimeNP: ", runTimeNP
    print "runTimeLIB: ", runTimeLIB
    print "runTimeLoop: ", runTimeLoop
