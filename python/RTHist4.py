# Version 4 implements multiprocess to process histograms faster 
import sys
sys.path.append('/mnt/odrive/HPD/ShanePyStuff/classes')
import multiprocessing as mp
import time, os, atexit, datetime, serial
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType
import pyqtgraph.ptime as ptime
import pyqtgraph.exporters
import pyqtgraph.exporters.ImageExporter as IE
import ttag, functionLib, logfile, configParser, SIM900gpib

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
updateTime = 1  # Measurement time in seconds
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
timer.setInterval(int(updateTime*1000))
cntr = 0
########## Parameter Tree #################

params = [
  {'name':'firstCh', 'type':'int', 'value':1},
  {'name':'secondCh', 'type':'int', 'value':2},
  {'name':'min', 'type':'float', 'value':-100e-9},
  {'name':'max', 'type':'float', 'value':100e-9},
  {'name':'binSize', 'type':'int', 'value':1},
  {'name':'Tacq', 'type':'float', 'value':0.1},
  {'name':'algorithm', 'type':'str', 'value':'c'},
  {'name':'numPlots', 'type':'int', 'value':1},
  {'name':'Reset Histogram', 'type':'action', 'visible':True},
  {'name':'Pause Histogram', 'type':'bool', 'value':False},
  {'name':'Save Histogram', 'type':'action', 'visible':True},
  {'name':'Save Figure', 'type':'action', 'visible':True}
]

p = Parameter.create(name = 'params', type = 'group', children = params)

def saveFig():
  dirName = "/mnt/odrive/HPD/Cooldown150605/"
  fname = "test.png"
  dataPath = dirName + fname
  exporter = IE.ImageExporter(plt)
  exporter.export(dataPath)

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
  fHistLog.write('Integration Time:   %fs\n'% (float(cntr*updateTime/8)))  # Divide total integration time by 8 since each hist was exposed for cntr*Tacq

  fHist.close()
  fHistLog.close()

def worker1(arr, outq):
  histMin = int(0/buf.resolution)
  histMax = int(500e-6/buf.resolution)  
  y,x = np.histogram(arr, bins = np.linspace(0, histMax, histMax-histMin))
  outq.put(y) 

def getChart(cnt, time, chartSize = 100):
  start = (cnt % chartSize) + 1
  singles = buf.singles(time)
  if (not hasattr(getChart, "chart")):
    getChart.chart = np.empty([len(singles), chartSize])
  for i in range(len(singles)):
      getChart.chart[i, cnt % chartSize] = singles[i]
  if start == chartSize:
    return getChart.chart
  else:
    return np.hstack([getChart.chart[:,start:], getChart.chart[:,:start]])

def getXtalkHist(ch1, ch2, time, window = 200e-9, algorithm = 'c'): #For histogramming cross correlations between different channels like the HH does.
  global buf, x, y
  buf.tagsAsTime = False
  chans, times = buf(time)
  ch1Tags, ch2Tags = (times[chans == ch1], times[chans == ch2])
  print "sizeCh1*sizeCh2: ", ch1Tags.shape[0]*ch2Tags.shape[0]
  histMin = -window/buf.resolution
  histMax = window/buf.resolution
  myFun = functionLib.fun()
  ynew, x = myFun.getHist(ch1Tags, ch2Tags, np.array([histMin, histMax], dtype = np.int64), algorithm = algorithm)
  y += ynew
  return reBin(x,y)

def getChHist():
  global buf, oldPnts, y, x
  buf.tagsAsTime = False
  pnts = buf.datapoints
  tup = buf(updateTime)
  oldPnts = pnts
  chans = tup[0]
  times = tup[1]
  channelTTags = np.array([], dtype = np.uint64)
  procList = []
  outqList = []
  for i in range(8):  # spawn processes for each histogram
    channelTTags = times[chans == i+8]
    dtimes = np.diff(channelTTags)
    q = mp.Queue()
    pp = mp.Process(target = worker1, args = (dtimes, q))
    pp.start()
    procList.append(pp)
    outqList.append(q)
  histMin = int(0/buf.resolution)
  histMax = int(500e-6/buf.resolution)  
  ynew = np.empty([8,histMax-histMin-1], dtype = np.uint64)
  for i, q in enumerate(outqList):  # get results of each process from output queues
    ynew[i,:] = q.get()
  x = np.linspace(0,histMax, histMax - histMin)
  y += ynew
  for i, pp in enumerate(procList):  # wait for all spawned processes to finish before continuing
    pp.join()
    pp.terminate()
  return reBin(x,y)

