# Version 4 implements multiprocess to process histograms faster 
import sys
sys.path.append('/mnt/odrive/HPD/ShanePyStuff/classes')
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
import SIM900gpib, serial

def startBuffer():
  bufNum = ttag.getfreebuffer()-1
  buf = ttag.TTBuffer(bufNum)
  buf.start()
  time.sleep(1)
  return buf

def setupTree(startup):
  params = [
    {'name':'ChA', 'type':'int', 'value': startup['ChA']},
    {'name':'BiasV_ChA', 'type':'float', 'value': startup['BiasV_ChA']},
    {'name':'ChA Singles (cps)', 'type':'float', 'value': startup['ChA Singles (cps)']},
    {'name':'ChB', 'type':'int', 'value':startup['ChB']},
    {'name':'BiasV_ChB', 'type':'float', 'value':startup['BiasV_ChB']},
    {'name':'ChB Singles (cps)', 'type':'float', 'value': startup['ChB Singles (cps)']},
    {'name':'Min (s)', 'type':'float', 'value':startup['Min (s)']},
    {'name':'Max (s)', 'type':'float', 'value':startup['Max (s)']},
    {'name':'binSize', 'type':'int', 'value':startup['binSize']},
    {'name':'Update Time (s)', 'type':'float', 'value' :startup['Update Time (s)']},
    {'name':'Counter', 'type':'int', 'value':startup['Counter']},
    {'name':'algorithm', 'type':'str', 'value':startup['algorithm']},
    {'name':'Pause Histogram', 'type':'bool', 'value':startup['Pause Histogram']},
    {'name':'Reset Histogram', 'type':'action', 'visible':startup['Reset Histogram']},
    {'name':'Save Path', 'type':'str', 'value':startup['Save Path']},
    {'name':'Save Figure', 'type':'action', 'visible':startup['Save Figure']},
    {'name':'Save Data', 'type':'action', 'visible':startup['Save Data']}
  ]
  p = Parameter.create(name = 'params', type = 'group', children = params)
  t = ParameterTree()
  t.setParameters(p, showTop = False)
  return t,p

def change(param, changes):
  global chA, chB, updateTime
  for param, change, data in changes:
    path = p.childPath(param)
    if path is not None:
      childName = '.'.join(path)
    else:
      childName = param.name()
    if childName != 'Counter':
      print('  parameter: %s'% childName)
      print('  change:    %s'% change)
      print('  data:      %s'% str(data))
      print('  ----------')
    if childName=='ChA':
      print "data: ", data
      chA = p.param('ChA').value()
      msg = "Ch%dCh%d" % (chA, chB)
      plt.setTitle(msg)
    if childName=='ChB':
      print "data: ", data
      chB = p.param('ChB').value()
      msg = "Ch%dCh%d" % (chA, chB)
      plt.setTitle(msg)
    if childName=='Update Time (s)':
      print "data: ", data
      updateTime = p.param('Update Time (s)').value()
      timer.setInterval(int(1.25*updateTime*1000))
    if childName=='BiasV_ChA':
      print "data: ", data
      V = p.param('BiasV_ChA').value()
      ch = p.param('ChA').value()
      setBias(V,ch)            
    if childName=='BiasV_ChB':
      print "data: ", data
      V = p.param('BiasV_ChB').value()
      ch = p.param('ChB').value()
      setBias(V,ch)            

def setupWindow(t):
  global chA, chB, plt, win, l, glw, splitter
  win = QtGui.QMainWindow()
  win.resize(1600,600)
  win.setWindowTitle('Real Time Histogram')
  glw = QtGui.QWidget()
  l = QtGui.QGridLayout()
  glw.setLayout(l)
  win.setCentralWidget(glw)
  pltWin = pg.GraphicsWindow()
  plt = pltWin.addPlot(labels = {'left': 'log10(Counts)', 'bottom': 'time'}, title = "Ch%dCh%d" %(chA,chB))
  splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
  splitter.addWidget(t)
  splitter.addWidget(pltWin)
  l.addWidget(splitter)
  win.show()
  win.raise_()
  return plt

def setBias(V,ch):
  outmsg = 'VOLT %f' %V
  sim.conn(ch+1)
  sim.write('OPON')
  sim.write(outmsg)
  sim.write('xyz')
  time.sleep(0.5)

def saveFig():
  global timestamp
  d = datetime.datetime.now()
  timestamp = d.strftime('%Y%m%d_%H%M%S')
  dirName = p.param('Save Path').value()
  msg = "Ch%dCh%d" % (p.param('ChA').value(), p.param('ChB').value())
  fname = "%s_%s_FW.png" % (timestamp, msg)
  dataPath1 = dirName + fname
  locObj = QtGui.QPixmap.grabWindow(glw.winId())
  locObj.save(dataPath1, 'png')
  fname2 = "%s_%s.png" % (timestamp, msg)
  dataPath2 = dirName + fname2
  exporter = IE.ImageExporter(plt)
  exporter.export(dataPath2)

