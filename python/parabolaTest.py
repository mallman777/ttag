import sys
import numpy as np
import datetime
import matplotlib.pyplot as plt
run = int(sys.argv[1])
format = '%Y_%m_%d'
#dataPath = '/hdd/%s/run%d/'%(datetime.datetime.today().strftime(format),run)
dataPath = "/hdd/2015_02_22/run%02d/"%run
#dataPath = "/hdd/run%02d/"%run
fname = "coin_%d.txt"%run
data = np.loadtxt(dataPath + fname)

sh = data.shape
data.shape=(sh[0]/8,8,8)

pixels = range(1)
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
     error = (norm-pk)/norm
     error_list.append(error)
     max_list.append(pk)      
  error_list = np.array([error_list])
  print error_list.shape
  ferror = "Pix%dAllErr.txt"%pix
  plt.figure(1)
  plt.plot(error_list[0,:])
  plt.show()
  error_list = np.reshape(error_list, [48,-1])
  np.savetxt(dataPath + ferror, error_list) 






