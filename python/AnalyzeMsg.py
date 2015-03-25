import sys
import time
import os
import numpy as np
import matplotlib.pyplot as plt
import glob
import datetime
import VisExp_msa2 as VE
import pickle
import argparse

def getSymbols(fTimes, fChans, gate, radius, heraldChan):
  bufRes = 156.25e-12
  gate = int(gate/bufRes)
  radius = int(radius/bufRes)
  coin = np.zeros([8,8], dtype = np.uint64)
  times = np.fromfile(fTimes, dtype = np.uint64)
  chans = np.fromfile(fChans, dtype = np.uint8)
  dtype = [('Pixel', int), ('index', int)] # create a dtype for a structured array so it can be sorted at the end
  goodClicks = []  #stores all the pixel number of the clicks that heralded in order they were recieved by the ttager.  Will be converted to a structured array at the end.
  for chan in range(8,16):
    colIdx = np.where(chans==chan)[0]
    for idx in colIdx:
      j = idx + 1
      while (j < len(times)) and (chans[j]==heraldChan) and (times[j] - gate <= times[idx]):
        i = idx - 1
        while (i >= 0):
          if (times[i] + radius >= times[idx]) and (chans[idx] != chans[i]) and chans[i] < 8:
            row = chans[i]
            col = chans[idx] % 8
            Pixel = row*8 + col
            tup = (Pixel, idx)
            goodClicks.append(tup)
            break
          elif (times[i] + radius <= times[idx]):
            row = heraldChan % 8 #works even if for some reason we had the rows plugged into channels 8-15 of the tagger
            col = chans[idx] % 8
            Pixel = row*8 + col
            tup = (Pixel, idx)
            goodClicks.append(tup)
            break
          i -= 1
        j += 1
  goodClicks = np.array(goodClicks, dtype = dtype)
  return np.sort(goodClicks, order = 'index')  #a structured array of tags.  Sorted
            
if __name__ == "__main__":
  pickFileName = sys.argv[0].strip('.py') + '.pickle'
  if os.path.isfile(pickFileName):
    pickleFile = open(pickFileName, 'r')
    path = pickle.load(pickleFile)
    pickleFile.close()
  else:
    path = '/hdd/'

  parser = argparse.ArgumentParser(description = 'Pass in params.')
  parser.add_argument('-r', type = str, help = 'run number')
  parser.add_argument('-d', type = str, help = 'run directory')
  args = parser.parse_args()
  if args.d and args.r:
    dataPath = args.d
    dirNum = args.r
  else:
    from pyqtgraph.Qt import QtGui, QtCore
    app = QtGui.QApplication([])
    fileDirectory = QtGui.QFileDialog.getExistingDirectory(None,
         "Select Directory", path)
    fileDirectory=str(fileDirectory).rstrip('/')
    runname = os.path.split(fileDirectory)[1]
    dirNum = int(runname.strip('run'))
    dataPath = fileDirectory + '/'    
   
  pickleFile = open(pickFileName, 'w')
  pickle.dump(dataPath, pickleFile)
  pickleFile.close()

  fSym = open(dataPath + 'symbols_%d.txt'%dirNum, 'w')
  tlist = sorted(glob.glob(dataPath+'tag_*.bin'))
  clist = sorted(glob.glob(dataPath+'chan_*.bin'))
  for (fTimes, fChans) in zip(tlist,clist):
    heraldChan = 0
    gate = 15e-9
    CoincidenceWindow = 7e-9
    print fTimes, fChans
    pixel_num = int(fChans.strip('.bin')[-6:])
    #print pixel_num
    symbols = getSymbols(fTimes, fChans, gate, CoincidenceWindow, heraldChan)
    pix = np.array([symbols['Pixel']], dtype = np.uint64)
    #coin = VE.getCoincidences(fTimes, fChans, gate, CoincidenceWindow, heraldChan)
    #np.savetxt(fSym, pix[:,:], fmt = '%d')
    np.savetxt(fSym, pix, fmt = '%d')
    #print pix[:,:n]
  fSym.close()




      
      




	    


