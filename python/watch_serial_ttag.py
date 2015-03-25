import sys
import time
import os
import atexit
import subprocess
import numpy as np
import threading
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType
import pyqtgraph.ptime as ptime
app = QtGui.QApplication([])
import VisExp_sn_v2 as VE
import glob

# Experimental Parameters
Tacq = 1  # Measurement time in seconds

timer = QtCore.QTimer()
#timer.setInterval(int(Tacq*1000)+10)
timer.setInterval(int(1000))
timer.setSingleShot(True)

params = [
  {'name':'start','type':'action','visible':True},
  {'name':'stop','type':'action','visible':False},
  {'name':'Tacq', 'type':'float','value':Tacq,'limits':(0,100)},
  {'name':'min', 'type':'int','value':0},
  {'name':'max', 'type':'int','value':100},
  {'name':'dirname','type':'str','value':''},
  {'name':'Set Dir Name','type':'action'},
  {'name':'Plot row','type':'int', 'value':0, 'limits':(0,8)},
  {'name':'LogScaleRow?','type':'bool', 'value':True},
  {'name':'Plot col','type':'int', 'value':0, 'limits':(0,8)},
  {'name':'LogScaleCol?','type':'bool', 'value':True},
  {'name':'Gate','type':'float', 'value':20e-9},
  {'name':'CoincidenceWindow','type':'float', 'value':10e-9},
]

p = Parameter.create(name='params', type='group', children=params)

#t.show()

def setdirname():
  dir = QtGui.QFileDialog.getExistingDirectory(None, 
     "Select Directory", "/hdd/") ;
  print dir
  p.param('dirname').setValue(dir)

def start():
  global dataPath, cnt, lastFile,timer
  if len(p['dirname'])==0:
    setdirname()
  if len(p['dirname'])==0:
    return
  dataPath = str(p['dirname']) 
  p.param('start').setOpts(visible=False)
  p.param('stop').setOpts(visible=True)
  cnt = 0
  lastFile = ''  
#  update_thread = threading.Thread(None, update2)
#  update_thread.start()
  #timer.start()
  update2()

def stop():
  global cnt,timer
  timer.stop()
  p.param('stop').setOpts(visible=False)
  p.param('start').setOpts(visible=True)

  cnt = -1
 
p.param('Set Dir Name').sigActivated.connect(setdirname)
p.param('start').sigActivated.connect(start)
p.param('stop').sigActivated.connect(stop)

def change(param, changes):
    global flatField
    print("tree changes:")
    print p
    for param, change, data in changes:
        path = p.childPath(param)
        if path is not None:
            childName = '.'.join(path)
        else:
            childName = param.name()
        #print('  parameter: %s'% childName)
        #print('  change:    %s'% change)
        #print('  data:      %s'% str(data))
        #print('  ----------')
        if childName=='Tacq':
          print "data: ", data
          timer.stop()
          timer.setInterval(int(data*1000)+10)
          Tacq = data
          timer.start()
        
p.sigTreeStateChanged.connect(change)
t = ParameterTree()
t.setParameters(p, showTop=False)

###############

if True:
  win = QtGui.QMainWindow()
  win.resize(1600,600)
  win.setWindowTitle(sys.argv[0])

  glw = QtGui.QWidget()
  #glw = pg.GraphicsLayoutWidget()
  l = QtGui.QGridLayout()
  glw.setLayout(l)

  win.setCentralWidget(glw)
  #view = glw.addViewBox()
  v = pg.GraphicsView()
  view = pg.ViewBox()
  view.setAspectLocked(True)
  v.setCentralItem(view)
  img = pg.ImageItem(border='y')
  view.addItem(img)
  
  v2 = pg.GraphicsView()
  l2 = pg.GraphicsLayout()
  v2.setCentralItem(l2) 
  plot1 = l2.addPlot()
  curve1 = plot1.plot(pen=(200,200,200), symbolBrush = (0,255,0), symbolPen = 'w')
  print plot1
  plot1.setTitle(title = 'label')
#  plot1.setYRange(0.01, 1000000)
  plot1.setLogMode(x = False, y = p.param("LogScaleRow?").value())
  l2.nextRow()
  plot2 = l2.addPlot()
  curve2 = plot2.plot(pen=(200,200,200), symbolBrush = (0,255,0), symbolPen = 'w')
  plot2.setYRange(0.01, 1000000)
  plot2.setLogMode(x = False, y = p.param("LogScaleCol?").value())
  l.addWidget(t,0,0)
  l.addWidget(v,0,1)
  l.addWidget(v2,0,2)
  win.show()

cnt = 0

def getFiles(dataPath):
  tlist = sorted(glob.glob(dataPath+'/tag_*.bin'))
  clist = sorted(glob.glob(dataPath+'/chan_*.bin'))
  return tlist[-1], clist[-1]  

def update():
    global p,img,cnt, logdata, fptr, buf,darks, plot1,plot2, dataPath, lastFile
    Tacq = p.param('Tacq').value()
    gate = p.param('Gate').value()
    CoincidenceWindow = p.param('CoincidenceWindow').value()  # Coincidence window based on observed delay between row and column pulses.
    heraldChan = 0
    offset = cnt*8
    thresh_low = 0
    thresh_high = 100
    print "Waiting for File"
    while True:
      fTimes, fChans = getFiles(dataPath)
      times = np.fromfile(fTimes, dtype = np.uint64)
      chans = np.fromfile(fChans, dtype = np.uint8)
      if len(times) > 0 and len(times) == len(chans) and fTimes != lastFile:
        break
    if cnt < 0:
      return
    print cnt, lastFile, fTimes, fChans, len(times),len(chans)
    singles, coins = VE.calcCoin(fTimes, fChans, thresh_low, thresh_high, heraldChan)
    lastFile = fTimes
    image = np.reshape(coins,(1,64))
    imageCorrected = image    
    displayimage = np.reshape(imageCorrected,(8,8))[::-1,::-1].T

    level=(p.param('min').value(), p.param('max').value() )
    img.setImage(displayimage,autoLevels=False,levels=level)
    plot1.setTitle('%s'%lastFile)

    if p.param('Plot row').value()>0:
      row = p.param('Plot row').value()-1
      idx = np.arange(8) + row*8
      curve1.setData(imageCorrected[0,idx]+0.1)
    plot1.setLogMode(x = False, y = p.param("LogScaleRow?").value())
      
    if p.param('Plot col').value()>0:
      col = p.param('Plot col').value()-1
      idx = np.arange(8)*8 + col 
      curve2.setData(imageCorrected[0,idx]+0.1)
    plot2.setLogMode(x = False, y = p.param("LogScaleCol?").value())
      
    cnt += 1
    app.processEvents()
    time.sleep(Tacq)
    app.processEvents()
    print 'finished update'

def update2():
  global cnt
  while True:
    update() 
    if cnt < 0:
      print "calling cleanup"
      p.param('stop').setOpts(visible=False)
      p.param('start').setOpts(visible=True)
      return

def cleanUp():
    #p.terminate()
    print "Cleaning"
    print "but nothing to clean"


atexit.register(cleanUp)
timer.timeout.connect(update)
#timer.start()
win.raise_()
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


	    


