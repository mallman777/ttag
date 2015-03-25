import numpy as np

import glob

data40 = np.loadtxt('/hdd/run40/coin_40.txt')
data41 = np.loadtxt('/hdd/run41/coin_41.txt')

def getErr(data, row, col, offset):
  norm = data[offset:offset+8, :].sum()
  err = 1 - (1.*data[offset + row, col])/norm
  return err
betterPeak = []
betterErr = []
pixel_list = [1,4,5,9,13,19,26,28,42,43,47,51,54]
count = 0
for pixel in pixel_list: #range(64):
  offset = count*8
  count = count + 1
  row = pixel/8
  col = pixel % 8
  err40 = getErr(data40, row, col, offset) 
  err41 = getErr(data41, row, col, offset)
  if data40[offset + row, col] > data41[offset + row, col]:
    betterPeak.append(40)
  else:
    betterPeak.append(41)
  if err40 > err41:
    betterErr.append(41)
  else:
    betterErr.append(40)
  print  'Pixel %2d: %4d %4d %1.2f %1.2f %2d %2d'%(pixel, data40[offset + row, col], data41[offset + row, col], err40, err41, betterPeak[-1], betterErr[-1])

betterPeak = np.array(betterPeak) 
betterErr = np.array(betterErr) 
print "betterPeak.mean: %f" % betterPeak.mean()
print "betterErr.mean: %f" % betterErr.mean()
