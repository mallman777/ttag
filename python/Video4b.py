#test 
import sys
import time
import os
import atexit
import subprocess
import numpy as np

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType
import pyqtgraph.ptime as ptime
from widget_sn import StretchedLabel
app = QtGui.QApplication([])

sys.path.append('/mnt/odrive/HPD/ShanePyStuff/classes')
import ttag_wrap

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
Tacq = 2  # Measurement time in seconds

timer = QtCore.QTimer()
timer.setInterval(int(Tacq*1000)+10)

params = [
  {'name':'Tacq', 'type':'float','value':Tacq,'limits':(0,100)},
  {'name':'min', 'type':'int','value':0},
  {'name':'max', 'type':'int','value':1},
  {'name':'AutoExpose','type':'action', 'visible':True},
  {'name':'AutoExpose?','type':'bool', 'value':False},
  {'name':'Gate?','type':'bool', 'value':False},
  {'name':'Err stat?','type':'bool','value':True},
  {'name':'Efficiency?','type':'bool','value':True},
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

def autoExpose():
  global image
  max = image.max()
  p.param('max').setValue(max)
  #p['max'] = max
 
p.param('Set File Name').sigActivated.connect(setfilename)
p.param('Logdata').sigActivated.connect(startlog)
p.param('Stop Logging').sigActivated.connect(stoplog)
p.param('AutoExpose').sigActivated.connect(autoExpose)

def change(param, changes):
    global flatField, image
    #print("tree changes:")
    #print p
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
        if childName == 'Use Flatfield' and data == True:
          fname = p.param('Flat Field filename').value() 
          f = open(fname)
          comment = f.readline()  # Could check header for "Flat Field" using if:
          line = f.readline()
          t_exp = float(line.split(':')[1])
          rawData = np.fromfile(f,sep=' ')
          flatField = rawData/rawData.max()
        if childName == 'Use DarkField' and data == True:
          fname = p.param('Dark Field filename').value() 
          f = open(fname)
          comment = f.readline()  # Could check header for "Flat Field" using if:
          line = f.readline()
          t_exp = float(line.split(':')[1])
          rawData = np.fromfile(f,sep=' ')
          darkField = rawData/t_exp
          
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
  stats_window = StretchedLabel()
  stats_window.resize(300,60)
  stats_window.setText('Stats')
  stats_window.show()
  stats_window.raise_()

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
buf = ttag_wrap.openttag()
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
  image.tofile(f,sep=' ')  # numpy array save to text file method2
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
def update():
    global p,img,cnt,updateTime, fps, logdata, fptr, buf,darks, flatField, seq_count,plot1,plot2, dataPath, stats_window, image
    Tacq = p.param('Tacq').value()
    gate = p.param('Gate').value()
    CoincidenceWindow = p.param('CoincidenceWindow').value()  # Coincidence window based on observed delay between row and column pulses.
    heraldChan = 0
    if p['Gate?'] == True:
      x = buf.coincidences(Tacq, CoincidenceWindow, gate = gate, heraldChan = heraldChan)
    else:
      x = buf.coincidences(Tacq, CoincidenceWindow)
    y = buf.singles(Tacq)
    chart = getChart(x,y,cnt)
    if p['Efficiency?']:
        printEff(x,y)
    image = np.reshape(x[0:8,8::],(1,64))
    
    if False:
      if os.path.isfile(os.path.join(dataPath, 'Photon%05d_tags.bin'%cnt)):
        fTimes = os.path.join(dataPath, 'Photon%05d_tags.bin'%cnt)
        fChans = os.path.join(dataPath, 'Photon%05d_chans.bin'%cnt)
        image = np.reshape(getCoincidences(fTimes, fChans, gate, CoincidenceWindow, heraldChan), (1,-1))
      else:
        image = np.zeros(64)

    imageCorrected = image
        
    displayimage = np.reshape(imageCorrected,(8,8))[::-1,::-1].T
    
    if p['AutoExpose?'] == True:
      autoExpose()

    level=(p.param('min').value(), p.param('max').value() )
    img.setImage(displayimage,autoLevels=False,levels=level)
    now = ptime.time()
    fps2 = 1.0 / (now-updateTime)
    updateTime = now
    fps = fps * 0.9 + fps2 * 0.1
    maxidx = np.argmax(imageCorrected)
    #print 'maxidx',maxidx
    #print 'imageCorrected.shape',imageCorrected.shape
    maxrow = maxidx/8
    maxcol = maxidx%8
    p['Plot col']=maxcol + 1
    p['Plot row']=maxrow + 1
    err = (1.* imageCorrected[0,maxidx])/imageCorrected.sum()
    if p['Err stat?']:
    #if True:
        labelstr = 'pk cts: %6d\ntot cts:%6d\nerr: %.4f\nrow:%d\ncol:%d\n'%(imageCorrected[0,maxidx], imageCorrected.sum(),1-err, maxrow, maxcol)
    	stats_window.setText(labelstr)
        stats_window.show()
    else:
	stats_window.hide()
     
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
    cnt+=1

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
timer.timeout.connect(update)
timer.start()
win.raise_()
#win.activateWindow()
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


	    


