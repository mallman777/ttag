# -*- coding: utf-8 -*-
"""
Created on Thu Dec 11 11:40:45 2014

@author: qittlab
"""

import random
import numpy as np

def getNextChannelIndex(tagArr, chanArr, curIndex, chan, minTime, minIndex):
    if (curIndex > minIndex):
        curIndex -= 1
        while ((curIndex > minIndex) & (tagArr[curIndex] >= minTime)):
            if (chanArr[curIndex] == chan):
                if (curIndex > 0):
                    return curIndex
                else:
                    return 2**60
            curIndex -= 1
    if ((curIndex == minIndex) & (curIndex >= int(0)) & (tagArr[curIndex] >= minTime)):
        if (chanArr[curIndex] == chan):
            return curIndex
    return 2**60
    
def getMinChannel(tagArr, chanArr, chanMax, chanIndex, numChans):
    mini = -1
    minD = 2**60
    for i in range(numChans):
        if (chanIndex[i] != 2**60):
            if ((chanMax[i] - tagArr[chanIndex[i]]) < minD):
                mini = i
                minD = chanMax[i] - tagArr[chanIndex[i]]
    return mini
    
            
arrSize = int(1e6)
ttags = np.empty(arrSize, dtype = np.uint64)
ttags = np.reshape(ttags, [2,-1])
chans = np.empty(arrSize, dtype = np.uint8)
chans = np.reshape(chans, [2,-1])
numChans = 16
tag = 0
res = 10e-9
radius = int(20e-9/res)
timeBins = int(10e-3/res)

for i in range(np.shape(ttags)[1]):
    tag += random.randint(30000,40000)
    ttags[0,i] = tag
    ttags[1,i] = tag
    chans[0,i] = random.randint(0,7)
    chans[1,i] = random.randint(8,15)
    
ttags = np.reshape(ttags, arrSize, order = 'F')
chans = np.reshape(chans, arrSize, order = 'F')    

chanIndex = np.empty(numChans, dtype = np.uint64)
chanMin = np.empty(numChans, dtype = np.uint64)
chanMax = np.empty(numChans, dtype = np.uint64)

#Find channel iterator locations and set the bounds for chan times

for i in range(numChans):
    chanIndex[i] = int(arrSize-1)
    chanMax[i] = ttags[-1]
    chanMin[i] = chanMax[i] - timeBins
    
#Now make sure channel indices are pointing to correct channels

for i in range(numChans):
    if (chanIndex[i] != 2**60):
        if (i != chans[chanIndex[i]]):
            chanIndex[i] = getNextChannelIndex(ttags, chans, chanIndex[i], i, chanMin[i], 0)
        
i = getMinChannel(ttags, chans, chanMax, chanIndex, numChans)

coincidenceMatrix = np.zeros([numChans, numChans], dtype = np.uint32)
while (i!=-1):
    for j in range(numChans):
        if (chanIndex[j]!=2**60):
            if (chanMax[i] - ttags[chanIndex[i]] + radius >= chanMax[j] - ttags[chanIndex[j]]):
                coincidenceMatrix[i,j] += 1
                if (i!=j):
                   coincidenceMatrix[j,i] += 1 
    chanIndex[i] = getNextChannelIndex(ttags, chans, chanIndex[i], i, chanMin[i], 0)
    i = getMinChannel(ttags, chans, chanMax, chanIndex, numChans)

subMat = coincidenceMatrix[0:8,8::]
subTtags = ttags[ttags >= chanMin[0]]
print "Len of data to coin over: ", len(subTtags)
print "Total Coincidences: ", np.sum(np.sum(subMat))
print chans[-20:]
print ttags[-20:]

    