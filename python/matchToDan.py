import sys
import numpy as np

data = np.loadtxt('/hdd/2015_02_13/run10/GoodSettings_list.txt')

def trans(data, col):
  f = data[:,col]
  f.shape = (8,8)
  return np.reshape(f.T, (1,-1))[0]
out = sys.stdout
dataout = np.vstack((trans(data,1), trans(data,2)))

np.savetxt(out, dataout.T, '%d\t%d')

