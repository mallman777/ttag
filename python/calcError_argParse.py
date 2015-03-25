import sys,os
import numpy as np
import datetime
import matplotlib.pyplot as plt
import pickle
import argparse

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

    parser = argparse.ArgumentParser(description = 'Pass in params.')
    parser.add_argument('-r', type = int, help = 'Run Number')
    parser.add_argument('-d', type = str, help = 'Run Directory')
    args = parser.parse_args()

    if args.r and args.d:
      run  = args.r
      dataPath = args.d
    else:
      from pyqtgraph.Qt import QtGui, QtCore
      app = QtGui.QApplication([])
      fileDirectory = QtGui.QFileDialog.getExistingDirectory(None, 
         "Select Directory", path)
      fileDirectory=str(fileDirectory).rstrip('/')
      runname = os.path.split(fileDirectory)[1]
      run = int(runname.strip('run'))
      dataPath = fileDirectory + '/'
      #print run, dataPath 

    pickleFile = open(pickFileName, 'w')
    pickle.dump(dataPath, pickleFile)
    pickleFile.close()

    fcoin = "coin_%d.txt"%run
    dataCoin = np.loadtxt(dataPath + fcoin)
    fsingle = "single_%d.txt"%run
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
    plt.plot(outCoin[:,1]/outCoin[:,0], label = 'Success Prob')
    plt.title('Coincidences')
    plt.legend()
    plt.savefig(dataPath + 'CoinSuccessProb.png', pad_inches = 0.1)
    plt.figure(2)
    plt.plot(outCoin[:,2]/outCoin[:,0], label = 'NNErr')
    plt.plot((outCoin[:,0] - outCoin[:,1] - outCoin[:,2])/outCoin[:,0], label = 'Scatter')
    plt.title('Coincidences')
    plt.legend()
    plt.savefig(dataPath + 'CoinNNErrScatter.png', pad_inches = 0.1)
    plt.figure(3)
    plt.plot(outSingle[:,1]/outSingle[:,0], label = 'Success Prob')
    plt.title('Singles')
    plt.legend()
    plt.savefig(dataPath + 'SingleSuccessProb.png', pad_inches = 0.1)
    plt.figure(4)
    plt.plot(outSingle[:,2]/outSingle[:,0], label = 'NNErr')
    plt.plot((outSingle[:,0] -outSingle[:,1]- outSingle[:,2])/outSingle[:,0], label = 'Scatter')
    plt.title('Singles')
    plt.legend()
    plt.savefig(dataPath + 'SingleNNErrScatter.png', pad_inches = 0.1)
    plt.show(block = True)
    

    """
      np.savetxt(sys.stdout, dataSingle[pix,:,:], "%4d")
      print
      np.savetxt(sys.stdout, dataCoin[pix,:,:], "%4d")
      print
    """





