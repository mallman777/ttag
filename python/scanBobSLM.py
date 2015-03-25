import time
import numpy as np
import ttag_wrap
import gen_find_nano_patterns as gp
import serial_SLM
import atexit
import os,sys,threading
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

pickFileName = sys.argv[0].strip('.py') + 'pickle'
if os.path.isfile(pickFileName):
  pickleFile = open(pickFileName, 'r')
  path = pickle.load(pickleFile)
  pickleFile.close()
else:
  path = '/hdd/'

if __name__=='__main__':
    if len(sys.argv)>1:
      Tacq = float(sys.argv[1])
      if len(sys.argv)==2:
          from pyqtgraph.Qt import QtGui, QtCore
          app = QtGui.QApplication([])
          fileDirectory = QtGui.QFileDialog.getExistingDirectory(None, 
         "Select Directory", path)
          fileDirectory=str(fileDirectory).rstrip('/')
          runname = os.path.split(fileDirectory)[1]
          run = int(runname.strip('run'))
          dataPathInterp = fileDirectory + '/'
      if len(sys.argv)==3:
        dataPathInterp=sys.argv[2].rstrip('/') + '/'
    else:
      Tacq = 1
      from pyqtgraph.Qt import QtGui, QtCore
      app = QtGui.QApplication([])
      fileDirectory = QtGui.QFileDialog.getExistingDirectory(None, 
         "Select Directory", "/hdd/")
      fileDirectory=str(fileDirectory).rstrip('/')
      runname = os.path.split(fileDirectory)[1]
      run = int(runname.strip('run'))
      dataPathInterp = fileDirectory + '/'

      print "You forgot to pass Tacq as a parameter "
      print "Using 1 second"

    pickleFile = open(pickFileName, 'w')
    pickle.dump(dataPathInterp, pickleFile)
    pickleFile.close()

    dataPath,dirCnt = createDatafolder()

    buf = ttag_wrap.openttag()
    buf.start()
    atexit.register(ttag_wrap.cleanUp, buf)

    CoincidenceWindow = 10e-9
    gate = 10e-9
    heraldChan = 0
    # get nanowire pixel locations from scan
    scanparams = np.loadtxt(dataPathInterp+'scanparameters.txt') 
    (xstart,xstop,xstep,ystart,ystop,ystep)=scanparams
    pixel_list = gp.interpolate2SLM(dataPathInterp, xstart, xstep, ystart, ystep)
    
    pixel = 27  # aim for middle of the nanowire array
    [xo,yo]= pixel_list[pixel,:]

    nrows = 512
    cnt = 0
    seed = 1  # use same random pattern all the time
    # compute random phase and set alice
    code = gp.encrypt(seed,512,128) 
    # figure phases to point to pixel
    fft_phase = gp.initial_phase_orig(257-xo,257-yo, 512)
    fft_phase += code
    gp.write2file(fft_phase, gp.phasemap, SLMpath, '99')

    for xshift in range(-10,11):
        for yshift in range(-10,11):
            print 'xshift, yshift: %3d %3d'%(xshift,yshift)
            # send decoding matrix to Bob SLM, vary xshift, yshift
            decode = gp.decrypt(code, xshift, yshift, nrows)
            gp.write2file(decode, gp.phasemap, SLMpath, '100')
            send(99)
            msg = wait()
            if int(msg)<0:
                print 'Problem with SLM setting'
                raise('Problem with SLM setting')
                break
            # start taking data
            start = buf.datapoints
            time.sleep(Tacq)
            stop = buf.datapoints
            if logtags:
                tup = buf[-(stop - start):]  # a tuple of chan tags, and time tags
                save_thread = threading.Thread(None, target = tags2file, args=(dataPath, tup,cnt))
                save_thread.start()
            cnts_single, cnts_coin = ttag_wrap.getCnts_nowait(Tacq, CoincidenceWindow,gate, heraldChan,buf)
            fname = 'single_%d_ccode.txt'%dirCnt
            write2file(dataPath, fname, cnts_single, xshift,yshift,cnt)
            fname = 'coin_%d_ccode.txt'%dirCnt
            write2file(dataPath, fname,cnts_coin,xshift, yshift,cnt)
            cnt += 1
