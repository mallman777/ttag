import time
import numpy as np
import ttag_wrap
import gen_find_nano_patterns as gp
import serial_SLM
import atexit
import os,sys,threading,shutil
from enigma_daq import createDatafolder, tags2file, write2file
#dataPathInterp = '/hdd/2015_03_11/run24/'

dataPathInterp = '/hdd/2015_03_12/run27/'
SLMpath = '/mnt/SLM/Dan/OptimizeSLM/Patterns/OrigSettings/'
logtags = True
PC = True
serial_SLM.setup(PC)
wait = serial_SLM.wait
send = serial_SLM.send
def get_Cnts_local(fftphase):
    gp.write2file(fft_phase, gp.phasemap, SLMpath, '99')
    send(99)
    (curr_single,curr_coin) = getcnts(pix, tacq, coincidencewindow,buf)
    f = curr_single[pixel]
    #f = curr_coin[pixel]
    norm = curr_single.sum()
    # norm = curr_coin.sum()
    return f,norm

if __name__=='__main__':
    if len(sys.argv)>2:
      Tacq = float(sys.argv[1])
      dataPathInterp = sys.argv[2].rstrip('/')+'/'
    else:
        if len(sys.argv)==2:
            Tacq = float(sys.argv[1])
            # Need path of the interpolation file
            #dataPathInterp = '/hdd/2015_03_12/run%/'
        from pyqtgraph.Qt import QtGui, QtCore
        app = QtGui.QApplication([])
        fileDirectory = QtGui.QFileDialog.getExistingDirectory(None, 
         "Select Directory", "/hdd/")
        fileDirectory=str(fileDirectory).rstrip('/')
        runname = os.path.split(fileDirectory)[1]
        run = int(runname.strip('run'))
        dataPathInterp = fileDirectory + '/'

    SLMpath = '/mnt/SLM/Dan/OptimizeSLM/Patterns/OrigSettings/'

    #dataPath,dirCnt = createDatafolder()
    buf = ttag_wrap.openttag()
    atexit.register(ttag_wrap.cleanUp, buf)
    buf.start()

    CoincidenceWindow = 10e-9
    gate = 10e-9
    heraldChan = 0
    bobMirrorFileName = "/mnt/SLM/Dan/FindNanowiresSERICALPORT/NanowireScanNOSCRAMBLE/Bob/on.dat"

    nrows = 512


    if True:
        infoname = sys.argv[0].strip('.py')+'.info.txt'
        infofp = open(infoname,'w')
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
    out_fp = open(dataPath+'rasterOptimize.txt','w')
    for pixel in pixel_list:
        (xo,yo)=pixel
        while True:
            fft_phase = gp.initial_phase_orig(257-xo,257-yo, 512)
            #print 'phase_offset',gp.phase_offset
            gp.write2file(fft_phase, gp.phasemap, SLMpath, '99')
            send(99)
            msgin = wait()
            if int(msgin)<0:
                print 'problem talking with loading a file on the SLM'
                break
            #print 'From PC: ',msgin
            prev_single, prev_coin = ttag_wrap.getCnts(Tacq, CoincidenceWindow,gate, heraldChan,buf)

            x_offsetList = np.arange(-2,3)*2            
            y_offsetList = np.arange(-2,3)*2

            cnts = []
            norms = []
            for x_offset in x_offsetList:
              fft_phase = gp.initial_phase_orig(257-(xo+x_offset),257-(yo), 512)
              f,norm = get_Cnts_local(fftphase)
              cnts.append(f)
              norms.append(norm)
              print 'x:%.3f %6d %6d %.3f'%(xo+x_offset, f,norm, 1.*f/norm)
            cnts = np.array(cnts)
            normsx = np.array(norms)
            p_fit = np.polyfit(x_offsetList, cnts/normsx, 2)
            newx = -p_fit[1]/(2*p_fit[0])

            cnts = []
            norms = []
            x_offset = 0
            for y_offset in y_offsetList:
              fft_phase = gp.initial_phase_orig(257-(xo+x_offset),257-(yo+y_offset), 512)
              f,norm = get_Cnts_local(fftphase)
              cnts.append(f)
              norms.append(norm)
              print 'y:%.3f %6d %6d %.3f'%(yo + y_offset,f,norm, 1.*f/norm)

            cnts = np.array(cnts)
            normsy = np.array(norms)
            p_fit = np.polyfit(x_offsetList, cnts/normsy, 2)
            newy = -p_fit[1]/(2*p_fit[0])
            xo += newx
            yo += newy
            print 'newx: %.2f\tnewy: %.2f'%(xo,yo) 
              
            if abs(newx)<0.1 and abs(newy)<0.1
                break
        print 'pixel: %d\t%.5f\t%.f'%(pixel,xo,yo)
        out_fp.write('%4d\t%.5f\t%.5f\n'%(pixel,xo,yo)   
     out_fp.close()
