# -*- coding: utf-8 -*-
"""
Created on Tue Feb 24 06:43:03 2015

@author: nams
"""
import time,os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import scipy.optimize as opt
import numpy as np
import sys
import datetime
import argparse
import pickle

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

if __name__=='__main__':
    pickFileName = sys.argv[0].strip('.py') + '.pickle'
    if os.path.isfile(pickFileName):
      pickleFile = open(pickFileName, 'r')
      dataPath = pickle.load(pickleFile)
      pickleFile.close()
    else:
      fmt = '%Y_%m_%d'
      dataPath = '/hdd/%s/'%(datetime.datetime.today().strftime(fmt))

    parser = argparse.ArgumentParser(description = 'Pass in params.')
    parser.add_argument('-r', type = int, nargs = 1, help = 'run Number')
    parser.add_argument('-d', type = str, nargs = 1, help = 'run directory')
    args = parser.parse_args()
    if args.r and args.d:
      run = args.r[0]
      dataPath = args.d[0]
    elif args.r and not args.d:
      run = args.r[0]
      format = '%Y_%m_%d'
      dataPath = '/hdd/%s/run%02d/'%(datetime.datetime.today().strftime(format),run)
      print "dataPath: ", dataPath
    else:
      from pyqtgraph.Qt import QtGui, QtCore
      app = QtGui.QApplication([])
      fmt = '%Y_%m_%d'
      fileDirectory = QtGui.QFileDialog.getExistingDirectory(None,
         "Select Directory", dataPath)
      fileDirectory=str(fileDirectory).rstrip('/')
      runname = os.path.split(fileDirectory)[1]
      run = int(runname.strip('run'))
      dataPath = fileDirectory + '/'

    pickleFile = open(pickFileName, 'w')
    pickle.dump(dataPath, pickleFile)
    pickleFile.close()

    dsingle = np.loadtxt(dataPath + 'single_%d.txt'%run)
    #dcoin = np.loadtxt(dataPath + 'coin_%d.txt'%run)

    #  Pick whether to fit to coin data or singles data to determine nanowire positions
    data = dsingle
    print data.shape
    #
    data.shape=(data.shape[0]/8,64)
    norms = data.sum(axis=1)
    data.shape=(data.shape[0],8,8)
    #data = data[1:,:,:]
    # number of rows = number of columns
    #  compute number of rows/columns for use reshaping data 
    settings = np.loadtxt(dataPath + 'scanparameters.txt')
    nrows = int((settings[1] - settings[0])/settings[2] + 1)
    ncols = int((settings[4] - settings[3])/settings[5] + 1)
    print nrows, ncols
    #nrows = (data.shape[0])**0.5
    #nrows = 71
    #ncols = nrows
    #nrows = nrows-20
    x = np.arange(ncols)
    y = np.arange(nrows)
    x,y=np.meshgrid(x,y)
    fits=[]
    for pixel in range(0,64):
        p = pixel%64
        row = p/8
        col = p%8

        pk = data[:nrows*ncols,row,col]
        norms = norms[:nrows*ncols]        
        # fit to 2D gaussian
        colguess = np.argmax(pk)%ncols # x
        rowguess = np.argmax(pk)/nrows # y
        initial_guess = (np.max(pk),colguess,rowguess,2,2,0,0)
        popt, pcov = opt.curve_fit(twoD_Gaussian, (x, y), pk, p0=initial_guess, maxfev = 1000000, ftol = 1.4e-6, xtol = 1.4e-6)
        print "popt: ", popt
        fits.append(popt)
        data_fitted = twoD_Gaussian((x, y), *popt)
        plt.clf()
        fig = plt.figure(1)
        pk.shape=(nrows,ncols)
        data_fitted.shape=(nrows,ncols)
        #ax = fig.gca(projection='3d')
        #surf = ax.plot_surface(x, y, pk, rstride=1, cstride=1,
        #        linewidth=0, antialiased=False)
        #fitsurf = ax.plot_wireframe(x, y, data_fitted,color='k', rstride=1, cstride=1,
        #       linewidth=1, antialiased=False)
        #"""
        plt.imshow(pk)
        try:    
            plt.contour(x, y, data_fitted, 8, colors='k')
        except:
            print "Couldn't do contour"
        #"""
        plt.title('pixel %d'%pixel)
        plt.draw();
        plt.show(block=False)
        print "pixel: ", pixel
        time.sleep(0.1)
        raw_input('hit enter')
    fits = np.array(fits)
    np.savetxt(dataPath + 'interpSettings.txt',fits)
