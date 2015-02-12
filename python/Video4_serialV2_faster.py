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

sys.path.append('/mnt/odrive/HPD/ShanePyStuff/classes')
import ttag

"""
darksFile = "../../../../../Cooldown140521/20140522_150355Row12345678Darks.txt"
flatFieldFile = "../../../../../Cooldown140521/20140522_150559Row12345678FlatField.txt"

darks = np.loadtxt(darksFile)
rawFlatField = np.loadtxt(flatFieldFile)
darks = darks[:,1:]  #Get rid of first column which is the bias Voltages
rawFlatField = rawFlatField[:,1:]
flatField = rawFlatField-darks
"""
# Experimental Parameters
Tacq = 10  # Measurement time in seconds

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
  fileName = QtGui.QFileDialog.getSaveFileName(None, 
     "Select of Type in Image Filename to Save", ".") ;
  print fileName
  p.param('filename').setValue(fileName)

def start():
  global dataPath, filepath
  dirCnt = 40 
  #dataPath = '/hdd/run41/'
  while True:
    dataPath = '/hdd/run%d/'%dirCnt
    try:  
      os.makedirs(dataPath)
      break
    except:
      dirCnt += 1
  filepath = dataPath
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


###################

#Run UQDinterface
# is this needed anymore? SN, May 17, 2014
#args = ['sudo', 'bash','launch.sh']
#f = open('test','w')
#process = subprocess.Popen(args,stdout=f)

#print "The process ID is:"
#print process.pid+1  # p.pid is the PID for the new shell.  p.pid is the PID for UQDinterface in the new shell
#print process.pid+2
#time.sleep(1)

#ttnumber = int(raw_input("Time tagger to open:"))
ttnumber = ttag.getfreebuffer()-1
print "ttnumber: ", ttnumber
buf = ttag.TTBuffer(ttnumber)  #Opens the buffer
buf.tagsAsTime = False
buf.start()
time.sleep(1)

print "Channels:", buf.channels
print "Resolution:", buf.resolution
print "Datapoints:", buf.datapoints
print "Buffer size:", buf.size()

ptr = 0

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

def getChart(x, y,cnt):
  chartSize = 100
  start = (cnt % chartSize) + 1
  if (not hasattr(getChart, "chart")):
    getChart.chart = np.empty([3, chartSize])
  for i in range(3):
    if i < 2:
      getChart.chart[i, cnt % chartSize] = y[i]
    else:
      getChart.chart[i, cnt % chartSize] = x[0,1]
  if start == chartSize:
    return getChart.chart
  else:
    return np.hstack([getChart.chart[:,start:], getChart.chart[:,:start]])

def printEff(x,y):
  print "Herald Singles: ", y[0]
  print "Signal Singles: ", y[1]
  print "Coincidences: ", x[0,1]
  efficiency_herald = x[0,1]/float(y[1])
  efficiency_signal = x[0,1]/float(y[0])
  efficiency_sum = x[0,1]/(0.5*(y[0] + y[1]))
  efficiency_geo = x[0,1]/((y[0]*y[1])**0.5)
  print "Efficiency_herald: ", efficiency_herald
  print "Efficiency_signal: ", efficiency_signal
  print "Efficiency_sum: ", efficiency_sum
  print "Efficiency_geo: ", efficiency_geo
  print "\n"

def getCoincidences(fTimes, fChans, gate, radius, heraldChan):
  coincidences = np.reshape(np.zeros(64), (8,-1))
  times = np.fromfile(fTimes, dtype = np.uint64)
  chans = np.fromfile(fChans, dtype = np.uint8)
  indices = np.arange(len(times))
  indices = indices[::-1]
  for idx in indices:
    if (chans[idx] == heraldChan):
      i = idx -1
      while (i >= 0) and (times[i] + gate >= times[idx]):
        coincidenceFound = False
        j = i - 1
        while (j >= 0):
          if (chans[i] != chans[j]) and (chans[j] != heraldChan) and (times[j] + radius >= times[i]):
            coincidenceFound = True
            coincidences[i,j] += 1
            coincidences[j,i] += 1
            j -= 1
          elif (not coincidenceFound and times[j] + radius < times[i]):
            coincidences[i,idx] += 1
            coincidences[idx,i] += 1
            break
          else:
            break
        i -= 1
  return coincidences*buf.resolution
            
