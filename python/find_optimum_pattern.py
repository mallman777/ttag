import random
import numpy as np
phasemap = np.loadtxt('slm3381_at635_DVI.txt', dtype = np.uint32)
phasemap = phasemap[:,1]
SLMPath = './test/'
#  Need to makedirs the SLMPath if necessary

def initial_phase(x0,y0):
    pi = np.pi
    phase = np.zeros((512,512))
    k_x = 2*pi*np.arange(-256,256)/512.0
    k_y = 2*pi*np.arange(-256,256)/512.0


    #xo,yo = (1,1)
    for i in range(phase.shape[0]):
      phase[i,:] += k_x*xo
    for i in range(phase.shape[1]):
      phase[:,i] += k_y*yo

    phase = np.mod(phase,2*np.pi)
    return phase
def write2file(phase,filenumber):
    out = phasemap[((phase.ravel()/2/np.pi)*2**16).astype(np.uint32)]
    #print out[:2]
    #out = out.byteswap()
    out.tofile(SLMpath+'%d.txt'%filenumber)

filenumber = 0
phase = initial_phase(1,1)
write2file(phase,filenumber)
#  Start looping to search
while True:
# signal SLM computer via the serial port

# Wait for signal SLM computer

# Take data

# Analyze data and save relevant criteria  

#  Decide whether it is worth continuing to search

#  Generate new random matrix if not good enough...
    randMat = np.random.rand(512,512)*2*np.pi
    G = 0
    phase = phase + G*randMat

"""
out = phasemap[((phase.ravel()/2/np.pi)*2**16).astype(np.uint32)]
print out[:2]
#out = out.byteswap()
out.tofile('slmSetting2.txt')
"""
