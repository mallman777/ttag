#test 
import sys
import time
import os
import atexit
import subprocess
import numpy as np
import random

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
Tacq = 1  # Measurement time in seconds
CoincidenceWindow = 5e-9  # Coincidence window based on observed delay between row and column pulses.
delays = np.zeros(16)

timer = QtCore.QTimer()
timer.setInterval(int(Tacq*1000)+10)

params = [
  {'name':'Tacq', 'type':'float','value':Tacq,'limits':(0,10)},
  {'name':'min', 'type':'int','value':0},
  {'name':'max', 'type':'int','value':1500},
  {'name':'Take Save Flat Field','type':'action','visible':True},
  {'name':'Import Flat Field File','type':'action','visible':True},
  {'name':'Flat Field filename','type':'str','value':''},
  {'name':'Use Flatfield','type':'bool','value':False},
  {'name':'Take Save Dark Field','type':'action','visible':True},
  {'name':'Import Dark Field File','type':'action','visible':True},
  {'name':'Dark Field filename','type':'str','value':''},
  {'name':'Use Darkfield','type':'bool','value':False},
  {'name':'filename','type':'str','value':''},
  {'name':'Set File Name','type':'action'},
  {'name':'Logdata','type':'action','visible':True},
  {'name':'Stop Logging','type':'action','visible':False},
  {'name':'Save Sequence','type':'bool','value':False},
  {'name':'Plot row','type':'int', 'value':0, 'limits':(0,8)},
  {'name':'Plot col','type':'int', 'value':0, 'limits':(0,8)},
]

p = Parameter.create(name='params', type='group', children=params)

#t.show()
def TakeSaveFlatField():
  fileName = QtGui.QFileDialog.getSaveFileName(None, 
     "Select or Type in Flat Field Filename", ".") ;
  tExposure = 1  # Exposure time for flat field in seconds
  print fileName, tExposure
  saveframe(fileName, "Flat Field", tExposure)  

def ImportFlatFieldFile():
  fileName = QtGui.QFileDialog.getOpenFileName(None, 
     "Select Flat Field Filename to Import", ".")
  p.param('Flat Field filename').setValue(fileName)

def TakeSaveDarkField():
  fileName = QtGui.QFileDialog.getSaveFileName(None, 
     "Select or Type in Dark Field Filename", ".") ;
  tExposure = 10  # Exposure time for dark field in seconds
  print fileName, tExposure
  saveframe(fileName, "Dark Field", tExposure)  

def ImportDarkFieldFile():
  fileName = QtGui.QFileDialog.getOpenFileName(None, 
     "Select Dark Field Filename to Import", ".")
  p.param('Dark Field filename').setValue(fileName)

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
 
p.param('Take Save Flat Field').sigActivated.connect(TakeSaveFlatField)
p.param('Import Flat Field File').sigActivated.connect(ImportFlatFieldFile)
p.param('Take Save Dark Field').sigActivated.connect(TakeSaveDarkField)
p.param('Import Dark Field File').sigActivated.connect(ImportDarkFieldFile)
p.param('Set File Name').sigActivated.connect(setfilename)
p.param('Logdata').sigActivated.connect(startlog)
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
  plot1.setLogMode(x = False, y = True)
  l2.nextRow()
  plot2 = l2.addPlot()
  curve2 = plot2.plot(pen=(200,200,200), symbolBrush = (0,255,0), symbolPen = 'w')
  plot2.setYRange(0.01, 1000000)
  plot2.setLogMode(x = False, y = True)
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

if False:  # For using real data from ttager
    ttnumber = ttag.getfreebuffer()-1
    print "ttnumber: ", ttnumber
    buf = ttag.TTBuffer(ttnumber)  #Opens the buffer
    buf.start()
    time.sleep(1)

if True:  # For using fake data, manually added to buffer
    bufNum = ttag.getfreebuffer()
    print "bufNum", bufNum
    bufSize = 100000000
    buf = ttag.TTBuffer(bufNum, create = True, datapoints = bufSize)
    buf.resolution = 156e-12
    buf.channels = 16

    res = buf.resolution
    rate = 4e-6
    dr = 50e-9
    delay = int(2e-9/res)
    tag = 0
    buf.add(random.randint(0,7), tag)
    buf.add(random.randint(8,15), tag)

    to = time.time()
    while (buf[-1][1] <= 1.5):
        #print buf[-1][1]
        tag += random.randint(int((rate-dr)/res), int((rate+dr)/res))
#        buf.add(3, tag + delay)
#        buf.add(8, tag)
        buf.add(random.randint(0,7), tag + delay)
        buf.add(random.randint(8,15), tag)
        tf = time.time()
    print "Time to fill buffer: ", tf-to
    print "Last few times: ", buf[-5:][1]

print "Channels:", buf.channels
print "Resolution:", buf.resolution
print "Datapoints:", buf.datapoints
print "Buffer size:", buf.size()

ptr = 0

#image = np.zeros(64)
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
runTime = 0
def update():
    global p,img, updateTime, fps, logdata, fptr, buf,darks, flatField, seq_count, plot1, plot2, cnt, runTime
    Tacq = p.param('Tacq').value()
    to = time.time()
#    x = buf.coincidences(Tacq, CoincidenceWindow)
    x = buf.coincidences(Tacq, CoincidenceWindow, delays)
    tf = time.time()
    runTime += tf - to
    cnt += 1
    meanRunTime = runTime/cnt
#    print "Mean Run Time: ", meanRunTime
    image = np.zeros(64)
    image = np.reshape(x[0:8,8::],(1,64))
#    print image
#    print "Total Counts: ", np.sum(image)
    if p.param('Use Darkfield').value():
      imageCorrected = image-darks[8,:]
    else:
      imageCorrected = image
    if p.param('Use Flatfield').value():
      imageCorrected = imageCorrected/flatField
    
    #displayimage = np.reshape(imageCorrected,(8,8))[::-1,:].T # This works
    displayimage = np.reshape(imageCorrected,(8,8))[::-1,::-1].T

    level=(p.param('min').value(), p.param('max').value() )
    img.setImage(displayimage,autoLevels=False,levels=level)
    now = ptime.time()
    fps2 = 1.0 / (now-updateTime)
    updateTime = now
    fps = fps * 0.9 + fps2 * 0.1
    if p.param('Plot row').value()>0:
      row = p.param('Plot row').value()-1
      idx = np.arange(8) + row*8
#      curve1.setData(image[0,idx])
#      curve1.setData(imageCorrected[0,idx]+0.001)
#      curve1.setData(np.log10(imageCorrected[0,idx]))
    if p.param('Plot col').value()>0:
      col = p.param('Plot col').value()-1
      idx = np.arange(8)*8 + col 
#      curve2.setData(imageCorrected[0,idx]+0.001)
#      curve2.setData(image[0,idx])
    #print logdata
    if logdata==True:
      print 'logging data'
      fptr.write('%f '%Tacq) 
      image.tofile(fptr,sep=' ')
      fptr.write('\n')
      fptr.flush() 
    #print "%0.1f fps" % fps

    if p.param('Save Sequence').value():
      print "saving image"
      fname = sequencepath + '/' + basename + '%05d.png'%seq_count
      img.save(fname) 
      seq_count = seq_count + 1

def cleanUp():
    #p.terminate()
    print "Cleaning"
    buf.stop()
    for i in range(100):
      ttag.deletebuffer(i)
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


	    


