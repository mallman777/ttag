# -*- coding: utf-8 -*-
"""
Created on Thu Dec 18 11:39:28 2014

@author: qittlab
"""

import ttag
import numpy as np
import random
import time
import matplotlib.pyplot as plt

# Load fake data into buffer.

if True:
    bufNum = ttag.getfreebuffer()
    bufSize = 100000000
    buf = ttag.TTBuffer(bufNum, create = True, datapoints = bufSize)
    buf.resolution = 156e-12
    buf.channels = 16

    res = buf.resolution
    rate = 10e-6
    dr = 50e-9
    tag = 0
    buf.add(random.randint(0,7), tag)
    buf.add(random.randint(8,15), tag)

    to = time.time()
    while (buf[-1][1] <= 1.2):
        #print buf[-1][1]
        tag += random.randint(int((rate-dr)/res), int((rate+dr)/res))
        buf.add(random.randint(0,7), tag)
        buf.add(random.randint(8,15), tag)
        tf = time.time()
    print "Time to fill buffer: ", tf-to
        
# Buffer is now loaded with fake data.  Now do analysis on it and compare times.

radius = 1e-9
delays = np.zeros(16)
t = np.linspace(0.01,1,10)
runTimes = np.zeros([4,len(t)])

for i in range(len(t)):
    to = time.time()
    x = buf.coincidences(t[i], radius)
    tf = time.time()
    runTimes[0,i] = tf-to
    to = time.time()
    x = buf.coincidences(t[i], radius, delays)
    tf = time.time()
    runTimes[1,i] = tf-to
    to = time.time()
    chans, times = buf.coincidenceTimes(t[i], radius)
    tf = time.time()
    runTimes[2,i] = tf-to
    to = time.time()
    chans, times = buf.coincidenceTimes2(t[i], radius)
    tf = time.time()
    runTimes[3,i] = tf-to

plt.figure(1)
plt.plot(t*1e3,runTimes[0], 'k', label = 'No Delays')
plt.plot(t*1e3,runTimes[1], 'r', label = 'With Delays')
plt.plot(t*1e3,runTimes[2], 'b', label = 'CoincidenceTimes')
plt.plot(t*1e3,runTimes[3], 'g', label = 'CoincidenceTimes2')
plt.xlabel('Integration Time(ms)')
plt.ylabel('Run Time(s)')
plt.title('Comparison of Coincidence functions')
plt.legend(loc = 'upper left')
#plt.savefig('CoincidenceCompare5.png')
plt.figure(2)
plt.plot(t*1e3,(runTimes[1]/runTimes[0]), 'r', label = 'With Delays')
plt.plot(t*1e3,(runTimes[2]/runTimes[0]), 'b', label = 'Coincidence Times')
plt.xlabel('Integration Time(ms)')
plt.ylabel('Relative to No Delays')
plt.axis([t[0]*1e3, t[-1]*1e3, 0, 10])
plt.legend(loc = 'lower left')
#plt.savefig('CoincidenceCompare6.png')
plt.show()

if True:
    for i in range(100):
        print "Deleting buffers"
        ttag.deletebuffer(i)
    

