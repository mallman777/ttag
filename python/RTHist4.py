# Version 4 implements multiprocess to process histograms faster 
import sys
sys.path.append('/mnt/odrive/HPD/ShanePyStuff/classes')
import multiprocessing as mp
import time
import os
import atexit
import subprocess
import numpy as np
import signal
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType
import pyqtgraph.ptime as ptime
import ttag
import logfile
import configParser
import datetime
import serial
import SIM900gpib 

# Load config settings and create objects
config = '../../../../config.ini'
uqdConfig = '../../CppDemo/uqd.uqcfg'
c = configParser.ConfigParser()
options = c.parse_config(config)
port = serial.Serial('/dev/ttyUSB0', 9600, timeout = 0.5)
sim = SIM900gpib.device(4,port)

# Experiment Parameters
program, run = sys.argv
R = float(options['biasResistance'])
LaserWvl = float(options['laserWavelength'])
LaserPwr = float(options['laserPower'])
LaserAttn1 = float(options['laserAttn1'])
LaserAttn2 = float(options['laserAttn2'])
Tacq = 1  # Measurement time in seconds
CoincidenceWindow = 5e-9  # Coincidence window based on observed delay between row and column pulses.

time.sleep(1)
bufNum = ttag.getfreebuffer()-1
buf = ttag.TTBuffer(bufNum)
oldPnts = 0
#pnts = 0
buf.start()
time.sleep(1)

app = QtGui.QApplication([])

timer = QtCore.QTimer()
timer.setInterval(int(Tacq*1000))
cntr = 0
########## Parameter Tree #################

params = [
  {'name':'min', 'type':'float', 'value':0},
  {'name':'max', 'type':'float', 'value':1e-6},
  {'name':'binSize', 'type':'int', 'value':10},
  {'name':'Reset Histogram', 'type':'action', 'visible':True},
  {'name':'Pause Histogram', 'type':'bool', 'value':True},
  {'name':'Save Histogram', 'type':'action', 'visible':True}
]

p = Parameter.create(name = 'params', type = 'group', children = params)

def resetHist():
  global y, cntr
  y = 0
  cntr = 0

def saveHist():
  global xx,yy,x, y, cntr
  d = datetime.datetime.now()
  timestamp = d.strftime('%Y%m%d_%H%M%S')
  dataLogPath = options['networkData&LogPath']
  fname = '%s_R%d.bin'%(timestamp, int(run))
  fnameLog = '%s_R%d.log'%(timestamp, int(run))
  fpath = os.path.join(dataLogPath, fname)
  fpathLog = os.path.join(dataLogPath, fnameLog)
  fHist = open(fpath, 'wa')
  fHistLog = open(fpathLog, 'w')
#  outMatrix = np.array([x[:-1],y], dtype = np.uint64)
  outMatrix = np.empty([9,np.shape(y)[1]], dtype = np.uint64)
  outMatrix[0,:] = x[:-1]
  outMatrix[1:,:] = y
  print "len(x): ", len(x)
  print "len(y): ", len(y)
  print "np.shape(outMatrix)", np.shape(outMatrix)
  sim.conn(int(run))
  sim.write('VOLT?')
  msg = sim.read()
  sim.write('xyz')
  sim.meter.loc()

  np.save(fHist, outMatrix)  # save as binary
#  np.savetxt(fHist, outMatrix, fmt = '%d',  delimiter = ' ', newline = '\n')
  fHistLog.write('histogram data is in integer number of buffer resolution\n')
  fHistLog.write('to turn xx into time, multiply by buf.resolution\n')
  fHistLog.write('Bins are first, then histogram data for all eight columns\n')
  fHistLog.write('First 10 bytes are header stuff from np.save and should be skipped over\n')
  fHistLog.write('sys.argv:   %r\n' % sys.argv)
  fHistLog.write('Row:   %d\n' % int(run))
  fHistLog.write('bias voltage:   %f\n' % (float(msg)))
  fHistLog.write('buffer resolution:   %fps\n' % (buf.resolution*1e12))
  fHistLog.write('Hist Start Time:   0\n')
  fHistLog.write('Hist Stop Time:   %fs\n' % 500e-6)
  fHistLog.write('Integration Time:   %fs\n'% (float(cntr*Tacq/8)))  # Divide total integration time by 8 since each hist was exposed for cntr*Tacq

  fHist.close()
  fHistLog.close()

def worker1(arr, outq):
  histMin = int(0/buf.resolution)
  histMax = int(500e-6/buf.resolution)  
  histBinNum = int((histMax-histMin)/p.param('binSize').value())
  #outArr = np.empty([8,histMax-histMin-1], dtype = np.uint64)
