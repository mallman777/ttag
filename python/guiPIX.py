import atexit
import sys
import time
import os, shutil
import numpy as np
import os.path
import gen_find_nano_patterns as gp
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType
import pyqtgraph.ptime as ptime
app = QtGui.QApplication([])
sys.path.append('/mnt/odrive/HPD/ShanePyStuff/classes')
import serial_SLM

bobMirrorFileName = "/mnt/SLM/Dan/FindNanowiresSERICALPORT/NanowireScanNOSCRAMBLE/Bob/on.dat"
SLMpath = '/mnt/SLM/Dan/OptimizeSLM/Patterns/OrigSettings/'

PC = True
serial_SLM.setup(PC)
wait = serial_SLM.wait
send = serial_SLM.send

params = [
  {'name':'row', 'type':'int','value':0,'limits':(0,8)},
  {'name':'col', 'type':'int','value':0, 'limits': (0,8)},
  {'name':'filename','type':'str','value':''},
  {'name':'Get File Name','type':'action'},
]

settingsFile = sys.argv[0].strip('.py') + '.settings'
p = Parameter.create(name='params', type='group', children=params)


def getfilename():
  global interpolation
  fileName = QtGui.QFileDialog.getOpenFileName(None, 
     "Select interpolation filename", "/hdd/") ;
  p.param('filename').setValue(fileName)
  fileName = str(fileName)
  split = os.path.split(fileName)
  dataPathInterp=split[0]+'/'
  scanparams = np.loadtxt(dataPathInterp+'scanparameters.txt')
  (xstart,xstop,xstep,ystart,ystop,ystep)=scanparams
  interpolation = gp.interpolate2SLM(dataPathInterp, xstart, xstep, ystart, ystep)
  
getfilename()
p.param('Get File Name').sigActivated.connect(getfilename)


try:
  pix = np.loadtxt(settingsFile)
  p['row'] = pix / 8
  p['col'] = pix % 8
except:
  pass
    

def change(param, changes):
    global flatField, interpolation
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
        if childName=='row' or childName=='col':
          print p['row'], p['col']
          pix = 8*p['row'] + p['col']
          # retrieve interpolation data 
          (xo,yo)=interpolation[pix]
          # calculate phase pattern
          fft_phase = gp.initial_phase_orig(257-xo,257-yo, 512)
          gp.write2file(fft_phase, gp.phasemap, SLMpath, '99')
          shutil.copyfile(bobMirrorFileName, '/mnt/SLM/Dan/OptimizeSLM/Patterns/OrigSettings/SLM_100.dat')
          send(99)
          print 'From PC: ', wait()
          f = open(settingsFile, 'w')
          f.write('%d'%pix + '\n')
          f.flush()
          f.close()        
        
p.sigTreeStateChanged.connect(change)
t = ParameterTree()
t.setParameters(p, showTop=False)
t.show()
t.raise_()
pix = 8*p['row'] + p['col']

send(pix)
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


	    


