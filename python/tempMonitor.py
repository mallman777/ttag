import temper
import time
import sys
import numpy as np
import datetime
import smtplib

def sendEmail(msg):
  print "Trying to send email"
  From = 'qittlab132.163.53.40@nist.gov'
  Recipients = ['michael.allman@colorado.edu', 'shane.allman@nist.gov', '3039166120@vtext.com', 'michael.allman777@gmail.com', 'nams@nist.gov']  
  server = 'smtp.boulder.nist.gov'
  s = smtplib.SMTP(server)
  s.sendmail(From, Recipients, msg)

if __name__ == "__main__":
  th = temper.TemperHandler()
  devices = th.get_devices()
  dataPath = '/mnt/odrive/HPD/Temperature_logs/'
  format = '%Y_%m_%d_%H_%M_%S'
  timestamp = datetime.datetime.now().strftime(format)
  cnt = 0
  with open(dataPath + '%s_usbProbes.txt'%timestamp, 'a') as f:
    try:
      while True:
        temps = []
        temps.append(time.time())
        for dev in devices:
          temps.append(dev.get_temperature())
        temps = np.array([temps])
        if cnt % 1 == 0 and cnt != 0: 
          np.savetxt(sys.stdout, temps, '%1.2f')
        np.savetxt(f, temps, '%1.2f')
        cnt += 1
        time.sleep(10*60)
    finally:
      sendEmail('Temp probes logger terminated') 