cnt = 0
dataPath = "/hdd/"

import serial
serialport = serial.Serial('/dev/ttyUSB1',38400,timeout=0.1)

def waitforPC():
    print 'Waiting for msg from PC'
    msgin = ''
    while (msgin == ''):
        msgin = serialport.read(80);
	   #app.processEvents() # process events on the GUI
    #print 'msg from PC: %s' %msgin 
    return msgin
def sendtoPC(count):
    print 'Sending photon num: %d'%count
    serialport.write('%05d'%count)

def update():
    global p,img,cnt,updateTime, fps, logdata, fptr, buf,darks, flatField, seq_count,plot1,plot2, dataPath
    #  talk to PC and wait for data first
    to = []
    to.append(time.time())
    msgin = waitforPC()
    to.append(time.time())
    cnt = int(msgin)
    if cnt == -1:
      return
    app.processEvents()
    Tacq = p.param('Tacq').value()
    start = buf.datapoints
    time.sleep(Tacq)
    stop = buf.datapoints
    tup = buf[-(stop - start):]  # a tuple of chan tags, and time tags
    sendtoPC(cnt)
    to.append(time.time())
    #  try to process and plot data while PC is setting up next frame
    gate = p.param('Gate').value()
    CoincidenceWindow = p.param('CoincidenceWindow').value()  # Coincidence window based on observed delay between row and column pulses.
    heraldChan = 0
    fnameTags = 'tag_%06d.bin'%cnt
    fnameChans = 'chan_%06d.bin'%cnt
    fTags = open(filepath+fnameTags,'wb')
    fChans = open(filepath+fnameChans,'wb')
  
    chans = tup[0]  #Single byte unsigned integer
    tags = tup[1] #8 byte unsigned integer
    chans.tofile(fChans)
    tags.tofile(fTags)
    fChans.close()
    fTags.close()
    
    x = buf.coincidences(Tacq, CoincidenceWindow, gate = gate, heraldChan = heraldChan)
#    x = buf.coincidences(Tacq, CoincidenceWindow)
    y = buf.singles(Tacq)

    chart = getChart(x,y,cnt)
    printEff(x,y)
    image = np.reshape(x[0:8,8::],(1,64))
    imageCorrected = image    
    displayimage = np.reshape(imageCorrected,(8,8))[::-1,::-1].T

    level=(p.param('min').value(), p.param('max').value() )
    img.setImage(displayimage,autoLevels=False,levels=level)

    
    if p.param('Plot row').value()>0:
      row = p.param('Plot row').value()-1
      idx = np.arange(8) + row*8
#      curve1.setData(image[0,idx])
      curve1.setData(imageCorrected[0,idx]+0.1)
    else:
      curve1.setData(chart[0,:])
    plot1.setLogMode(x = False, y = p.param("LogScaleRow?").value())
      
    if p.param('Plot col').value()>0:
      col = p.param('Plot col').value()-1
      idx = np.arange(8)*8 + col 
      curve2.setData(imageCorrected[0,idx]+0.1)
    else:
      curve2.setData(chart[2,:])
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
    
    to.append(time.time())
    print np.diff(np.array(to))

def update2():
  global cnt
  while True:
    update() 
    if cnt < 0:
      print "calling cleanup"
      p.param('start').setOpts(visible=True)
      return

def cleanUp():
    #p.terminate()
    buf.stop()
    print "Cleaning"
    #for i in range(100):
     # ttag.deletebuffer(i)
#    os.kill(p.pid+2,signal.SIGKILL)
    #os.kill(p.pid+2,signal.SIGINT)
#    os.fsync(f)


atexit.register(cleanUp)
#timer.timeout.connect(update2)
#timer.start()
win.raise_()
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


	    


