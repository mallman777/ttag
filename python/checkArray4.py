import numpy as np
firstTime = True
def writeSingles(dataPath, tup):
    chans, times = tup
    rowSingles = np.zeros(8, dtype = np.uint64)
    for i in range(8):
      rowSingles[i] = len(times[chans == i])
    rowSingles = np.array([rowSingles], dtype = np.uint64)
    f = open(dataPath + 'rowSingles.txt', 'a')
    np.savetxt(f, rowSingles, fmt = '%05d')
    f.close()
    return rowSingles

def detectorGood(dataPath,tup):
  global firstTime
  if not hasattr(detectorGood, 'oldSingles'):
    detectorGood.oldSingles = 1000*np.ones([1,8], dtype = np.uint64)
  if  not hasattr(detectorGood, 'result'):
    detectorGood.result = None

  #if detectorGood.cnt != cnt:
  if firstTime:
    #detectorGood.cnt = cnt
    rowSingles = writeSingles(dataPath, tup)
    badRows = np.array([np.arange(8)])
    badBool = rowSingles < 0.05*detectorGood.oldSingles
    badRows = badRows[badBool]
    detectorGood.oldSingles = rowSingles
    if len(badRows) == 0:
      detectorGood.result = True
      firstTime = True
    else:
      print rowSingles
      detectorGood.result = False
      firstTime = False
#  else:
#    firstTime = True
  return detectorGood.result