def saveData():
  dirName = p.param('Save Path').value()
  msg = "Ch%dCh%d" % (p.param('ChA').value(), p.param('ChB').value())
  fname = "%s_%s.bin" % (timestamp, msg)
  fnameLog = "%s_%s.log" % (timestamp, msg)
  dataPath1 = dirName + fname
  dataPath2 = dirName + fnameLog
  f = open(dataPath1, 'ab')
  x.tofile(f)
  y.tofile(f)
  f.flush()
  f.close()
  fLog = open(dataPath2, 'w')
  fLog.write('# test\n')
  fLog.flush()
  fLog.close()

def resetHist():
  global y, cntr
  y = 0
  cntr = 0

  
def getXtalkHist(ch1, ch2, time, window = 200e-9, algorithm = 'c'): #For histogramming cross correlations between different channels like the HH does.
  global buf, x, y
  buf.tagsAsTime = False
  chans, times = buf(time)
  ch1Tags, ch2Tags = (times[chans == ch1], times[chans == ch2])
  p.param('ChA Singles (cps)').setValue(len(ch1Tags)/time)
  p.param('ChB Singles (cps)').setValue(len(ch2Tags)/time)
  histMin = -window/buf.resolution
  histMax = window/buf.resolution
  myFun = functionLib.fun()
  ynew, x = myFun.getHist(ch1Tags, ch2Tags, np.array([histMin, histMax], dtype = np.int64), algorithm = algorithm)
  y += ynew
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
    
def plotHist(xx,yy):
  #global curve
  (xo, xf) = (int(p.param('Min (s)').value()/buf.resolution), int(p.param('Max (s)').value()/buf.resolution))
  start = findNear(xx, xo)
  stop = findNear(xx, xf)
  if not hasattr(plotHist, 'firstRun'):
    plotHist.firstRun = True
    plotHist.oldCurve = None
  curve = pg.PlotCurveItem(xx[start:stop]*buf.resolution, np.log10(yy[0,start:stop-1].astype(float)+0.01), stepMode = True, fillLevel = 0, brush = (0,0,255,80))
  if plotHist.firstRun:
    plt.addItem(curve)
    plotHist.firstRun = False
  else:
    plt.removeItem(plotHist.oldCurve)
    plt.addItem(curve)
  plotHist.oldCurve = curve
  plt.setXRange(p.param('Min (s)').value(), p.param('Max (s)').value())
  plt.setYRange(0, np.max(np.log10(yy[0,start:stop-1].astype(float)+0.01)))
  #plt.setLogMode(y  = True)

y = 0
cntr = 0
def update():
  global p, cntr, buf, xx, yy
  if p.param('Pause Histogram').value() == False:
    yy,xx = getXtalkHist(chA, chB, updateTime, algorithm = p.param('algorithm').value())
    cntr += 1
    p.param('Counter').setValue(cntr)
  plotHist(xx,yy)

def cleanUp():
  print "Cleaning"
  buf.stop()

if __name__ == '__main__':
  config = '../../../../config.ini'
  c = configParser.ConfigParser()
  options = c.parse_config(config)
  dataLogPath = options['networkData&LogPath']
  port = serial.Serial('/dev/ttyUSB0', 9600, timeout  = 0.05)
  sim = SIM900gpib.dev(4,port)

  buf = startBuffer()

  app = QtGui.QApplication([])

  startup = {'ChA': 1, 'BiasV_ChA': 0, 'ChA Singles (cps)': 0, 'ChB': 2, 'BiasV_ChB': 0,'ChB Singles (cps)': 0, 'Min (s)': -100e-9, 'Max (s)': 100e-9, 'binSize': 1, 'Update Time (s)': 0.5,
              'Counter': 0, 'algorithm': 'c', 'Pause Histogram': True, 'Reset Histogram': True, 'Save Path': dataLogPath, 'Save Figure': True, 'Save Data': True}
  t,p = setupTree(startup)
  chA = p.param('ChA').value()
  chB = p.param('ChB').value()
  
  p.param('Reset Histogram').sigActivated.connect(resetHist)
  p.param('Save Figure').sigActivated.connect(saveFig)
  p.param('Save Data').sigActivated.connect(saveData)
  p.sigTreeStateChanged.connect(change)

  setupWindow(t)

  updateTime = p.param('Update Time (s)').value()
  timer = QtCore.QTimer()
  timer.setInterval(int(1.25*updateTime*1000))
  timer.timeout.connect(update)
  timer.start()

  atexit.register(cleanUp)

  import sys
  if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    QtGui.QApplication.instance().exec_()
        

	    


