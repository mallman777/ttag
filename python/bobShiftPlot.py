# -*- coding: utf-8 -*-
"""
Created on Fri Mar 13 14:28:23 2015

@author: qittlab
"""
import numpy as np
import matplotlib.pyplot as plt

pixel = 27
data = np.loadtxt('/hdd/2015_03_17/run05/single_5_ccode.txt')
data = np.reshape(data, (-1,64))
pk = data[:,pixel]
pk.shape = (21,21)
norms = data.sum(axis = 1)
norms.shape = (21,21)
normPk = pk/norms
amax =  np.argmax(normPk)
xshift = amax / 21
yshift = amax % 21
print xshift, yshift
plt.figure(1)
plt.clf()
plt.imshow(pk)
plt.title('%d'%pixel)
plt.figure(2)
plt.imshow(normPk)
plt.title('%d'%pixel)
plt.show()
