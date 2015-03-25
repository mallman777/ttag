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
import serial

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
serialport = serial.Serial('/dev/ttyUSB1',38400,timeout=0.5)

# Experiment Parameters
program, V = sys.argv
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
#dataLogPath = options['networkData&LogPath']
dataLogPath = "/hdd/"

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
buf.tagsAsTime = False

print "Channels:", buf.channels
print "Resolution:", buf.resolution
print "Datapoints:", buf.datapoints
print "Buffer size:", buf.size()


def waitforPC():
    print 'Waiting for msg from PC'
    msgin = ''
    while (msgin == ''):
        msgin = serialport.read(80);
    print 'msg from PC: %s' %msgin 

def sendtoPC(count):
    print 'Sending photon num: %d'%count
    serialport.write('%05d'%count)

biasList = np.array([x for x in range(8)])
numPhotons = 4
print "Starting"

buf = ttag.TTBuffer(0)
buf.start()
time.sleep(1)
for i in range(1):
    #  Wait for the PC to send a message to start taking data
    outmsg = 'VOLT %f' %(float(V))
    if (i != 0 and not i % 100):
      for k in biasList:
        sim.conn(k+1)
        sim.write('OPON')
        sim.write(outmsg)
        sim.write('xyz')
      time.sleep(0.5)
#    waitforPC()
    if True:
        #timestamp = d.strftime('%Y%m%d_%H%M%S')
#        fnameTags = 'Photon%05d_tags.bin'%i
        fnameTags = 'test_tags.bin'
#        fnameChans = 'Photon%05d_chans.bin'%i
        fnameChans = 'test_chans.bin'
        fpathTags = os.path.join(dataLogPath, fnameTags)
        fpathChans = os.path.join(dataLogPath, fnameChans)
#        fTags = open(fpathTags,'wb')
#        fChans = open(fpathChans,'wb')
        start = buf.datapoints
        time.sleep(Tacq)
        stop = buf.datapoints    
        tup = buf[-(stop - start):]  # a tuple of chan tags, and time tags
        chans = tup[0]  #Single byte unsigned integer
        tags = tup[1] #8 byte unsigned integer
        chans.tofile(fpathChans)
        tags.tofile(fpathTags)
#        fChans.flush()
#        fTags.flush()
#        fChans.close()
#        fTags.close()
#    sendtoPC(i)
    if (i != 0 and not i % 100):
      for k in biasList:
        sim.conn(k+1)
        sim.write('VOLT 0')
        sim.write('xyz')
      time.sleep(0.5)

buf.stop()
sim.meter.loc()
print "Finished"
#for i in range(100):
#  ttag.deletebuffer(i)

#p.terminate()
#os.kill(p.pid+2,signal.SIGKILL)
#os.fsync(f)
