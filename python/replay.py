#test 
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

# Experimental Parameters
Tacq = 1  # Measurement time in seconds

timer = QtCore.QTimer()
#timer.setInterval(int(Tacq*1000)+10)
timer.setInterval(int(1000)+10)
timer.setSingleShot(True)

params = [
  {'name':'start','type':'action','visible':True},
  {'name':'Tacq', 'type':'float','value':Tacq,'limits':(0,100)},
  {'name':'min', 'type':'int','value':0},
  {'name':'max', 'type':'int','value':100},
  {'name':'filename','type':'str','value':''},
  {'name':'Set File Name','type':'action'},
  {'name':'Logdata','type':'action','visible':True},
  {'name':'Stop Logging','type':'action','visible':False},
  {'name':'Save Sequence','type':'bool','value':False},
  {'name':'Plot row','type':'int', 'value':0, 'limits':(0,8)},
  {'name':'LogScaleRow?','type':'bool', 'value':True},
  {'name':'Plot col','type':'int', 'value':0, 'limits':(0,8)},
  {'name':'LogScaleCol?','type':'bool', 'value':True},
  {'name':'Gate','type':'float', 'value':20e-9},
  {'name':'CoincidenceWindow','type':'float', 'value':10e-9},
]

p = Parameter.create(name='params', type='group', children=params)

#t.show()

def setfilename():
  fileName = QtGui.QFileDialog.getOpenFileName(None, 
     "Select of Type in Image Filename to Save", ".") ;
  print fileName
  p.param('filename').setValue(fileName)

def start():
  global buf
  if len(p['filename'])==0:
    setfilename()
  if len(p['filename'])==0:
    return 
  buf = np.loadtxt(str(p['filename']))
  update_thread = threading.Thread(None, update2)
  update_thread.start()
  p.param('start').setOpts(visible=False)

def startlog():
  global logdata,fptr
  if p.param('filename').value()=='':
    setfilename() 
  if p.param('filename').value()=='':
    logdata = False;
  else:
    logdata = True;
    fptr = open(p.param('filename').value(),'a')
    p.param('Logdata').setOpts(visible=False)
    #p.param('Logdata').setReadonly()
    p.param('Stop Logging').setOpts(visible=True)

def stoplog():
  global logdata,fptr
  fptr.close()
  p.param('Logdata').setOpts(visible=True)
  p.param('Stop Logging').setOpts(visible=False)
  #p.param('Stop Logging').setWriteable()
  logdata = False
 
p.param('Set File Name').sigActivated.connect(setfilename)
p.param('Logdata').sigActivated.connect(startlog)
p.param('start').sigActivated.connect(start)
p.param('Stop Logging').sigActivated.connect(stoplog)

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
        print('  parameter: %s'% childName)
        print('  change:    %s'% change)
        print('  data:      %s'% str(data))
        print('  ----------')
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
  win.setWindowTitle('window title')

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


updateTime = ptime.time()
fps = 0
logdata = False
seq_count = 0
sequencepath = './sequence'
basename = 'image'
def saveframe(filename, msg, t_exposure):
  x = buf.coincidences(t_exposure, CoincidenceWindow)
  image = x[0:8,8::]
  f = open(filename,'w')
  f.write('#%s\n'%msg)
  f.write('tExsposure: %f\n'%t_exposure)
  image.tofile(f,sep=' ')  # numpy array save to text file method
  f.write('\n')
  f.close()

            
cnt = 0

def update():
    global p,img,cnt,updateTime, fps, logdata, fptr, buf,darks, flatField, seq_count,plot1,plot2, dataPath
    Tacq = p.param('Tacq').value()
    gate = p.param('Gate').value()
    CoincidenceWindow = p.param('CoincidenceWindow').value()  # Coincidence window based on observed delay between row and column pulses.
    heraldChan = 0
    offset = cnt*8
    x = buf[offset:(offset+8),:]
    #print x
    #print x.shape
    if len(x)==0:
      cnt = -1
      return 
    image = np.reshape(x,(1,64))
    imageCorrected = image    
    displayimage = np.reshape(imageCorrected,(8,8))[::-1,::-1].T


    level=(p.param('min').value(), p.param('max').value() )
    img.setImage(displayimage,autoLevels=False,levels=level)

    if p.param('Plot row').value()>0:
      row = p.param('Plot row').value()-1
      idx = np.arange(8) + row*8
#      curve1.setData(image[0,idx])
      curve1.setData(imageCorrected[0,idx]+0.1)
    plot1.setLogMode(x = False, y = p.param("LogScaleRow?").value())
      
    if p.param('Plot col').value()>0:
      col = p.param('Plot col').value()-1
      idx = np.arange(8)*8 + col 
      curve2.setData(imageCorrected[0,idx]+0.1)
    plot2.setLogMode(x = False, y = p.param("LogScaleCol?").value())
      
    if logdata==True:
      print 'logging data'
      fptr.write('%f '%Tacq) 
      image.tofile(fptr,sep=' ')
      fptr.write('\n')
      fptr.flush() 

    if p.param('Save Sequence').value():
      print "saving image"
      fname = sequencepath + '/' + basename + '%05d.png'%seq_count
      img.save(fname) 
      seq_count = seq_count + 1
    cnt = cnt+1
    time.sleep(Tacq)

def update2():
  global cnt
  while True:
    update() 
    if cnt < 0:
      cnt = 0
      print "calling cleanup"
      p.param('start').setOpts(visible=True)
      return

def cleanUp():
    #p.terminate()
    print "Cleaning"
    print "but nothing to clean"


atexit.register(cleanUp)
#timer.timeout.connect(update2)
#timer.start()
win.raise_()
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


	    


