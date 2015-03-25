import sys
import numpy as np
import datetime

run = int(sys.argv[1])
format = '%Y_%m_%d'
#dataPath = '/hdd/%s/run%d/'%(datetime.datetime.today().strftime(format),run)
dataPath = "/hdd/2015_03_02/run%02d/"%run
#dataPath = "/hdd/run%02d/"%run
#fname = "coin_%d.txt"%run
fname = "single_%d.txt"%run
data = np.loadtxt(dataPath + fname)

sh = data.shape
data.shape=(sh[0]/8,8,8)

pixels = range(64)

# Containers for settings, errors, and peaks based on choosing the setting with minimum error
minErrSettings = []
errors = []
pkList = []

# Containers for settings, errors, and peaks based on choosing the setting with maximum peak
maxPkSettings = []
errors2 = []
pkList2 = []

for pix in pixels:
  row = pix / 8
  col = pix % 8
  error_list = []
  max_list = []
  for page in range(data.shape[0]):
     pk = data[page,row,col]
     norm = data[page,:,:].sum()
     if norm == 0:
       norm = 1
     error = (norm-pk)/norm
     error_list.append(error)
     max_list.append(pk)
      
  error_list = np.array(error_list)
  max_list = np.array(max_list)

  minErrIdx = np.argmin(error_list)
  maxPkIdx = np.argmax(max_list)

  minErrSettings.append(minErrIdx)
  errors.append(error_list[minErrIdx])
  pkList.append(max_list[minErrIdx])

  maxPkSettings.append(maxPkIdx)
  errors2.append(error_list[maxPkIdx])
  pkList2.append(max_list[maxPkIdx])

minErrSettings = np.array(minErrSettings, dtype = np.uint64)
errors = np.array(errors)
pkList = np.array(pkList)

maxPkSettings = np.array(maxPkSettings, dtype = np.uint64)
errors2 = np.array(errors2)
pkList2 = np.array(pkList2)

# Look at % diff in peak
diffPk = (pkList2 - pkList)/pkList

diffErr = np.zeros(len(errors))
errBool = errors > 0

diffErr[errBool] = (errors2[errBool]-errors[errBool])/errors[errBool]
diffErr[np.logical_not(errBool)] = errors2[np.logical_not(errBool)]-errors[np.logical_not(errBool)]
# Look at % diff in err
#if errors == 0:
  #diffErr = (errors2 - errors)
#else:
  #diffErr = (errors2 - errors)/errors

BestSettings = np.array(minErrSettings[:])
BestBool = diffPk > diffErr
BestSettings[BestBool] = maxPkSettings[BestBool] 

BestSettingsErr = np.array(errors[:])
BestSettingsErr[BestBool] = errors2[BestBool]

BestPk = np.array(pkList[:])
BestPk[BestBool] = pkList2[BestBool]

dataout = np.vstack((np.arange(64),minErrSettings, errors, pkList, maxPkSettings, errors2, pkList2, diffErr, diffPk, BestSettings, BestSettingsErr, BestPk))
f = open(dataPath+'GoodSettings_list.txt','w')
header = "Pix" + "\t" + "GSErr" + "\t" + "Err" + "\t" + "Pk" + "\t" + "GSPk" + "\t" + "Err" + "\t" + "Pk" + "\t" + "dErr" + "\t" + "dPk" + "\t" + "BstSet" + "\t" + "BstErr" + "\t" + "BstPk" + "\n" 
f.write(header) 
np.savetxt(f, dataout.T,'%d\t%d\t%1.2f\t%1.2f\t%d\t%1.2f\t%1.2f\t%1.2f\t%1.2f\t%d\t%1.2f\t%1.2f')
 
f.close()




