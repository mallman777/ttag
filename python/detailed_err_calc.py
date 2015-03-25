# -*- coding: utf-8 -*-
"""
Created on Sun Mar  8 12:58:43 2015

@author: nams
"""
import numpy as np

data= np.loadtxt('SuccessProbPerRow.txt')
def build_grey(n):
    if n==1:
        return np.array([0,1])
    offset = 2**(n-1)
    prev_grey = build_grey(n-1)
    grey = np.hstack( (prev_grey, offset+prev_grey[::-1]))
    return grey
    
def biterr(x,y):
    return (bin(x^y).count('1'))
    
grey3 = build_grey(3)
greycode = np.array([])
# make greycode for each row (i.e. column is different by one bit)
for loop in range(len(grey3)):
    greycode = np.hstack((greycode, grey3))
# make each row different by one bit
greycode += 8*grey3.repeat(8)
fulldist=[]
for loop in range(len(greycode)):
    code = int(greycode[loop])
    dist=[]
    for elt in greycode:
        dist.append(biterr(code,int(elt)))
    fulldist.append(dist)
fulldist = np.array(fulldist,dtype=int)
all_err=[]
for loop in range(data.shape[0]):
    err=[]
    for dist in range(7):
        #print fulldist[loop][:]
        idx = np.where(fulldist[loop][:]==dist)[0]
        #print idx
        err.append(data[loop,idx].sum())
    all_err.append(err)
all_err = np.array(all_err)
    
        
