import time
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
import sys

SLMpath = '/mnt/SLM/Dan/OptimizeSLM/Patterns/OrigSettings/'
PC = True

phasemap = np.loadtxt('slm3381_at635_DVI.txt', dtype = np.uint32)
phasemap = phasemap[:,1]

ttnumber = ttag.getfreebuffer()-1
print "ttnumber: ", ttnumber
buf = ttag.TTBuffer(ttnumber)  #Opens the buffer
buf.start()


def getCnts(pix, Tacq, CoincidenceWindow, buf):
  #buf.start()
  #time.sleep(Tacq + 0.1*Tacq)
  #buf.stop()
  time.sleep(Tacq)
  x = buf.coincidences(Tacq, CoincidenceWindow)
  cnts = x[0:8,8:16]
  norm = cnts.sum()
  #print 'norm',norm
  row = pix / 8
  col = pix % 8
  return cnts[row,col], norm


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

if len(sys.argv)>1:
  Tacq = float(sys.argv[1])
else:
  Tacq = 1
  print "You forgot to include inttime as input parameter"
  print "Using 1 second"

CoincidenceWindow = 10e-9
xo = 127
yo = 135 
pix = 27 
xo = 172.0
yo = 98.0

phaseMap = np.loadtxt('slm3381_at635_DVI.txt', dtype = np.uint32)
interpSettings = gp.getInterpSettings()
origPath = "/mnt/SLM/Dan/OptimizeSLM/Patterns/OrigSettings/"
nrows = 512
for pix in range(35,36):
  #print interpSettings[pix,0],interpSettings[pix,1]
  xo = (interpSettings[pix,0])
  yo = (interpSettings[pix,1])
  print pix, xo,yo
  #while True:
  gp.phase_offset = 0
  while True:
    fft_phase = gp.initial_phase_orig(257-xo,257-yo, 512)
    gp.phase_offset += 1000
    print 'phase_offset',gp.phase_offset
    gp.write2file(fft_phase, gp.phasemap, SLMpath, '99')
    send(99)
    raw_input('Hit enter to try another phase')
"""
    fprev = getCnts(pix, Tacq, CoincidenceWindow,buf) 

    x_offsetList = np.arange(-2,3)*2            
    y_offsetList = np.arange(-2,3)*2

    cnts = []
    norms = []
    for x_offset in x_offsetList:
      fft_phase = gp.initial_phase_orig(257-(xo+x_offset),257-(yo), 512)
      gp.write2file(fft_phase, gp.phasemap, SLMpath, '99')
      send(99)
      (f,norm) = getCnts(pix, Tacq, CoincidenceWindow,buf)
      cnts.append(1.*f)
      norms.append(norm)
      print 'x:%.3f %6d %6d %.3f'%(xo+x_offset, f,norm, 1.*f/norm)
    cnts = np.array(cnts)
    normsx = np.array(norms)

    p_fit = np.polyfit(x_offsetList, cnts/normsx, 2)
    newx = -p_fit[1]/(2*p_fit[0])

    cnts = []
    norms = []
    x_offset = 0
    for y_offset in y_offsetList:
      fft_phase = gp.initial_phase_orig(257-(xo+x_offset),257-(yo+y_offset), 512)
      gp.write2file(fft_phase, gp.phasemap, SLMpath, '99')
      send(99)
      (f,norm) = getCnts(pix, Tacq, CoincidenceWindow,buf)
      cnts.append(1.*f)
      norms.append(norm)
      print 'y:%.3f %6d %6d %.3f'%(yo + y_offset,f,norm, 1.*f/norm)
    cnts = np.array(cnts)
    normsy = np.array(norms)
    p_fit = np.polyfit(x_offsetList, cnts/normsy, 2)
    newy = -p_fit[1]/(2*p_fit[0])
      
    xo += newx
    yo += newy
    print 'newx: %.2f\tnewy: %.2f'%(xo,yo) 
"""
