import time,datetime
import scipy.optimize as opt
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import random
import ttag
import gen_find_nano_patterns as gp
import serial
import math
import atexit
import os,sys
import glob
import shutil
SLMpath = '/mnt/SLM/Dan/OptimizeSLM/Patterns/OrigSettings/'
PC =True 

phasemap = np.loadtxt('slm3381_at635_DVI.txt', dtype = np.uint32)
phasemap = phasemap[:,1]

format = '%Y_%m_%d'
folder = '/hdd/%s/'%datetime.datetime.today().strftime(format)
print folder
# creating directory for data
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

ttnumber = ttag.getfreebuffer()-1
print "ttnumber: ", ttnumber
buf = ttag.TTBuffer(ttnumber)  #Opens the buffer
buf.start()

def getCnts(Tacq, CoincidenceWindow, gate, heraldChan, buf):
    global dataPath
    time.sleep(Tacq)
    x = buf.coincidences(Tacq, CoincidenceWindow)
    xx = buf.coincidences(Tacq, CoincidenceWindow, gate = gate, heraldChan = heraldChan)
    cnts_single = x[0:8,8:16]
    cnts_coin = xx[0:8,8:16]
    
    return cnts_single, cnts_coin

serialport = serial.Serial('/dev/ttyUSB0',38400,timeout=0.05)

def waitforPC():
    #print 'Waiting for msg from PC'
    msgin = ''
    while (msgin == ''):
        #print "waiting for msg"
        msgin = serialport.read(80);
    #print 'msg from PC: %s' %msgin 
    return msgin

def sendtoPC(count):
    #print 'Sending photon num: %d'%count
    serialport.write('%d'%count)

if PC==True:
    wait = waitforPC
    send = sendtoPC
else:
    wait = fakewait
    send = fakesend

def cleanUp():
    global buf
    print "Cleaning"
    buf.stop()
atexit.register(cleanUp)

def write2file(fname, cnts, xo, yo):
    global dataPath
    print 'Saving to %s'%(fname)
    fp = open(dataPath+fname,'a')
    np.savetxt(fp, cnts, fmt = '%7d')
    fp.write('#x:%5d  y:%5d\n'%(xo,yo))

if len(sys.argv)>1:
  Tacq = float(sys.argv[1])
else:
  Tacq = 1
  print "You forgot to include inttime as input parameter"
  print "Using 1 second"

CoincidenceWindow = 10e-9
gate = 10e-9
heraldChan = 0
alist = sorted(glob.glob('/home/qittlab/Downloads/Alice/*'))
blist = sorted(glob.glob('/home/qittlab/Downloads/Bob/*')) 

for afilename, bfilename in zip(alist,blist):
    # copy file to SLM_99.dat
    shutil.copyfile(afilename, '/mnt/SLM/Dan/OptimizeSLM/Patterns/OrigSettings/SLM_99.dat')
    # copy file to SLM_100.dat
    shutil.copyfile(bfilename, '/mnt/SLM/Dan/OptimizeSLM/Patterns/OrigSettings/SLM_100.dat')
    # send msg to PC 
    send(99)
    msg = wait()
    print int(msg)
    time.sleep(0.1)
    cnts_single, cnts_coin = getCnts(Tacq, CoincidenceWindow,gate, heraldChan,buf)
    fname = 'single_%d.txt'%dirCnt
    write2file(fname, cnts_single, 0,0)
    fname = 'coin_%d.txt'%dirCnt
    write2file(fname,cnts_coin,0,0)