def reBin(xarr,yarr):
  if len(yarr.shape) == 1:
    yarr = np.array([yarr])
  if p.param('binSize').value() <= 1:
    return yarr,xarr
  else:
    binSize = p.param('binSize').value()
    rows = yarr.shape[0]
    cols = yarr.shape[1]
    yy = np.empty([rows,int(len(yarr[0,:])/binSize)], dtype = np.uint64)
    for i in range(rows):
      yreshape = np.reshape(yarr[i,0:binSize*int(len(yarr[i,:])/binSize)], [int(len(yarr[i,:])/binSize), binSize])
      yy[i,:] = np.sum(yreshape, axis = 1)
    xx = xarr[0::binSize]
  return yy,xx

def findNear(array, value):
  idx = (np.abs(array-value)).argmin()
  return idx
    
def plotChart(chart):
  if not hasattr(plotChart, 'firstRun'):
    plotChart.firstRun = True
    plotChart.curveList2 = []
  if plotChart.firstRun:
    for i in range(chart.shape[0]):
      plotChart.curveList2.append(plt2.plot(pen=(200,200,200), symbolBrush = (0,255,0), symbolPen = 'w'))
    plotChart.firstRun = False
  for idx, c in enumerate(plotChart.curveList2):
    c.setData(chart[idx, :])

def plotHist(xx,yy, num = p.param('numPlots').value()):
  #global curve
  (xo, xf) = (int(p.param('min').value()/buf.resolution), int(p.param('max').value()/buf.resolution))
  start = findNear(xx, xo)
  stop = findNear(xx, xf)
  if not hasattr(plotHist, 'firstRun'):
    plotHist.firstRun = True
    plotHist.oldCurve = None
  curve = pg.PlotCurveItem(xx[start:stop]*buf.resolution, np.log10(yy[i,start:stop-1].astype(float)+0.01), stepMode = True, fillLevel = 0, brush = (0,0,255,80))
  if plotHist.firstRun:
    plotList[0].addItem(curve)
    plotHist.firstRun = False
  else:
    plotList[0].removeItem(plotHist.oldCurve)
    plotList[0].addItem(curve)
  plotHist.oldCurve = curve
  plotList[0].setXRange(p.param('min').value(), p.param('max').value())
  plotList[0].setYRange(0, np.max(np.log10(yy[0,start:stop-1].astype(float)+0.01)))
  #plotList[i].setLogMode(y  = True)

def change(param, changes):
    global chA, chB
    print("tree changes:")
    print p
    for param, change, data in changes:
        path = p.childPath(param)
        if path is not None:
            childName = '.'.join(path)
        else:
            childName = param.name()
        print('  parameter: %s'% childName)
        print('  change:    %s'% change)
        print('  data:      %s'% str(data))
        print('  ----------')
        if childName=='firstCh':
          print "data: ", data
          chA = p.param('firstCh').value()
          msg = "Ch%dCh%d" % (chA, chB)
          plotList[0].setTitle(msg)
        if childName=='secondCh':
          print "data: ", data
          chB = p.param('secondCh').value()
          msg = "Ch%dCh%d" % (chA, chB)
          plotList[0].setTitle(msg)
                    

p.param('Reset Histogram').sigActivated.connect(resetHist)
p.param('Save Histogram').sigActivated.connect(saveHist)
p.param('Save Figure').sigActivated.connect(saveFig)

p.sigTreeStateChanged.connect(change)
t = ParameterTree()
t.setParameters(p, showTop = False)
t.show()  


chA = p.param('firstCh').value()
chB = p.param('secondCh').value()
if True:
  win = pg.GraphicsWindow()
  win.resize(1600,600)
  win.setWindowTitle('Real Time Histogram')
  plotList = []
  for i in range(p.param('numPlots').value()):
    if i == 3:
      plt = win.addPlot(labels = {'left': 'log10(Counts)', 'bottom': 'time'}, title = "Ch%dCh%d" %(chA,chB))
      plotList.append(plt)
      win.nextRow()
    else:
      plt = win.addPlot(labels = {'left': 'log10(Counts)', 'bottom': 'time'}, title = "Ch%dCh%d" %(chA,chB))
      plotList.append(plt)
  win2 = pg.GraphicsWindow()
  win2.setWindowTitle('Singles')
  plt2 = win2.addPlot(labels = {'left': 'Counts'}, title = 'Singles')
  win.show()

###################

y = 0

def update():
    global p, cntr, buf, xx, yy
    if p.param('Pause Histogram').value() == False:
        measTime = p.param('Tacq').value()
        yy,xx = getXtalkHist(chA, chB, measTime, algorithm = p.param('algorithm').value())
        cntr += 1
    print "Count: ", cntr 
    chart = getChart(cntr, updateTime, 10)
    plotHist(xx,yy)
    plotChart(chart)

def cleanUp():
    print "Cleaning"
    buf.stop()

atexit.register(cleanUp)
    
timer.timeout.connect(update)
timer.start()
win.raise_()
#win.activateWindow()
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
        

	    


