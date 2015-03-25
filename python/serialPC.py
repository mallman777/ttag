import serial

s = serial.Serial('/dev/ttyUSB1',38400,timeout=0.05)

def waitformsg():
    print 'Waiting for msg from PC'
    while True:
        msgin = s.read(80);
        if len(msgin)>0:
            break;
        print 'Waiting'

    count = int(msgin.strip())
    print 'count: %d'%count
    return count
def sendmsg2pc(count):
    print 'Sending: %d'%count
    s.write('%d'%count)

while True:
    count = waitformsg()
    sendmsg2pc(count+1)



