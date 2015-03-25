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
program, run, Vstart, Vstop, Vstep = sys.argv
R = float(options['biasResistance'])
LaserWvl = float(options['laserWavelength'])
LaserPwr = float(options['laserPower'])
LaserAttn1 = float(options['laserAttn1'])
LaserAttn2 = float(options['laserAttn2'])
Tacq = 1  # Measurement time in seconds
CoincidenceWindow = 10e-9  # Coincidence window based on observed delay between row and column pulses.

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

fname = '%s%s.txt'%(timestamp, run)
fnameSingCnt = '%s%s_SinglesCnts.txt'%(timestamp, run)
fpath = os.path.join(dataLogPath, fname)
fpathSinglesCnts = os.path.join(dataLogPath, fnameSingCnt)
L = logfile.log()
L.UQD(sys.argv,config,uqdConfig)

#Run UQDinterface
#args = ['sudo', '../../CppDemo/UQDinterface', '&']
args = ['sudo', 'bash','launch.sh']
f = open('test','w')
p = subprocess.Popen(args,stdout=f)
#p = subprocess.Popen(args)

print "The process ID is:"
#print p.pid+1  # p.pid is the PID for the new shell.  p.pid is the PID for UQDinterface in the new shell
print p.pid+2
time.sleep(1)

#ttnumber = int(raw_input("Time tagger to open:"))
ttnumber = ttag.getfreebuffer()-1
buf = ttag.TTBuffer(ttnumber)  #Opens the buffer

print "Channels:", buf.channels
print "Resolution:", buf.resolution
print "Datapoints:", buf.datapoints
print "Buffer size:", buf.size()

fintcnts = open(fpath,'w')
fsingcnts = open(fpathSinglesCnts,'w')

Varray = np.arange(float(Vstart), float(Vstop), float(Vstep))
#Varray = float(Vstart)*np.ones(int(Vstep))

currentTag = 1
lastTag = 0
biasList = np.array([x for x in range(8)])
biasList = biasList[biasList == 7]

delays = -1*np.array([0,0,0,0,0,0,0,0,5e-9,5e-9,5e-9,5e-9,5e-9,5e-9,5e-9,5e-9])
data = np.empty([1,65])
for V in Varray:
    data[0] = V
    outmsg = 'VOLT %f' %V
    for i in biasList:
        sim.conn(i+1)
        sim.write('OPON')
        sim.write(outmsg)
        sim.write('xyz')
#    time.sleep(0.5)
    time.sleep(1)  #Quick test to see if settle time an issue
    buf.start()
    time.sleep(Tacq+0.5)
    buf.stop()
    
    try:
        xx = buf(Tacq)  # an array of the last 1 seconds worth of data
        currentTag = xx[1][-1]
    except:
        print "Can't run buf(Tacq) code"
#    x = buf.coincidences(Tacq, CoincidenceWindow, delays)
    x = buf.coincidences(Tacq, CoincidenceWindow)
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
        data[0,1::] = 0
    else:
        data[0,1::] = np.reshape(x[0:8,8::], [1,-1])
    if not currentTag == 1:
        lastTag = currentTag
    np.savetxt(fintcnts, data, fmt = '%0.2f')
    totalCoincidences = np.sum(data[0,1::])

    print "Total Row and Column Singles:"
    print sum(y[:8]), sum(y[-8:])
    print "Total coincidences:"
    print totalCoincidences
    msg2 = '\t' + '%d'%(sum(y[:8])) + '\t' + '%d'%(sum(y[-8:])) + '\t' + '%d'%totalCoincidences
    fsingcnts.write('%f%s' % (V,msg2) + '\n')
    
fintcnts.flush()
fintcnts.close()
fsingcnts.flush()
fsingcnts.close()

for i in biasList:
    sim.conn(i+1)
    sim.write('VOLT 0')
    sim.write('xyz')
time.sleep(.5)
sim.meter.loc()

# Plot after data acquired.  Need to add Rob/SW's code for plotting as data acquired.
if True:
    data = np.loadtxt(fpath, delimiter = ' ')
    data2 = np.loadtxt(fpathSinglesCnts, delimiter = '\t')
    colors = cm.rainbow(np.linspace(0,1,64))
    for i in range(64):
        plt.figure(3)
        plt.subplot(211)
        plt.plot(data[:,0], data[:,i+1], '.', label = 'Pix%d'%(i+1), color = colors[i])
        plt.axis([float(Vstart), float(Vstop), 0, 30000])
        plt.ylabel('Counts')
        plt.xlabel('Bias Current (V)')
#        plt.legend(loc = 'upper left')
        plt.title('Run:%r, MeasTime:%rs'% (run, Tacq))
        plt.subplot(212)
        plt.semilogy(data[:,0], data[:,i+1]+0.01, '.', label = 'C%d'%i, color = colors[i])
        plt.ylabel('Counts')
        plt.xlabel('Bias Current (V)')
    savefig('%s_lin.png' %fpath, bbox_inches = 'tight', pad_inches=0)
    savefig('%s_lin.eps' %fpath, bbox_inches = 'tight', pad_inches=0)
    
    plt.figure(2)
    plt.plot(data2[:,0], data2[:,1], 'r-', label = 'Row Singles')
    plt.plot(data2[:,0], data2[:,2], 'b-', label = 'Col Singles')
    plt.plot(data2[:,0], data2[:,3], 'k-', label = 'Total Coincidences')
    plt.legend(loc = 'upper left')
    savefig('%s_.png' %fpath, bbox_inches = 'tight', pad_inches=0)
    savefig('%s_.eps' %fpath, bbox_inches = 'tight', pad_inches=0)

    plt.show()


for i in range(100):
  ttag.deletebuffer(i)

#p.terminate()
os.kill(p.pid+2,signal.SIGKILL)
#os.kill(p.pid+2,signal.SIGINT)
os.fsync(f)
