import random
import numpy as np
import ttag
import matplotlib.pyplot as plt

pi = np.pi
x = np.loadtxt('slm3381_at635_DVI.txt', dtype = np.uint32)

def getPatt(xo,yo, res):
  phase = np.zeros((res,res))
  k_x = 2*pi*np.arange(-res/2,res/2)/res
  k_y = 2*pi*np.arange(-res/2,res/2)/res
  for i in range(phase.shape[0]):
    phase[i,:] += k_x*xo
  for i in range(phase.shape[1]):
    phase[:,i] += k_y*yo
  phase = np.mod(phase,2*pi)
  return phase
  
def getBlockPatt(res):
  phase = np.zeros((res,res))
  idx = np.arange(-res/2,res/2)
  bool = np.abs(idx) < 10
  for i in range(np.shape(phase)[0]):
    if np.abs(idx[i]) < 10:      
      phase[bool,i] = np.pi
  phase = np.mod(phase,2*pi)
  return phase 

def getRandPatt(G,T, res):
  return G*T*np.random.rand(res,res)*2*pi

def getCnts(pix,Tacq, CoincidenceWindow, gate, heraldChan, buf):
  buf.start()
  time.sleep(Tacq + 0.5*Tacq)
  buf.stop()
  x = buf.coincidences(Tacq, CoincidenceWindow, gate = gate, heraldChan = heraldChan)
  cnts = x[0:8,8:16]
  row = pix / 8
  col = pix % 8
  return cnts[row,col]

if __name__ == '__main__':
  T = 100
  G = 1
  SACIT_start = 100
  SACIT_stop = 10
  iTslope = (SACIT_start - SACIT_stop)/(T-1)
  iToffset = -T*iTslope + SACIT_start
  DC = 1 #Choose this such that you have a roughly 50% chance of keeping a "bad" pattern when T = 100
  k = -T*np.log(0.5)
  numTries = 100
    
  bestCnts = []
  bestPatt = []
  res = 100
  xo,yo = (0,0)
  patt = getPatt(xo,yo,res)
  randPatt = getRandPatt(1,1, res)
  E = (1.0/res**2)*np.exp(1j*(patt))
  EFFT = np.fft.fft2(E)
  EFFT = np.fft.fftshift(EFFT)
  I = np.absolute(EFFT)**2
  plt.subplot(2,1,1)
  plt.pcolor(patt)
  plt.subplot(2,1,2)
  plt.pcolor(I)
  plt.show()
  print np.sum(I)
  while False:#T > 2:
    SACIT = T * iTslope + iToffset 
    for i in range(numTries):
      cnts = getCnts(patt)
      randPatt = getRandPatt(G,T)
      pertPatt = patt + randPatt
      pertCnts = getCnts(pertPatt)
      delCnts = cnts - pertCnts
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
  bestCnts = np.array([bestCnts])
  bestPatt = np.array([bestPatt])         
