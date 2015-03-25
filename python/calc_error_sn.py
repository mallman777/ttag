# -*- coding: utf-8 -*-
"""
Created on Tue Feb 24 06:43:03 2015

@author: nams
"""
import time
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import scipy.optimize as opt
import numpy as np
import sys
def twoD_Gaussian((x, y), amplitude, xo, yo, sigma_x, sigma_y, theta, offset):
    #   http://stackoverflow.com/questions/21566379/fitting-a-2d-gaussian-function-using-scipy-optimize-curve-fit-valueerror-and-m
    xo = float(xo)
    yo = float(yo)    
    a = (np.cos(theta)**2)/(2*sigma_x**2) + (np.sin(theta)**2)/(2*sigma_y**2)
    b = -(np.sin(2*theta))/(4*sigma_x**2) + (np.sin(2*theta))/(4*sigma_y**2)
    c = (np.sin(theta)**2)/(2*sigma_x**2) + (np.cos(theta)**2)/(2*sigma_y**2)
    g = offset + amplitude*np.exp( - (a*((x-xo)**2) + 2*b*(x-xo)*(y-yo) 
                            + c*((y-yo)**2)))
    return g.ravel()

#data = np.load('tmp.npz')
#run = int(sys.argv[1])
run = 14
format = '%Y_%m_%d'
#dataPath = '/hdd/%s/run%d/'%(datetime.datetime.today().strftime(format),run)
dataPath = "/hdd/2015_02_26/run%02d/"%run

dsingle = np.loadtxt(dataPath + 'single_%d.txt'%run)
dcoin = np.loadtxt(dataPath + 'coin_%d.txt'%run)

#  Pick whether to fit to coin data or singles data to determine nanowire positions

def calc_xtalk_nn(d,row,col):
    fullxtalk = []
    xtalk = 0
    if row>0:
        xtalk = d[row-1, col]
    fullxtalk.append(xtalk)
    if row<7:
        xtalk = d[row+1, col]
    else:
        xtalk = 0
    fullxtalk.append(xtalk)
    if col>0:
        xtalk = d[row, col-1]
    else:
        xtalk = 0
    fullxtalk.append(xtalk)
    if col<7:
        xtalk = d[row, col+1]
    else:
        xtalk = 0
    fullxtalk.append(xtalk)
    return np.array(fullxtalk)
def compute_stuff(data, row, col):
    nn = calc_xtalk_nn(data,row,col).sum()    
    return data[row,col], data.sum(), nn
#dsingle = single
#dcoin = coin
dsingle.shape=(dsingle.shape[0]/8,8,8)
dcoin.shape = dsingle.shape
single = []
coin = []
for pixel in range(64):
    p = pixel%64
    row = p/8
    col = p%8
    idx = pixel
    row_single = compute_stuff(dsingle[idx], row,col)       
    row_coin = compute_stuff(dcoin[idx], row,col)       
    single.append(row_single)
    coin.append(row_coin)
    
single = np.array(single)
coin = np.array(coin)
