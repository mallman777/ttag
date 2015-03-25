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
app = QtGui.QApplication([])

sys.path.append('/mnt/odrive/HPD/ShanePyStuff/classes')
import ttag

def getCoincidences(fTimes, fChans, gate, radius, heraldChan):
  bufRes = 156.25e-12
  gate = int(gate/bufRes)
  radius = int(radius/bufRes)
  numChans = 16
  coincidences = np.zeros(16*16, dtype = np.uint64)
  times = np.fromfile(fTimes, dtype = np.uint64)
  chans = np.fromfile(fChans, dtype = np.uint8)
  print len(times)
  print len(chans)
  print (times[-2] - times[-3])*bufRes
  print times[0:10]
  chan_idx = np.where(chans > 0)[0]
  print "len(chan_idx): %d"%(len(chan_idx))
  indices = np.arange(len(times))
  indices = indices[::-1]
  herald_idx = np.where(chans == heraldChan)[0]
#  for el in herald_idx:
#    dt = (times[el] - times[el-1])*bufRes
#    print dt
  for idx in indices:
    if (chans[idx] == heraldChan):
      coincidences[chans[idx]*(numChans+1)] += 1
      i = idx -1
      while (i >= 0) and (times[i] + gate >= times[idx]):
        coincidenceFound = False
        j = i - 1
        while (j >= 0):
          if (chans[i] != chans[j]) and (chans[j] != chans[idx]) and (times[j] + radius >= times[i]):
            coincidenceFound = True
            coincidences[chans[i]*numChans + chans[j]] += 1
            coincidences[chans[j]*numChans + chans[i]] += 1
            j -= 1
          elif (not coincidenceFound and (chans[i] != chans[idx]) and (times[j] + radius < times[i])):
            coincidences[chans[i]*numChans + chans[idx]] += 1
            coincidences[chans[idx]*numChans + chans[i]] += 1
            break
          else:
            break
        i -= 1
  return np.reshape(coincidences, (16,-1))
            
cnt = 2
dataPath = "/hdd/"
dataPath = '/hdd/run1/'
if True:
#if os.path.isfile(os.path.join(dataPath, 'Photon%05d_tags.bin'%cnt)):
#  fTimes = os.path.join(dataPath, 'Photon%05d_tags.bin'%cnt)
#  fChans = os.path.join(dataPath, 'Photon%05d_chans.bin'%cnt)

#  fTimes = os.path.join(dataPath, 'test_tags.bin')
#  fChans = os.path.join(dataPath, 'test_chans.bin')
  pixel_num = 0  
  fTimes = dataPath + 'tag_%06d.bin'%pixel_num
  fChans = dataPath + 'chan_%06d.bin'%pixel_num
  heraldChan = 0
  gate = 100e-9
  CoincidenceWindow = 100e-9
#  image = np.reshape(getCoincidences(fTimes, fChans, gate, CoincidenceWindow, heraldChan), (1,-1))
  image = getCoincidences(fTimes, fChans, gate, CoincidenceWindow, heraldChan)

print image




      
      




	    


