import time,datetime
import scipy.optimize as opt
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import random
import ttag_wrap
import gen_find_nano_patterns as gp
import serial_SLM
import math
import atexit
import os,sys
import shutil
dataPathInterp = ''
if len(sys.argv)>3:
  if len(sys.argv)==7:
    offset = 0
    Tacq =1
  else:
    offset = 1
    Tacq = float(sys.argv[1])

  xstart=int(sys.argv[offset+1])
  xstop = int(sys.argv[offset+2])
  xstep = int(sys.argv[offset+3])
  ystart = int(sys.argv[offset+4])
  ystop = int(sys.argv[offset+5])
  ystep = int(sys.argv[offset+6])
  SCAN = True
elif len(sys.argv)==2:
  Tacq = 1 
  # Need path of the interpolation file
  #dataPathInterp = '/hdd/2015_03_12/run%/'
  SCAN=False
  dataPathInterp = sys.argv[1]
elif len(sys.argv)==3:
  Tacq = float(sys.argv[1])
  dataPathInterp = sys.argv[2]
  SCAN = False
dataPathInterp = dataPathInterp.rstrip('/')+'/' 
SLMpath = '/mnt/SLM/Dan/OptimizeSLM/Patterns/OrigSettings/'
PC =True 
serial_SLM.setup(PC)
send = serial_SLM.send
wait = serial_SLM.wait
CoincidenceWindow = 10e-9
gate = 10e-9
heraldChan = 0
bobMirrorFileName = "/mnt/SLM/Dan/FindNanowiresSERICALPORT/NanowireScanNOSCRAMBLE/Bob/on.dat"

phasemap = np.loadtxt('slm3381_at635_DVI.txt', dtype = np.uint32)
phasemap = phasemap[:,1]

format = '%Y_%m_%d'
folder = '/hdd/%s/'%datetime.datetime.today().strftime(format)
#print folder

dirCnt=1
while True:
    dataPath = folder+'run%02d/'%dirCnt
    #print dataPath
    try:
      os.makedirs(dataPath)
      break
    except:
      dirCnt += 1
print 'dataPath:',dataPath


#os.makedirs(dataPath)
buf = ttag_wrap.openttag()
buf.start()


def getCnts(Tacq, CoincidenceWindow, buf):
    global dataPath
    time.sleep(Tacq)
    x = buf.coincidences(Tacq, CoincidenceWindow)
    cnts = x[0:8,8:16]
    return cnts

def getCnts(Tacq, CoincidenceWindow, gate, heraldChan, buf):
    global dataPath
    time.sleep(Tacq)
    x = buf.coincidences(Tacq, CoincidenceWindow)
    xx = buf.coincidences(Tacq, CoincidenceWindow, gate = gate, heraldChan = heraldChan)
    cnts_single = x[0:8,8:16]
    cnts_coin = xx[0:8,8:16]
    
    return cnts_single, cnts_coin


def cleanUp():
    global buf
    print "Cleaning"
    buf.stop()
atexit.register(cleanUp)

def write2file(fname, cnts, xo, yo,cnt):
    global dataPath
    #print 'Saving to %s'%(fname)
    fp = open(dataPath+fname,'a')
    np.savetxt(fp, cnts, fmt = '%7d')
    fp.write('#x:%5d  y:%5d  cnt:%6d\n'%(xo,yo,cnt))

CoincidenceWindow = 10e-9

nrows = 512

if SCAN:
    #  scanning the SLM
    scanparams = [xstart, xstop, xstep, ystart, ystop, ystep] 
    np.savetxt(dataPath + 'scanparameters.txt',scanparams,fmt='%d')
    pixel_list = []
    for xo in range(xstart, xstop+1, xstep):
        for yo in range(ystart, ystop+1, ystep):
            pixel_list.append([xo,yo])

else:
    scanparams = np.loadtxt(dataPathInterp+'scanparameters.txt') 
    (xstart, xstop, xstep, ystart, ystop, ystep)=scanparams
    pixel_list = gp.interpolate2SLM(dataPathInterp, xstart, xstep, ystart, ystep)
    #print pixel_list
cnt = 0
for pixel in pixel_list:
        (xo,yo)=pixel
        if SCAN:
            print xo,yo
        fft_phase = gp.initial_phase_orig(257-xo,257-yo, 512)
        #print 'phase_offset',gp.phase_offset
        gp.write2file(fft_phase, gp.phasemap, SLMpath, '99')
        shutil.copyfile(bobMirrorFileName, '/mnt/SLM/Dan/OptimizeSLM/Patterns/OrigSettings/SLM_100.dat')
        send(99)
        msgin = wait()
        if int(msgin)<0:
            print 'problem talking with loading a file on the SLM'
            break
        #print 'From PC: ',msgin
        cnts_single, cnts_coin = getCnts(Tacq, CoincidenceWindow,gate, heraldChan,buf)
        fname = 'single_%d.txt'%dirCnt
        write2file(fname, cnts_single, xo,yo,cnt)
        fname = 'coin_%d.txt'%dirCnt
        write2file(fname,cnts_coin,xo,yo,cnt)
        cnt += 1

