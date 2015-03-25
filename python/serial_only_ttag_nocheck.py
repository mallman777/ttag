import serial, time, datetime,os,sys
import threading
import ttag
import atexit
import numpy as np
import checkArray4 as CA
import checkTemp as CT
import sys
sys.path.append('/mnt/odrive/HPD/ShanePyStuff/classes')
import SIM900gpib
print CA.firstTime
#  Set whether to take data wtih the serial port interlock
PC = True
CT.EMAIL = True
#

format = '%Y_%m_%d'
folder = '/hdd/%s/'%datetime.datetime.today().strftime(format)
# creating directory for data
dirCnt=1
while True:
    dataPath = folder+'run%02d/'%dirCnt
    #print dataPath
    try:  
      os.makedirs(dataPath)
      break
    except:
      dirCnt += 1
print 'dataPath:',dataPath
#
# create fake wait of 100ms incase no interlock with pc
def fakewait():
    global cnt
    time.sleep(0.1)
    return cnt 
def fakesend(value):
    global cnt
    cnt = value+1
    return 
# the real methods for waiting when interlock present with pc
serialport = serial.Serial('/dev/ttyUSB0',38400,timeout=0.05)
#simport = serial.Serial('/dev/ttyUSB1',38400,timeout=0.05)
#sim = SIM900gpib.device(4,simport)
def waitforPC():
    print 'Waiting for msg from PC'
    msgin = ''
    while (msgin == ''):
        msgin = serialport.read(80);
    #print 'msg from PC: %s' %msgin 
    return msgin

def sendtoPC(count):
    print 'Sending photon num: %d'%count
    serialport.write('%05d'%count)

# assigning function to use to wait for data/send data
if PC==True:
    wait = waitforPC
    send = sendtoPC
else:
    wait = fakewait
    send = fakesend
cnt = 0

def save2file():
    global tup,cnt

    fnameTags = 'tag_%06d.bin'%cnt
    fnameChans = 'chan_%06d.bin'%cnt
    print 'Saving to %s, %s'%(fnameTags, fnameChans)
    fTags = open(dataPath+fnameTags,'wb')
    fChans = open(dataPath+fnameChans,'wb')
  
    chans = tup[0]  #Single byte unsigned integer
    tags = tup[1] #8 byte unsigned integer
    chans.tofile(fChans)
    tags.tofile(fTags)
    fChans.close()
    fTags.close()

def checkTempGood():
    #  Check file
    ret = CT.check()
    print 'checking temp',ret
    return ret

def detectorGood():
    #  Check file generated by code watching data taking
    ret = CA.detectorGood(dataPath,tup)
    #ret = CA.detectorGood(dataPath,cnt, save_thread)
    #print 'detector good',ret
    if cnt % 100 == 0 and cnt != 0 and CA.firstTime == False:  # added this to stop checking array and reset the bias every 100 measurements.
      return False
    else:
      return True

ttnumber = ttag.getfreebuffer()-1
print cnt
print "ttnumber: ", ttnumber
buf = ttag.TTBuffer(ttnumber)  #Opens the buffer
buf.tagsAsTime = False
buf.start()
Tacq = 1
if len(sys.argv) > 1:
  Tacq = float(sys.argv[1])

def cleanUp():
    print "Cleaning"
    buf.stop()
atexit.register(cleanUp)
tup=[]
retake = False
send(cnt)
while True:
    to = []
    to.append(time.time())
    if retake == False:
        msgin = wait()
    to.append(time.time())
    cnt = int(msgin)
    if cnt < 0:
        break
    start = buf.datapoints
    print "waiting: ", Tacq
    time.sleep(Tacq)
    stop = buf.datapoints
    tup = buf[-(stop - start):]  # a tuple of chan tags, and time tags
    to.append(time.time())
    save_thread = threading.Thread(None, target = save2file)
    save_thread.start()
    send(cnt)
    to.append(time.time())
    print np.diff(np.array([to]))
buf.stop()
