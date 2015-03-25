# This version is designed to analyze the data as it is coming in.
import sys
import time
import os
import numpy as np
import matplotlib.pyplot as plt
import glob
import datetime
import subprocess

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
           
def isActive(pid):
  try:
    os.kill(pid, 0)  # Doesn't actually kill the process!  Just a way to check to see if it is active.  If not active, and exception is thrown that we catch.
    return True
  except:
    return False

def getPid():
  args = ['ps', 'ax']
  args2 = ['grep', 'encode_decode']
  p = subprocess.Popen(args, stdout = subprocess.PIPE)
  output = subprocess.check_output(args2, stdin = p.stdout)
  p.wait()
  outList = [int(s) for s in output.split() if s.isdigit()]
  return outList[0]

if __name__ == "__main__":

  if len(sys.argv)>2:
    dirnum = int(sys.argv[1])
    Tacq = float(sys.argv[2])
    pid = getPid()
  else:
    dirnum = 9
    Tacq = 1
    print "You forgot to include dirnum, and inttime, as input parameters"
    print "Goodbye"
    sys.exit()
  dataPath = '/hdd/2015_03_12/run%02d/'%dirnum
  format = '%Y_%m_%d'
#  dataPath = '/hdd/%s/run%d/'%(datetime.datetime.today().strftime(format),dirnum)

  fcoin = open(dataPath + 'coin_%d.txt'%dirnum, 'w')
  fsingle = open(dataPath + 'single_%d.txt'%dirnum, 'w')

  heraldChan = 0
  gate = 10e-9
  CoincidenceWindow = 10e-9
  thresh_low = 0
  thresh_high = 100 # changed by shane to try to reduce error.  Original value 100

  cnt = -1
  tlist = sorted(glob.glob(dataPath+'tag_*.bin'))
  clist = sorted(glob.glob(dataPath+'chan_*.bin'))
  tlist = tlist[0:-1] # Omit most recent file in case it is still being used by data program.  It will be looked at on next call to glob
  clist = clist[0:-1]
  serial_only_ttag_Running = isActive(pid)
  extraCheck = 0
  while extraCheck < 3:
    for (fTimes, fChans) in zip(tlist,clist):
      pixel_num = int(fChans.strip('.bin')[-6:])
      if pixel_num > cnt:
        cnt = pixel_num
        print pixel_num
        print fTimes, fChans
        print fTimes, fChans
        while True:
          try:
            single,coin = calcCoin(fTimes, fChans, thresh_low, thresh_high, heraldChan) # Try to get coin.  If can't, try again after 1s.  
            break
          except:
            time.sleep(3*Tacq)
        np.savetxt(sys.stdout, single,'%4d')
        print
        np.savetxt(sys.stdout, coin,'%4d')
        print
        np.savetxt(fcoin,coin, '%4d')
        np.savetxt(fsingle,single, '%4d')
        fcoin.write('# %d\n'%pixel_num)
      else:
        continue
    time.sleep(4*Tacq)
    tlist = sorted(glob.glob(dataPath+'tag_*.bin'))
    clist = sorted(glob.glob(dataPath+'chan_*.bin'))
    if extraCheck == 0:
      tlist = tlist[0:-1] #Omit the most recent file if data program still running to eliminate any race condition problems
      clist = clist[0:-1]
    if not serial_only_ttag_Running:
      extraCheck += 1
    serial_only_ttag_Running = isActive(pid)
  fcoin.close()
