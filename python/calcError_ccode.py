import sys,os
import numpy as np
import datetime
import matplotlib.pyplot as plt
import pickle

def getData(data): 
  rows = []
  fNum = range(data.shape[0])
  for f in fNum:
    pix = f % 64
    row = pix/8
    col = pix%8
    norm = data[f,:,:].sum()
    pk = data[f, row, col]
    nnerr = getNNErr(data[f],row,col)
    #print [norm, pk, nnerr]
    rowData = np.array([norm, pk, nnerr])
    rows.append(rowData)
  return np.array(rows)

def getNNErr(data, row, col):
  nnErr = 0
  if row == 7:
    pass
  else:
    nnErr = nnErr + data[row+1, col]
  if row == 0:
    pass
  else:
    nnErr = nnErr + data[row-1, col]
  if col == 7:
    pass
  else:
    nnErr = nnErr + data[row, col + 1]
  if col == 0:
    pass
  else:
    nnErr = nnErr + data[row, col - 1]
  return nnErr

if __name__=='__main__':
    pickFileName = sys.argv[0].strip('.py') + '.pickle'
    if os.path.isfile(pickFileName):
      pickleFile = open(pickFileName, 'r')
      path = pickle.load(pickleFile)
      pickleFile.close()
    else:
      path = '/hdd/'

    if len(sys.argv) == 1:
      from pyqtgraph.Qt import QtGui, QtCore
      app = QtGui.QApplication([])
      fileDirectory = QtGui.QFileDialog.getExistingDirectory(None, 
         "Select Directory", path)
      fileDirectory=str(fileDirectory).rstrip('/')
      runname = os.path.split(fileDirectory)[1]
      run = int(runname.strip('run'))
      dataPath = fileDirectory + '/'
      #print run, dataPath 
    else:
        run = int(sys.argv[1])
        format = '%Y_%m_%d'
        #dataPath = '/hdd/%s/run%d/'%(datetime.datetime.today().strftime(format),run)
        #dataPath = "/hdd/2015_02_25/run%02d/"%run

        dataPath = "/hdd/2015_03_12/run%02d/"%run

    pickleFile = open(pickFileName, 'w')
    pickle.dump(dataPath, pickleFile)
    pickleFile.close()


    fcoin = "coin_%d_ccode.txt"%run
    dataCoin = np.loadtxt(dataPath + fcoin)
    fsingle = "single_%d_ccode.txt"%run
    dataSingle = np.loadtxt(dataPath + fsingle)

    sh = dataCoin.shape
    dataCoin.shape=(sh[0]/8,8,8)
    dataSingle.shape=(sh[0]/8,8,8)

    ratios = []
    #rows = [sum, peak, nnerr]


    outCoin = getData(dataCoin)
    outSingle = getData(dataSingle)

    print outCoin[0]  
    print outSingle[0]  

    print "Coin mean: ", (outCoin[:,1]/outCoin[:,0]).mean()
    print "Singles mean: ", (outSingle[:,1]/outSingle[:,0]).mean()
    maxArg = np.argmax(outCoin[:,1])
    print "max Coin: ", outCoin[maxArg,1]
    fcErr = open(dataPath + 'coinError.txt', 'w')
    np.savetxt(fcErr, outCoin)
    fsErr = open(dataPath + 'singleError.txt', 'w')
    np.savetxt(fsErr, outSingle)
    plt.figure(1)
    plt.plot(outCoin[:,1]/outCoin[:,0])
    plt.title('Coincidences')
    plt.figure(2)
    plt.plot(outSingle[:,1]/outSingle[:,0])
    plt.title('Singles')
    plt.show(block = True)


    """
      np.savetxt(sys.stdout, dataSingle[pix,:,:], "%4d")
      print
      np.savetxt(sys.stdout, dataCoin[pix,:,:], "%4d")
      print
    """





