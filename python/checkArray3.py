import numpy as np
import os
import VisExp_sn_v2 as VE
import threading

def writeSingles(dataPath, rowSingles):
  f = open(dataPath + 'rowSingles.txt', 'a')
  #print "Saving singles to %s"%(dataPath + 'rowSingles.txt')
  np.savetxt(f, rowSingles, fmt = '%05d')
  f.close()

def detectorGood(dataPath, cnt, save_thread):
  if not hasattr(detectorGood, "cnt"):
    detectorGood.cnt = -1
  if  not hasattr(detectorGood, 'runningAvg'):
    detectorGood.runningAvg = np.zeros([1,8])
  if  not hasattr(detectorGood, 'result'):
    detectorGood.result = True
  if detectorGood.cnt != cnt:
    heraldChan = 0
    thresh_low = 0
    thresh_high = 100
    if cnt > 0: # Do one data point behind
      fTimes = dataPath + 'tag_%06d.bin'%(cnt-1)
      fChans = dataPath + 'chan_%06d.bin'%(cnt-1)
      try:
        singles, coins = VE.calcCoin(fTimes, fChans, thresh_low, thresh_high, heraldChan)
      except:
        print "calcCoin bombed out"
        detectorGood.result = False
        return False
      rowSingles = np.array([singles.sum(1)])
      write_thread = threading.Thread(None, target = writeSingles, args = (dataPath, rowSingles))
      write_thread.start()
      #writeSingles(dataPath, rowSingles)
      detectorGood.runningAvg = ((cnt-1)*detectorGood.runningAvg + 1.*rowSingles)/(cnt)
      print "Row Singles: ", rowSingles 
      print "Running Avg: ", detectorGood.runningAvg
      badRows = np.array([np.arange(8)])
      badBool = rowSingles < 0.05*detectorGood.runningAvg
      #print "badBool: %r"%badBool
      badRows = badRows[badBool]
      if len(badRows) == 0:
        detectorGood.result = True
        print "detectorGood.result:", detectorGood.result
        return True
      else:
        detectorGood.result = False
        print "detectorGood.result:", detectorGood.result
        return False
    else:
      return True
  else:
    return detectorGood.result
  detectorGood.cnt = cnt
    
