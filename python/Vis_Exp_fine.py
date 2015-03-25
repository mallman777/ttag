import sys
import time
import os
import numpy as np
import matplotlib.pyplot as plt
import glob
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
tlist = glob.glob(dataPath+'/tag*.bin')
clist = glob.glob(dataPath+'/chan*.bin')
#for pixel_num in range(start,stop):
  #pixel_num = 9  
#  fTimes = dataPath + 'tag_%06d.bin'%pixel_num
#  fChans = dataPath + 'chan_%06d.bin'%pixel_num
#  f6bit = dataPath + '6bitNums_%06d.txt'%pixel_num
for (fTimes, fChans) in zip(tlist,clist):
  heraldChan = 0
  gate = 10e-9
  CoincidenceWindow = 10e-9
#  image = np.reshape(getCoincidences(fTimes, fChans, gate, CoincidenceWindow, heraldChan), (1,-1))
#  image = getCoincidences(fTimes, fChans, f6bit, gate, CoincidenceWindow, heraldChan)
  thresh_low = 0
  thresh_high = 100
  single,coin = calcCoin(fTimes, fChans, thresh_low, thresh_high, heraldChan)
  #print pixel_num
  print fTimes, fChans
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
  np.savetxt(fcoin,coin, '%4d')
  fcoin.write('#\n')
#  np.savetxt(f,errs, '%4f')
#  coin.tofile(fcoin)
#  np.savetxt(fcoin, coin,'%4d')
#  raw_input('hit enter')
