from VisExp_sn_v2 import calcCoin
import glob,os,sys,time,datetime
import numpy as np
if __name__ == "__main__":
  dirnum = 6
  dataPath = '/hdd/2015_03_10/run%02d/'%dirnum
  dirnum = 6
  dataPath = '/hdd/2015_03_13/run%02d/'%dirnum
  #format = '%Y_%m_%d'
  #dataPath = '/hdd/%s/run%d/'%(datetime.datetime.today().strftime(format),dirnum)

  tlist = sorted(glob.glob(dataPath+'tag_*.bin'))
  clist = sorted(glob.glob(dataPath+'chan_*.bin'))
  tlist=tlist[:]
  clist=clist[:]
  for (fTimes, fChans) in zip(tlist,clist):
    heraldChan = 0
    gate = 10e-9
    CoincidenceWindow = 10e-9
    thresh_low = 0
    thresh_high = 100 # changed by shane to try to reduce error.  Original value 100
    single,coin = calcCoin(fTimes, fChans, thresh_low, thresh_high, heraldChan)
    pixel_num = int(fChans.strip('.bin')[-6:])
    print 'pixel',pixel_num
    f = sys.stdout
    np.savetxt(f, single,'%4d')
    print
    np.savetxt(f, coin,'%4d')
    print