#  print "Start worker1"
  y,x = np.histogram(arr, bins = np.linspace(0, histMax, histMax-histMin))
  outq.put(y) 
#  print "End worker1"

def getChHist():
  global buf, oldPnts, y, x
  buf.tagsAsTime = False
  pnts = buf.datapoints
#  tup = buf[-(pnts-oldPnts):]
  tup = buf(Tacq)
  oldPnts = pnts
  chans = tup[0]
  times = tup[1]
  channelTTags = np.array([], dtype = np.uint64)
#  ynew = np.empty([8,histMax-histMin-1], dtype = np.uint64)
  procList = []
  outqList = []
  for i in range(8):  # spawn processes for each histogram
    channelTTags = times[chans == i+8]
    dtimes = np.diff(channelTTags)
    q = mp.Queue()
#    print "starting process %d" % (i + 1)
    pp = mp.Process(target = worker1, args = (dtimes, q))
    pp.start()
    procList.append(pp)
    outqList.append(q)
  histMin = int(0/buf.resolution)
  histMax = int(500e-6/buf.resolution)  
  histBinNum = int((histMax-histMin)/p.param('binSize').value())

  ynew = np.empty([8,histMax-histMin-1], dtype = np.uint64)
  for i, q in enumerate(outqList):  # get results of each process from output queues
#    print "Getting Result %d" % (i+1)
    ynew[i,:] = q.get()
  x = np.linspace(0,histMax, histMax - histMin)
  y += ynew

  for i, pp in enumerate(procList):  # wait for all spawned processes to finish before continuing
#    print "waiting for process %d to finish" % (i+1)
    pp.join()
    pp.terminate()
 
  if p.param('binSize').value() <= 1:
      return y,x
  else:
    binSize = p.param('binSize').value()
    yy = np.empty([8,int(len(y[i,:])/binSize)], dtype = np.uint64)
    for i in range(8):
      yreshape = np.reshape(y[i,0:binSize*int(len(y[i,:])/binSize)], [int(len(y[i,:])/binSize), binSize])
      yy[i,:] = np.sum(yreshape, axis = 1)
    xx = x[0::binSize]

  return yy,xx

def findNear(array, value):
  idx = (np.abs(array-value)).argmin()
  return idx
    
p.param('Reset Histogram').sigActivated.connect(resetHist)
p.param('Save Histogram').sigActivated.connect(saveHist)

t = ParameterTree()
t.setParameters(p, showTop = False)
t.show()  

if True:
  win = pg.GraphicsWindow()
  win.resize(1600,600)
  win.setWindowTitle('Real Time Histogram')
  plotList = []
  for i in range(8):
    if i == 3:
      plt = win.addPlot(labels = {'left': 'log10(Counts)', 'bottom': 'time'}, title = "Col%d" %(i+1))
      plotList.append(plt)
      win.nextRow()
    else:
      plt = win.addPlot(labels = {'left': 'log10(Counts)', 'bottom': 'time'}, title = "Col%d" %(i+1))
      plotList.append(plt)
  win.show()

###################

oldCurves = [0]*8
y = 0

def update():
    global p, cntr, oldCurves, buf, xx, yy, cntr
    if p.param('Pause Histogram').value() == False:
        yy,xx = getChHist()
        cntr += 1 # This is the "integration time".  Simply the number of times update has been called, since getChHist gets data from last 1 sec. 
    xo = int(p.param('min').value()/buf.resolution)
    xf = int(p.param('max').value()/buf.resolution)
    start = findNear(xx, xo) 
    stop = findNear(xx, xf)
    curveList = []
    for i in range(8):
      curve = pg.PlotCurveItem(xx[start:stop]*buf.resolution, np.log10(yy[i,start:stop-1].astype(float)+0.01), stepMode = True, fillLevel = 0, brush = (0,0,255,80))
      curveList.append(curve)
      plotList[i].setXRange(p.param('min').value(), p.param('max').value())
      plotList[i].setYRange(0, np.max(np.log10(yy[i,start:stop-1].astype(float)+0.01)))
#      plotList[i].setLogMode(y  = True)
      plotList[i].addItem(curve)
      if oldCurves[i] != 0:
        plotList[i].removeItem(oldCurves[i])
      oldCurves[i] = curve
    print "intTime: ", (cntr*Tacq)

def cleanUp():
    print "Cleaning"
    for i in range(100):
      ttag.deletebuffer(i)

atexit.register(cleanUp)
    
timer.timeout.connect(update)
timer.start()
win.raise_()
#win.activateWindow()
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


	    


