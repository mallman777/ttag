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
    print (times[0] - times[-1])*bufRes
    for chan in range(8,16):
        np_all = 0
        nm_all = 0
        herald_idx = np.where(chans==chan)[0]
        #print 'len(herald_idx)',len(herald_idx)
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


def getCoincidences(fTimes, fChans, gate, radius, heraldChan):
  bufRes = 156.25e-12
  gate = int(gate/bufRes)
  radius = int(radius/bufRes)
  coin = np.zeros([8,8], dtype = np.uint64)
  times = np.fromfile(fTimes, dtype = np.uint64)
  chans = np.fromfile(fChans, dtype = np.uint8)
  #print "len(times), len(chans)", len(times), len(chans)
  for chan in range(8,16):
    colIdx = np.where(chans==chan)[0]
    for idx in colIdx:
      #print "chans[idx]: %d"%chans[idx]
      #print "few chans: ",chans[idx-3:idx+3]
      #print "few times: ",times[idx-3:idx+3]
      i = idx - 1
      while (i >= 0):# and (times[i] + radius >= times[idx]):
        if (times[i] + radius >= times[idx]) and (chans[idx] != chans[i]):
          coincidenceFound = True
          j = idx + 1
        while (j < len(times)) and (chans[j]==heraldChan) and (times[j] - gate <= times[idx]):
          "we have found a heralded row/col coincidence"
          if chans[i] < 8:
            row = chans[i]
            col = chans[idx] - 8
            #print "row, col:", row, col
            coin[row, col] += 1
            #print "%d, %d"%(i,j)
          j += 1
        i -= 1
  return coin
        
  """
  for idx in indices:
    if (chans[idx] == heraldChan):
      coincidences[chans[idx]*(numChans+1)] += 1
      i = idx -1
      while (i >= 0) and (times[i] + gate >= times[idx]):
        coincidenceFound = False
        j = i - 1
        while (j >= 0):
          if (chans[i] != chans[j]) and (chans[j] != chans[idx]) and (times[j] + radius >= times[i]):
            coincidenceFound = True
            coincidences[chans[i]*numChans + chans[j]] += 1
            coincidences[chans[j]*numChans + chans[i]] += 1
            j -= 1
          elif (not coincidenceFound and (chans[i] != chans[idx]) and (times[j] + radius < times[i])):
            coincidences[chans[i]*numChans + chans[idx]] += 1
            coincidences[chans[idx]*numChans + chans[i]] += 1
            break
          else:
            break
        i -= 1
  return np.reshape(coincidences, (16,-1))
  """
            
if __name__ == "__main__":

#  dataPath = "/hdd/2015_02_13/"
  if len(sys.argv)>1:
    dirnum = int(sys.argv[1])
  else:
    dirnum = 9
  dataPath = '/hdd/2015_02_15/run%02d/'%dirnum
  format = '%Y_%m_%d'
#  dataPath = '/hdd/%s/run%d/'%(datetime.datetime.today().strftime(format),dirnum)

  fcoin = open(dataPath + 'coin_%d_void.txt'%dirnum, 'w')
  tlist = sorted(glob.glob(dataPath+'tag_*.bin'))
  clist = sorted(glob.glob(dataPath+'chan_*.bin'))
#  tlist = tlist[0]
#  clist = clist[0]
#  print tlist, clist
  for (fTimes, fChans) in zip(tlist,clist):
    heraldChan = 0
    gate = 7e-9
    CoincidenceWindow = 5e-9
    thresh_low = 10
    thresh_high = 100
    print fTimes, fChans
    single_sn, coin_sn = calcCoin(fTimes, fChans, thresh_low, thresh_high, heraldChan)
    coin_sa = getCoincidences(fTimes, fChans, gate, CoincidenceWindow, heraldChan)
    pixel_num = int(fChans.strip('.bin')[-6:])
    print pixel_num
    print fTimes, fChans
    print
    np.savetxt(sys.stdout, coin_sn,'%4d')
    print
    np.savetxt(sys.stdout, coin_sa,'%4d')
    print
    np.savetxt(fcoin,coin_sn, '%4d')
    fcoin.write('# %d\n'%pixel_num)
    np.savetxt(fcoin,coin_sa, '%4d')
    fcoin.write('# %d\n'%pixel_num)
  #raw_input('hit enter')
  fcoin.close()




      
      




	    


