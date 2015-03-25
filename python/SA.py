import time
import scipy.optimize as opt
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import random
import gen_find_nano_patterns as gp

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
        #fig = plt.figure()
        #fig.clf()
        ax = plt.gca(projection='3d')
        #surf = ax.plot_surface(x, y, pk, rstride=1, cstride=1,
        #            linewidth=0, antialiased=False)
        surf = ax.plot_wireframe(x, y, zmag,color='k', rstride=1, cstride=1,
                    linewidth=1, antialiased=False)
        plt.title('image_plane image, loop:%d'%loop)
        plt.draw()
        plt.show()
        #initial_guess = (np.max(zmag),x0,y0,2,2,0,0)
        #popt, pcov = opt.curve_fit(twoD_Gaussian_fit, (x, y), zmag.ravel(), p0=initial_guess)
        #print 'popt',popt

def get_rnd(T):
    noise = np.random.rand(nrows,nrows)*2*np.pi/100.
    #noise = noise * T/normT
    return noise

def image(phase):
    # Compute complete image in fft_plane  (Z)
    Z = np.exp(1j*phase) 
    #  Use fftshift to move the origin to the zero index for the fft 
    Z = np.fft.fftshift(Z)    
    # Compute image in image_plane using fft2
    z = np.fft.ifft2(Z)
    zmag = np.fft.ifftshift(abs(z))
    return zmag
def measure(zmag):
    global y0_idx, x0_idx
    return zmag[y0_idx, x0_idx]
    
nrows = 512
x0,y0 = (100,50)
phase = gp.initial_phase(x0,y0, nrows)

nrows = 64
T = 2.8
slm_noise = gp.get_rnd(T,nrows)
#print phase
fft_phase = phase + 1*slm_noise
fft_phase = np.mod(fft_phase,2*np.pi)
target = [1, x0, y0, 3.395, 3.395, 0, 0]
#target_image = twoD_Gaussian((x, y), *target)
loop = 0;
#
# compute initial value
#
zmag = image(fft_phase)
# See result in image plane
#plt.figure(1)
#plt.clf()
#plt.subplot(2,1,1)
nrows = 512
x = np.arange(nrows)
y = np.arange(nrows)
x,y = np.meshgrid(x,y)
x = x-(nrows/2)-1
y = y-(nrows/2)-1
y0_idx = y0+nrows/2
x0_idx = x0+nrows/2
#plotimage(zmag)

fprev  = measure(zmag)
list_phases=[fft_phase]
list_f = [fprev]
print 'Start f',fprev
##################################################
# Simulated Annealing
##################################################
# Number of cycles
n = 50
# Number of trials per cycle
tries_per_cycle = 100
# Number of accepted solutions
na = 0
# Probability of accepting worse solution at the start
p1 = 0.5
# Probability of accepting worse solution at the end
p50 = 0.001
# Initial temperature
t1 = -1.0/math.log(p1)
# Final temperature
t50 = -1.0/math.log(p50)
# Fractional reduction every cycle
frac = (t50/t1)**(1.0/(n-1.0))
# Current temperature
t = t1
nrows = 64

for loopT in range(n):
    print 'Cycle: %d with Temperature: %.2f f:%f'%(loopT, t, fprev) 
    for loop in range(tries_per_cycle):
        rnd = gp.get_rnd(280, nrows)
        new_phase = np.mod(fft_phase+rnd, 2*np.pi)
        zmag = image(new_phase)
        # See result in image plane
        #plotimage(zmag)
        f  = measure(zmag)
        DeltaE = abs(f-fprev)
        if f < fprev:
            # instead of minimize in conventional SA, look for maximum
            # Initialize DeltaE_avg if a worse solution was found
            #   on the first iteration
            if (loopT==0 and loop==0): DeltaE_avg = DeltaE
            # objective function is worse
            # generate probability of acceptance
            p = math.exp(-DeltaE/(DeltaE_avg * t))
            # determine whether to accept worse point
            if (random.random()<p):
                # accept the worse solution
                accept = True
            else:
                # don't accept the worse solution
                accept = False
        else:
            # objective function is lower, automatically accept
            accept = True
        if (accept==True):
            # update currently accepted solution
            fft_phase = new_phase
            fprev = f
            # increment number of accepted solutions
            na += 1.
            # update DeltaE_avg
            DeltaE_avg = (DeltaE_avg * (na-1.0) +  DeltaE) / na
    # Record the best values at the end of every cycle
    list_phases.append(fft_phase)
    list_f.append(fprev)
    #print 'Current f',fprev
    # Lower the temperature for next cycle
    t = frac * t

print "na: ", na            
zmag = image(fft_phase)
plt.figure(1)
plt.subplot(2,1,2)
plotimage(zmag)

