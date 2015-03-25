import time
import numpy as np
import ttag_wrap
import gen_find_nano_patterns as gp
import serial_SLM
import atexit
import os,sys,threading
from enigma_daq import createDatafolder, tags2file, write2file
import argparse
#dataPathInterp = '/hdd/2015_03_11/run24/'

dataPathInterp = '/hdd/2015_03_12/run27/'
SLMpath = '/mnt/SLM/Dan/OptimizeSLM/Patterns/OrigSettings/'
logtags = True
PC = True
serial_SLM.setup(PC)
wait = serial_SLM.wait
send = serial_SLM.send

if __name__=='__main__':
    parser = argparse.ArgumentParser(description = 'Pass in params.')
    parser.add_argument('-t', type = float, help = 'Integration time')
    parser.add_argument('-d', type = str, help = 'Interp settings directory')
    args = parser.parse_args()
    if args.t:
      Tacq = args.t
    else:
      Tacq = 1
      print "Defaulting to 1 sec integration"
    if args.d:
      dataPathInterp = args.d
    else:
      from pyqtgraph.Qt import QtGui, QtCore
      app = QtGui.QApplication([])
      fileDirectory = QtGui.QFileDialog.getExistingDirectory(None, 
             "Select Directory", "/hdd/")
      fileDirectory=str(fileDirectory).rstrip('/')
      runname = os.path.split(fileDirectory)[1]
      run = int(runname.strip('run'))
      dataPathInterp = fileDirectory + '/'
    
    dataPath,dirCnt = createDatafolder()

    buf = ttag_wrap.openttag()
    atexit.register(ttag_wrap.cleanUp, buf)
    buf.start()

    CoincidenceWindow = 10e-9
    gate = 10e-9
    heraldChan = 0
    # get pixel positions in terms of SLM settings
    scanparams = np.loadtxt(dataPathInterp+'scanparameters.txt') 
    print 'Scan parameters:',scanparams
    (xstart,xstop,xstep,ystart,ystop,ystep)=scanparams
    pixel_list = gp.interpolate2SLM(dataPathInterp, xstart, xstep, ystart, ystep)

    nrows = 512
    xshift = -1
    yshift = 1

    infoname = sys.argv[0].strip('.py')+'.info.txt'
    infofp = open(dataPath+infoname,'w')
    infofp.write('# use the pixel mapping in this folder %s\n'%dataPathInterp)
    infofp.write('# Tacq %f\n'%Tacq) 
    infofp.write('#  BOB SLM xshift: %d, yshift: %d\n'%(xshift,yshift))
    infofp.close()

    cnt = 0
    while True:
      for pixel in range(64):
        [xo,yo]= pixel_list[pixel,:]
        print '%2d: %.3f %.3f'%(pixel,xo,yo)
        for seedA in range(8):
           fft_phase = gp.initial_phase_orig(257-xo,257-yo, 512)
           #print 'phase_offset',gp.phase_offset
           # generate encoding matrix
           #seed = cnt+1
           codeA = gp.encrypt(seedA+1,512,128) #using seed+1 to make consistent with matlab ???
           fft_phase += codeA
           # send to Alice SLM
           gp.write2file(fft_phase, gp.phasemap, SLMpath, '99')
           for seedB in range(8):
             # send decoding matrix to Bob SLM
             codeB = gp.encrypt(seedB+1,512,128)
             decode = gp.decrypt(codeB, xshift, yshift, nrows)
             gp.write2file(decode, gp.phasemap, SLMpath, '100')
             send(99)
             msg = wait()
             time.sleep(0.1)
             if int(msg)<0:
               print 'Problem with SLM setting'
               break
               # start taking data
             start = buf.datapoints
             time.sleep(Tacq)
             stop = buf.datapoints
             if logtags:
               tup = buf[-(stop - start):]  # a tuple of chan tags, and time tags
               save_thread = threading.Thread(None, target = tags2file, args=(dataPath,tup,cnt))
               save_thread.start()
             cnts_single, cnts_coin = ttag_wrap.getCnts_nowait(Tacq, CoincidenceWindow,gate, heraldChan,buf)
             fname = 'single_%d_ccode.txt'%dirCnt
             write2file(dataPath, fname, cnts_single, xo,yo,cnt)
             fname = 'coin_%d_ccode.txt'%dirCnt
             write2file(dataPath, fname,cnts_coin,xo,yo,cnt)
             cnt += 1
             print cnt
        
