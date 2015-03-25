def checkArray(rowSinglesFile):
  rowSingles = np.loadtxt(rowSinglesFile, dtype = np.uint64)
  if (rowSingles[-1,0] - rowSingles[0,0])*156.25e-12 > 1:
    numberofOneSecondChunks = int((rowSingles[-1,0] - rowSingles[0,0])*156.25e-12)

  return -1

def getRowCnts(chans, times):
  rowCnts = np.zeros(9, dtype = np.uint64)
  rowCnts[0] = times[0]
  for i in range(8):
    rowSingles = times[chans == i]
    rowCnts[i+1] = rowSingles.sum()
  return np.array([rowCnts])

def getFiles(dataPath):
  tlist = sorted(glob.glob(dataPath+'/tag_*.bin'))
  clist = sorted(glob.glob(dataPath+'/chan_*.bin'))
  return tlist[-1], clist[-1]

if __name__ == "__main__":
  dataPath = "/hdd/2015_02_13/run08/"
  while True:
    fTimes, fChans = getFiles(dataPath)
    times = np.fromfile(fTimes, dtype = np.uint64)
    chans = np.fromfile(fChans, dtype = np.uint8)
    if len(times) > 0 and len(times) == len(chans) and fTimes != lastFile:
      break

  fRowSingles = open(dataPath + 'rowSingles.txt', 'a')
  rowCnts = getRowCnts(chans, times)
  np.savetxt(fRowSingles, rowCnts)
  fRowSingles.close()


