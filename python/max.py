import numpy as np

#data70 = np.loadtxt('/hdd/run70/coin_70.txt')
data80 = np.loadtxt('/hdd/run80/coin_80.txt')
betterPeak = []
betterErr = []
ans = None
line = []
dataList = [data80]
def getErr(data):
  ans = []
  for pixel in range(64):
    offset = pixel*8
    row = pixel/8
    col = pixel % 8
    norm = data[offset:offset+8,:].sum()
    err = 1 - (1.*data[offset + row,col])/norm
    ans.append([err, data[offset + row, col]])
  return np.array(ans)

for dat in dataList:
  if ans == None:
    ans = getErr(dat)
    print ans.shape
  else:
    ans = np.hstack((ans,getErr(dat)))
"""  
  if data62[offset + row, col] > data38[offset + row, col]:
    betterPeak.append(37)
  else:
    betterPeak.append(38)
  if err62 > err38:
    betterErr.append(38)
  else:
    betterErr.append(62)
  if True: #betterErr[pixel] != betterPeak[pixel]:
    print  'Pixel %2d: %4d %4d %1.2f %1.2f %2d %2d'%(pixel, data62[offset + row, col], data38[offset + row, col], err62, err38, betterPeak[-1], betterErr[-1])
"""
print ans
print ans.shape
"""
betterPeak = np.array(betterPeak) 
betterErr = np.array(betterErr) 
print "betterPeak.mean: %f" % betterPeak.mean()
print "betterErr.mean: %f" % betterErr.mean()
"""
