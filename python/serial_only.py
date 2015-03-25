import serial, time
serialport = serial.Serial('/dev/ttyUSB1',38400,timeout=0.5)
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

while True:
   number = int(waitforPC())
   print 'got number:',number
   if number < 0:
       break;
   time.sleep(10)
   sendtoPC(number) 
