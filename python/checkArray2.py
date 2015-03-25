import numpy as np

def writeSingles(dataPath, tup):
  chans, times = tup
  rowSingles = np.zeros(8, dtype = np.uint64)
  for i in range(8):
    rowSingles[i] = len(times[chans == i])
  rowSingles = np.array([rowSingles], dtype = np.uint64)
  f = open(dataPath + 'rowSingles.txt', 'a')
  #print "Saving singles to %s"%(dataPath + 'rowSingles.txt')
  np.savetxt(f, rowSingles, fmt = '%05d')
  f.close()

def detectorGood(dataPath, tup):
  writeSingles(dataPath, tup)
  oldSingles = np.loadtxt(dataPath + 'rowSingles.txt', dtype = np.uint64)
  meanSingles = np.mean(oldSingles, axis = 0)
  currTimes = tup[1]
  currChans = tup[0]
#  intTime = (currTimes[-1] - currTimes[0])*156.25e-12
  currentSingles = np.zeros(8, dtype = np.uint64)
  for i in range(8):
    #currentSingles[i] = int(len(currTimes[currChans == i])/intTime)
    currentSingles[i] = len(currTimes[currChans == i])
  badRows = np.arange(8)
  #print meanSingles
  #print currentSingles
  badBool = currentSingles < 0.1*meanSingles
  #print "badBool: %r"%badBool
  badRows = badRows[badBool]
  if len(badRows) == 0:
    return True
  else:
    return False
    
