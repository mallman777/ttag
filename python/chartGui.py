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

def setupTree():
  params = [
    {'name':'Update Time (s)', 'type':'float', 'value':1},
    {'name':'std', 'type':'float', 'value':0},
    {'name':'Save Figure', 'type':'action', 'visible':True}
  ]
  p = Parameter.create(name = 'params', type = 'group', children = params)
  t = ParameterTree()
  t.setParameters(p, showTop = False)
  return t,p

def saveFig():
  dirName = "/mnt/odrive/HPD/Cooldown150605/"
  fname = "test.png"
  dataPath = dirName + fname
  exporter = IE.ImageExporter(plt)
  exporter.export(dataPath)

def change(param, changes):
  global updateTime
  for param, change, data in changes:
    path = p.childPath(param)
    if path is not None:
      childName = '.'.join(path)
    else:
      childName = param.name()
    if childName != 'std':
      print('  parameter: %s'% childName)
      print('  change:    %s'% change)
      print('  data:      %s'% str(data))
      print('  ----------')
    if childName=='Update Time (s)':
      print "data: ", data
      updateTime = p.param('Update Time (s)').value()
      timer.setInterval(int(1.25*updateTime*1000))

def setupWindow(t):
  global chA, chB, plt, win
  win = QtGui.QMainWindow()
  win.resize(1600,600)
  win.setWindowTitle('Scroll Chart')
  glw = QtGui.QWidget()
  l = QtGui.QGridLayout()
  glw.setLayout(l)
  win.setCentralWidget(glw)
  pltWin = pg.GraphicsWindow()
  plt = pltWin.addPlot(labels = {'left': 'Counts'}, title = "Singles")
  splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
  splitter.addWidget(t)
  splitter.addWidget(pltWin)
  l.addWidget(splitter)
  win.show()
  win.raise_()
  return plt

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

def getSTD(chart):
  s = np.std(chart, axis = 1)
  p.param('std').setValue(s[1])


def plotChart(chart):
  if not hasattr(plotChart, 'firstRun'):
    plotChart.firstRun = True
    plotChart.curveList2 = []
  if plotChart.firstRun:
    for i in range(chart.shape[0]):
      plotChart.curveList2.append(plt.plot(pen=(200,200,200), symbolBrush = (0,255,0), symbolPen = 'w'))
    plotChart.firstRun = False
  for idx, c in enumerate(plotChart.curveList2):
    c.setData(chart[idx, :])

def startBuffer():
  bufNum = ttag.getfreebuffer()-1
  buf = ttag.TTBuffer(bufNum)
  buf.start()
  time.sleep(1)
  return buf

cntr = 0
def update():
  global p, cntr, buf
  chart = getChart(cntr, updateTime, 10)
  getSTD(chart)
  plotChart(chart)
  cntr += 1
  print "Count: ", cntr

def cleanUp():
  print "Cleaning"
  buf.stop()

if __name__ == '__main__':
  buf = startBuffer()

  app = QtGui.QApplication([])

  t,p = setupTree()

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
        

	    


