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
  bitErrArr = []
  for page in range(data.shape[0]):
    norm = data[page,:,:].sum()
    if norm != 0:
      normDat = 1.0*data[page,:,:]/norm
    else:
      normDat = 1.0*data[page,:,:]
    pix = page % 64
    bitErrMat = getRelErr(pix,gcm)
    bitErrArr.append(getBitErr(normDat, bitErrMat))
  bitErrArr = np.array(bitErrArr)
  bitErrArr = np.reshape(bitErrArr, (64,625,-1), order = 'F') # properly shaped so that page 0 is all the 0 pixel errors, etc

  meanBitErr = []
  for page in range(np.shape(bitErrArr)[0]):
    meanBitErr.append(np.mean(bitErrArr[page,:,:], axis =0))
  meanBitErr = np.array(meanBitErr)
  print np.shape(meanBitErr)
  #print np.mean(meanBitErr, axis = 0)
  #plt.figure(1)
  #plt.plot(np.mean(meanBitErr, axis = 0))
  #plt.xlabel('Bit #')
  #plt.ylabel('Error Probability')
  #plt.savefig('BitErr.png', bbox_inches = 'tight', pad_inches = 1)
  #plt.show()
