import sys
import numpy as np
import datetime

run = int(sys.argv[1])
format = '%Y_%m_%d'
#dataPath = '/hdd/%s/run%d/'%(datetime.datetime.today().strftime(format),run)
dataPath = "/hdd/2015_03_09/run%02d/"%run
#dataPath = "/hdd/run%02d/"%run
fname = "coin_%d.txt"%run
data = np.loadtxt(dataPath + fname)

sh = data.shape
data.shape=(sh[0]/8,8,8)

pixels = range(64)
goodSettings = []
errors = []
pkList = []
maxSettings = []
errors2 = []
for pix in pixels:
  row = pix/8
  col = pix%8
  error_list = []
  max_list = []
  for page in range(data.shape[0]):
     pk = data[page,row,col]
     norm = data[page,:,:].sum()
     error = (norm-pk)/norm
     error_list.append(error)
     max_list.append(pk)
      
  error_list = np.array(error_list)
  minErrIdx = np.argmin(error_list)
  maxPkIdx = np.argmax(max_list)
  print pix, minErrIdx
  maxSettings.append(maxPkIdx)
  goodSettings.append(minErrIdx)
  errors.append(error_list[minErrIdx])
  errors2.append(error_list[maxPkIdx])
  pkList.append(data[minErrIdx,row,col])
goodSettings = np.array(goodSettings, dtype = np.uint64)
maxSettings = np.array(maxSettings, dtype = np.uint64)
#f = open(dataPath + 'GoodSettings.txt', 'w')
#goodSettings.tofile(f)
#f.close()

pkList = np.array(pkList)
errors = np.array(errors)
dataout = np.vstack((np.arange(64),goodSettings, maxSettings, errors, pkList, errors2))
f = open(dataPath+'GoodSettings_list.txt','w')
np.savetxt(f, dataout.T,'%d\t%d\t%d\t%1.2f\t%d\t%1.2f')
 
f.close()




