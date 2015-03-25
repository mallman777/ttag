import atexit
import sys
import time
import os,shutil
import numpy as np

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType
import pyqtgraph.ptime as ptime
app = QtGui.QApplication([])
sys.path.append('/mnt/odrive/HPD/ShanePyStuff/classes')
import serial_SLM
import gen_find_nano_patterns as gp
pm = gp.phasemap

bobMirrorFileName = "/mnt/SLM/Dan/FindNanowiresSERICALPORT/NanowireScanNOSCRAMBLE/Bob/on.dat"

path = '/mnt/SLM/Dan/OptimizeSLM/Patterns/OrigSettings/'
#path = './test/'
PC = True
serial_SLM.setup(PC)
send = serial_SLM.send
wait = serial_SLM.wait

filenumber=99



def write(x,y):
  phase = gp.initial_phase_orig(257.-x, 257.-y, 512)
  gp.write2file(phase, pm, path, filenumber)
  shutil.copyfile(bobMirrorFileName, '/mnt/SLM/Dan/OptimizeSLM/Patterns/OrigSettings/SLM_100.dat')

params = [
  {'name':'x', 'type':'float','value':0,'limits':(0,511)},
  {'name':'y', 'type':'float','value':0, 'limits': (0,511)},
]

settingsFile = sys.argv[0].strip('.py') + '.settings'
p = Parameter.create(name='params', type='group', children=params)

try:
  arr = np.loadtxt(settingsFile)
  p['x'] = arr[0]
  p['y'] = arr[1]
except:
  pass
    
def change(param, changes):
    global flatField
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
        if childName=='x' or childName=='y':
          print p['x'], p['y']
          np.savetxt(settingsFile, np.array([p['x'], p['y']]))
          write(p['x'], p['y'])
          send(99)
          #msgin = wait()

p.sigTreeStateChanged.connect(change)
t = ParameterTree()
t.setParameters(p, showTop=False)
t.show()
t.raise_()
write(p['x'], p['y'])
send(filenumber)
#msgin = wait()
#print msgin
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


	    


