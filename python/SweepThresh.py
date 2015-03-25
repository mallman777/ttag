import sys
sys.path.append('/mnt/odrive/HPD/ShanePyStuff/classes')
import ttag
import time
import numpy as np
import matplotlib.pyplot as plt
import subprocess
import signal
import os
import configParser
import MG9637Agpib
import TEKOA5002gpib
import HP8152A
import time
import SIM900gpib
import serial
import datetime
from pylab import *
import logfile
import matplotlib.cm as cm


#Run UQDinterface
def writeSH(level):
    optStr = '../UQD/src/UQDinterface '
    for i in range(8):
        optStr += "--c%dv %f --c%de 1 --c%dv %f --c%de 0 " % (i+1, level, i+1, i+9, -1*level, i+9)
    optStr += '&'
    fsh = open('launch2.sh', 'w')
    fsh.write(optStr)
    fsh.flush()
    fsh.close()

def launch():
    args = ['sudo', 'bash','launch2.sh']
    f = open('test','w')
    p = subprocess.Popen(args,stdout=f)
    os.fsync(f)
    f.close()
    time.sleep(1)
    return p

def kill(p):
    for i in range(100):
        ttag.deletebuffer(i)
    os.kill(p.pid+2,signal.SIGKILL)
    time.sleep(1)
   # os.fsync(f)

def runExperiment(threshLevels):
    currentTag = 1
    lastTag = 0
    delays = -1*np.array([0,0,0,0,0,0,0,0,5e-9,5e-9,5e-9,5e-9,5e-9,5e-9,5e-9,5e-9])
    data = np.empty([1,16])
    biasList = np.array([x for x in range(8)])
#    biasList = biasList[biasList == 0]
    outmsg = 'VOLT %f' %float(V)
    for i in biasList:
        sim.conn(i+1)
        sim.write('OPON')
        sim.write(outmsg)
        sim.write('xyz')
    time.sleep(1)  #Quick test to see if settle time an issue

    for level in threshLevels:
        writeSH(level)
        p = launch()

        print "The process ID is:"
        print p.pid+2
        time.sleep(1)

        ttnumber = ttag.getfreebuffer()-1
        buf = ttag.TTBuffer(ttnumber)  #Opens the buffer

        print "Channels:", buf.channels
        print "Resolution:", buf.resolution
        print "Datapoints:", buf.datapoints
        print "Buffer size:", buf.size()

        buf.start()
        time.sleep(Tacq+0.5)
        buf.stop()
    
        try:
            xx = buf(Tacq)  # an array of the last 1 seconds worth of data
            currentTag = xx[1][-1]
        except:
            print "Can't run buf(Tacq) code"
        y = buf.singles(Tacq)
    
        for i in range(8):
            print "Row %d singles: " % (i+1)
            print y[i]
        for i in range(8):
            print "Col %d singles: " % (i+1)
            print y[i+8]

        print "lastTag, currentTag:"
        print lastTag, currentTag

        if currentTag == lastTag:
            data[0,:] = 0
        else:
            data[0,:] = y
        if not currentTag == 1:
            lastTag = currentTag
        np.savetxt(fintcnts, data, fmt = '%0.2f')
        kill(p)
    fintcnts.flush()
    fintcnts.close()

    for i in biasList:
        sim.conn(i+1)
        sim.write('VOLT 0')
        sim.write('OPOF')
        sim.write('xyz')
    time.sleep(.5)
    sim.meter.loc()

def plotData():
    data = np.loadtxt(fpath, delimiter = ' ')
    colors = cm.rainbow(np.linspace(0,1,16))
    fig = plt.figure(3)

    for i in range(16):
        plt.subplot(111)
        plt.plot(threshLevels, data[:,i], '-', label = 'Ch%d'%(i), color = colors[i])
#        plt.axis([float(threshStart), float(threshStop), 0, 20000])
        plt.ylabel('Counts')
        plt.xlabel('Threshold (V)')
        plt.legend(loc = 'upper left')
        plt.title('Run:%r, MeasTime:%rs'% (run, Tacq))
    fig.set_size_inches(12,0.7*12)
    savefig('%s_lin.png' %fpath, bbox_inches = 'tight', pad_inches=0)
    savefig('%s_lin.eps' %fpath, bbox_inches = 'tight', pad_inches=0)
    
    plt.show()

if __name__ == '__main__':
    # Load config settings and create objects
    config = '../../../../config.ini'
    uqdConfig = '../UQD/src/uqd.uqcfg'
    c = configParser.ConfigParser()
    options = c.parse_config(config)
    d = datetime.datetime.now()
    port = serial.Serial('/dev/ttyUSB0', 9600, timeout = 0.5)
    sim = SIM900gpib.device(4,port)
    laser = MG9637Agpib.device(12,port)
    Attn1 = TEKOA5002gpib.device(5,port)
    Attn2 = TEKOA5002gpib.device(6,port)
    PwrMeter = HP8152A.device(8,port)

    # Experiment Parameters
    program, run, threshStart, threshStop, threshStep, V = sys.argv
    R = float(options['biasResistance'])
    LaserWvl = float(options['laserWavelength'])
    LaserPwr = float(options['laserPower'])
    LaserAttn1 = float(options['laserAttn1'])
    LaserAttn2 = float(options['laserAttn2'])
    Tacq = 1  # Measurement time in seconds
    CoincidenceWindow = 5e-9  # Coincidence window based on observed delay between row and column pulses.

    # Setup Laser and Attenuators
    laser.setWavelength(LaserWvl)
    laser.setPower(LaserPwr)
    laser.setModeCW()
    Attn1.set_att(LaserAttn1)
    Attn2.set_att(LaserAttn2)
    Attn1.set_lambda(LaserWvl)
    Attn2.set_lambda(LaserWvl)

    # File I/O Stuff
    timestamp = d.strftime('%Y%m%d_%H%M%S')
    dataLogPath = options['networkData&LogPath']

    fname = '%s_R%s.txt'%(timestamp, run)
    fpath = os.path.join(dataLogPath, fname)

    L = logfile.log()
    L.UQD(sys.argv,config,uqdConfig)

    fintcnts = open(fpath,'w')
    threshLevels = np.arange(float(threshStart), float(threshStop), float(threshStep))
    runExperiment(threshLevels)    
    plotData()
