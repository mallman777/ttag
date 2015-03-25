import random
import numpy as np
pi = np.pi
phase = np.zeros((512,512))
k_x = 2*pi*np.arange(-256,256)/512.0
k_y = 2*pi*np.arange(-256,256)/512.0

x = np.loadtxt('slm3381_at635_DVI.txt', dtype = np.uint32)

xo,yo = (1,1)
for i in range(phase.shape[0]):
  phase[i,:] += k_x*xo
for i in range(phase.shape[1]):
  phase[:,i] += k_y*yo

randMat = np.random.rand(512,512)*2*np.pi
G = 0
phase = phase + G*randMat
phase = np.mod(phase,2*np.pi)
x = x[:,1]

out = x[((phase.ravel()/2/np.pi)*2**16).astype(np.uint32)]
print out[:2]
#out = out.byteswap()
out.tofile('slmSetting2.txt')





