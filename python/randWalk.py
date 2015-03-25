import random
import numpy as np
import ttag

pi = np.pi
x = np.loadtxt('slm3381_at635_DVI.txt', dtype = np.uint32)

def getPatt(xo,yo):
  phase = np.zeros((512,512))
  k_x = 2*pi*np.arange(-256,256)/512.0
  k_y = 2*pi*np.arange(-256,256)/512.0
  xo,yo = (1,1)
  for i in range(phase.shape[0]):
    phase[i,:] += k_x*xo
  for i in range(phase.shape[1]):
    phase[:,i] += k_y*yo
  phase = np.mod(phase,2*pi)
  return phase

def getRandPatt(G,T):
  return G*T*np.random.rand(512,512)*2*pi

def setPatt(phase):
  x = x[:,1]
  out = x[((phase.ravel()/2/np.pi)*2**16).astype(np.uint32)]
  #out = out.byteswap()
  out.tofile('slm.bin')

def startTagger():
  ttnumber = ttag.getfreebuffer()-1
  print "ttnumber: ", ttnumber
  buf = ttag.TTBuffer(ttnumber)  #Opens the buffer
  return buf

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
  gate = 10e-9
  coinWindow = 10e-9
  heraldChan = 0
  Tacq = 1
  buf = startTagger()

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
  patt = getPatt(xo,yo)
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
  bestCnts = np.array([bestCnts])
  bestPatt = np.array([bestPatt])         
