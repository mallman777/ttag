import time
import scipy.optimize as opt
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import random

def twoD_Gaussian((x, y), amplitude, xo, yo, sigma_x, sigma_y, theta, offset):
    #   http://stackoverflow.com/questions/21566379/fitting-a-2d-gaussian-function-using-scipy-optimize-curve-fit-valueerror-and-m
    xo = float(xo)
    yo = float(yo)    
    a = (np.cos(theta)**2)/(2*sigma_x**2) + (np.sin(theta)**2)/(2*sigma_y**2)
    b = -(np.sin(2*theta))/(4*sigma_x**2) + (np.sin(2*theta))/(4*sigma_y**2)
    c = (np.sin(theta)**2)/(2*sigma_x**2) + (np.cos(theta)**2)/(2*sigma_y**2)
    g = offset + amplitude*np.exp( - (a*((x-xo)**2) + 2*b*(x-xo)*(y-yo) 
                            + c*((y-yo)**2)))
    return g
def twoD_Gaussian_fit((x, y), amplitude, xo, yo, sigma_x, sigma_y, theta, offset):
    ret = twoD_Gaussian((x, y), amplitude, xo, yo, sigma_x, sigma_y, theta, offset)
    return ret.ravel()
def plotimage(zmag):
        fig = plt.figure()
        fig.clf()
        ax = fig.gca(projection='3d')
        #surf = ax.plot_surface(x, y, pk, rstride=1, cstride=1,
        #            linewidth=0, antialiased=False)
        surf = ax.plot_wireframe(x, y, zmag,color='k', rstride=1, cstride=1,
                    linewidth=1, antialiased=False)
        plt.title('image_plane image, loop:%d'%loop)
        plt.draw()
        plt.show()
        initial_guess = (np.max(zmag),x0,y0,2,2,0,0)
        popt, pcov = opt.curve_fit(twoD_Gaussian_fit, (x, y), zmag.ravel(), p0=initial_guess)
        print 'popt',popt
normT = 100
def get_rnd(T):
    noise = np.random.rand(nrows,nrows)*2*np.pi
    noise = noise * T/normT

nrows=64
x = np.arange(nrows)
y = np.arange(nrows)
x,y=np.meshgrid(x,y)

x = x-nrows/2
y = y-nrows/2

x0 = 10
y0 = 5

y0_idx = y0+nrows/2
x0_idx = x0+nrows/2
phase_xslope = -2.*np.pi / nrows * x0
phase_yslope = -2.*np.pi / nrows * y0
phase= phase_xslope * x + phase_yslope * y
phase = np.mod(phase,2*np.pi)

slm_noise = np.random.rand(nrows,nrows)*2*np.pi/1.5
#print phase
fft_phase = phase + 0*slm_noise
fft_phase = np.mod(fft_phase,2*np.pi)
target = [1, x0, y0, 3.395, 3.395, 0, 0]
target_image = twoD_Gaussian((x, y), *target)
loop = 0;
#
# compute initial value
#
# Compute complete image in fft_plane  (Z)
Z = np.exp(1j*fft_phase) 
print abs(Z).sum()
#  Use fftshift to move the origin to the zero index for the fft 
Z = np.fft.fftshift(Z)

# Compute image in image_plane using fft2
z = np.fft.ifft2(Z)
print abs(z).sum()
zmag = np.fft.ifftshift(abs(z))

# See result in image plane
plotimage(zmag)
Jprev  = zmag[y0_idx, x0_idx]
bestJ = []
bestPhase = []
bestJ.append(Jprev)
bestPhase.append(fft_phase)
if False:
#if True:
#while T > 10:
    for loop in range(numTries):
        rnd = get_rnd(T)
        new_phase = np.mod(fft_phase+rnd, 2*np.pi)
        # Compute complete image in fft_plane  (Z)
        Z = np.exp(1j*new_phase) 
        #  Use fftshift to move the origin to the zero index for the fft 
        Z = np.fft.fftshift(Z)
        # Compute image in image_plane using fft2
        z = np.fft.ifft2(Z)
        zmag = np.fft.ifftshift(abs(z))
        # See result in image plane
        #plotimage(zmag)
        
        J  = zmag[y0_idx, x0_idx]
        if J > Jprev:
            # update pattern
            fft_phase = new_phase
            if J > bestJ[-1]:
                bestJ.append(J)
                bestPhase.append(new_phase)
        else:
            if jump(T):
                fft_phase = new_phase
    T -= 1
"""
  while T > 2:
    SACIT = T * iTslope + iToffset 
    for i in range(numTries):
      setPatt(patt):
      cnts = getCnts()
      randPatt = getRandPatt(G,T)
      pertPatt = patt + randPatt
      setPatt(pertPatt)
      cntsPert = getCnts()
      delCnts = cntsPert - cnts
      if delCnts >= SACIT:
        patt = pertPatt
        if cntsPert > np.max(bestCnts):
          bestCnts.append(cntsPert)
          bestPatt.append(np.reshape(pertPatt, (1,-1)))
      else:
        PA = np.exp[-(np.abs(delCnts) + SACIT)*k/T]
        randNum = random.randint(0,100)/100.0
        if randNum <= PA:
          patt = pertPatt
    T -= 1    
    #  Compute phase in image plane
"""
