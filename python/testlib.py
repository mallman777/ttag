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
lib.myHist.restypes = ctypes.POINTER(ctypes.c_longlong)
lib.myHist.argtypes = [ctypes.POINTER(ctypes.c_longlong), 
                       ctypes.POINTER(ctypes.c_longlong)]

x = 6
y = 6

m = lib.myFun(20)

#print dir(m.contents)
#print m.contents._fields_
#print m.contents.size
#print m.contents.times[0:m.contents.size]
#print m.contents.chans[0:m.contents.size]

if True:
    SIZE = int(100000)
    z = np.ones(SIZE, dtype = np.int32)
    range = np.array([0,7], dtype = np.int64)
    binNum = range[1] - range[0] + 1
    y = np.random.randint(range[0], range[1],SIZE)
    hist = np.zeros(2*binNum, dtype = np.int64)    
    
    to = time.time()
    lib.myHist(hist.ctypes.data_as(ctypes.POINTER(ctypes.c_longlong)), y.ctypes.data_as(ctypes.POINTER(ctypes.c_longlong)), range.ctypes.data_as(ctypes.POINTER(ctypes.c_longlong)))
    yy = hist[0:binNum]
    xx = hist[binNum::]
    tf = time.time()
    runTimeMyHist = tf-to

    print xx
    print yy

    to = time.time()
    yy,xx = np.histogram(y, binNum, range = (range[0],range[1]))
    tf = time.time()
    runTimeNpHist = tf-to

    print xx
    print yy
    
    print runTimeMyHist
    print runTimeNpHist



