import sys
import time
import os
import numpy as np
import matplotlib.pyplot as plt
import glob
import datetime
def calcCoin(fTimes, fChans, thresh_low, thresh_high, heraldChan):
    coin = np.zeros([8,8]).astype(int)
    single = np.zeros([8,8]).astype(int)
    bufRes = 156.25e-12
    numChans = 16
    times = np.fromfile(fTimes, dtype = np.uint64)
    #times = np.fromfile(fTimes, dtype = np.dtype('<u8'))
    chans = np.fromfile(fChans, dtype = np.uint8)
    if len(times)!=len(chans):
       truncate_len = min(len(times),len(chans))
       #print 'Warning... lengths are not the same',len(times)*8,len(times),len(chans)
       times = times[:truncate_len]
       chans = chans[:truncate_len]
    do_histogram=False
    print 'Number of heraldChan',(chans==heraldChan).sum()
    #for chan in range(1,16):
    #    print 'chan %02d: %d'%(chan, (chans==chan).sum())
    times = times[::-1]
    chans = chans[::-1]
    print 'Time window',(times[0] - times[-1])*bufRes
    for chan in range(8,16):
        np_all = 0
        nm_all = 0
        herald_idx = np.where(chans==chan)[0]
        #print 'len(herald_idx)',len(herald_idx)
        
        if len(herald_idx) == 0: #added the len(herald_idx)!=0 to handle case where no counts for column.        
          continue              #we are running into this case now and then since the backround is so low now.

        if herald_idx[-1] == len(times)-1:
          herald_idx = herald_idx[:-1]
        for idx in herald_idx:
            start = idx-3;
            if start<0:
              start = 0
            stop = idx+4;
            #print idx,stop, len(times), len(chans)

            dtplus = (times[idx]-times[idx:stop])
            goodplus = chans[idx:stop]==heraldChan
            dtminus = (times[start:idx]-times[idx])
            goodminus = chans[start:idx]==heraldChan
            #print idx, len(chans), len(times)
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
            if (deltat > thresh_low and deltat < thresh_high and chans[idx-1] == heraldChan): # last and condition added by shane to garuntee idx-1 belongs to a herald
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
           
if __name__ == "__main__":

#  dataPath = "/hdd/2015_02_13/"
  if len(sys.argv)>1:
    dirnum = int(sys.argv[1])
  else:
    dirnum = 9
  dataPath = '/hdd/2015_03_10/run%02d/'%dirnum
  format = '%Y_%m_%d'
#  dataPath = '/hdd/%s/run%d/'%(datetime.datetime.today().strftime(format),dirnum)

  #fcoin = open(dataPath + 'coin_%db.txt'%dirnum, 'w')
  #fsingle = open(dataPath + 'single_%db.txt'%dirnum, 'w')
  tlist = sorted(glob.glob(dataPath+'tag_*.bin'))
  clist = sorted(glob.glob(dataPath+'chan_*.bin'))
  tlist=tlist[1:]
  clist=clist[1:]
#  tlist = tlist[0]
#  clist = clist[0]
#  print tlist, clist
  for (fTimes, fChans) in zip(tlist,clist):
    heraldChan = 0
    gate = 10e-9
    CoincidenceWindow = 10e-9
    thresh_low = 0
    thresh_high = 100 # changed by shane to try to reduce error.  Original value 100
    #print fTimes, fChans
    single,coin = calcCoin(fTimes, fChans, thresh_low, thresh_high, heraldChan)
    pixel_num = int(fChans.strip('.bin')[-6:])
    print 'pixel',pixel_num
    #print fTimes, fChans
    f = sys.stdout
    np.savetxt(f, single,'%4d')
    print
    np.savetxt(f, coin,'%4d')
    print
    np.savetxt(fcoin,coin, '%4d')
    np.savetxt(fsingle,single, '%4d')
    fcoin.write('# %d\n'%pixel_num)
  #raw_input('hit enter')
  fcoin.close()
