import time
import numpy as np
import ttag_wrap
import gen_find_nano_patterns as gp
import serial_SLM
import atexit
import os,sys,threading,shutil
from enigma_daq import createDatafolder, tags2file, write2file
import pickle

#dataPathInterp = '/hdd/2015_03_11/run24/'

dataPathInterp = '/hdd/2015_03_12/run27/'
SLMpath = '/mnt/SLM/Dan/OptimizeSLM/Patterns/OrigSettings/'
logtags = True
PC = True
serial_SLM.setup(PC)
wait = serial_SLM.wait
send = serial_SLM.send

pickFileName = sys.argv[0].strip('.py') + '.pickle'
if os.path.isfile(pickFileName):
  pickleFile = open(pickFileName, 'r')
  path = pickle.load(pickleFile)
  pickleFile.close()
else:
  path = '/hdd/'


if __name__=='__main__':
    if len(sys.argv)>3:
      if len(sys.argv)==7:
        offset = 0
        Tacq =1
      else:
        offset = 1
        Tacq = float(sys.argv[1])

      xstart=int(sys.argv[offset+1])
      xstop = int(sys.argv[offset+2])
      xstep = int(sys.argv[offset+3])
      ystart = int(sys.argv[offset+4])
      ystop = int(sys.argv[offset+5])
      ystep = int(sys.argv[offset+6])
      SCAN = True
    elif len(sys.argv)==2:
      Tacq = float(sys.argv[1])
      # Need path of the interpolation file
      #dataPathInterp = '/hdd/2015_03_12/run%/'
      from pyqtgraph.Qt import QtGui, QtCore
      app = QtGui.QApplication([])
      fileDirectory = QtGui.QFileDialog.getExistingDirectory(None, 
         "Select Directory", path)
      fileDirectory=str(fileDirectory).rstrip('/')
      runname = os.path.split(fileDirectory)[1]
      run = int(runname.strip('run'))
      dataPathInterp = fileDirectory + '/'
      SCAN=False
    elif len(sys.argv)==3:
      Tacq = float(sys.argv[1])
      dataPathInterp = sys.argv[2].rstrip('/')+'/'
      SCAN = False
    pickleFile = open(pickFileName, 'w')
    pickle.dump(dataPathInterp, pickleFile)
    pickleFile.close()
    SLMpath = '/mnt/SLM/Dan/OptimizeSLM/Patterns/OrigSettings/'

    dataPath,dirCnt = createDatafolder()
    buf = ttag_wrap.openttag()
    atexit.register(ttag_wrap.cleanUp, buf)
    buf.start()

    CoincidenceWindow = 10e-9
    gate = 10e-9
    heraldChan = 0
    bobMirrorFileName = "/mnt/SLM/Dan/FindNanowiresSERICALPORT/NanowireScanNOSCRAMBLE/Bob/on.dat"

    nrows = 512

    if SCAN:
        #  scanning the SLM
        scanparams = [xstart, xstop, xstep, ystart, ystop, ystep] 
        np.savetxt(dataPath + 'scanparameters.txt',scanparams,fmt='%d')
        pixel_list = []
        for xo in range(xstart, xstop+1, xstep):
            for yo in range(ystart, ystop+1, ystep):
                pixel_list.append([xo,yo])

    else:
        infoname = sys.argv[0].strip('.py')+'.info.txt'
        infofp = open(dataPath+infoname,'w')
        infofp.write('# use the pixel mapping in this folder %s\n'%dataPathInterp)
        infofp.write('# Tacq %f\n'%Tacq) 
        infofp.close()

        scanparams = np.loadtxt(dataPathInterp+'scanparameters.txt') 
        (xstart, xstop, xstep, ystart, ystop, ystep)=scanparams
        pixel_list = gp.interpolate2SLM(dataPathInterp, xstart, xstep, ystart, ystep)
        #print pixel_list

    cnt = 0
    # Set Bob's SLM to a mirror, only need to do this once
    shutil.copyfile(bobMirrorFileName, '/mnt/SLM/Dan/OptimizeSLM/Patterns/OrigSettings/SLM_100.dat')
    for pixel in pixel_list:
            (xo,yo)=pixel
            if SCAN:
                print xo,yo
            fft_phase = gp.initial_phase_orig(257-xo,257-yo, 512)
            #print 'phase_offset',gp.phase_offset
            gp.write2file(fft_phase, gp.phasemap, SLMpath, '99')
            send(99)
            msgin = wait()
            time.sleep(0.1)
            if int(msgin)<0:
                print 'problem talking with loading a file on the SLM'
                break
            #print 'From PC: ',msgin
            cnts_single, cnts_coin = ttag_wrap.getCnts(Tacq, CoincidenceWindow,gate, heraldChan,buf)
            fname = 'single_%d.txt'%dirCnt
            write2file(dataPath, fname, cnts_single, xo,yo,cnt)
            fname = 'coin_%d.txt'%dirCnt
            write2file(dataPath, fname,cnts_coin,xo,yo,cnt)
            cnt += 1

