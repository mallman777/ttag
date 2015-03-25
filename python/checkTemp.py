import numpy as np
import glob
import time, datetime
from datetime import timedelta
import smtplib
EMAIL = False

def sendEmail(msg):
  sender = 'pi132.163.53.67@nist.gov'
  From = 'pi132.163.53.67@nist.gov'
  Recipients =['michael.allman@colorado.edu','shane.allman@nist.gov','3038823841@vtext.com', 'michael.allman777@gmail.com', 'nams@nist.gov', '3039166120@vtext.com']
  server = 'smtp.boulder.nist.gov'
  s = smtplib.SMTP(server)
  s.sendmail(From, Recipients, msg)


#  Need to log into the pi and check that the permission to the file below
#  are set for global read

def send_message(msg):
    print 'Problem: %s'%msg
    if EMAIL == True:
      sendEmail(msg)
def check():
    filename = '/mnt/hpdpi/ramcache/fridge_recent_temp.dat'
    """ Loop until we read a file with 10 values in it"""
    #print filename
    cntlen = 0
    while True:
        """  Loop until we can load the file """
        cnt = 0
        while True:
            try:
                #print 'try',filename 
                cnt = cnt + 1
                data = np.loadtxt(filename)
                bad = False
            except:
                print 'problem loading',cnt
                if cnt > 10:
                   send_message('Can not load temperature log')
                   return False
                else:
                   bad = True
            if not bad:
                break;    
        if len(data)==10:
            break;
        else:
            print 'problem getting 10 values from the log file',cnt
            cntlen = cntlen + 1
            if cntlen > 10:
                send_message('Can not load a temperature log with 10 values') 
    now = time.time()
    if abs(now-data[0]) > 600:
        send_message('Temp log is not being updated')
        return False
    if data[-1]<0.9:
        return True
    else:
        return False
  
if __name__ == '__main__':
    print check() 
#    print now-templogtime, templogtime - now
#    print len(data), data[-1]

#now = datetime.datetime.now()
#templogtime = datetime.datetime.fromtimestamp(data[0])

