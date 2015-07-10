# A template for writing pyqt guis. This template will run without changes.  
import sys
import time, os, atexit, datetime, serial
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType
import pyqtgraph.ptime as ptime
import pyqtgraph.exporters
import pyqtgraph.exporters.ImageExporter as IE


def setupTree():
  params = [
    {'name':'Update Time (s)', 'type':'float', 'value':1},
    {'name':'Sample Name', 'type':'int', 'value':1},
    {'name':'Counter', 'type':'int', 'value':0}
  ]
  p = Parameter.create(name = 'params', type = 'group', children = params)
  t = ParameterTree()
  t.setParameters(p, showTop = False)
  return t,p

def saveFig(): # Get pix map of window and save png
  dirName = "/home"
  fname = "sampleWindow.png"
  fname2 = "samplePlotWindow.png"
  dataPath = dirName + fname
  dataPath2 = dirName + fname2
  locObj = QtGui.QPixmap.grabWindow(glw.winId())
  locObj.save(dataPath, 'png')
  exporter = IE.ImageExporter(plt)
  exporter.export(dataPath2)

def change(param, changes):
  global updateTime
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
    if childName=='Update Time (s)':
      print "data: ", data
      updateTime = p.param('Update Time (s)').value()
      timer.setInterval(int(1.1*updateTime*1000))
    if childName=='Sample Name':
      print "data: ", data
      # do something
      pass

def setupWindow(t):
  global plt, win
  win = QtGui.QMainWindow()
  win.resize(1600,600)
  win.setWindowTitle('Window Title')
  glw = QtGui.QWidget()
  l = QtGui.QGridLayout()
  glw.setLayout(l)
  win.setCentralWidget(glw)
  pltWin = pg.GraphicsWindow()
  plt = pltWin.addPlot(labels = {'left': 'Y axis', 'bottom': 'X axis'}, title = "Plot of Y vs X")
  splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
  splitter.addWidget(t)
  splitter.addWidget(pltWin)
  l.addWidget(splitter)
  win.show()
  win.raise_()
  return plt

def fun1():
  # function1
  return None

def plotter(data):
  curve = plt.plot(pen=(200,200,200), symbolBrush = (0,255,0), symbolPen = 'w')
  curve.setData([1,2,3,4,5])

def cleanUp():
  # Need to do anything before the program ends?
  pass

cntr = 0
def update():
  global p, cntr, buf
  myData = fun1()
  plotter(myData)
  cntr += 1
  p.param('Counter').setValue(cntr)

if __name__ == '__main__':
  app = QtGui.QApplication([])

  t,p = setupTree()

  p.sigTreeStateChanged.connect(change)

  setupWindow(t)

  updateTime = p.param('Update Time (s)').value()
  timer = QtCore.QTimer()
  timer.setInterval(int(1.1*updateTime*1000))
  timer.timeout.connect(update)
  timer.start()

  atexit.register(cleanUp)

  import sys
  if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    QtGui.QApplication.instance().exec_()
        

	    


