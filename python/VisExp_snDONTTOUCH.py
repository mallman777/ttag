#test 
import sys
import time
import os
#import atexit
#import subprocess
import numpy as np
import matplotlib.pyplot as plt
#sys.path.append('/mnt/odrive/HPD/ShanePyStuff/classes')
#import ttag
def calcCoin(fTimes, fChans, thresh_low, thresh_high, heraldChan):
    coin = np.zeros([8,8]).astype(int)
    single = np.zeros([8,8]).astype(int)
    bufRes = 156.25e-12
    numChans = 16
    #times = np.fromfile(fTimes, dtype = np.uint64)
    times = np.fromfile(fTimes, dtype = np.dtype('<u8'))
    chans = np.fromfile(fChans, dtype = np.uint8)
    do_histogram=False
    print 'Number of heraldChan',(chans==heraldChan).sum()
    #for chan in range(1,16):
    #    print 'chan %02d: %d'%(chan, (chans==chan).sum())
    times = times[::-1]
    chans = chans[::-1]
    print (times[0] - times[-1])*bufRes
    for chan in range(8,16):
        np_all = 0
        nm_all = 0
        herald_idx = np.where(chans==chan)[0]
        #print 'len(herald_idx)',len(herald_idx)
        for idx in herald_idx:
            start = idx-3;
            if start<0:
              start = 0
            stop = idx+4;

            dtplus = (times[idx]-times[idx:stop])
            goodplus = chans[idx:stop]==heraldChan
            dtminus = (times[start:idx]-times[idx])
            goodminus = chans[start:idx]==heraldChan

            row = chans[idx+1]
            if (times[idx]-times[idx+1])>50:
               # couldn't find row to match up with... must be row 0
               row = 0
                        
            col = chan-8    
            if False or row>7:
                print '-', np.hstack((-dtminus.astype(int),dtplus.astype(int)))
                print chans[start:stop]
                # Assume that it missed row0 and we are looking at a column
                row = 0
                
            single[row,col]=single[row,col]+1
            deltat = times[idx-1]-times[idx]
            #print deltat
            if deltat > thresh_low and deltat < thresh_high:
            	coin[row,col]=coin[row,col]+1

            if do_histogram:
                bins = np.arange(1,1000,10)
                #n,x = np.histogram(dtplus[goodplus],np.arange(1,50000,1000))
                n,x = np.histogram(dtplus,bins)
                nm,x = np.histogram(dtminus[goodminus],bins)
                np_all = np_all + n
                nm_all = nm_all + nm
        if do_histogram:
            plt.clf()
            plt.plot(x[:-1], np_all, '+', x[:-1],nm_all,'o')
            plt.title('chan: %d'%chan)
            plt.show()
        #raw_input('hit enter')
    #print np_all.sum(), nm_all.sum()
    return single,coin
    """
numpy.savetxt    herald_idx = np.where(chans==heraldChan)[0]
    for idx in herald_idx:
      start = idx;
      if start<0:
        start = 0
      stop = idx+100;
      dt = (times[idx]-times[start:stop])
      good = chans[idx:(idx+100)]==8
      if False:
      #if good.sum()>0:
        print dt
        print chans[start:stop]
        print dt[good]
      n,x = np.histogram(dt[good],np.arange(0,1e6,1e3))
      n_all = n_all + n
      if idx%100000 == 0:
          print idx, n_all
    print n_all.sum()
    return n_all 
    """

def getCoincidences(fTimes, fChans, f6bit, gate, radius, heraldChan):
  bufRes = 156.25e-12
  gate = int(gate/bufRes)
  radius = int(radius/bufRes)
  numChans = 16
  coincidences = np.zeros(16*16, dtype = np.uint64)
  times = np.fromfile(fTimes, dtype = np.uint64)
  chans = np.fromfile(fChans, dtype = np.uint8)
  indices = np.arange(len(times))
  indices = indices[::-1]
  sixBitNums = []
  for idx in indices:
    if (chans[idx] == heraldChan):
      coincidences[chans[idx]*(numChans+1)] += 1
      i = idx -1
      while (i >= 0) and (times[i] + gate >= times[idx]):
        coincidenceFound = False
        j = i - 1
        while (j >= 0):
          if (chans[i] != chans[j]) and (chans[j] != heraldChan) and (times[j] + radius >= times[i]):
            coincidenceFound = True
            coincidences[chans[i]*numChans + chans[j]] += 1
            coincidences[chans[j]*numChans + chans[i]] += 1
            if chans[i] < 8:
              sixBitNums.append(chans[i]*8 + (chans[j]-8))
            else:
              sixBitNums.append(chans[j]*8 + (chans[i]-8))
            j -= 1
          elif (not coincidenceFound and chans[i] != heraldChan and times[j] + radius < times[i]):
            coincidences[chans[i]*numChans + chans[idx]] += 1
            coincidences[chans[idx]*numChans + chans[i]] += 1
            if chans[i] < 8:
              sixBitNums.append(chans[i]*8 + (chans[idx]-8))
            else:
              sixBitNums.append(chans[idx]*8 + (chans[i]-8))
            break
          else:
            break
        i -= 1
  np.savetxt(f6bit, np.array(sixBitNums, dtype = np.uint8), fmt = '%d', )
  return np.reshape(coincidences, (16,-1))
            
dataPath = "/hdd/"
start = 0
stop = 64
if len(sys.argv)>1:
  dirnum = int(sys.argv[1])
  if len(sys.argv)>2:
    start = int(sys.argv[2])
    if len(sys.argv)>3:
      stop = int(sys.argv[3])
else:
  dirnum = 9
dataPath = '/hdd/run%d/'%dirnum

fcoin = open(dataPath + 'coin_%d.txt'%dirnum, 'w')

for pixel_num in range(start,stop):
  #pixel_num = 9  
  fTimes = dataPath + 'tag_%06d.bin'%pixel_num
  fChans = dataPath + 'chan_%06d.bin'%pixel_num
  f6bit = dataPath + '6bitNums_%06d.txt'%pixel_num
  heraldChan = 0
  gate = 10e-9
  CoincidenceWindow = 10e-9
#  image = np.reshape(getCoincidences(fTimes, fChans, gate, CoincidenceWindow, heraldChan), (1,-1))
#  image = getCoincidences(fTimes, fChans, f6bit, gate, CoincidenceWindow, heraldChan)
  thresh_low = 0
  thresh_high = 100
  single,coin = calcCoin(fTimes, fChans, thresh_low, thresh_high, heraldChan)
  print pixel_num
  f = sys.stdout
 # fcoin = dataPath + 'coin_%06d.bin'%pixel_num
  np.savetxt(f, single,'%4d')
  print
  np.savetxt(f, coin,'%4d')
#  coin = np.reshape(coin, (1,-1))
#  norm = np.sum(coin)
#  print "norm: %d"%norm
#  normedCoin = (1.*coin)/norm
#  errBool = normedCoin < np.max(normedCoin)
#  errs = normedCoin[errBool]
#  normedCoin = np.reshape(normedCoin, (8,-1))
  print
#  np.savetxt(f,normedCoin, '%4f')
  print
  np.savetxt(fcoin,coin, '%4f')
  fcoin.write('#\n')
#  np.savetxt(f,errs, '%4f')
#  coin.tofile(fcoin)
#  np.savetxt(fcoin, coin,'%4d')
#  raw_input('hit enter')
