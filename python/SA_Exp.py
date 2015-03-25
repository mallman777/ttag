import time
import scipy.optimize as opt
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import random
import ttag
import gen_find_nano_patterns as gp
import serial
import math
PC = True

phasemap = np.loadtxt('slm3381_at635_DVI.txt', dtype = np.uint32)
phasemap = phasemap[:,1]

def startTagger():
  ttnumber = ttag.getfreebuffer()-1
  print "ttnumber: ", ttnumber
  buf = ttag.TTBuffer(ttnumber)  #Opens the buffer
  return buf

def getCnts(pix, Tacq, CoincidenceWindow, buf):
  buf.start()
  time.sleep(Tacq + 0.1*Tacq)
  buf.stop()
  x = buf.coincidences(Tacq, CoincidenceWindow)
  cnts = x[0:8,8:16]
  norm = cnts.sum()
  #print 'norm',norm
  row = pix / 8
  col = pix % 8
  return 1.0*cnts[row,col]/norm

serialport = serial.Serial('/dev/ttyUSB0',38400,timeout=0.05)

def waitforPC():
    #print 'Waiting for msg from PC'
    msgin = ''
    while (msgin == ''):
        msgin = serialport.read(80);
    #print 'msg from PC: %s' %msgin 
    return msgin

def sendtoPC(count):
    #print 'Sending photon num: %d'%count
    serialport.write('%d'%count)

if PC==True:
    wait = waitforPC
    send = sendtoPC
else:
    wait = fakewait
    send = fakesend

##################################################
# Simulated Annealing
##################################################
# Number of cycles
n = 50
# Number of trials per cycle
tries_per_cycle = 500
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

buf = startTagger()
Tacq = 0.25  # need to change to shorter 
CoincidenceWindow = 10e-9

# Run the SA algorithm
send(11)
msg = wait()
print 'msg from PC',msg
pix = int(msg)
print 'pix',pix

interpSettings = gp.getInterpSettings()
xo,yo = (interpSettings[pix,0], interpSettings[pix,1])
fft_phase = gp.initial_phase_orig(257-xo,257-yo, 512)
#fft_phase = gp.initial_phase(xo,yo, 512)
fprev = getCnts(pix, Tacq, CoincidenceWindow,buf) 
list_phases=[fft_phase]
list_f = [fprev]
nrows = 64
thresh = 0.95
pertPath =  "/mnt/SLM/Dan/OptimizeSLM/Patterns/PerturbSettings/"
for loopT in range(n):
    print 'Cycle: %d with Temperature: %.2f f:%f'%(loopT, t, fprev) 
    for loop in range(tries_per_cycle):
        rnd = gp.get_rnd(2800,nrows)
        new_phase = np.mod(fft_phase+rnd, 2*np.pi)
        gp.write2file(new_phase, phasemap, pertPath, '%d'%pix)
        send(pix)
        msg = wait()
        f = getCnts(pix, Tacq, CoincidenceWindow, buf)
        print 'loopT: %d, fprev %.3f, Current f: %f'%(loopT, fprev, f)
        DeltaE = abs(f-fprev)
	# Initialize DeltaE_avg if a worse solution was found
	#   on the first iteration
	if (loopT==0 and loop==0): DeltaE_avg = DeltaE

        if f < fprev:
            # instead of minimize in conventional SA, look for maximum
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
        if f > thresh:
          break
    # Record the best values at the end of every cycle
    list_phases.append(fft_phase)
    list_f.append(fprev)
    #print 'Current f',fprev
    # Lower the temperature for next cycle
    t = frac * t
    if f > thresh:
      break
send(-1)
list_phases = np.array(list_phases)
list_f = np.array(list_f)
SLM_path = '/mnt/SLM/Dan/OptimizeSLM/Patterns/'
list_phases.tofile(SLM_path + 'pix%02d_list_phases.bin'%pix)
list_f.tofile(SLM_path + 'pix_%02d_list_f.bin'%pix)
            
