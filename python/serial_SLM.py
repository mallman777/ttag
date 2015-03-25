import serial
import glob

serialport = None
wait= None
send = None
PC = False

listing = glob.glob('/sys/bus/usb-serial/drivers/pl2303/*USB*')
listing = listing[0].split('/')
name = listing[-1]
#print name
def fakewait():
    global cnt
    time.sleep(0.1)
    return cnt 
def fakesend(value):
    global cnt
    cnt = value+1
    return 


def waitforPC():
    #print 'Waiting for msg from PC'
    global serialport
    msgin = ''
    while (msgin == ''):
        #print "waiting for msg"
        msgin = serialport.read(80);
    #print 'msg from PC: %s' %msgin 
    return msgin

def sendtoPC(count):
    #print 'Sending photon num: %d'%count
    global serialport
    serialport.write('%d'%count)

def setup(boolin):
    global PC, wait, send,serialport, name
    PC = boolin
    print 'Serial port for SLM computer: %s'%name
    serialport = serial.Serial('/dev/%s'%name,38400,timeout=0.05)
    if PC==True:
        wait = waitforPC
        send = sendtoPC
    else:
        wait = fakewait
        send = fakesend
