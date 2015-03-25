import numpy as np
import matplotlib.pyplot as plt

def getRelErr(num,arr):
  arr = np.reshape(arr, (-1,1))
  if num != 0:
    numArr = arr[num]*np.ones(len(arr), dtype = np.uint8)
  else:
    numArr = np.zeros(len(arr), dtype = np.uint8)
  numArrBit = np.unpackbits(numArr)
  arrBit = np.unpackbits(arr)
  xorArr = np.bitwise_xor(numArrBit, arrBit)
  xorArr = np.reshape(xorArr, (len(arr),-1))
  outArr = np.zeros(len(arr), dtype = np.uint8)    
  for i in range(len(arr)):
    cnts = np.bincount(xorArr[i,:])
    if len(cnts) > 1:
      outArr[i] = cnts[1]
    else:
      outArr[i] = 0
  return np.reshape(outArr,(8,-1))  

def getBitErr(data,bitErrArr):
  out = np.zeros(7)
  for i in range(len(out)):
    bool = bitErrArr == i
    out[i] = data[bool].sum()
  return out

if __name__ == '__main__':
  dataPath = "/hdd/2015_02_28/run02/"
  data = np.loadtxt(dataPath + 'coin_2.txt', dtype = np.uint64)
  gcm = np.loadtxt('graycodematrix.txt', dtype = np.uint8)
  pixels = range(1)
  sh = data.shape
  data = np.reshape(data,(sh[0]/8,8,8))
  normDat = []
  for page in range(data.shape[0]):
    norm = data[page,:,:].sum()
    if norm != 0:
      nd = np.reshape(1.0*data[page,:,:]/norm,(1,64))
      normDat.append(nd)
    else:
      nd = np.reshape(1.0*data[page,:,:],(1,64))
      normDat.append(nd)
    pix = page % 64
  normDat = np.array(normDat)
  normDat = np.reshape(normDat, (40000,64))
  print np.shape(normDat)
  out = []
  for pix in range(64):
    idx = np.arange(pix,normDat.shape[0],64)
    out.append(np.mean(normDat[idx,:], axis = 0))
  out = np.array(out)
  for i in range(64):
    print out[i,i]
  np.savetxt('jointProb.txt', out,fmt = '%1.2f')
  plt.plot(out.T)
  plt.show()
