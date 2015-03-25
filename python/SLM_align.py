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
program, V = sys.argv
R = float(options['biasResistance'])
LaserWvl = float(options['laserWavelength'])
LaserPwr = float(options['laserPower'])
LaserAttn1 = float(options['laserAttn1'])
LaserAttn2 = float(options['laserAttn2'])
Tacq = 10  # Measurement time in seconds
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
dataLogPath = options['networkData&LogPath']

L = logfile.log()
L.UQD(sys.argv,config,uqdConfig)

#Run UQDinterface
#args = ['sudo', '../../CppDemo/UQDinterface', '&']
#args = ['sudo', 'bash','launch.sh']
#f = open('test','w')
#p = subprocess.Popen(args,stdout=f)
#p = subprocess.Popen(args)

print "The process ID is:"
#print p.pid+1  # p.pid is the PID for the new shell.  p.pid is the PID for UQDinterface in the new shell
#print p.pid+2
#time.sleep(1)

#ttnumber = int(raw_input("Time tagger to open:"))
ttnumber = ttag.getfreebuffer()-1
#buf = ttag.TTBuffer(ttnumber)  #Opens the buffer
buf = ttag.TTBuffer(0)  #Opens the buffer

print "Channels:", buf.channels
print "Resolution:", buf.resolution
print "Datapoints:", buf.datapoints
print "Buffer size:", buf.size()

currentTag = 1
lastTag = 0
biasList = np.array([x for x in range(8)])
#biasList = biasList[biasList == 7]

startOutter = 120
startInner = 120
numPatterns = 42
step = 2
outter = [startOutter + z*step for z in range(numPatterns)]
inner = [startInner + z*step for z in range(numPatterns)]
heraldChan = 0
gate = 10e-9

print "Starting"
for i in outter:
  for j in inner:
    data = np.zeros([1,65])
    done  = False
    data[0] = float(V)
    while not done:
      time.sleep(0.5)
      if os.path.isfile(os.path.join(dataLogPath,"flagfile.txt")):
        #timestamp = d.strftime('%Y%m%d_%H%M%S')
        fname = 'x%dy%d.txt'%(i,j)
        fpath = os.path.join(dataLogPath, fname)
        fintcnts = open(fpath,'w')
        outmsg = 'VOLT %f' %(float(V))
        for k in biasList:
          sim.conn(k+1)
          sim.write('OPON')
          sim.write(outmsg)
          sim.write('xyz')
#        buf.start()
        time.sleep(Tacq + 0.5)    
#        buf.stop()
        xx = buf(Tacq)  # an array of the last 1 seconds worth of data
        currentTag = xx[1][-1]
        x = buf.coincidences(Tacq, CoincidenceWindow, gate = gate, heraldChan = heraldChan)    
        if currentTag == lastTag:
          data[0,1::] = 0
        else:
          data[0,1::] = np.reshape(x[0:8,8::], [1,-1])
        if not currentTag == 1:
          lastTag = currentTag
        np.savetxt(fintcnts, data, fmt = '%0.2f')
        fintcnts.flush()
        fintcnts.close()
        os.remove(os.path.join(dataLogPath,"flagfile.txt"))
        for k in biasList:
          sim.conn(k+1)
          sim.write('VOLT 0')
          sim.write('xyz')
        done = True

sim.meter.loc()
print "Finished"
#for i in range(100):
#  ttag.deletebuffer(i)

#p.terminate()
#os.kill(p.pid+2,signal.SIGKILL)
#os.fsync(f)
